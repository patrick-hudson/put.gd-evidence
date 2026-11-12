import subprocess as s,sys,pathlib,threading,json,time
b=pathlib.Path('/tmp/kr61');out=b/'2026-11-12-proton-k72-revoke-reliability';out.mkdir(mode=0o700)
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/k72/known_hosts','patrick@192.168.68.72']
scp=['scp','-q']+ssh[1:-1]
lock=[sys.executable,'/home/patrick/work/put.gd/tools/lab/desktop_lock.py']
def remote(c,**kw):return s.run(ssh+[c],check=True,**kw)
def lease(action,res,extra=[]):
 r=s.run(lock+[action,'k72','--resource',res,'--session','kr61']+extra,capture_output=True,text=True)
 with (out/'leases.log').open('a') as f:f.write(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('Lease failed: '+r.stdout+r.stderr)
lease('acquire','desktop',['--owner','codex-reliability','--purpose','PR1414 six k72 revoke passes; /tmp/kr61','--minutes','45'])
try:lease('acquire','proton',['--owner','codex-reliability','--purpose','PR1414 six k72 revoke passes; /tmp/kr61','--minutes','45'])
except:lease('release','desktop',['--verified-clean']);raise
stop=threading.Event()
def heartbeat():
 while not stop.wait(60):
  for res in ('desktop','proton'):lease('heartbeat',res)
t=threading.Thread(target=heartbeat,daemon=True);t.start()
try:
 remote('mkdir -m 700 ~/work/kr61')
 files=[b/'run.py',b/'round4/proton_accept.py',pathlib.Path('/home/patrick/work/put.gd/tools/lab/desktop_lock.py'),next(pathlib.Path('/tmp/p4a/packages/ubuntu26.04').glob('*.deb')),next(b.glob('*.deb'))]
 s.run(scp+[str(x) for x in files]+[ssh[-1]+':work/kr61/'],check=True)
 remote('cd ~/work/kr61 && mkdir pr nightly && dpkg-deb -x putgd_26.1112.4657~dev+gfe1e30056934_amd64.deb pr && dpkg-deb -x putgd-26.1111.4633-nightly-ubuntu26.04-x86_64.deb nightly && sha256sum *.deb')
 with (out/'driver.log').open('w') as f:
  r=s.run(ssh+['cd ~/work/kr61 && python3 -u run.py'],stdout=f,stderr=s.STDOUT)
 print('remote exit',r.returncode,flush=True)
 with (b/'outputs.tar').open('wb') as f:remote('cd ~/work/kr61 && tar -cf - p*/results.json p*/resident.log',stdout=f)
 s.run(['tar','-xf',str(b/'outputs.tar'),'-C',str(out)],check=True)
finally:
 stop.set();t.join()
 lease('release','proton',['--verified-clean'])
 lease('release','desktop',['--verified-clean'])
