set -eu
systemd-run --user --unit=putgd-vm-1364-b1364v --collect --property=Type=exec --property=Restart=on-failure --property=RestartSec=3s /usr/bin/ssh -NT -i /home/patrick/.ssh/awskey_110724 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -L 127.0.0.1:5996:127.0.0.1:5946 patrick@192.168.68.69
python3 - <<'PY'
from pathlib import Path
import json,fcntl
p=Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json')
with open('/tmp/putgd-wall-config.lock','w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 entries=json.loads(p.read_text()); assert not any(x['port']==5996 for x in entries)
 entries.append({'name':'Budgie recording1364 b1364v','port':5996,'type':'vm','hostIp':'192.168.68.69'})
 tmp=p.with_suffix('.b1364.tmp');tmp.write_text(json.dumps(entries,indent=1)+'\n');tmp.replace(p)
PY
python3 /tmp/b1364/control.py h 'python3 /home/patrick/work/b1364/host_lab.py launch --profile fedora45-budgie --golden /home/patrick/work/put.gd/work/lab-images/fedora45-budgie/image.qcow2 --run /home/patrick/work/put.gd/work/lab-runs/b1364v --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-d69/identity --known-hosts /home/patrick/work/b1364/known_hosts --ssh-port 22446 --vnc-display 46 --timeout 300'
