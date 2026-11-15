import os,json,subprocess,hashlib,shutil,socket,errno,stat,time
from pathlib import Path
P=Path.home()/'work/sfa15';assert not(P/'squashfs-root').exists()
for n in ['putgd','putgd-ui','putgd-record','firefox','firefox-bin']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
f=Path.home()/'.config/kcminputrc';before={'exists':f.exists(),'mode':oct(stat.S_IMODE(f.stat().st_mode))if f.exists()else None,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()if f.exists()else None}
if f.exists():assert not f.is_symlink();shutil.copyfile(f,P/'kcminputrc-before');(P/'kcminputrc-before').chmod(stat.S_IMODE(f.stat().st_mode))
(P/'input-before.json').write_text(json.dumps(before,indent=1))
paths=[P/'r/putgd/session.sock',Path('/run/user/1000/wayland-0'),Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]
proof=[{'resolved':str(x.resolve()),'utf8Bytes':len(str(x.resolve()).encode())}for x in paths];assert all(x['utf8Bytes']<=107 for x in proof);(P/'socket-preflight.json').write_text(json.dumps(proof,indent=1))
assert hashlib.sha256((P/'candidate.AppImage').read_bytes()).hexdigest()=='b6d8079774125b5fec692b7b8614bfabf0ea027ecc9118abda694fbfdab19bec'
(P/'candidate.AppImage').chmod(0o700)
with(P/'extract.log').open('w')as out:subprocess.run([str(P/'candidate.AppImage'),'--appimage-extract'],cwd=P,stdout=out,check=True)
shutil.copyfile(P/'accept-f44-runtime.py',P/'accept.py');shutil.copyfile(P/'live7-native-viewport.py',P/'live7.py');shutil.copyfile(P/'trial-native-pointer.py',P/'trial_relative.py')
(P/'tools/firefox').mkdir(parents=True);(P/'tools/firefox/firefox').write_text('#!/bin/sh\nexec /usr/bin/firefox "$@"\n');(P/'tools/firefox/firefox').chmod(0o700);(P/'cli').chmod(0o700)
os.environ['SFA_DESKTOP']='Kubuntu26.04 Plasma6.6.6 native Wayland';import accept as A
A.start();A.stop();time.sleep(.5)
f=P/'r/putgd/session.sock'
if f.exists():
 z=f.lstat();assert stat.S_ISSOCK(z.st_mode)and z.st_uid==os.getuid();s=socket.socket(socket.AF_UNIX);c=s.connect_ex(str(f));s.close();assert c==errno.ECONNREFUSED;f.unlink()
E=A.E
subprocess.Popen(['systemd-run','--user','--scope','--unit=sfa15-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold.log').open('w'),stderr=subprocess.STDOUT)
for _ in range(150):
 try:d=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('Cold resident not ready')
settings=A.rpc('settings.get')['document'];assert all(x['destination']=='local'for x in settings['actions'].values()if isinstance(x,dict)and'destination'in x);assert not settings['preferences']['scrollCaptureFromTop'];time.sleep(2)
assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
(P/'cold-start-proof.json').write_text(json.dumps({'build':d['build'],'allDestinationsLocal':True,'putgdUiPids':[],'fromTop':False},indent=1));print(json.dumps(d['build']),flush=True)
