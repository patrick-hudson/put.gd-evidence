import os,json,subprocess,time,stat,socket,errno
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
