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
oldrun=r.subprocess.run
def run(cmd,*args,**kwargs):
 if isinstance(cmd,list) and 'precheck' in cmd and any('cover_player.py' in str(x) for x in cmd):
  from rfb import RFB
  import time
  v=RFB(5900);v.pointer(1877,35,True);time.sleep(.1);v.pointer(1877,35,False);v.close();time.sleep(.3)
 return oldrun(cmd,*args,**kwargs)
r.subprocess.run=run
sys.exit(r.main())
