import os,pathlib,subprocess,json,time,sys,tempfile,signal
out=pathlib.Path.home()/'repo1428p3'; port=int(sys.argv[1]); name=sys.argv[2]
for proc in pathlib.Path('/proc').iterdir():
 try:
  if (proc/'comm').read_text().strip() in ('quickshell',):
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
os.environ['QT_QPA_PLATFORM']='wayland'
f=None; log=open(out/(name+'-app.log'),'w')
p=subprocess.Popen(['/usr/bin/putgd','--background'],stdout=log,stderr=log)
sys.path.insert(0,str(out));from rfb import RFB
try:
 for i in range(40):
  if sock.exists():break
  time.sleep(.25)
 def cli(m,params={}):
  z=subprocess.run(['/usr/bin/putgd-cli','--socket',str(sock),m,json.dumps(params)],capture_output=True,text=True);print(m,z.stdout,flush=True);return json.loads(z.stdout)
 cli('capabilities');f=subprocess.Popen(['/usr/bin/python3',str(out/'fixture.py')])
 time.sleep(2)
 c=RFB(port,host='10.0.2.2');w,h,pixels=c.frame(); white=sum(pixels[i:i+3]==b'\xff\xff\xff' for i in range(0,len(pixels),4))/ (w*h);print('fixture white coverage',white,flush=True);print('size',w,h); from PIL import Image
 def frame(path):
  ww,hh,pp=c.frame();im=Image.frombytes('RGB',(ww,hh),bytes(pp),'raw','BGRX');im=im.crop((100,100,700,340)); assert sum(px==(255,255,255) for px in im.getdata())/(600*240)>.90;im.save(path)
 frame(str(out/(name+'-fixture.png')))
 z=cli('text.recognize',{'source':'region','copy':True});oid=z['result']['operationId']
 time.sleep(1);c.drag(110,130,650,300)
 for i in range(40):
  time.sleep(.25);z=cli('text.inspect',{'id':oid})
  if z.get('result',{}).get('state') in ('completed','failed','cancelled'):break
 time.sleep(.5);frame(str(out/(name+'-result.png')));c.close()
 # Independent clipboard tool uses the actual desktop runtime.
 pasteenv=os.environ.copy();pasteenv['XDG_RUNTIME_DIR']=env['XDG_RUNTIME_DIR']
 z=subprocess.run(['wl-paste','--no-newline'],capture_output=True,env=pasteenv)
 (out/(name+'-clipboard.txt')).write_bytes(z.stdout)
 expected=b'Repository upgrade test\nEnglish text is ready\nCopy this region'
 (out/(name+'-fixture.txt')).write_bytes(expected)
 print('clipboard',repr(z.stdout),'exact',z.stdout==expected,flush=True)
finally:
 for child in [p,f]:
  if child is None:continue
  child.terminate()
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 print('stopped owned PIDs',p.pid,f.pid,flush=True)
 (out/(name+'-private-dir.txt')).write_text(str(r))
