from pathlib import Path
from argparse import Namespace
import sys,json,socket
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');P=Path('/home/patrick/work/s3a');gold=Path('/home/patrick/work/put.gd/work/lab-images/neon-user-6.8.1-20261023-9ef808278853');run=Path('/home/patrick/work/put.gd/work/lab-runs/s3n')
for port in [22489,5989]:
 s=socket.socket();s.bind(('127.0.0.1',port));s.close()
assert not run.exists()
pin=P/'neon-known_hosts';line=(gold/'known_hosts').read_text().splitlines()[0].split();pin.write_text('[127.0.0.1]:22489 '+' '.join(line[1:])+'\n');pin.chmod(0o600)
r=lab.launch(Namespace(profile='neon-kde-wayland',golden=str(gold/'image.qcow2'),run=str(run),bootstrap_key='/home/patrick/work/put.gd/work/lab-bootstrap-d69/neon-user/identity',known_hosts=str(pin),ssh_port=22489,vnc_display=89,acceleration='kvm',timeout=180,heads=1,layout='1920x1080+0+0'))
(P/'neon-launch.json').write_text(json.dumps(r,indent=2));print(r,flush=True)
