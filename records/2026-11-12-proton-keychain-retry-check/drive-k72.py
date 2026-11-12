import subprocess as s,sys,pathlib,threading,json,time,tarfile,os
b=pathlib.Path('/tmp/kr19');out=b/'2026-11-12-proton-keychain-retry-check';out.mkdir(mode=0o700,exist_ok=True)
host=sys.argv[1];ip={'k72':'72','d69':'69'}[host]
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}']
scp=['scp','-q']+ssh[1:-1]
lock=[sys.executable,'/home/patrick/work/put.gd/tools/lab/desktop_lock.py']
def remote(c,**kw):return s.run(ssh+[c],check=True,**kw)
def lease(action,res,extra=[]):
 r=s.run(lock+[action,host,'--resource',res,'--session','kr19']+extra,capture_output=True,text=True)
 with (out/(host+'-leases.log')).open('a') as f:f.write(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('Lease failed: '+r.stdout+r.stderr)
lease('acquire','desktop',['--owner','codex-retry-check','--purpose','PR1419 reliability; notes /tmp/kr19','--minutes','45'])
try:lease('acquire','proton',['--owner','codex-retry-check','--purpose','PR1419 reliability; notes /tmp/kr19','--minutes','45'])
except:lease('release','desktop',['--verified-clean']);raise
stop=threading.Event()
def heartbeat():
 while not stop.wait(60):
  for res in ('desktop','proton'):lease('heartbeat',res)
t=threading.Thread(target=heartbeat,daemon=True);t.start()
try:
 remote('mkdir -m 700 ~/work/kr19')
 package=next((b/'packages'/('ubuntu26.04' if host=='k72' else 'debian13')).rglob('*.deb'))
 files=[b/'run.py',b/'proton_accept.py',b/'never.py',pathlib.Path('/home/patrick/work/put.gd/tools/lab/desktop_lock.py'),package]
 s.run(scp+[str(x) for x in files]+[ssh[-1]+':work/kr19/'],check=True)
 with (out/(host+'-environment.txt')).open('w') as f:
  remote('cat /etc/os-release; plasmashell --version; uname -r',stdout=f)
 with (out/(host+'-package.txt')).open('w') as f:
  remote('cd ~/work/kr19 && mkdir pr && dpkg-deb -x '+package.name+' pr && sha256sum *.deb',stdout=f)
 with (out/(host+'-driver.log')).open('w') as f:
  r=s.run(ssh+[f'cd ~/work/kr19 && LAB_HOST={host} PASSES={6 if host=="k72" else 1} python3 -u run.py'],stdout=f,stderr=s.STDOUT)
 print(host,'remote exit',r.returncode,flush=True)
 if host=='k72' and r.returncode==0:
  with (out/'never-driver.log').open('w') as f:remote('cd ~/work/kr19 && python3 -u never.py',stdout=f,stderr=s.STDOUT)
 with (b/(host+'-outputs.tar')).open('wb') as f:remote('cd ~/work/kr19 && tar -cf - p*/results.json p*/resident.log p*/profile/state/putgd/logs/*.jsonl',stdout=f)
 dest=out/host;dest.mkdir(mode=0o700)
 with tarfile.open(b/(host+'-outputs.tar')) as archive:
  for m in archive:
   target=dest/m.name.split('/')[0];target.mkdir(exist_ok=True)
   (target/('app.jsonl' if m.name.endswith('.jsonl') else pathlib.Path(m.name).name)).write_bytes(archive.extractfile(m).read())
 if host=='k72' and r.returncode==0:
  (out/'never-connected.json').write_bytes(s.check_output(ssh+['cat ~/work/kr19/never/results.json']))
  (out/'never-app.jsonl').write_bytes(s.check_output(ssh+['cat ~/work/kr19/never/profile/state/putgd/logs/*.jsonl']))
finally:
 stop.set();t.join()
 lease('release','proton',['--verified-clean'])
 lease('release','desktop',['--verified-clean'])
