import os,sys,json,time,subprocess,signal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import record_run as rr
mode=sys.argv.pop(1)
def effect(method,*args):
 p=subprocess.run(['gdbus','call','--session','--dest','org.kde.KWin','--object-path','/Effects','--method','org.kde.kwin.Effects.'+method,*args],capture_output=True,text=True,check=True)
 return p.stdout.strip()
def state():return {'loaded':effect('isEffectLoaded','mouseclick'),'support':effect('supportInformation','mouseclick')}
original=rr.Driver.cli
def cli(self,b,m,p=None,timeout=60):
 result=original(self,b,m,p,timeout)
 if m in ('recording.start','recording.stop','recording.cancel'):
  with (self.run/'effect-events.jsonl').open('a') as f:f.write(json.dumps({'method':m,'state':state()})+'\n')
 return result
rr.Driver.cli=cli
if mode!='stop':
 def record(self,build,number,fmt):
  result={'mode':mode,'before':state()}; rid=None
  try:
   self.start_resident(build)
   req={'target':{'kind':'monitor'},'format':'mp4','fps':30,'audio':{'system':True,'microphone':False},'clickHighlights':True}
   prepared=self.cli(build,'recording.prepare',req);rid=prepared['recordingId']
   self.wait_state(build,rid,('ready',),120);self.cli(build,'recording.start',{'id':rid});time.sleep(6)
   result['during']=state();self.desktop_frame(self.run/'frames/during.png')
   if mode=='kill':
    pids=[]
    for p in Path('/proc').iterdir():
     if p.name.isdecimal():
      try:
       if (p/'comm').read_text().strip()=='putgd-record' and p.stat().st_uid==os.getuid():pids.append(int(p.name))
      except OSError:pass
    if len(pids)!=1:raise RuntimeError('expected one exact helper PID, got '+repr(pids))
    result['killedPid']=pids[0];(self.run/'kill-action.json').write_text(json.dumps(result));os.kill(pids[0],signal.SIGKILL);time.sleep(4)
    try:result['inspect']=self.cli(build,'recording.inspect',{'id':rid})
    except rr.RunError as e:result['inspectError']=str(e)
   else:self.cli(build,'recording.cancel',{'id':rid});rid=None;time.sleep(1)
   result['after']=state();self.desktop_frame(self.run/'frames/after.png')
   return result
  finally:
   if rid:
    try:self.cli(build,'recording.cancel',{'id':rid})
    except Exception:pass
   self.stop_resident(build)
 rr.Driver.record=record
sys.exit(rr.main(sys.argv[1:]))
