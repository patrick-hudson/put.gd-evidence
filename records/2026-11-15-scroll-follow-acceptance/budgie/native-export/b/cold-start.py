import os,json,time,subprocess,socket,stat,errno
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
