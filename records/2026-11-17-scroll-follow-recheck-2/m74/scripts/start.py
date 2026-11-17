from pathlib import Path
import os,subprocess,json,time,stat
P=Path.cwd();os.environ['SFA_ROOT']=str(P)
assert (P/'candidate.AppImage').is_file()
(P/'candidate.AppImage').chmod(0o700)
with(P/'extract.log').open('w')as f:subprocess.run([str(P/'candidate.AppImage'),'--appimage-extract'],cwd=P,stdout=f,check=True)
(P/'extracted-file-list.json').write_text(json.dumps([str(f.relative_to(P))for f in(P/'squashfs-root').rglob('*')if f.is_file()or f.is_symlink()],indent=1))
import accept as A
proof=[{'resolved':str(p.resolve()),'utf8Bytes':len(str(p.resolve()).encode())}for p in[Path(A.E['XDG_RUNTIME_DIR'])/'putgd/session.sock',Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]+([Path(A.E['WAYLAND_DISPLAY'])]if A.E.get('WAYLAND_DISPLAY')else[])];assert all(v['utf8Bytes']<=107 for v in proof);(P/'actual-socket-preflight.json').write_text(json.dumps(proof,indent=1))
A.start();A.stop();time.sleep(1)
E=A.E
subprocess.Popen(['systemd-run','--user','--scope','--unit=sfr2-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS','DISPLAY','XAUTHORITY']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold.log').open('w'),stderr=subprocess.STDOUT)
for _ in range(150):
 try:dg=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('cold resident not ready')
assert dg['build']['gitTree']=='18a701a57cb74324481d7d2877bde086819fc160'
s=A.rpc('settings.get')['document'];assert all(v['destination']=='local'for v in s['actions'].values()if isinstance(v,dict)and'destination'in v)
(P/'cold-start-proof.json').write_text(json.dumps({'build':dg['build'],'allDestinationsLocal':True},indent=1));print('READY',flush=True)
