"""Restart the already configured all-local profile without reopening Settings."""
import os,json,subprocess,time
from pathlib import Path
P=Path.home()/'work/sfa15/b';os.environ.update(json.loads((P/'session-env.json').read_text()));os.environ['SFA_DESKTOP']='Hyprland0.56.2 Omarchy4.5.0 KVM guest'
os.environ['SFA_ROOT']=str(P)
os.environ['SFA_EXPECT_TREE']='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
import accept as A
A.stop()
for _ in range(100):
 if not subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.strip():break
 time.sleep(.1)
assert not subprocess.run(['pgrep','-x','putgd'],capture_output=True,text=True).stdout.strip()
assert not subprocess.run(['pgrep','-x','putgd-ui'],capture_output=True,text=True).stdout.strip()
E=A.E;sock=Path(E['XDG_RUNTIME_DIR'])/'putgd/session.sock';assert not sock.exists();assert len(str(sock).encode())<=107
q=subprocess.Popen(['systemd-run','--user','--scope','--unit=sfa15-res','env',*[k+'='+v for k,v in E.items()if k.startswith('XDG_')or k.startswith('PUTGD_')or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER']],str(P/'squashfs-root/AppRun'),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=(P/'resident-cold-start.log').open('w'),stderr=subprocess.STDOUT)
(P/'resident-scope.pid').write_text(str(q.pid))
for _ in range(150):
 try:d=A.rpc('diagnostics');break
 except Exception:time.sleep(.1)
else:raise RuntimeError('Resident restart not ready')
assert d['build']['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
s=A.rpc('settings.get')['document'];assert all(v['destination']=='local'for v in s['actions'].values()if isinstance(v,dict)and 'destination'in v)
time.sleep(2)
env=dict(os.environ,**json.loads((P/'session-env.json').read_text()));clients=json.loads(subprocess.check_output(['hyprctl','clients','-j'],env=env,text=True));proof={'build':d['build'],'allDestinationsLocal':True,'nativeClients':[{k:x.get(k)for k in ['pid','class','at','size','xwayland']}for x in clients]}
(P/'cold-start-proof.json').write_text(json.dumps(proof,indent=1));print(json.dumps(proof),flush=True)
