#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
run=$PWD/work/lab-runs/p2
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-p2-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-p2.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/p2
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-bootstrap-f44/known_hosts-kde')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22603 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/p2/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-p2-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sb1114'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-p2-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-p2-load.txt
free -b > vm-p2-ram.txt
python3 tools/lab/lab.py launch --profile kde-wayland --golden /home/patrick/work/put.gd/work/lab-images/transfer-459d0181e995/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity --known-hosts work/hostkeys/p2/known_hosts --ssh-port 22603 --vnc-display 115 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 300 > vm-p2-launch.json
python3 tools/lab/lab.py layout --run "$run" > vm-p2-layout.json
python3 tools/lab/lab.py install --run "$run" --deb $(python3 -c 'from pathlib import Path; print(next(Path("artifacts/ubuntu26.04").glob("*.deb")))') > vm-p2-install.json
python3 tools/lab/lab.py start --run "$run" > vm-p2-start.json
for i in $(seq 1 180); do test ! -f wall-p2.ready || break; sleep 1; done
test -f wall-p2.ready
SWEEP_ROOT=$PWD python3 guest_b.py p2 /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity kde > vm-p2-checks.log 2>&1
