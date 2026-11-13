#!/bin/bash
set -eu
cd /home/patrick/work/sa1113
run=$PWD/work/lab-runs/b2
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-b2-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-b2.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/b2
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/fedora45-budgie/known_hosts')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22533 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/b2/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-b2-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sa1113'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-b2-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-b2-load.txt
free -b > vm-b2-ram.txt
python3 tools/lab/lab.py launch --profile fedora45-budgie --golden /home/patrick/work/put.gd/work/lab-images/fedora45-budgie/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity --known-hosts work/hostkeys/b2/known_hosts --ssh-port 22533 --vnc-display 95 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 300 > vm-b2-launch.json
cp vm-b2-launch.json vm-b2-layout-from-preflight.json
python3 tools/lab/lab.py install --run "$run" --appimage artifacts/appimage/putgd-26.1113.4899-dev+g036a9225e188-x86_64.AppImage > vm-b2-install.json
python3 tools/lab/lab.py start --run "$run" > vm-b2-start.json
for i in $(seq 1 180); do test ! -f wall-b2.ready || break; sleep 1; done
test -f wall-b2.ready
SWEEP_ROOT=$PWD python3 capture_f.py b2 /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity budgie > vm-b2-checks.log 2>&1
