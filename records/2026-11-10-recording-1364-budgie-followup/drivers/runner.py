import sys,json,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(root/'lab'))
import record_run
class SharedBuild:
 def __init__(self,label,path,run):
  self.label=label;self.path=pathlib.Path(path).resolve();self.launcher=[str(self.path),'--background'];self.cli=str(root/'an/squashfs-root/usr/bin/putgd-cli');self.identity={'kind':'appimage','file':self.path.name,'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()}
def shared_open(self):
 assert self.args.mic=='off' and self.args.system=='tone'
 s=json.loads((root/'shared-audio.json').read_text());self.args.audio_device=s['systemSink'];return s
record_run.Build=SharedBuild
record_run.Driver.open_microphone=shared_open
record_run.Driver.close_microphone=lambda self:{'sharedSinkStillActive':True,'teardown':'batch finally'}
sys.exit(record_run.main())
