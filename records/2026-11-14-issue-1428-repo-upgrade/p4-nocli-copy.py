import os,pathlib,subprocess,json,time,sys,tempfile,shutil
out=pathlib.Path.home()/'repo1428p4'
for proc in pathlib.Path('/proc').iterdir():
 try:
  if (proc/'comm').read_text().strip()=='quickshell':
   e=dict(x.split('=',1) for x in (proc/'environ').read_bytes().decode().split('\0') if '=' in x)
   if 'HYPRLAND_INSTANCE_SIGNATURE' in e:break
 except (OSError,UnicodeError):pass
os.environ.update(e)
r=pathlib.Path(tempfile.mkdtemp(prefix='r1428-',dir='/tmp'));r.chmod(0o700)
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 (r/sub).mkdir(mode=0o700);os.environ[key]=str(r/sub)
rt=pathlib.Path(e['XDG_RUNTIME_DIR']);paths=[rt/'putgd/session.sock',rt/e['WAYLAND_DISPLAY'],rt/'hypr'/e['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock',rt/'hypr'/e['HYPRLAND_INSTANCE_SIGNATURE']/'.socket2.sock']
print('socket preflight',[(str(p.resolve()),len(str(p.resolve()).encode())) for p in paths],flush=True);assert all(len(str(p.resolve()).encode())<=107 for p in paths)
cfg=r/'config/putgd';cfg.mkdir(mode=0o700);v=json.loads((out/'p4-hotkey-config.json').read_text());v['archive']['root']=str(r/'archive');(cfg/'config.json').write_text(json.dumps(v));(cfg/'config.json').chmod(0o600)
log=open(out/'p4-resident.log','w');p=subprocess.Popen(['/usr/bin/putgd','--background'],stdout=log,stderr=log);f=None;c=None
try:
 time.sleep(5);print('resident PID',p.pid,'poll after 5 seconds',p.poll(),flush=True);assert p.poll() is None
 b=subprocess.run(['hyprctl','binds','-j'],capture_output=True,text=True);(out/'p4-binds.json').write_text(b.stdout);binds=json.loads(b.stdout);text=[x for x in binds if x.get('description')=='put.gd: Copy text from region'];print('text binding',json.dumps(text),flush=True);assert text,'Text hotkey was not bound'
 (out/'p4-resident-maps.txt').write_text(pathlib.Path('/proc',str(p.pid),'maps').read_text())
 f=subprocess.Popen(['/usr/bin/python3',str(out/'fixture.py')]);time.sleep(2)
 sys.path.insert(0,str(out));from rfb import RFB
 c=RFB(5940,host='10.0.2.2');w,h,pixels=c.frame();print('frame size',w,h,flush=True);c.screenshot(str(out/'p4-fixture.png'))
 expected=b'Repository upgrade test\nEnglish text is ready\nCopy this region';(out/'p4-fixture.txt').write_bytes(expected)
 subprocess.run(['wl-copy','--type','text/plain'],input=b'putgd acceptance pending',check=True)
 c.key('ctrl','shift','9');print('one physical Ctrl+Shift+9 sent',flush=True);time.sleep(1)
 c.screenshot(str(out/'p4-selector.png'));c.drag(110,130,650,300);print('one physical drag sent',flush=True)
 result=None
 for i in range(40):
  time.sleep(.25);z=subprocess.run(['wl-paste','--no-newline'],capture_output=True,timeout=3);result=z.stdout
  if result!=b'putgd acceptance pending':break
 (out/'p4-clipboard.txt').write_bytes(result);print('clipboard',repr(result),'exact match',result==expected,flush=True)
 time.sleep(.5);c.screenshot(str(out/'p4-result.png'));print('resident still up',p.poll() is None,flush=True)
finally:
 if c:c.close()
 for child in [f,p]:
  if child is None:continue
  child.terminate()
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 print('stopped owned PIDs',p.pid,f.pid if f else None,flush=True)
