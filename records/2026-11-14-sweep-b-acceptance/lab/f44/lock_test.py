#!/usr/bin/env python3
"""Lock refusal and visible-console unlock on this run's disposable Budgie guest."""
import os,sys,json,time,pathlib,stat,re,socket
root=pathlib.Path('/home/patrick/work/sb1114');sys.path.insert(0,str(root/'tools/lab'))
import lab
from rfb import RFB
run=root/'work/lab-runs'/sys.argv[1];state=lab.state(run);out=run/'acceptance';report={}
def save(): (out/'6-lock.json').write_text(json.dumps(report,indent=2))
def inspect_op(op):
 for _ in range(200):
  v=lab.cli(run,'operation.inspect',{'id':op})
  if v['state'] in ('completed','failed','cancelled'):return v
  time.sleep(.1)
 raise RuntimeError('Locked capture did not finish')
try:
 assert lab.cli(run,'diagnostics')['build']['gitTree']=='e12d7610bec4319749a5b55b5411ce3f2b7318c2'
 # No historical private login input exists for this golden. Its manifest uses the
 # documented standard disposable-guest login; stage it privately on this host.
 secret_file=root/'private-login'
 if not secret_file.exists():
  text=(root/'docs/lab/remote-golden-images.md').read_text();secret=re.search(r'Shared default lab password\s*\|\s*`([^`]+)`',text)[1]
  fd=os.open(secret_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as f:f.write(secret+'\n')
  secret=''
 st=secret_file.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1
 lab.guest_session(run,'gtklock --daemonize > /tmp/gtklock-sb.log 2>&1 < /dev/null\n')
 time.sleep(2)
 for h in (0,1):
  lab.screenshot(run,head=h)
  from PIL import Image
  Image.open(run/f'witness-head{h}.ppm').save(out/f'6-locked-head{h}.png')
 report['lockedFramePaths']=[str(run/f'witness-head{h}.ppm') for h in (0,1)];save();(run/'lock-visible.ready').touch()
 op=lab.cli(run,'action.invoke',{'action':'desktop'})['operationId'];v=inspect_op(op);report['lockedCapture']=v;save()
 # The controller observes the masked lock screen, then supplies only coordinates.
 for _ in range(180):
  if (run/'lock-enter.json').exists():break
  time.sleep(1)
 assert (run/'lock-enter.json').is_file(),'No visibly verified unlock coordinates'
 point=json.loads((run/'lock-enter.json').read_text());base=int(state['vnc_display'])+5900
 client=RFB(base+int(point['head']))
 try:
  client.pointer(point['point'][0]-3,point['point'][1]-3);client.click(*point['point']);fd=os.open(secret_file,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd) as f:secret=f.read().rstrip('\n')
  client.type(secret);secret='';client.key('ret')
 finally:client.close()
 time.sleep(2)
 for h in (0,1):
  lab.screenshot(run,head=h)
  from PIL import Image
  Image.open(run/f'witness-head{h}.ppm').save(out/f'6-unlocked-head{h}.png')
 (run/'unlock-visible.ready').touch()
 for _ in range(180):
  if (run/'unlock-verified.ready').exists():break
  time.sleep(1)
 assert (run/'unlock-verified.ready').is_file(),'Unlocked desktop not visibly verified'
 op=lab.cli(run,'action.invoke',{'action':'desktop'})['operationId'];after=inspect_op(op);report['afterUnlock']=after;report['passed']=v['state']=='failed' and v['error']['code']=='session_locked' and after['state']=='completed';save()
 assert report['passed'], 'Lock/refusal or unlock capture failed'
 (run/'lock-test.done').write_text(json.dumps(report));secret_file.unlink()
except Exception as e:
 report.update(passed=False,driverError=str(e));save();(run/'lock-test.done').write_text(json.dumps(report));raise
finally:
 p=root/'private-login'
 if p.exists():p.unlink()
