import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import types
import unittest
from unittest.mock import patch
from reviewed_workflow_handoff import reviewed_policy, session_class, encoded, sha


def fixture_policy():
    old = {'schema':1, 'root':'/synthetic/checkout', 'contract':{'protected_files':['tools/work_session.py','tools/test_work_session.py']},
           'pins':{'tools/work_session.py':'a'*64,'tools/test_work_session.py':'b'*64},
           'controller_sha':'a'*64,'checker_sha':'e'*64,'dependency_fingerprint':'f'*64,
           'author_email':'fixture@example.invalid','approved_at':'old fixture'}
    future=copy.deepcopy(old);future['controller_sha']='c'*64;future['pins']={'tools/work_session.py':'c'*64,'tools/test_work_session.py':'d'*64}
    future['approved_at']='reviewed fixture'
    future['transition_review']={'reviewed':True,'from_head':'1'*40,'to_head':'2'*40}
    plan={'schema':1,'reviewed':True,'root':old['root'],'from_head':'1'*40,'to_head':'2'*40,'future_policy':future,
          'protected_changes':{k:{'before':old['pins'][k],'after':future['pins'][k]} for k in old['pins']}}
    return old,plan


class HandoffTests(unittest.TestCase):
    def test_unreviewed_or_mismatched_target_cannot_approve_policy(self):
        old,plan=fixture_policy()
        for key,value in [('reviewed',False),('to_head','3'*40)]:
            bad=copy.deepcopy(plan);bad[key]=value
            with self.assertRaises(ValueError):reviewed_policy(old,bad)
        self.assertEqual(reviewed_policy(old,plan),plan['future_policy'])

    def test_dependencies_contract_identity_and_unlisted_pins_stay_frozen(self):
        old,plan=fixture_policy()
        for key,value in [('dependency_fingerprint','0'*64),('author_email','other@example.invalid'),('contract',{})]:
            bad=copy.deepcopy(plan);bad['future_policy'][key]=value
            with self.assertRaisesRegex(ValueError,'NON_CONTROL_POLICY_CHANGE_NOT_ADMITTED'):reviewed_policy(old,bad)
        bad=copy.deepcopy(plan);bad['future_policy']['pins']['new.py']='0'*64
        with self.assertRaises(ValueError):reviewed_policy(old,bad)

    def test_validation_failure_restores_operative_policy_without_promotion(self):
        old,plan=fixture_policy()
        class Blocked(Exception):pass
        class Base:
            def __init__(self):self.cfg=copy.deepcopy(old)
            def text(self,*args):return plan['to_head']
            def validate(self,revision):
                if self.cfg != plan['future_policy']:raise AssertionError('candidate not validated against the review')
                raise Blocked('SYNTHETIC_VALIDATION_FAILURE')
        with tempfile.TemporaryDirectory() as temp:
            config=Path(temp)/'config.json';config.write_bytes(encoded(old));config.chmod(0o600)
            module=types.SimpleNamespace(Session=Base,Blocked=Blocked)
            cls=session_class(module,plan,config,'0'*64);session=cls()
            with self.assertRaisesRegex(Blocked,'SYNTHETIC_VALIDATION_FAILURE'):session.validate('candidate')
            self.assertEqual(session.cfg,old);self.assertEqual(config.read_bytes(),encoded(old))

    def test_policy_changed_after_review_blocks_before_fetch(self):
        old,plan=fixture_policy()
        class Blocked(Exception):pass
        class Base:
            def __init__(self):self.cfg=copy.deepcopy(old)
            def load(self):pass
            def text(self,*args):return plan['from_head']
        with tempfile.TemporaryDirectory() as temp:
            config=Path(temp)/'config.json';config.write_bytes(encoded(old));config.chmod(0o600)
            plan['policy_before_sha256']=sha(config.read_bytes());config.write_bytes(encoded({'changed':'fixture'}))
            cls=session_class(types.SimpleNamespace(Session=Base,Blocked=Blocked),plan,config,'0'*64)
            with self.assertRaisesRegex(Blocked,'POLICY_CHANGED_AFTER_REVIEW'):cls().load()

    def test_real_git_validates_then_applies_and_promotes_only_the_reviewed_blob(self):
        tools=Path(__file__).resolve().parents[1]
        sys.path.insert(0,str(tools))
        workflow=importlib.import_module('work_session')
        cases=importlib.import_module('test_work_session')
        case=cases.WorkflowIntegration('test_private_configuration');case.setUp()
        try:
            (case.repo/'tools').mkdir()
            for name in ('work_session.py','check_env.py','test_work_session.py'):
                (case.repo/'tools'/name).write_bytes((tools/name).read_bytes())
            contract=json.loads((case.repo/'.mestry-workflow.json').read_text())
            contract['allowed_prefixes'].append('tools/')
            contract['protected_files'] += ['tools/work_session.py','tools/test_work_session.py']
            (case.repo/'.mestry-workflow.json').write_text(json.dumps(contract))
            case.run_git(case.repo,'add','tools','.mestry-workflow.json');case.run_git(case.repo,'commit','-qm','Admit fixture controls');case.run_git(case.repo,'push','-q','origin','main')
            case.command('configure','--review-policy')
            before=case.head();config=case.state/'config.json';old=json.loads(config.read_text());old_bytes=config.read_bytes()
            case.peer_commit('tools/work_session.py',(tools/'work_session.py').read_text()+'\n# reviewed fixture controller revision\n')
            target=case.peer_commit('tools/test_work_session.py',(tools/'test_work_session.py').read_text()+'\n# reviewed fixture test revision\n')
            future=copy.deepcopy(old)
            case.run_git(case.repo,'fetch','-q','origin','main')
            for name in ('tools/work_session.py','tools/test_work_session.py'):
                body=subprocess.check_output(['git','show',target+':'+name],cwd=case.repo)
                future['pins'][name]=sha(body)
            future['controller_sha']=future['pins']['tools/work_session.py'];future['approved_at']='reviewed fixture'
            future['transition_review']={'reviewed':True,'from_head':before,'to_head':target}
            plan={'schema':1,'reviewed':True,'root':str(case.repo),'from_head':before,'to_head':target,
                  'policy_before_sha256':sha(old_bytes),'future_policy':future,
                  'protected_changes':{k:{'before':old['pins'][k],'after':future['pins'][k]} for k in old['pins'] if old['pins'][k]!=future['pins'][k]}}
            plan['state_root']=str(case.storage)
            plan_file=case.base/'review.json';plan_file.write_bytes(encoded(plan));plan_file.chmod(0o600)
            adapter=Path(__file__).with_name('reviewed_workflow_handoff.py')
            process=subprocess.Popen([sys.executable,'-B',str(adapter),'--plan',str(plan_file),'--plan-sha256',sha(plan_file.read_bytes()),'--','-B',str(case.repo/'tools/work_session.py'),'--repo',str(case.repo),'--state-root',str(case.storage),'lease'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                ready=json.loads(process.stdout.readline())
                self.assertEqual(ready['state'],'LEASE_READY',ready)
                result=ready
                output,error=process.communicate('release\n',timeout=20)
                self.assertEqual(process.returncode,0,(output,error))
            finally:
                if process.poll() is None:process.communicate('release\n',timeout=20)
            state=json.loads((case.state/'status.json').read_text())
            self.assertTrue(result['applied']);self.assertEqual(case.head(),target)
            self.assertEqual(json.loads(config.read_text()),future)
            self.assertEqual(config.stat().st_mode & 0o777,0o600)
            self.assertTrue((case.state/('handoff-'+target+'.json')).is_file())
            self.assertEqual(state['validation']['tree'],case.run_git(case.repo,'rev-parse','HEAD^{tree}'))
            self.assertEqual(state['phase'],'idle')
        finally:case.doCleanups()

if __name__=='__main__':unittest.main()
