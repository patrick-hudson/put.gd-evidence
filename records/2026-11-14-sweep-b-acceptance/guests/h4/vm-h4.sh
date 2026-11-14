#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
run=$PWD/work/lab-runs/h4
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-h4-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-h4.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/h4
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/known_hosts')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22602 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/h4/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-h4-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sb1114'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-h4-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-h4-load.txt
free -b > vm-h4-ram.txt
python3 tools/lab/lab.py launch --profile omarchy-hyprland --golden /home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity --known-hosts work/hostkeys/h4/known_hosts --ssh-port 22602 --vnc-display 113 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 600 > vm-h4-launch.json
cp vm-h4-launch.json vm-h4-layout-from-preflight.json
python3 tools/lab/lab.py install --run "$run" --appimage $(python3 -c 'from pathlib import Path; print(next(Path("artifacts/appimage").glob("*.AppImage")))') > vm-h4-install.json
python3 tools/lab/lab.py start --run "$run" > vm-h4-start.json
for i in $(seq 1 180); do test ! -f wall-h4.ready || break; sleep 1; done
test -f wall-h4.ready
SWEEP_ROOT=$PWD python3 guest_b.py h4 /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity hyprland > vm-h4-checks.log 2>&1
