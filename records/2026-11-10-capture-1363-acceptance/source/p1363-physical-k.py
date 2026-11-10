import os,json,subprocess,time,sys
from pathlib import Path
BASE=Path('/tmp/p1363k');BASE.mkdir(mode=0o700);E=BASE/'evidence';E.mkdir();PKG=BASE/'pkg';PKG.mkdir()
source=next((Path.home()/'work/i1363/work/acceptance-packages-13570fca9/release-native-ubuntu26.04').glob('*.deb'))
subprocess.run(['dpkg-deb','-x',str(source),str(PKG)],check=True)
pid=subprocess.check_output(['pgrep','-xo','plasmashell']).decode().strip();raw=Path('/proc/'+pid+'/environ').read_bytes()
env=dict(os.environ)
for item in raw.split(b'\0'):
 if b'=' not in item:continue
 k,v=item.split(b'=',1)
 if k.decode() in ['DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','XDG_CONFIG_DIRS','XDG_DATA_DIRS']:env[k.decode()]=v.decode()
for k,n in [('XDG_CONFIG_HOME','c'),('XDG_DATA_HOME','d'),('XDG_STATE_HOME','s'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','r')]:
 p=BASE/n;p.mkdir(mode=0o700);env[k]=str(p)
session=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','--user','show-environment'],text=True).splitlines() if '=' in line)
wl=session.get('WAYLAND_DISPLAY','wayland-0');env['WAYLAND_DISPLAY']=wl if wl.startswith('/') else '/run/user/1000/'+wl
env['PIPEWIRE_RUNTIME_DIR']='/run/user/1000';env['XDG_SESSION_TYPE']='wayland';env['XDG_CURRENT_DESKTOP']='KDE';env['QT_QPA_PLATFORM']='wayland';env['PATH']=str(PKG/'usr/bin')+':'+env['PATH'];sock=BASE/'r/putgd/session.sock'
subprocess.run(['python3',str(Path.home()/'work/i1363/tools/diagnostics/check_socket_paths.py'),'--socket',str(sock)],check=True)
(BASE/'environment.json').write_text(json.dumps({k:v for k,v in env.items() if k.startswith('XDG_') or k in ['DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','QT_QPA_PLATFORM','PATH','WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR']}));(BASE/'environment.json').chmod(0o600)
real_entry=Path.home()/'.local/share/applications/putgd-appimage-acceptance1363.desktop'
assert not real_entry.exists(),str(real_entry)
entry='[Desktop Entry]\nType=Application\nName=put.gd acceptance1363\nExec='+str(PKG/'usr/bin/putgd')+'\nNoDisplay=true\nX-KDE-DBUS-Restricted-Interfaces=org.kde.KWin.ScreenShot2;\n'
real_entry.parent.mkdir(parents=True,exist_ok=True);real_entry.write_text(entry);(BASE/'d/applications').mkdir();(BASE/'d/applications/putgd.desktop').write_text(entry)
cache_env=dict(os.environ,**session);subprocess.run(['kbuildsycoca6','--noincremental'],env=cache_env,check=True,stdout=open(E/'service-cache.log','w'),stderr=subprocess.STDOUT)
log=open(E/'resident.log','w');p=subprocess.Popen([str(PKG/'usr/bin/putgd'),'--background'],env=env,stdout=log,stderr=log,start_new_session=True);(BASE/'pid').write_text(str(p.pid))
def cli(method,params=None):
 r=subprocess.run([str(PKG/'usr/bin/putgd-cli'),'--socket',str(sock),method,json.dumps(params or {})],env=env,capture_output=True,text=True,timeout=30);return json.loads(r.stdout)
for _ in range(50):
 try:
  d=cli('diagnostics')
  if d.get('ok'):break
 except Exception:pass
 time.sleep(.2)
(E/'diagnostics.json').write_text(json.dumps(d,indent=2));assert d['result']['build']['gitTree']=='1e2d35a411dc2f281b3c3414c87503a62476eba8',d
s=cli('settings.get')['result'];cli('settings.patch',{'patch':{'archive':{'keepUploads':True,'root':str(BASE/'archive')},'preferences':{'notifications':False}},'expectedRevision':s['metadata']['observedRevision']});time.sleep(3)
# Full-screen only this private UI before any frame is exported from the host.
ui=[]
for item in Path('/proc').iterdir():
 if not item.name.isdigit():continue
 try:
  if item.joinpath('comm').read_text().strip()=='putgd-ui' and b'XDG_RUNTIME_DIR=/tmp/p1363k/r' in item.joinpath('environ').read_bytes().split(b'\0'):ui.append(int(item.name))
 except OSError:pass
assert len(ui)==1,ui
import dbus
os.environ['DBUS_SESSION_BUS_ADDRESS']=env['DBUS_SESSION_BUS_ADDRESS']
bus=dbus.SessionBus();scripting=dbus.Interface(bus.get_object('org.kde.KWin','/Scripting'),'org.kde.kwin.Scripting');plugin='putgd-acceptance1363-fullscreen'
js=BASE/'fullscreen.js';js.write_text('for (const w of workspace.windowList()) if(w.pid === '+str(ui[0])+' && w.normalWindow) w.fullScreen = true;')
id=int(scripting.loadScript(str(js),plugin,signature='ss'))
try:dbus.Interface(bus.get_object('org.kde.KWin','/Scripting/Script'+str(id)),'org.kde.kwin.Script').run();time.sleep(2)
finally:scripting.unloadScript(plugin)
sys.path.insert(0,str(Path.home()/'work/i1363/tools/lab'));from surface_driver.probe import kwin_windows
windows=kwin_windows();own=[w for w in windows['windows'] if int(w.get('pid',0))==ui[0] and w.get('normal')];assert len(own)==1,own;assert own[0]['content']==[0,0,1920,1080],own;(E/'fullscreen-placement.json').write_text(json.dumps({'windows':own},indent=2))
sys.path.insert(0,str(Path.home()/'work/i1363/tools/lab'));from rfb import RFB
v=RFB(5900);v.screenshot(E/'initial.png');v.close()
print('started',p.pid,flush=True)
