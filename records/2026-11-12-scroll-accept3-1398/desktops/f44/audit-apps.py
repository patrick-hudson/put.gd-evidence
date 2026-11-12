from pathlib import Path
import os,json,sys
import record_run
e,_=record_run.session_environment();os.environ.update(e)
import pyatspi
rows=[];blocked=[]
for app in pyatspi.Registry.getDesktop(0):
 try:
  pid=app.get_process_id();q=Path('/proc')/str(pid)
  if not q.exists():continue
  comm=(q/'comm').read_text().strip();count=app.childCount;env=(q/'environ').read_bytes().split(bytes([0]));args=(q/'cmdline').read_bytes().split(bytes([0]));ours=any(x.startswith(b'XDG_CONFIG_HOME=/home/patrick/work/s3a/') for x in env)
  system=comm=='gnome-shell' or any(x in [b'/usr/share/gnome-shell/org.gnome.Shell.Notifications',b'/usr/share/gnome-shell/org.gnome.ScreenSaver'] for x in args)
  r={'pid':pid,'comm':comm,'accessibleChildren':count,'ownedTestApp':ours,'systemShell':system};rows.append(r)
  if count and not ours and not system:blocked.append(r)
 except Exception as ex:blocked.append({'inventoryError':type(ex).__name__})
print(json.dumps({'apps':rows,'blocked':blocked}));sys.exit(bool(blocked))
