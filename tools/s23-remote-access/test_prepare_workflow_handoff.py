import copy
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from prepare_workflow_handoff import build_plan, launcher_source, expected_profile
from reviewed_workflow_handoff import sha

class PreparationTests(unittest.TestCase):
    def test_reviewed_plan_changes_only_the_two_source_pins(self):
        old={'schema':1,'root':'/fixture/checkout','contract':{'fixture':True},'approved_at':'old',
             'controller_sha':'a'*64,'pins':{'tools/work_session.py':'a'*64,'tools/test_work_session.py':'b'*64},
             'dependency_fingerprint':'e'*64,'checker_sha':'f'*64,'author_email':'fixture@example.invalid'}
        before=copy.deepcopy(old)
        with self.assertRaisesRegex(ValueError,'EXPLICIT_REVIEW_REQUIRED'):build_plan(old,'1'*40,'2'*40,'c'*64,'d'*64,'reviewed',False)
        plan=build_plan(old,'1'*40,'2'*40,'c'*64,'d'*64,'reviewed',True)
        self.assertEqual(old,before)
        self.assertEqual(set(plan['protected_changes']),{'tools/work_session.py','tools/test_work_session.py'})
        self.assertEqual(plan['future_policy']['dependency_fingerprint'],old['dependency_fingerprint'])
        self.assertEqual(plan['future_policy']['contract'],old['contract'])

    def test_scoped_launcher_preserves_other_python_and_pins_its_adapter(self):
        class Executed(Exception):pass
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);adapter=directory/'adapter.py';adapter.write_text('# reviewed fixture adapter\n')
            runner=directory/'checkout/tools/work_session.py';plan=directory/'plan.json'
            code=launcher_source('/usr/bin/python3',runner,adapter,sha(adapter.read_bytes()),plan,'a'*64)
            for args,delegated in [(['proxy','--version'],False),(['proxy','-B',str(runner),'--repo',str(runner.parents[1]),'lease'],True)]:
                with patch.object(sys,'argv',args),patch.object(os,'execv',side_effect=Executed) as execute:
                    with self.assertRaises(Executed):exec(compile(code,'fixture-launcher','exec'),{})
                    target,argv=execute.call_args.args
                    self.assertEqual(target,'/usr/bin/python3')
                    self.assertEqual('--plan-sha256' in argv,delegated)
            adapter.write_text('# changed fixture adapter\n')
            with patch.object(sys,'argv',['proxy','-B',str(runner),'lease']),patch.object(os,'execv') as execute:
                with self.assertRaisesRegex(SystemExit,'HANDOFF_ADAPTER_CHANGED'):exec(compile(code,'fixture-launcher','exec'),{})
                execute.assert_not_called()

    def test_wrong_profile_stops_before_any_runtime_action(self):
        with patch.object(Path,'home',return_value=Path('/synthetic/external-home')):
            with self.assertRaisesRegex(ValueError,'EXISTING_HORUS_PROFILE_REQUIRED'):expected_profile()

if __name__=='__main__':unittest.main()
