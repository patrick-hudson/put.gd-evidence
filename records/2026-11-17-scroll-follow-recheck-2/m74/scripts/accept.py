import os,sys,json,time,subprocess,threading,shutil
from pathlib import Path
P=Path(os.environ.get('SFA_ROOT',str(Path.home()/'work/sfa15')))
sys.path.insert(0,str(P)); import live7 as L
L.P=P
BASE=Path.home()/'work/scroll-session/lab/tools'
# Keep browser executables, but isolate profiles and all run outputs.
(P/'tools').mkdir(exist_ok=True)
found=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','--user','show-environment'],text=True,env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000')).splitlines() if '=' in x)
def env():
 e=dict(os.environ); e.update({k:found[k] for k in ['DISPLAY','WAYLAND_DISPLAY','XAUTHORITY','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','DBUS_SESSION_BUS_ADDRESS'] if k in found})
 e.update(XDG_RUNTIME_DIR=str(P/'r'),XDG_CONFIG_HOME=str(P/'c'),XDG_DATA_HOME=str(P/'d'),XDG_STATE_HOME=str(P/'s'),XDG_CACHE_HOME=str(P/'cache'),PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native',QT_QPA_PLATFORM='wayland',PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'))
 
 if e.get('WAYLAND_DISPLAY'):e['WAYLAND_DISPLAY']='/run/user/1000/'+e['WAYLAND_DISPLAY'].split('/')[-1]
 return e
E=env(); E.update(DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',DISPLAY=':0',XAUTHORITY=str(Path.home()/'.Xauthority'),XDG_SESSION_TYPE='x11',XDG_CURRENT_DESKTOP='X-Cinnamon',QT_QPA_PLATFORM='xcb'); E.pop('WAYLAND_DISPLAY',None)
DESKTOP=os.environ.get('SFA_DESKTOP','Plasma 6.8.2 Wayland')
L.session_env=lambda:(E,DESKTOP)
def rpc(m,p={}):
 r=subprocess.run([str(P/'cli'),m,json.dumps(p)],env=E,capture_output=True,text=True,timeout=100)
 o=json.loads(r.stdout)
 if not o.get('ok'):raise RuntimeError(o)
 return o['result']
def start():
 for n in ['r','c','d','s','cache','archive']:(P/n).mkdir(mode=0o700,exist_ok=True)
 sock=str((P/'r/putgd/session.sock').resolve());print('socket bytes',len(sock.encode()),flush=True); assert len(sock.encode())<=107
 q=subprocess.Popen(['systemd-run','--user','--scope','--unit=sfr2-res','env',*[k+'='+E[k] for k in E if k.startswith('XDG_') or k.startswith('PUTGD_') or k in ['WAYLAND_DISPLAY','PIPEWIRE_RUNTIME_DIR','PULSE_SERVER']],os.environ.get('SFA_APP',str(P/'squashfs-root/AppRun')),'--background'],env=dict(E,XDG_RUNTIME_DIR='/run/user/1000'),stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT)
 (P/'resident-scope.pid').write_text(str(q.pid))
 for _ in range(150):
  if (P/'r/putgd/session.sock').exists():break
  time.sleep(.1)
 s=rpc('settings.get'); t=rpc('settings.developmentTemplate'); (P/'template.json').write_text(json.dumps(t,indent=1))
 d=t.get('document',t)
 for v in d['actions'].values():
  if isinstance(v,dict) and 'destination'in v:v.update(destination='local',profileId=None)
 d['limits']['imagePixels']=120000000;d['archive'].update(keepUploads=True,root=str(P/'archive'))
 d['preferences']['scrollCaptureAutoScroll']=False;d['preferences']['scrollCaptureMaxHeight']=60000; d['preferences']['updates']={'check':False}
 rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']}); rpc('settings.reload')
 diagnostic=rpc('diagnostics'); (P/'diagnostics.json').write_text(json.dumps(diagnostic,indent=1)); assert diagnostic['build']['gitTree']==os.environ.get('SFA_EXPECT_TREE','18a701a57cb74324481d7d2877bde086819fc160'),diagnostic['build']; print((P/'diagnostics.json').read_text()[:1600])
 print('CONFIGURED',flush=True)
def stop():
 subprocess.run(['systemctl','--user','stop','sfr2-res.scope'])
if __name__=='__main__':
 if sys.argv[1]=='start':start()
 elif sys.argv[1]=='stop':stop()
 elif sys.argv[1]=='rpc':print(json.dumps(rpc(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {}),indent=1))
