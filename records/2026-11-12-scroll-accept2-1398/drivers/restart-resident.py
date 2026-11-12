import os,json,subprocess,time
from pathlib import Path
import record_run
P=Path('/home/patrick/work/sa2');e,_=record_run.session_environment()
for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','r')]:e['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
e.update(PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native',PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'),SC_Y='200');assert len(str(P/'r/putgd/session.sock').encode())<=107
(P/'env.json').write_text(json.dumps(e));os.chmod(P/'env.json',0o600);q=subprocess.Popen(['putgd','--background'],env=e,stdout=open(P/'restarted-resident.log','a'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid));time.sleep(4)
