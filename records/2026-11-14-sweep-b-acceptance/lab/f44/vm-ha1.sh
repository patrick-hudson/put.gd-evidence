#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
run=$PWD/work/lab-runs/ha1
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-ha1-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-ha1.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/ha1
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/known_hosts')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22605 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/ha1/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-ha1-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sb1114'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-ha1-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-ha1-load.txt
free -b > vm-ha1-ram.txt
python3 tools/lab/lab.py launch --profile omarchy-hyprland --golden /home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity --known-hosts work/hostkeys/ha1/known_hosts --ssh-port 22605 --vnc-display 119 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 600 > vm-ha1-launch.json
cp vm-ha1-launch.json vm-ha1-layout-from-preflight.json
python3 tools/lab/lab.py install --run "$run" --appimage /home/patrick/work/sa1113/artifacts/appimage/putgd-26.1113.4899-dev+g036a9225e188-x86_64.AppImage > vm-ha1-install.json
python3 tools/lab/lab.py start --run "$run" > vm-ha1-start.json
for i in $(seq 1 180); do test ! -f wall-ha1.ready || break; sleep 1; done
test -f wall-ha1.ready
SWEEP_EXPECTED_TREE=1148ea1108a4f28a749607cf4a8ee8cbbdd90fc7 SWEEP_ROOT=$PWD python3 guest_h_baseline.py ha1 /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity hyprland > vm-ha1-checks.log 2>&1
