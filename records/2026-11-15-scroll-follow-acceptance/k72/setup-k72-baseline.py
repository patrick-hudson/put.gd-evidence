import os,json,subprocess,hashlib,shutil,socket,stat,errno,time
from pathlib import Path
P=Path.cwd();B=P/'b';assert not B.exists()
subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],check=True)
for n in ['putgd','putgd-ui','putgd-record','firefox','firefox-bin']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
shutil.copyfile(Path.home()/'work/scroll-1514-lab/putgd-26.1113.4757-nightly-x86_64.AppImage',P/'nightly.AppImage')
assert hashlib.sha256((P/'nightly.AppImage').read_bytes()).hexdigest()=='0b60880785851dee4febd216998dc0d2d00bfada167d7cc366eb7c254b198695'
B.mkdir(mode=0o700);(P/'nightly.AppImage').chmod(0o700)
paths=[B/'r/putgd/session.sock',Path('/run/user/1000/wayland-0'),Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')];proof=[{'resolved':str(f.resolve()),'utf8Bytes':len(str(f.resolve()).encode())}for f in paths];assert all(x['utf8Bytes']<=107 for x in proof);(B/'socket-preflight.json').write_text(json.dumps(proof,indent=1))
with(B/'extract.log').open('w')as f:subprocess.run([str(P/'nightly.AppImage'),'--appimage-extract'],cwd=B,stdout=f,check=True)
for f in P.glob('*.py'):shutil.copyfile(f,B/f.name)
(B/'tools').mkdir();(B/'tools/firefox').symlink_to(P/'tools/firefox',target_is_directory=True);(B/'helper.log').touch()
(B/'cli').write_text((P/'cli').read_text().replace(str(P/'squashfs-root'),str(B/'squashfs-root')).replace(str(P/'r/putgd/session.sock'),str(B/'r/putgd/session.sock')));(B/'cli').chmod(0o700)
entry=Path.home()/'.local/share/applications/putgd-sfa15-baseline-record.desktop';assert not entry.exists();entry.write_text('[Desktop Entry]\nType=Application\nName=put.gd isolated nightly acceptance recorder\nExec="'+str(B/'squashfs-root/usr/bin/putgd-record')+'"\nIcon=putgd\nNoDisplay=true\nX-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1,org_kde_kwin_fake_input\n');shutil.copyfile(entry,P/'installed-baseline-recorder-permission-entry.txt')
env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME']:env.pop(k,None)
subprocess.run(['kbuildsycoca6','--noincremental'],env=env,check=True,stdout=(B/'kbuildsycoca-setup.log').open('w'),stderr=subprocess.STDOUT)
code="""import os,json,subprocess,time,stat,socket,errno
from pathlib import Path
P=Path.cwd()
import accept as A
A.start()
s=A.rpc('settings.get');d=s['document'];d['preferences']['scrollCaptureFromTop']=False;A.rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']});A.rpc('settings.reload');A.stop();time.sleep(.5)
f=P/'r/putgd/session.sock'
if f.exists():
 st=f.lstat();assert stat.S_ISSOCK(st.st_mode)and st.st_uid==os.getuid();q=socket.socket(socket.AF_UNIX);v=q.connect_ex(str(f));q.close();assert v==errno.ECONNREFUSED;f.unlink()
E=A.E;subprocess.Popen(['systemd-run','--user','--scope','--unit=sfa15-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold.log').open('w'),stderr=subprocess.STDOUT)
for _ in range(150):
 try:d=A.rpc('diagnostics')
 except Exception:time.sleep(.1);continue
 if d['capabilities']['scroll'].get('reason')=='scroll_probe_pending':time.sleep(.2);continue
 break
else:raise RuntimeError('Baseline not ready')
assert d['build']['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3';assert d['capabilities']['scroll']['available'],d['capabilities']['scroll']
s=A.rpc('settings.get')['document'];assert all(x['destination']=='local'for x in s['actions'].values()if isinstance(x,dict)and'destination'in x);assert not s['preferences']['scrollCaptureFromTop'];time.sleep(2);assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
(P/'cold-start-proof.json').write_text(json.dumps({'build':d['build'],'allDestinationsLocal':True,'fromTop':False,'putgdUiPids':[]},indent=1));print(json.dumps(d['build']),flush=True)
"""
(B/'baseline-cold-setup.py').write_text(code)
env.update(SFA_ROOT=str(B),SFA_EXPECT_TREE='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3',SFA_DESKTOP='Kubuntu26.04 Plasma6.6.6 native Wayland',SFA_NATIVE_POINTER='1')
with(B/'setup.log').open('w')as f:subprocess.run(['python3','baseline-cold-setup.py'],cwd=B,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
print((B/'cold-start-proof.json').read_text(),flush=True)
