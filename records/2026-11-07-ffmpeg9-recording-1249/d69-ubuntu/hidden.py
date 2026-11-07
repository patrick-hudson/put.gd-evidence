import sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent/'tools/lab'))
engine=sys.argv.pop(1);r=__import__(engine);original=r.Driver.cli

def cli(self,build,method,params=None,timeout=60):
 result=original(self,build,method,params,timeout)
 if method=='recording.start':original(self,build,'recording.overlay',{'id':params['id'],'visible':False})
 return result
r.Driver.cli=cli
sys.exit(r.main())
