import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import record_run
old=record_run.Driver.start_resident
def start(self,build):
 caps=old(self,build)
 s=self.cli(build,'settings.get')
 self.cli(build,'settings.patch',{'patch':{'preferences':{'recordingClickHighlights':True}},'expectedRevision':s['metadata']['observedRevision']})
 return caps
record_run.Driver.start_resident=start
record_run.main()
