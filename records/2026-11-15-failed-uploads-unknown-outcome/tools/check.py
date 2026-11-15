import sys,json,time,shlex
from pathlib import Path
sys.path.insert(0,'.');sys.path.insert(0,'work/ta1532/r2')
from control import Control
from tools.lab.surface_driver.target import Target
class Check(Control):
 def __init__(self):
  self.host='k72';self.root='/tmp/t541';self.out=Path('work/ta1541');self.t=Target(host_profile='work/ta1532/k72.json',session_root=self.root,placement='native');self.t.require_lock('k72','ta1541');self.port=5972
 def js(self,code):
  script='import dbus,tempfile,os,time\nb=dbus.SessionBus();s=dbus.Interface(b.get_object("org.kde.KWin","/Scripting"),"org.kde.kwin.Scripting")\nf=tempfile.NamedTemporaryFile(mode="w",suffix=".js",delete=False);f.write('+repr(code)+');f.close()\nname="ta1541-"+str(os.getpid())\ntry:\n i=int(s.loadScript(f.name,name,signature="ss"));dbus.Interface(b.get_object("org.kde.KWin","/Scripting/Script%d"%i),"org.kde.kwin.Script").run();time.sleep(.3)\nfinally:\n s.unloadScript(name);os.unlink(f.name)\n'
  return self.session("python3 - 2>&1 <<'JS' || true\n"+script+'JS\n')
 def size(self,w):
  self.js('for(const w of workspace.windowList()){if(w.caption==="put.gd" && w.resourceClass==="putgd-ui"){w.frameGeometry={x:240,y:73,width:'+str(w)+',height:880};workspace.activeWindow=w;}}');time.sleep(1)
 def windows(self):
  return self.t.probe('compositor_windows',{})
