import sys,os,time,json,subprocess,socket
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import record_run as r
root=Path.home()/'work/r9b'
oldbuild=r.Build.__init__
def build(self,label,path,run):
 oldbuild(self,label,path,root/'extract')
r.Build.__init__=build
oldstart=r.Driver.start_resident
def start(self,b):
 result=oldstart(self,b);time.sleep(11);return result
r.Driver.start_resident=start
oldcli=r.Driver.cli
def cli(self,b,m,p=None,timeout=60):
 result=oldcli(self,b,m,p,timeout)
 if m=='recording.start':oldcli(self,b,'recording.overlay',{'id':p['id'],'visible':False})
 return result
r.Driver.cli=cli
oldrecord=r.Driver.record
def record(self,b,n,f):
 free=subprocess.check_output(['df','-B1',str(root)],text=True)
 (self.run/'logs'/f'df-{b.label}-{f}.txt').write_text(free)
 return oldrecord(self,b,n,f)
r.Driver.record=record

