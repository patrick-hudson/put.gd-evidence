import os,json,subprocess,time
from pathlib import Path
import pass2 as p
P=p.P
try:p.rpc('ui.quit')
except Exception as ex:(P/'quit-error.txt').write_text(str(ex))
time.sleep(2);stopped=[]
for d in Path('/proc').iterdir():
 if not d.name.isdecimal():continue
 try:
  env=(d/'environ').read_bytes().split(b'\0');args=(d/'cmdline').read_bytes().split(b'\0');comm=(d/'comm').read_text().strip()
  own=b'XDG_CONFIG_HOME=/home/patrick/work/sa2/c' in env
  if own and int(d.name)!=os.getpid():os.kill(int(d.name),15);stopped.append({'pid':int(d.name),'comm':comm})
 except (OSError,ProcessLookupError):pass
f=P/'receiver.pid'
if f.exists():
 pid=int(f.read_text());d=Path('/proc')/str(pid)
 if d.exists():
  args=(d/'cmdline').read_bytes().split(b'\0');assert any(str(P/x).encode() in args for x in ['receiver.py','controlled_receiver.py']);os.kill(pid,15);stopped.append({'pid':pid,'comm':'owned loopback receiver'})
time.sleep(2);(P/'stopped-owned.json').write_text(json.dumps(stopped,indent=2));print(stopped)
