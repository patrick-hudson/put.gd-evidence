import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import record_run as rr
original=rr.Driver.start_resident
def start(self,b):
 caps=original(self,b)
 s=self.cli(b,'settings.get')
 self.cli(b,'settings.patch',{'patch':{'preferences':{'recordingClickHighlights':True}},'expectedRevision':s['metadata']['observedRevision']})
 (self.run/'remembered-setting.json').write_text(json.dumps(self.cli(b,'settings.get')['document']['preferences']))
 return caps
rr.Driver.start_resident=start
sys.exit(rr.main())
