"""Fresh disposable Omarchy overlay: exact CI package, all-local cold resident."""
import os,json,subprocess,hashlib,tarfile,socket,stat,errno,time
from pathlib import Path
P=Path.home()/'work/sfa15';P.chmod(0o700)
pid=subprocess.check_output(['pgrep','-x','Hyprland'],text=True).split();assert len(pid)==1
raw=(Path('/proc')/pid[0]/'environ').read_bytes().split(b'\0');env=dict(x.decode().split('=',1)for x in raw if b'='in x)
keys=['DISPLAY','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','HYPRLAND_INSTANCE_SIGNATURE','LANG']
E={k:env[k]for k in keys if k in env};E.update(XDG_RUNTIME_DIR='/run/user/1000',QT_QPA_PLATFORM='wayland')
assert E['XDG_SESSION_TYPE']=='wayland'and'Hyprland'in E.get('XDG_CURRENT_DESKTOP','')
for f in [P/'session-env.json',Path('/tmp/sfa15-session-env.json')]:f.write_text(json.dumps(E));f.chmod(0o600)
os.environ.update(E)
rt=Path('/tmp/sh25');assert not rt.exists();rt.mkdir(mode=0o700);(rt/'hypr').symlink_to('/run/user/1000/hypr',target_is_directory=True)
sig=E['HYPRLAND_INSTANCE_SIGNATURE'];paths=[rt/'putgd/session.sock',rt/'hypr'/sig/'.socket.sock',rt/'hypr'/sig/'.socket2.sock',Path('/run/user/1000')/E['WAYLAND_DISPLAY'].split('/')[-1],Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]
proof=[{'text':str(f),'textUtf8Bytes':len(str(f).encode()),'resolved':str(f.resolve()),'resolvedUtf8Bytes':len(str(f.resolve()).encode())}for f in paths];assert all(x['textUtf8Bytes']<=107 and x['resolvedUtf8Bytes']<=107 for x in proof);(P/'socket-preflight.json').write_text(json.dumps(proof,indent=1))
assert hashlib.sha256((P/'candidate.AppImage').read_bytes()).hexdigest()=='b6d8079774125b5fec692b7b8614bfabf0ea027ecc9118abda694fbfdab19bec'
assert not(P/'squashfs-root').exists();(P/'candidate.AppImage').chmod(0o700)
with(P/'extract.log').open('w')as f:subprocess.run([str(P/'candidate.AppImage'),'--appimage-extract'],cwd=P,stdout=f,check=True)
(P/'tools').mkdir(exist_ok=True)
with tarfile.open(P/'firefox-test-input.tar')as t:
 assert all(not x.name.startswith('/')and'..'not in Path(x.name).parts for x in t.getmembers());t.extractall(P/'tools',filter='data')
(P/'cli').write_text('#!/bin/sh\nexport LD_LIBRARY_PATH='+str(P)+'/squashfs-root/usr/lib:'+str(P)+'/squashfs-root/usr/lib/putgd\nexec '+str(P)+'/squashfs-root/usr/bin/putgd-cli --socket /tmp/sh25/putgd/session.sock "$@"\n');(P/'cli').chmod(0o700)
os.environ['SFA_DESKTOP']='Hyprland0.56.2 Omarchy4.5.0 h2 native Wayland'
import accept as A
A.start();A.stop();time.sleep(.5);f=rt/'putgd/session.sock'
if f.exists():
 st=f.lstat();assert stat.S_ISSOCK(st.st_mode)and st.st_uid==os.getuid();q=socket.socket(socket.AF_UNIX);c=q.connect_ex(str(f));q.close();assert c==errno.ECONNREFUSED;f.unlink()
E=A.E
subprocess.Popen(['systemd-run','--user','--scope','--unit=sfa15-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold-start.log').open('w'),stderr=subprocess.STDOUT)
for _ in range(150):
 try:d=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('Resident not ready')
assert d['build']['gitTree']=='bd64ffc5ac593690430bdbabb7e1f9ce6964de7e'
s=A.rpc('settings.get')['document'];assert all(v['destination']=='local'for v in s['actions'].values()if isinstance(v,dict)and'destination'in v);assert not s['preferences']['scrollCaptureFromTop'];time.sleep(2);assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
(P/'cold-start-proof.json').write_text(json.dumps({'build':d['build'],'allDestinationsLocal':True,'fromTop':False,'putgdUiPids':[]},indent=1));print(json.dumps(d['build']),flush=True)
