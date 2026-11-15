"""Prepare the published nightly only after all candidate driving has ended."""
import os,json,subprocess,hashlib,socket,stat,errno,time,shutil
from pathlib import Path
P=Path.home()/'work/sfa15';B=P/'b';TREE='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
os.environ.update(json.loads((P/'session-env.json').read_text()));os.environ['XDG_RUNTIME_DIR']='/run/user/1000'
for n in ['putgd-record','firefox']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],check=True)
for n in ['putgd','putgd-ui','putgd-record','firefox']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
assert not B.exists();B.mkdir(mode=0o700)
assert hashlib.sha256((P/'nightly.AppImage').read_bytes()).hexdigest()=='0b60880785851dee4febd216998dc0d2d00bfada167d7cc366eb7c254b198695'
paths=[B/'r/putgd/session.sock',P/'pointer.sock',Path('/run/user/1000/wayland-0'),Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]
rows=[{'resolved':str(f.resolve()),'utf8Bytes':len(str(f.resolve()).encode())}for f in paths];assert all(x['utf8Bytes']<=107 for x in rows);(B/'socket-preflight.json').write_text(json.dumps(rows,indent=1))
(P/'nightly.AppImage').chmod(0o700)
with(B/'extract.log').open('w')as f:subprocess.run([str(P/'nightly.AppImage'),'--appimage-extract'],cwd=B,stdout=f,check=True)
for n in ['accept.py','live7.py','rfb.py','umouse-native.py','ukey-native.py','ukey-ready-native.py','session-env.json']:shutil.copyfile(P/n,B/n)
(B/'session-env.json').chmod(0o600)
s=(P/'guest-agent.py').read_text().replace("P=Path.home()/'work/sfa15'","P=Path.home()/'work/sfa15/b'")
s=s.replace("str(P/'pointer.sock')","'/home/lab/work/sfa15/pointer.sock'")
s=s.replace("os.environ['SFA_DESKTOP']=","os.environ['SFA_ROOT']=str(P)\nos.environ['SFA_EXPECT_TREE']='"+TREE+"'\nos.environ['SFA_DESKTOP']=",1);(B/'guest-agent.py').write_text(s)
(B/'tools').mkdir();(B/'tools/firefox').symlink_to(P/'tools/firefox',target_is_directory=True)
(B/'cli').write_text('#!/bin/sh\nexport LD_LIBRARY_PATH='+str(B)+'/squashfs-root/usr/lib:'+str(B)+'/squashfs-root/usr/lib/putgd\nexec '+str(B)+'/squashfs-root/usr/bin/putgd-cli --socket '+str(B)+'/r/putgd/session.sock "$@"\n');(B/'cli').chmod(0o700)
code="""import os,json,time,subprocess,socket,stat,errno
from pathlib import Path
P=Path.cwd();os.environ.update(json.loads((P/'session-env.json').read_text()));os.environ['SFA_ROOT']=str(P);os.environ['SFA_EXPECT_TREE']='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3';os.environ['SFA_DESKTOP']='Fedora45 Budgie10.10.3 labwc0.20.2 native Wayland KVM guest'
import accept as A
A.start();A.stop();time.sleep(.5)
f=P/'r/putgd/session.sock'
if f.exists():
 z=f.lstat();assert stat.S_ISSOCK(z.st_mode)and z.st_uid==os.getuid();q=socket.socket(socket.AF_UNIX);c=q.connect_ex(str(f));q.close();assert c==errno.ECONNREFUSED;f.unlink()
E=A.E
subprocess.Popen(['systemd-run','--user','--scope','--unit=sfa15-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS','LABWC_PID']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold-start.log').open('w'),stderr=subprocess.STDOUT)
for _ in range(150):
 try:d=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('Baseline cold start not ready')
assert d['build']['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3';settings=A.rpc('settings.get')['document'];assert all(v['destination']=='local'for v in settings['actions'].values()if isinstance(v,dict)and'destination'in v);assert not settings['preferences']['scrollCaptureFromTop']
time.sleep(2);assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
(P/'cold-start-proof.json').write_text(json.dumps({'build':d['build'],'allDestinationsLocal':True,'fromTop':False,'putgdUiPids':[]},indent=1));print(json.dumps(d['build']),flush=True)
"""
(B/'cold-start.py').write_text(code)
with(B/'setup.log').open('w')as f:subprocess.run(['python3','cold-start.py'],cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
print(json.dumps({'baselineRoot':str(B),'tree':TREE,'allLocal':True}),flush=True)
