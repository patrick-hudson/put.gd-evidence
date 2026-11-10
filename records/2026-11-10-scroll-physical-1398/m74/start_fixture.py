import json,subprocess,os,time
from pathlib import Path
p=Path('/tmp/sp1398');e=json.loads((p/'env.json').read_text());pidfile=p/'qt.pid'
if pidfile.exists():
 pid=int(pidfile.read_text())
 try:
  if b'/tmp/sp1398/qt_fixture.py' in Path('/proc/%d/cmdline'%pid).read_bytes():os.kill(pid,15)
 except FileNotFoundError:pass
 time.sleep(.5)
q=subprocess.Popen(['python3',str(p/'qt_fixture.py')],env=e,stdout=open(p/'mcp-fixture.log','w'),stderr=subprocess.STDOUT,start_new_session=True);pidfile.write_text(str(q.pid))
