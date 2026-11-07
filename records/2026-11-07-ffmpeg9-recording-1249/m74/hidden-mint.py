import sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent/'tools/lab'))
engine=sys.argv.pop(1);r=__import__(engine);original=r.Driver.cli

def cli(self,build,method,params=None,timeout=60):
 result=original(self,build,method,params,timeout)
 if method=='recording.start':original(self,build,'recording.overlay',{'id':params['id'],'visible':False})
 return result
r.Driver.cli=cli
oldstart=r.Driver.start_resident
def start(self,b):
 caps=oldstart(self,b);s=original(self,b,'settings.get')
 if s['document'].get('preferences',{}).get('fileManagerMenu',True):original(self,b,'settings.patch',{'patch':{'preferences':{'fileManagerMenu':False}},'expectedRevision':s['metadata']['observedRevision']})
 return caps
r.Driver.start_resident=start
def close_notice(self):
 code='Object.values(imports.ui.main.notificationDaemon._notifications).filter(n => n.appName === "put.gd" && n.summary === "put.gd — file manager menu").map(n => { imports.ui.main.notificationDaemon.CloseNotification(n.id); return n.id; })'
 r.subprocess.run(['gdbus','call','--session','--dest','org.Cinnamon.LookingGlass','--object-path','/org/Cinnamon/LookingGlass','--method','org.Cinnamon.LookingGlass.Eval',code],env=self.env,capture_output=True)
oldstart2=r.Driver.start_resident
def start2(self,b):
 result=oldstart2(self,b)
 import time
 time.sleep(2);close_notice(self)
 return result
r.Driver.start_resident=start2
oldcli2=r.Driver.cli
def cli2(self,b,method,params=None,timeout=60):
 result=oldcli2(self,b,method,params,timeout)
 if method=='recording.start':close_notice(self)
 return result
r.Driver.cli=cli2
sys.exit(r.main())
