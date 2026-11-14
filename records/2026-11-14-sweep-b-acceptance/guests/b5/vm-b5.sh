#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
run=$PWD/work/lab-runs/b5
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-b5-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-b5.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/b5
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/fedora45-budgie/known_hosts')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22601 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/b5/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-b5-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sb1114'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-b5-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-b5-load.txt
free -b > vm-b5-ram.txt
python3 tools/lab/lab.py launch --profile fedora45-budgie --golden /home/patrick/work/put.gd/work/lab-images/fedora45-budgie/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity --known-hosts work/hostkeys/b5/known_hosts --ssh-port 22601 --vnc-display 111 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 600 > vm-b5-launch.json
cp vm-b5-launch.json vm-b5-layout-from-preflight.json
python3 tools/lab/lab.py install --run "$run" --appimage $(python3 -c 'from pathlib import Path; print(next(Path("artifacts/appimage").glob("*.AppImage")))') > vm-b5-install.json
python3 tools/lab/lab.py start --run "$run" > vm-b5-start.json
for i in $(seq 1 180); do test ! -f wall-b5.ready || break; sleep 1; done
test -f wall-b5.ready
SWEEP_ROOT=$PWD python3 guest_b_lock.py b5 /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity budgie > vm-b5-checks.log 2>&1
