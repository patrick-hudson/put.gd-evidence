import os,pathlib,subprocess,json,time,sys,tempfile,signal
out=pathlib.Path.home()/'repo1428'; port=int(sys.argv[1]); name=sys.argv[2]
for proc in pathlib.Path('/proc').iterdir():
 try:
  if (proc/'comm').read_text().strip() in ('plasmashell','gnome-shell'):
   env=dict(x.split('=',1) for x in (proc/'environ').read_bytes().decode().split('\0') if '=' in x)
   if 'WAYLAND_DISPLAY' in env:break
 except (OSError,UnicodeError):pass
env.update(dict(x.split('=',1) for x in subprocess.check_output(['systemctl','--user','show-environment'],text=True).splitlines() if '=' in x))
os.environ.update(env)
os.environ['WAYLAND_DISPLAY']=env['XDG_RUNTIME_DIR']+'/'+env['WAYLAND_DISPLAY'] if not env['WAYLAND_DISPLAY'].startswith('/') else env['WAYLAND_DISPLAY']
r=pathlib.Path(tempfile.mkdtemp(prefix='r1428-',dir='/tmp'));r.chmod(0o700)
for x in ['config','data','cache','state','rt']:(r/x).mkdir(mode=0o700)
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state'),('XDG_RUNTIME_DIR','rt')]:os.environ[key]=str(r/sub)
sock=r/'rt/putgd/session.sock'; print('socket',str(sock),len(str(sock).encode()),flush=True);assert len(str(sock).encode())<=107
f=None; log=open(out/(name+'-app.log'),'w')
p=subprocess.Popen(['/usr/bin/putgd','--background'],stdout=log,stderr=log)
sys.path.insert(0,str(out));from rfb import RFB
try:
 for i in range(40):
  if sock.exists():break
  time.sleep(.25)
 def cli(m,params={}):
  z=subprocess.run(['/usr/bin/putgd-cli','--socket',str(sock),m,json.dumps(params)],capture_output=True,text=True);print(m,z.stdout,flush=True);return json.loads(z.stdout)
 cli('capabilities');cli('action.invoke',{'action':'text'})
finally:
 for child in [p,f]:
  if child is None:continue
  child.terminate()
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 print('stopped owned PIDs',p.pid,f.pid if f else None,flush=True)
 (out/(name+'-private-dir.txt')).write_text(str(r))
