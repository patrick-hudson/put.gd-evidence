import sys,json,shlex
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(mode=0o700,parents=True,exist_ok=False)
lab.verify_owned_guest(run);lab.put(run,'tools/lab/cover_player.py','/dev/shm/np-cover-probe.py')
script='''import json,os,subprocess,time,signal
from pathlib import Path
root=Path('/dev/shm/np-cover-private2');root.mkdir(mode=0o700);(root/'runtime').mkdir(mode=0o700)
native_runtime=os.environ['XDG_RUNTIME_DIR']
os.environ['WAYLAND_DISPLAY']=str(Path(os.environ['XDG_RUNTIME_DIR'])/os.environ['WAYLAND_DISPLAY']) if not Path(os.environ['WAYLAND_DISPLAY']).is_absolute() else os.environ['WAYLAND_DISPLAY'];os.environ['XDG_RUNTIME_DIR']=str(root/'runtime')
fifo=root/'control';os.mkfifo(fifo,0o600);fd=os.open(fifo,os.O_RDWR)
with (root/'player.log').open('xb') as log:
 p=subprocess.Popen(['python3','/dev/shm/np-cover-probe.py','play','--pattern','--media-now','--video-size','640x320','--title','putgd synthetic fixture'],env=dict(os.environ,GTK_USE_PORTAL='0'),stdin=fd,stdout=log,stderr=log,start_new_session=True)
 start=Path('/proc/%d/stat'%p.pid).read_text().split(') ',1)[1].split()[19]
try:
 time.sleep(12)
 clients=json.loads(subprocess.check_output(['hyprctl','clients','-j'],env=dict(os.environ,XDG_RUNTIME_DIR=native_runtime)))
 records=[]
 for line in (root/'player.log').read_text().splitlines():
  try:records.append(json.loads(line))
  except ValueError:pass
 print(json.dumps({'pid':p.pid,'start':start,'exitCode':p.poll(),'records':records,'clients':[{k:c.get(k) for k in ('pid','title','class','at','size','fullscreen','mapped')} for c in clients if c.get('pid')==p.pid]}))
finally:
 if p.poll() is None:
  os.write(fd,b'quit\\n')
  try:p.wait(10)
  except subprocess.TimeoutExpired:
   assert Path('/proc/%d/stat'%p.pid).read_text().split(') ',1)[1].split()[19]==start
   p.terminate();p.wait(10)
 os.close(fd)
 fifo.unlink();(root/'player.log').unlink();(root/'runtime/dconf/user').unlink(missing_ok=True);(root/'runtime/dconf').rmdir() if (root/'runtime/dconf').exists() else None;(root/'runtime').rmdir();root.rmdir();Path('/dev/shm/np-cover-probe.py').unlink()
'''
result=json.loads(lab.guest_session(run,"python3 - <<'PY'\n"+script+"\nPY\n",timeout=90));(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
