#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
run=$PWD/work/lab-runs/p3
finish() {
 result=$?
 trap - EXIT
 python3 tools/lab/lab.py reset --run "$run" > vm-p3-reset.json 2>&1 || true
 printf '%s\n' "$result" > vm-p3.done
 exit "$result"
}
trap finish EXIT
mkdir -p work/lab-runs work/hostkeys/p3
python3 - <<'PY'
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-bootstrap-f44/known_hosts-kde')
lines=[]
for line in p.read_text().splitlines():
 parts=line.split()
 if len(parts)>=3 and not line.startswith('#'): lines.append('[127.0.0.1]:22607 '+parts[1]+' '+parts[2])
assert lines
Path('work/hostkeys/p3/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > vm-p3-sockets.json
python3 - <<'PY'
import json,sys
sys.path.insert(0,'tools/lab')
import storage_preflight as s
v=s.measure_filesystem('/home/patrick/work/sb1114'); assert v['statvfs']['f_bavail']*v['statvfs']['f_frsize']>20*1024**3
open('vm-p3-storage.json','w').write(json.dumps(v,indent=2))
PY
uptime > vm-p3-load.txt
free -b > vm-p3-ram.txt
python3 tools/lab/lab.py launch --profile kde-wayland --golden /home/patrick/work/put.gd/work/lab-images/transfer-459d0181e995/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity --known-hosts work/hostkeys/p3/known_hosts --ssh-port 22607 --vnc-display 123 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 600 > vm-p3-launch.json
python3 tools/lab/lab.py layout --run "$run" > vm-p3-layout.json
python3 tools/lab/lab.py install --run "$run" --deb $(python3 -c 'from pathlib import Path; print(next(Path("artifacts/ubuntu26.04").glob("*.deb")))') > vm-p3-install.json
python3 tools/lab/lab.py start --run "$run" > vm-p3-start.json
for i in $(seq 1 180); do test ! -f wall-p3.ready || break; sleep 1; done
test -f wall-p3.ready
SWEEP_ROOT=$PWD python3 guest_p_editor.py p3 /home/patrick/work/put.gd/work/lab-bootstrap-f44/identity kde > vm-p3-checks.log 2>&1
