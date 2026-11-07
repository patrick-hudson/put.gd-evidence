import pathlib,sys,os,json,time,shutil
home=pathlib.Path.home().resolve();sys.path.insert(0,str(home/'nd'));os.chdir(home/'nd')
from tools.lab import lab
from tools.lab import nightly_desktops as n
from tools.lab.desktop_lock import Desktop
out=home/'c1245b/out/aurora';owner=json.loads((home/'putgd-lab/locks/tier1-guest.lock.d/owner.json').read_text());run=pathlib.Path(owner['run']).resolve()
lock=Desktop(home/'putgd-lab/locks','aurora-amd');n.save(out/'manual-lock-extend.json',lock.extend(owner['session'],45))
os.environ['PATH']=str(home/'.local/libexec/putgd-nightly/bin')+':'+os.environ['PATH']
n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket','/run/user/1000/putgd/session.sock'],log=out/'manual-sockets.json')
r={'source':'manual production CLI + real QMP input on owned visible guest','steps':[]}
def save():n.save(out/'manual-selector.json',r)
def inspect(rid):return lab.cli(run,'recording.inspect',{'id':rid})
def wait(rid,condition):
 for i in range(45):
  d=inspect(rid)
  if condition(d):return d
  time.sleep(.3)
 raise RuntimeError('manual_recording_timeout')
def frame(name):
 from PIL import Image
 f=lab.screenshot(run,name);src=pathlib.Path(f['path']);dest=out/(name+'.png');Image.open(src).save(dest);r['steps'].append(dict(screenshot=str(dest),sha256=n.digest(dest)));save()
lab.start(run);r['capabilities']=lab.cli(run,'capabilities');save()
try:
 rid=lab.cli(run,'recording.prepare',{'target':{'kind':'region'},'format':'mp4','codec':'h264','fps':15,'audio':{'system':False}})['recordingId'];r['cancelRecordingId']=rid
 r['selectingBeforeEscape']=wait(rid,lambda d:d.get('selecting'));frame('manual-selector-before-escape');lab.key(run,['esc']);r['afterEscape']=wait(rid,lambda d:d['state']=='cancelled');frame('manual-selector-after-escape');save()
 rid=lab.cli(run,'recording.prepare',{'target':{'kind':'region'},'format':'mp4','codec':'h264','fps':15,'audio':{'system':False}})['recordingId'];r['dragRecordingId']=rid
 wait(rid,lambda d:d.get('selecting'));frame('manual-selector-before-drag')
 lab.pointer(run,320,200,1280,800,down=True);lab.pointer(run,960,600,1280,800,down=True);lab.pointer(run,960,600,1280,800,down=False)
 r['afterDrag']=wait(rid,lambda d:d['state']=='ready');frame('manual-selector-ready');lab.cli(run,'recording.cancel',{'id':rid});r['afterCancel']=wait(rid,lambda d:d['state']=='cancelled');r['status']='PASS';save()
finally:lab.cli(run,'ui.quit')
print('manual selector',r.get('status'))
