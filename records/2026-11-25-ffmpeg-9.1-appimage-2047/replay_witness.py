import json,subprocess as sp,sys,time
from pathlib import Path
from types import SimpleNamespace
from accept import rr,wall_frame
import desktop_lock

desktop_lock.refuse_unless_held('repeat playback wall witness')
source=Path(sys.argv[1]).resolve(); run=source/'replay-witness'; run.mkdir(mode=0o700); (run/'frames').mkdir()
d=SimpleNamespace(run=run,args=SimpleNamespace(vnc_port=int(sys.argv[2])),env=rr.session_environment()[0])
d.env['SDL_AUDIODRIVER']='dummy'
path=source/'out/webm.webm'
proc=sp.Popen(['ffplay','-fs','-autoexit','-loglevel','error','-window_title','FFmpeg 9.1 acceptance: WebM',str(path)],env=d.env,stdout=sp.DEVNULL,stderr=sp.PIPE,text=True)
report={'player':'ffplay','file':path.name,'wallFrames':[]}
try:
    time.sleep(2)
    for i,t in enumerate([.75,1.3,.93,1.45,1.2]):
        if proc.poll() is not None: break
        try: report['wallFrames'].append(wall_frame(d,f'player-webm-repeat-{i}'))
        except Exception as e: report['wallFrames'].append({'error':str(e)})
        time.sleep(t)
    _,err=proc.communicate(timeout=20)
except sp.TimeoutExpired:
    proc.terminate(); _,err=proc.communicate(timeout=5)
finally:
    if proc.poll() is None: proc.terminate(); proc.wait(5)
report['exit']=proc.returncode; report['stderr']=err; report['distinctHashes']=len({f['sha256'] for f in report['wallFrames'] if f.get('ok')})
(run/'receipt.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); sys.exit(not (report['exit']==0 and report['distinctHashes']>=2))
