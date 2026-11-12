from pathlib import Path
import sys,shlex,json,os,subprocess,time
R=Path('/home/patrick/work/sc2');sys.path.insert(0,str(R/'tools/lab'));import lab
run=R/'work/lab-runs/ck';out=R/'evidence/k';bad=out/'failed-cp2';bad.mkdir(exist_ok=True)
for name in ['rpc.jsonl','version.json','capabilities.json','socket-preflight.json','resident.log']:
 try:lab.get(run,'/tmp/cp2/'+name,bad/name)
 except Exception:pass
lab.get(run,'/tmp/cap-proof.log',bad/'guest-error.log')
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  a=(p/'cmdline').read_bytes().split(bytes([0]))
  if str(R/'drivers/cap-proof-host.py').encode() in a and b'k' in a:os.kill(int(p.name),15)
 except OSError:pass
code="""from pathlib import Path
import os,time
killed=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  a=(p/'cmdline').read_bytes().split(bytes([0]));e=(p/'environ').read_bytes().split(bytes([0]))
  if b'XDG_CONFIG_HOME=/tmp/cp2/c' in e or b'/home/lab/cap-receiver.py' in a:os.kill(int(p.name),15);killed.append(int(p.name))
 except OSError:pass
print(killed);time.sleep(2)
"""
(bad/'owned-cleanup.log').write_text(lab.guest_session(run,'python3 -c '+shlex.quote(code),timeout=60))
f=R/'drivers/cap-proof-guest.py';s=f.read_text().replace('/tmp/cp2','/tmp/cp3').replace('/home/lab/cap-receiver.py','/home/lab/cap-receiver3.py');s=s.replace("e=dict(os.environ);real", "apps=Path.home()/'.local/share/applications';apps.mkdir(parents=True,exist_ok=True);(P/'d/applications').symlink_to(apps,target_is_directory=True)\ne=dict(os.environ);real");temp=R/'drivers/cap-proof-guest3.py';temp.write_text(s);lab.put(run,temp,'/home/lab/cap-proof-guest3.py');temp=R/'drivers/cap-receiver3.py';temp.write_text((R/'drivers/cap-receiver.py').read_text().replace('/tmp/cp2','/tmp/cp3'));lab.put(run,temp,'/home/lab/cap-receiver3.py')
source=(R/'drivers/cap-proof-host.py').read_text();body=source[source.index("print(lab.guest_session"):];body=body.replace('/home/lab/cap-proof-guest.py','/home/lab/cap-proof-guest3.py').replace('/tmp/cp2/','/tmp/cp3/');header="from pathlib import Path\nimport sys,subprocess,json,time,shlex,hashlib,tarfile\nfrom PIL import Image\nR=Path('/home/patrick/work/sc2');sys.path.insert(0,str(R/'tools/lab'));sys.path.insert(0,str(R/'drivers'));import lab,scroll_run,argparse\nk='k';run=R/'work/lab-runs/ck';out=R/'evidence/k'\n";script=R/'drivers/k-retry-capture.py';script.write_text(header+body);subprocess.run(['python3',str(script)],check=True)
