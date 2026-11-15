"""Fresh short isolated physical-desktop supplement; test adapters only."""
import os,json,subprocess,hashlib,shutil,socket,stat,errno,time,sys,importlib.util
from pathlib import Path
P=Path.cwd();old=Path.home()/'work/sfa15';host=sys.argv[1];assert P.name=='sfa15u'and not(P/'squashfs-root').exists()
for n in ['putgd','putgd-ui','putgd-record','firefox','firefox-bin','chrome']:
 assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
proof=[{'resolved':str(f.resolve()),'utf8Bytes':len(str(f.resolve()).encode())}for f in [P/'r/putgd/session.sock',old/'r/putgd/session.sock',Path('/run/user/1000/wayland-0'),Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]]
assert all(x['utf8Bytes']<=107 for x in proof);(P/'socket-preflight.json').write_text(json.dumps(proof,indent=1))
f=Path.home()/'.config/kcminputrc'
if host=='aurora-amd':
 d={'exists':f.exists(),'mode':oct(stat.S_IMODE(f.stat().st_mode))if f.exists()else None,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()if f.exists()else None}
 if f.exists():assert not f.is_symlink();shutil.copyfile(f,P/'kcminputrc-before');(P/'kcminputrc-before').chmod(stat.S_IMODE(f.stat().st_mode))
else:
 env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus');schema='org.cinnamon.desktop.peripherals.mouse'if host=='m74'else'org.gnome.desktop.peripherals.mouse';d={'schema':schema,'values':{k:subprocess.check_output(['gsettings','get',schema,k],env=env,text=True).strip()for k in ['accel-profile','speed']}}
(P/'input-before.json').write_text(json.dumps(d,indent=1))
shutil.copyfile(old/'candidate.AppImage',P/'candidate.AppImage');assert hashlib.sha256((P/'candidate.AppImage').read_bytes()).hexdigest()=='b6d8079774125b5fec692b7b8614bfabf0ea027ecc9118abda694fbfdab19bec';(P/'candidate.AppImage').chmod(0o700)
with(P/'extract.log').open('w')as log:subprocess.run([str(P/'candidate.AppImage'),'--appimage-extract'],cwd=P,stdout=log,check=True)
shutil.copyfile(P/('accept-m74.py'if host=='m74'else'accept-f44-runtime.py'),P/'accept.py')
s=(P/'accept.py').read_text()
if host=='m74':start=s.index('for n in [');end=s.index('found=dict',start);s=s[:start]+s[end:]
(P/'accept.py').write_text(s)
shutil.copyfile(P/'live7-native-viewport.py',P/'live7.py');shutil.copyfile(P/'trial-native-pointer.py',P/'trial_relative.py')
(P/'tools').mkdir()
for n in ['firefox','chrome-linux64']:
 f=old/'tools'/n
 if f.exists():(P/'tools'/n).symlink_to(f,target_is_directory=True)
assert (P/'tools/firefox/firefox').exists()
(P/'cli').write_text('#!/bin/sh\nexport LD_LIBRARY_PATH='+str(P)+'/squashfs-root/usr/lib:'+str(P)+'/squashfs-root/usr/lib/putgd\nexec '+str(P)+'/squashfs-root/usr/bin/putgd-cli --socket '+str(P)+'/r/putgd/session.sock "$@"\n');(P/'cli').chmod(0o700)
(P/'helper.log').touch()
if '--prepare-only'in sys.argv:
 print('Prepared isolated package and inputs; resident has not started',flush=True);raise SystemExit(0)
os.environ['SFA_ROOT']=str(P)
import accept as A
actual=[Path(A.E['XDG_RUNTIME_DIR'])/'putgd/session.sock',Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0'),Path('/run/user/1000/pulse/native')]
if A.E.get('WAYLAND_DISPLAY'):actual.append(Path(A.E['WAYLAND_DISPLAY']))
actualProof=[{'resolved':str(f.resolve()),'utf8Bytes':len(str(f.resolve()).encode())}for f in actual];assert all(x['utf8Bytes']<=107 for x in actualProof);(P/'actual-socket-preflight.json').write_text(json.dumps(actualProof,indent=1))
def launch_cold(root,unit,log):
 E=dict(A.E,XDG_RUNTIME_DIR=str(root/'r'),XDG_CONFIG_HOME=str(root/'c'),XDG_DATA_HOME=str(root/'d'),XDG_STATE_HOME=str(root/'s'),XDG_CACHE_HOME=str(root/'cache'),PUTGD_RECORD_DEBUG_LOG=str(P/('helper.log'if unit=='sfa15-res'else unit+'-helper.log')))
 sock=root/'r/putgd/session.sock'
 if sock.exists():
  st=sock.lstat();assert stat.S_ISSOCK(st.st_mode)and st.st_uid==os.getuid();q=socket.socket(socket.AF_UNIX);code=q.connect_ex(str(sock));q.close();assert code==errno.ECONNREFUSED;sock.unlink()
 subprocess.Popen(['systemd-run','--user','--scope','--unit='+unit,'env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER','QT_QPA_PLATFORM','DBUS_SESSION_BUS_ADDRESS','DISPLAY','XAUTHORITY']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/log).open('w'),stderr=subprocess.STDOUT)
 return E,sock
if host=='aurora-amd':
 E,sock=launch_cold(old,'sfa15-audit','old-audit-resident.log')
 original=A.rpc;A.P=old
 def rpc(m,p={}):
  r=subprocess.run([str(P/'squashfs-root/usr/bin/putgd-cli'),'--socket',str(sock),m,json.dumps(p)],env=dict(E,LD_LIBRARY_PATH=str(P/'squashfs-root/usr/lib')+':'+str(P/'squashfs-root/usr/lib/putgd')),capture_output=True,text=True,timeout=100);v=json.loads(r.stdout)
  if not v.get('ok'):raise RuntimeError(v)
  return v['result']
 A.rpc=rpc
 for _ in range(150):
  try:dg=rpc('diagnostics');break
  except Exception:time.sleep(.1)
 else:raise RuntimeError('Old profile audit resident not ready')
 assert dg['build']['gitTree']=='bd64ffc5ac593690430bdbabb7e1f9ce6964de7e';s=rpc('settings.get')['document'];assert all(v['destination']=='local'for v in s['actions'].values()if isinstance(v,dict)and'destination'in v)
 exec(compile((P/'audit-controls.py').read_text(),'old-profile-audit','exec'),{'__name__':'old_profile_audit'})
 shutil.copyfile(old/'control-history-staging-audit.json',P/'old-control-history-staging-audit.json');subprocess.run(['systemctl','--user','stop','sfa15-audit.scope'],check=True);A.P=P;A.rpc=original
A.start();A.stop();time.sleep(.5);E,sock=launch_cold(P,'sfa15-res','resident-cold.log')
for _ in range(150):
 try:dg=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('Cold supplement resident not ready')
assert dg['build']['gitTree']=='bd64ffc5ac593690430bdbabb7e1f9ce6964de7e';s=A.rpc('settings.get')['document'];assert all(v['destination']=='local'for v in s['actions'].values()if isinstance(v,dict)and'destination'in v);assert not s['preferences']['scrollCaptureFromTop'];time.sleep(2);assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
(P/'cold-start-proof.json').write_text(json.dumps({'build':dg['build'],'allDestinationsLocal':True,'fromTop':False,'putgdUiPids':[]},indent=1));print(json.dumps(dg['build']),flush=True)
