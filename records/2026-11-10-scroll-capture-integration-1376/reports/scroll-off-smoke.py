import tempfile,pathlib,os,subprocess,time,json
r=pathlib.Path(tempfile.mkdtemp(prefix='sc-off-',dir='/tmp'));(r/'r').mkdir(mode=0o700);s=r/'r/putgd/session.sock';subprocess.run(['python3','tools/diagnostics/check_socket_paths.py','--socket',str(s)],check=True)
env=os.environ|{'QT_QPA_PLATFORM':'offscreen','XDG_SESSION_TYPE':'unspecified','XDG_CURRENT_DESKTOP':'scroll-off-test','XDG_RUNTIME_DIR':str(r/'r'),'XDG_CONFIG_HOME':str(r/'c'),'XDG_DATA_HOME':str(r/'d'),'XDG_STATE_HOME':str(r/'s')}
for k in ['DISPLAY','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS']:env.pop(k,None)
with (r/'resident.log').open('w') as f:
 p=subprocess.Popen(['build/no-record/putgd','--background'],env=env,stdout=f,stderr=f)
 try:
  for _ in range(100):
   if s.exists():break
   time.sleep(.05)
  v=json.loads(subprocess.check_output(['build/no-record/putgd-cli','--socket',str(s),'scroll.capabilities'],env=env));print(json.dumps(v));assert v['result']['reason']=='recording_helper_missing' and not v['result']['available']
 finally:p.terminate();p.wait()
print('PASS helper-disabled production resident',r)
