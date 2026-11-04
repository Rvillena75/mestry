#!/usr/bin/env python3
"""Prepare an explicitly reviewed control handoff on the existing Horus deployment."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from reviewed_workflow_handoff import encoded, sha, private_json, reviewed_policy


def expected_profile():
    if Path.home() != Path('/home/horus') or os.getuid() != 1000 or os.uname().machine != 'aarch64':
        raise ValueError('EXISTING_HORUS_PROFILE_REQUIRED')


def build_plan(old, before, target, controller_sha, tests_sha, reviewed_at, review):
    if not review:
        raise ValueError('EXPLICIT_REVIEW_REQUIRED')
    future = copy.deepcopy(old)
    future['controller_sha'] = controller_sha
    future['pins']['tools/work_session.py'] = controller_sha
    future['pins']['tools/test_work_session.py'] = tests_sha
    future['approved_at'] = reviewed_at
    future['transition_review'] = {'reviewed':True, 'from_head':before, 'to_head':target}
    plan = {'schema':1, 'reviewed':True, 'root':old['root'], 'from_head':before, 'to_head':target,
            'future_policy':future, 'protected_changes':{
                k:{'before':old['pins'][k], 'after':future['pins'][k]}
                for k in old['pins'] if old['pins'][k] != future['pins'][k]}}
    reviewed_policy(old, plan)
    return plan


def launcher_source(real_python, runner, adapter, adapter_sha, plan, plan_sha):
    values = repr(dict(real_python=str(real_python), runner=str(runner), adapter=str(adapter),
                       adapter_sha=adapter_sha, plan=str(plan), plan_sha=plan_sha))
    return ('#!'+str(real_python)+'\nimport os,sys,hashlib\nfrom pathlib import Path\nq='+values+'\n'
            'a=sys.argv[1:]\n'
            'match=any(x.endswith("work_session.py") and Path(x).resolve()==Path(q["runner"]) for x in a)\n'
            'if match and "lease" in a:\n'
            ' if hashlib.sha256(Path(q["adapter"]).read_bytes()).hexdigest()!=q["adapter_sha"]: raise SystemExit("HANDOFF_ADAPTER_CHANGED")\n'
            ' os.execv(q["real_python"],[q["real_python"],"-B",q["adapter"],"--plan",q["plan"],"--plan-sha256",q["plan_sha"],"--",*a])\n'
            'os.execv(q["real_python"],[q["real_python"],*a])\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('/workspace/projects/mestry'))
    p.add_argument('--from-head');p.add_argument('--to-head');p.add_argument('--controller-sha256');p.add_argument('--tests-sha256')
    p.add_argument('--review',action='store_true',required=True)
    p.add_argument('--restore-launcher',type=Path)
    a=p.parse_args();expected_profile();os.umask(0o077)
    root=a.repo.resolve()
    if not a.repo.is_absolute() or a.repo.is_symlink() or root != Path('/workspace/projects/mestry'):
        raise ValueError('ADMITTED_PROJECT_REQUIRED')
    sys.path.insert(0,str(root/'tools'))
    spec=importlib.util.spec_from_file_location('mestry_operative_controller',root/'tools/work_session.py')
    w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
    u=runpy.run_path(str(root/'tools/s25-codex-client/horus_upgrade.py'))
    atomic=u['atomic_write'];active=u['active_turns'];s=w.Session(root)
    home=Path.home();controller=home/'.local/bin/mestry-bridge';store=home/'.local/state/mestry-s25-client/state.json'
    pointer=home/'.local/lib/mestry-s25-pilot/current.json';token=home/'.local/state/mestry-s25-client/bridge-token'
    def call(*args,env=None):
        r=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=40,env=env)
        if r.returncode:raise ValueError('EXISTING_COMPONENT_ACTION_FAILED')
        return r.stdout.strip()
    def token_meta():
        t=token.stat();return [t.st_ino,t.st_size,t.st_mtime_ns,t.st_uid,t.st_mode]
    def threads():
        d=json.loads(store.read_text());return [sha(encoded(sorted(d['sessions']))),sum(len(v.get('events',[])) for v in d['sessions'].values())]
    with s.lock():
        s.load();s.environment()
        if s.status() or s.state.get('phase') in ('running','recovery_required') or (s.directory/'lease.json').exists() or active(json.loads(store.read_text())):
            raise ValueError('CLEAN_FREE_RECONCILED_PROJECT_REQUIRED')
        running=json.loads(call(controller,'status'))
        if not running['owned_process_running'] or not running['loopback_health_matches']:
            raise ValueError('OWNED_HEALTHY_BRIDGE_REQUIRED')
        config=s.directory/'config.json';cfg=config.read_bytes();index=(root/'.git/index').read_bytes();point=pointer.read_bytes();tok=token_meta();thread_set=threads()
        if a.restore_launcher:
            directory=a.restore_launcher;metadata=private_json(directory/'prepared.json');plan=private_json(directory/'plan.json')
            if plan['root'] != str(root) or sha((directory/'plan.json').read_bytes()) != metadata['plan_sha256']:
                raise ValueError('RESTORE_PLAN_CHANGED')
            head=s.text('rev-parse','HEAD')
            if head not in (plan['from_head'],plan['to_head']) or sha(point)!=metadata['release_pointer_sha256'] or tok!=metadata['token_metadata']:
                raise ValueError('RESTORE_SCOPE_CHANGED')
            original_path=metadata['original_path']
        else:
            if not all((a.from_head,a.to_head,a.controller_sha256,a.tests_sha256)) or s.text('rev-parse','HEAD')!=a.from_head:
                raise ValueError('EXACT_REVIEWED_VERSIONS_REQUIRED')
            s.fetch()
            if s.text('rev-parse','refs/remotes/origin/main')!=a.to_head:
                raise ValueError('REMOTE_OUTSIDE_REVIEWED_HANDOFF')
            for name,digest in [('tools/work_session.py',a.controller_sha256),('tools/test_work_session.py',a.tests_sha256)]:
                if sha(s.git('show',a.to_head+':'+name))!=digest:
                    raise ValueError('REVIEWED_SOURCE_DIGEST_MISMATCH')
            plan=build_plan(s.cfg,a.from_head,a.to_head,a.controller_sha256,a.tests_sha256,w.now(),a.review)
            plan['policy_before_sha256']=sha(cfg)
            directory=home/'.local/state/mestry-h3-handoff'/a.to_head[:16]
            if directory.exists():raise ValueError('HANDOFF_DIRECTORY_EXISTS_RECONCILE_FIRST')
            directory.mkdir(parents=True,mode=0o700)
            atomic(directory/'policy-before.json',cfg);atomic(directory/'status-before.json',(s.directory/'status.json').read_bytes())
            w.write_private(directory/'plan.json',plan)
            adapter=Path(__file__).with_name('reviewed_workflow_handoff.py')
            digest=sha(adapter.read_bytes());plan_sha=sha((directory/'plan.json').read_bytes())
            (directory/'bin').mkdir(mode=0o700)
            atomic(directory/'bin/python3',launcher_source(sys.executable,root/'tools/work_session.py',adapter,digest,directory/'plan.json',plan_sha).encode(),0o700)
            original_path=os.environ['PATH']
            metadata={'at':w.now(),'prepared_head':a.from_head,'incoming_not_applied':a.to_head,
                      'policy_before_sha256':sha(cfg),'future_policy_sha256':sha(encoded(plan['future_policy'])),
                      'adapter_sha256':digest,'plan_sha256':plan_sha,'original_path':original_path,
                      'release_pointer_sha256':sha(point),'token_metadata':tok}
            w.write_private(directory/'prepared.json',metadata)
        call(controller,'stop')
        path=original_path if a.restore_launcher else str(directory/'bin')+os.pathsep+original_path
        try:
            call(controller,'start',env=dict(os.environ,PATH=path))
        except ValueError:
            call(controller,'start',env=dict(os.environ,PATH=original_path))
            raise ValueError('SCOPED_START_FAILED_OPERATIVE_PATH_RESTORED')
        if config.read_bytes()!=cfg or (root/'.git/index').read_bytes()!=index or pointer.read_bytes()!=point or token_meta()!=tok or threads()!=thread_set:
            raise ValueError('PRESERVATION_RECONCILE_REQUIRED')
        result={'marker':'H3_CONTROL_LAUNCHER_RESTORED' if a.restore_launcher else 'H3_CONTROL_HANDOFF_PREPARED',
                'head':s.text('rev-parse','HEAD'),'policy_unchanged':True,'index_unchanged':True,
                'release_unchanged':True,'pairing_unchanged':True,'threads_preserved':True,'active_turns':0,
                'review_directory':str(directory),'path_scoped_to_bridge':not bool(a.restore_launcher)}
        w.write_private(directory/('restored.json' if a.restore_launcher else 'activated.json'),result)
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as error:
        reason=str(error) if isinstance(error,ValueError) and str(error).replace('_','').isupper() else 'PREPARATION_FAILED_NO_PRIVATE_DETAILS'
        print(json.dumps({'state':'BLOCKED','reason':reason,'local_work_preserved':True}));raise SystemExit(3)
