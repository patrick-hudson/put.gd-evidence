import sys,json,shlex,os,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs/of')
os.kill(2751642,15)
code="import json,subprocess;from pathlib import Path;p=Path('/tmp/v2/cases/long3/live.json');i=json.loads(p.read_text())['id'];subprocess.run(['python3','/home/lab/v2guest.py','rpc','scroll.stop',json.dumps({'id':i})])"
print(lab.guest_session(r,'python3 -c '+shlex.quote(code)),flush=True);time.sleep(3)
# This fixture belongs to the stopped custom script; exact argv identifies its PID.
code="""from pathlib import Path
import os
for d in Path('/proc').iterdir():
 if not d.name.isdecimal():continue
 try:
  a=(d/'cmdline').read_bytes().split(b'\\0')
  if len(a)>2 and a[1]==b'/home/lab/v2ruler.py':print(d.name,a[:4]);os.kill(int(d.name),15)
 except OSError:pass
"""
print(lab.guest_session(r,'python3 -c '+shlex.quote(code)),flush=True)
print(lab.guest_session(r,"gdbus call --session -d org.freedesktop.Notifications -o /org/freedesktop/Notifications -m org.freedesktop.Notifications.Notify put.gd 0 '' 'Harness reset' 'Closing old test notifications' '[]' '{}' 1000"),flush=True)
