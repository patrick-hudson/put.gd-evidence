import pathlib,sys,json,hashlib,time
root=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(root/'lab'));import record_run_visible as record_run
class SharedBuild:
 def __init__(self,label,path,run):
  self.label=label;self.path=pathlib.Path(path).resolve();self.launcher=[str(self.path),'--background'];self.cli=str(root/'an/squashfs-root/usr/bin/putgd-cli');self.identity={'kind':'appimage','file':self.path.name,'sha256':hashlib.sha256(self.path.read_bytes()).hexdigest()}
def shared_open(self):
 s=json.loads((root/'audio.json').read_text());self.args.audio_device=s['systemSink'];return s
original_cli=record_run.Driver.cli
def cli(self,build,method,params=None,timeout=60):
 assert method!='recording.overlay','No overlay call is permitted in the visible-bar cell'
 with (self.run/'method-audit.jsonl').open('a')as f:f.write(json.dumps({'method':method,'monotonic':time.monotonic()})+'\n')
 return original_cli(self,build,method,params,timeout)
record_run.Build=SharedBuild;record_run.Driver.cli=cli;record_run.Driver.open_microphone=shared_open;record_run.Driver.close_microphone=lambda self:{'sharedSinkStillActive':True,'teardown':'batch finally'}
sys.exit(record_run.main())
