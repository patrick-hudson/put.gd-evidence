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
  import socket,json,time
  v=socket.socket(socket.AF_UNIX);v.connect('/run/user/1000/ff9-input.sock');f=v.makefile('rwb',buffering=0);f.readline()
  def send(x):f.write((json.dumps(x)+'\n').encode());f.readline()
  send({'execute':'qmp_capabilities'})
  events=[{'type':'abs','data':{'axis':'x','value':round(1877/1919*32767)}},{'type':'abs','data':{'axis':'y','value':round(35/1079*32767)}}]
  send({'execute':'input-send-event','arguments':{'events':events}})
  for down in [True,False]:send({'execute':'input-send-event','arguments':{'events':[{'type':'btn','data':{'button':'left','down':down}}]}});time.sleep(.1)
  v.close();time.sleep(.5)
 return oldrun(cmd,*args,**kwargs)
r.subprocess.run=run
sys.exit(r.main())
