#!/bin/bash
set -eu
cd /home/patrick/work/sa1113
run=$PWD/work/lab-runs/hn1
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-hn1-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-hn1.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/hn1
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/known_hosts')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22536 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/hn1/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-hn1-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sa1113'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-hn1-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-hn1-load.txt
free -b > vm-hn1-ram.txt
python3 tools/lab/lab.py launch --profile omarchy-hyprland --golden /home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity --known-hosts work/hostkeys/hn1/known_hosts --ssh-port 22536 --vnc-display 101 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 300 > vm-hn1-launch.json
cp vm-hn1-launch.json vm-hn1-layout-from-preflight.json
python3 tools/lab/lab.py install --run "$run" --appimage baseline/putgd-26.1113.4757-nightly-x86_64.AppImage > vm-hn1-install.json
python3 tools/lab/lab.py start --run "$run" > vm-hn1-start.json
for i in $(seq 1 180); do test ! -f wall-hn1.ready || break; sleep 1; done
test -f wall-hn1.ready
SWEEP_ROOT=$PWD python3 hyprland_baseline.py hn1 /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity hyprland > vm-hn1-checks.log 2>&1
