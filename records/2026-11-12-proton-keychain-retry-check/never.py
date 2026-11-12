import proton_accept as p
from pathlib import Path
import json,time,subprocess,os,signal,copy
p.require_locks('k72','kr19')
w=Path.cwd()/'never2';w.mkdir(mode=0o700);a=p.App(Path.cwd()/'pr',w)
def browsers():
 found=[]
 for path in Path('/proc').iterdir():
  if not path.name.isdigit():continue
  try:
   name=(path/'comm').read_text().strip()
   if path.stat().st_uid==os.getuid() and any(x in name.lower() for x in ['firefox','chrome','chromium','brave']):found.append({'pid':int(path.name),'name':name})
  except OSError:pass
 return sorted(found,key=lambda x:x['pid'])
report={}
try:
 a.start();caps=a.need('capabilities');(w/'capabilities.json').write_text(json.dumps(caps,indent=2)+'\n')
 p.configure(a)
 settings=a.need('settings.get');profile=copy.deepcopy(next(x for x in settings['document']['profiles'] if x['id']==p.PROFILE_ID))
 profile.update(id='proton-never-kr19',label='Never connected reliability check')
 profile['credentials']={'mode':'keychain','reference':'putgd/proton/lab-k72-never-connected-kr19'}
 a.need('settings.patch',{'patch':{'profiles':settings['document']['profiles']+[profile]},'expectedRevision':settings['metadata']['observedRevision']})
 settings=a.need('settings.get');before=browsers();start=time.monotonic()
 reply,error=a.call('setup.testDestination',{'profileId':profile['id'],'expectedRevision':settings['metadata']['observedRevision']})
 report={'method':'setup.testDestination','request':reply,'error':error}
 if not error:
  deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   state,error=a.call('setup.inspect',{'id':reply['setupId']})
   if error or state.get('state')!='running':break
   time.sleep(.1)
  report.update(result=state,error=error)
 report['seconds']=round(time.monotonic()-start,3);report.update(browsersBefore=before,browsersAfter=browsers())
finally:
 a.call('ui.quit',timeout=15)
 if a.process:
  try:a.process.wait(timeout=30)
  except subprocess.TimeoutExpired:os.kill(a.process.pid,signal.SIGTERM);a.process.wait(timeout=15)
 report['helpersGoneAfter']=p.helpers_gone(15)
 (w/'results.json').write_text(json.dumps(report,indent=2)+'\n')
