import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import record_run
orig_cli=record_run.Driver.cli
def cli(self,build,method,params=None,timeout=60):
 if method=='recording.start':orig_cli(self,build,'recording.overlay',{'id':params['id'],'visible':False})
 r=orig_cli(self,build,method,params,timeout)
 return r
record_run.Driver.cli=cli
if '--rewrite' in sys.argv:
 sys.argv.remove('--rewrite')
 exec(compile((Path(__file__).parent/'rewrite_run.py').read_text(),str(Path(__file__).parent/'rewrite_run.py'),'exec'))
else:record_run.main()
