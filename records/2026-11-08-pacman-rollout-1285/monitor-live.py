import subprocess,time,pathlib,json,datetime
root=pathlib.Path(__file__).resolve().parent
ssh=['ssh','-n','-i',str(pathlib.Path.home()/'.ssh/awskey_110724'),'-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts','patrick@192.168.68.69']
while True:
 r=subprocess.run(ssh+['systemctl --user show putgd-signer.service -p ActiveState -p SubState -p MainPID -p ExecMainStatus'],capture_output=True,text=True)
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (root/'live-monitor.jsonl').open('a') as f:f.write(json.dumps({'time':now,'returncode':r.returncode,'state':r.stdout,'error':r.stderr})+'\n')
 print(now,r.stdout.strip(),flush=True)
 if r.returncode==0:
  d=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
  if d.get('ActiveState') in ('failed','inactive'):
   log=subprocess.run(ssh+['journalctl --user _SYSTEMD_INVOCATION_ID=849dcfa85212496b918d98c7550bc137 --no-pager > ~/work/rollout1285/live-journal.log'],capture_output=True,text=True)
   if d.get('ActiveState')=='failed' or d.get('ExecMainStatus')!='0':
    rollback=subprocess.run(ssh+['git -C ~/putgd-signer/src checkout --detach 1887c4c9a90dfd0d0bc37ef031757aab56bc04f7 > ~/work/rollout1285/rollback.log 2>&1; result=$?; cat ~/work/rollout1285/rollback.log; exit "$result"'],capture_output=True,text=True)
    (root/'live-result.json').write_text(json.dumps({'result':'FAIL','service':d,'rollbackReturncode':rollback.returncode,'rollbackOutput':rollback.stdout,'rollbackError':rollback.stderr},indent=2));raise SystemExit(2)
   (root/'live-result.json').write_text(json.dumps({'result':'SERVICE_SUCCESS','service':d},indent=2));raise SystemExit(0)
 time.sleep(60)
