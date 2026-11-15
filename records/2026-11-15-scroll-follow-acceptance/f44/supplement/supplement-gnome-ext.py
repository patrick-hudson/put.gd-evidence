# Run only while holding f44's desktop lease. Never call with a resident running across login.
import json,os,subprocess,sys,time,shutil,hashlib
from pathlib import Path
P=Path(os.environ.get('SFA_ROOT',str(Path.home()/'work/sfa15')));ext=Path.home()/'.local/share/gnome-shell/extensions/putgd@put.gd'
E=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME']:E.pop(k,None)
def g(key,schema='org.gnome.shell'):return subprocess.check_output(['gsettings','get',schema,key],env=E,text=True).strip()
def put(key,value,schema='org.gnome.shell'):subprocess.run(['gsettings','set',schema,key,value],env=E,check=True)
def files():return {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in ext.iterdir() if f.is_file()} if ext.exists() else None
def save():
 assert not (P/'gnome-before.json').exists()
 d={k:g(k) for k in ['enabled-extensions','disabled-extensions','disable-user-extensions']};d['accel-profile']=g('accel-profile','org.gnome.desktop.peripherals.mouse');d['pointer-speed']=g('speed','org.gnome.desktop.peripherals.mouse');d['files']=files()
 if ext.exists():shutil.copytree(ext,P/'gnome-extension-before')
 (P/'gnome-before.json').write_text(json.dumps(d,indent=1));os.chmod(P/'gnome-before.json',0o600);print(json.dumps(d))
def install(version):
 src=next((P/'squashfs-root').glob('usr/share/gnome-shell/extensions/putgd@put.gd')) if version=='24' else Path(os.environ.get('SFA_EXTENSION23_SOURCE',str(Path.home()/'work/scroll-session/gnome/ext-v23')))
 assert json.loads((src/'metadata.json').read_text())['version']==int(version)
 ext.mkdir(parents=True,exist_ok=True)
 for n in ['extension.js','metadata.json']:shutil.copyfile(src/n,ext/n)
 print('installed',version,files(),flush=True)
def login(active=True):
 assert not subprocess.run(['pgrep','-x','putgd'],capture_output=True,text=True).stdout.strip(),'stop resident before login'
 subprocess.run(['sudo','-n','systemctl','restart','gdm'],check=True)
 for _ in range(60):
  time.sleep(2)
  p=subprocess.run(['gnome-extensions','info','putgd@put.gd'],capture_output=True,text=True,env=E)
  if (active and 'State: ACTIVE' in p.stdout) or (not active and subprocess.run(['pgrep','-x','gnome-shell'],capture_output=True,text=True).stdout.strip()):break
 else:raise RuntimeError('login/extension not ready: '+p.stdout+p.stderr)
 time.sleep(4);subprocess.run(['systemctl','--user','restart','putgd-gnome-vnc'],env=E,check=True);time.sleep(3)
 import rfb
 v=rfb.RFB(5901);v.key('esc');time.sleep(.5);v.screenshot(P/('login-'+sys.argv[1]+'.png'));v.close()
 info=subprocess.run(['gnome-extensions','info','putgd@put.gd'],capture_output=True,text=True,env=E)
 (P/('extension-'+sys.argv[1]+'.txt')).write_text(info.stdout+info.stderr);print(info.stdout,flush=True)
def enable():
 import ast
 for k in ['enabled-extensions','disabled-extensions']:
  raw=g(k).replace('@as ','');v=ast.literal_eval(raw)
  v=[x for x in v if x!='putgd@put.gd']
  if k=='enabled-extensions':v.append('putgd@put.gd')
  put(k,str(v))
 put('disable-user-extensions','false');put('accel-profile',"'flat'",'org.gnome.desktop.peripherals.mouse');put('speed','0.0','org.gnome.desktop.peripherals.mouse')
a=sys.argv[1]
if a=='save':save()
elif a in ['24','23','22']:install(a);enable();login()
elif a=='swap24':install('24')
elif a=='restore':
 d=json.loads((P/'gnome-before.json').read_text())
 for k in ['enabled-extensions','disabled-extensions','disable-user-extensions']:put(k,d[k])
 put('accel-profile',d['accel-profile'],'org.gnome.desktop.peripherals.mouse');put('speed',d['pointer-speed'],'org.gnome.desktop.peripherals.mouse')
 if ext.exists():
  assert set(x.name for x in ext.iterdir())<=set(['extension.js','metadata.json'])
  for f in ext.iterdir():f.unlink()
  ext.rmdir()
 if d['files'] is not None:shutil.copytree(P/'gnome-extension-before',ext)
 login(active=False)
 after={k:g(k) for k in ['enabled-extensions','disabled-extensions','disable-user-extensions']};after['accel-profile']=g('accel-profile','org.gnome.desktop.peripherals.mouse');after['pointer-speed']=g('speed','org.gnome.desktop.peripherals.mouse');after['files']=files();assert after==d,(after,d)
 (P/'gnome-restored.json').write_text(json.dumps(after,indent=1));print('RESTORED EXACTLY',flush=True)
