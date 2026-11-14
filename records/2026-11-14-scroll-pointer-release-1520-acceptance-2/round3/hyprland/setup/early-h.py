from pathlib import Path
from trial import cli,flat,cursorpos
import subprocess,time,json
l=Path.home()/'work/s5302';a=l/'a';c=str(l/'bin/cli-a');subprocess.run(['firefox','--profile',str(l/'ff'),'https://en.wikipedia.org/wiki/Linux'],check=True);time.sleep(5)
s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];t0=time.monotonic();cli(c,'scroll.start',{'id':s});t1=time.monotonic();p0=time.monotonic();pause=cli(c,'scroll.pause',{'id':s});p1=time.monotonic();(a/'early-pause-timing.json').write_text(json.dumps({'id':s,'startCallMs':(t1-t0)*1000,'pauseSentAfterStartReplyMs':(p0-t1)*1000,'pauseSentAfterStartInvocationMs':(p0-t0)*1000,'pauseReply':pause},indent=2));assert (p0-t1)*1000<200
v=cli(c,'scroll.inspect',{'id':s});assert v['result'].get('paused') and v['result'].get('pausedBy')=='request',v;(a/'terminal-paused.json').write_text(json.dumps(v,indent=2));(a/'terminal-session-id').write_text(s);(a/'terminal-offset.txt').write_text(str((a/'helper.log').stat().st_size))
p=subprocess.Popen(['foot','-e','python3',str(l/'terminal-witness.py')],stdout=open(a/'terminal-launch.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(a/'terminal.pid').write_text(str(p.pid));time.sleep(2);print('paused and terminal open',s,p.pid,flush=True)
