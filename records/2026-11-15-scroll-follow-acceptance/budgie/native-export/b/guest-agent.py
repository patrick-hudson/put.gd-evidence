import sys,os,json,subprocess,time,hashlib,shutil,socket,xml.etree.ElementTree as ET
from pathlib import Path
P=Path.home()/'work/sfa15/b';E=json.loads(Path('/tmp/sfa15-session-env.json').read_text());os.environ.update(E)
os.environ['SFA_ROOT']=str(P)
os.environ['SFA_EXPECT_TREE']='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
os.environ['SFA_DESKTOP']='Fedora45 Budgie10.10.3 labwc0.20.2 native Wayland KVM guest'
def pointer():
 s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.connect('/home/lab/work/sfa15/pointer.sock');d=json.loads(s.recv(4096));s.close();assert d['valid'] and d['inside'],d;return [d['x'],d['y']]
mode=sys.argv[1]
if mode=='pointer':print(json.dumps(pointer()))
elif mode=='anchor':
 target=list(map(int,sys.argv[2:4]));before=pointer()
 p=subprocess.Popen(['python3',str(P/'umouse-native.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert p.stdout.readline().startswith('ready')
 try:
  p.stdin.write('m %d %d\n'%(target[0]-before[0],target[1]-before[1]));p.stdin.flush();time.sleep(.2);after=pointer();assert after==target,(before,target,after)
  print(json.dumps({'before':before,'target':target,'after':after,'method':'Real relative guest uinput before prepare; independent read-only native cursor metadata'}))
 finally:p.stdin.write('q\n');p.stdin.flush();p.wait(5)
elif mode=='flat':
 f=Path('/home/lab/.config/budgie-desktop/labwc/rc.xml');r=ET.fromstring(f.read_text());d=next(x for x in r.findall('./libinput/device')if x.attrib.get('category')=='non-touch')
 assert d.findtext('accelProfile')=='flat' and float(d.findtext('pointerSpeed'))==0
 print(json.dumps({'nativeConfig':str(f),'category':'non-touch','accelProfile':'flat','pointerSpeed':0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'changed':False}))
elif mode=='helper-pids':print(json.dumps(subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.split()))
elif mode=='staging-files':print(json.dumps([str(f.relative_to(P/'d'))for f in(P/'d').rglob('*')if f.is_file()and'/scroll/'in str(f)]))
elif mode=='browser-start':
 kind=sys.argv[2];assert kind=='firefox';prof=P/'profile-firefox'
 if prof.exists():prof.rename(P/('profile-firefox-'+str(time.time_ns())))
 prof.mkdir(mode=0o700)
 prefs={'marionette.port':28291,'media.webspeech.synth.enabled':False,'browser.aboutwelcome.enabled':False,'browser.shell.checkDefaultBrowser':False,'browser.startup.homepage_override.mstone':'ignore','browser.sessionstore.resume_from_crash':False,'datareporting.policy.dataSubmissionEnabled':False,'browser.tabs.warnOnClose':False}
 (prof/'user.js').write_text(''.join('user_pref(%s,%s);\n'%(json.dumps(k),json.dumps(v))for k,v in prefs.items()))
 env=dict(os.environ,**E,MOZ_ENABLE_WAYLAND='1',MOZ_DBUS_REMOTE='0',MOZ_NO_REMOTE='1',MOZ_REMOTE_ALLOW_SYSTEM_ACCESS='1',XDG_CONFIG_HOME=str(P/'c'),XDG_DATA_HOME=str(P/'d'),XDG_STATE_HOME=str(P/'s'),XDG_CACHE_HOME=str(P/'cache'),QT_QPA_PLATFORM='wayland')
 binary=str(P/'tools/firefox/firefox');log=(P/'firefox.log').open('w');proc=subprocess.Popen([binary,'--new-instance','--no-remote','--marionette','--remote-allow-system-access','--profile',str(prof),'about:blank'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (P/'browser.pid').write_text(str(proc.pid));print(json.dumps({'pid':proc.pid,'version':subprocess.run([binary,'--version'],capture_output=True,text=True,env=env).stdout.strip()}))
elif mode=='browser-stop':
 pid=int((P/'browser.pid').read_text());d=Path('/proc')/str(pid)
 if d.exists():
  args=(d/'cmdline').read_bytes();assert str(P/'profile-firefox').encode()in args
  os.kill(pid,15)
  for _ in range(40):
   if not d.exists()or(d/'stat').read_text().split()[2]=='Z':break
   time.sleep(.25)
  else:raise RuntimeError('Owned Firefox did not exit')
 print(json.dumps({'stoppedPid':pid}))
elif mode=='artifact':
 import accept as A
 sid=sys.argv[2]
 for _ in range(100):
  found=None
  for off in range(0,4000,200):
   records=A.rpc('history.list',{'limit':200,'offset':off})['records'];found=next((r for r in records if r.get('operationId')==sid),None)
   if found or len(records)<200:break
  if found:
   candidate=Path(found.get('local',{}).get('path','/nonexistent'))
   if candidate.is_relative_to(P/'archive') and candidate.is_file() and not candidate.is_symlink():break
  time.sleep(.2)
 assert found,sid
 f=Path(found['local']['path']);assert f.is_relative_to(P/'archive') and f.is_file() and not f.is_symlink();assert hashlib.sha256(f.read_bytes()).hexdigest()==found['sha256']
 print(json.dumps(found))
elif mode=='env':print(json.dumps(E))
else:raise RuntimeError('Unknown guest command')
