from pathlib import Path
import os,signal,json,subprocess,time
p=Path('/tmp/sp1398');receipts=[]
for name,match in [('qt.pid',b'/tmp/sp1398/qt_fixture.py'),('receiver.pid',b'/tmp/sp1398/receiver.py')]:
 f=p/name
 if not f.exists():continue
 pid=int(f.read_text());cmd=Path('/proc/%d/cmdline'%pid)
 if cmd.exists() and match in cmd.read_bytes():os.kill(pid,signal.SIGTERM);receipts.append({'pid':pid,'file':name,'action':'TERM'})
e=json.loads((p/'env.json').read_text());r=subprocess.run(['putgd-cli','--socket',str(p/'runtime/putgd/session.sock'),'ui.quit'],env=e,text=True,capture_output=True);receipts.append({'quit':json.loads(r.stdout)})
time.sleep(3)
left=[]
for d in Path('/proc').iterdir():
 if not d.name.isdigit():continue
 try:
  if b'XDG_CONFIG_HOME=/tmp/sp1398/config' in (d/'environ').read_bytes().split(b'\0') and (d/'comm').read_text().startswith('putgd'):left.append(int(d.name))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
receipts.append({'remainingPrivateProductPids':left});(p/'cleanup.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipts))
