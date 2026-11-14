#!/bin/bash
# vm-w3.sh RUN APPIMAGE: launch a fresh two-head Omarchy overlay on f44, install the AppImage.
# Leaves the guest running (the caller drives and retires it). Writes RUN.done with the exit code.
set -eu
cd "$HOME/work/w3-1487"
name=$1; appimage=$2
run=$PWD/work/lab-runs/$name
finish() { result=$?; trap - EXIT; printf '%s\n' "$result" > "$name.done"; exit "$result"; }
trap finish EXIT
rm -f "$name.done"
mkdir -p work/lab-runs "work/hostkeys/$name"
python3 - "$name" <<'PY'
import sys
from pathlib import Path
p=Path('/home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/known_hosts')
lines=['[127.0.0.1]:22592 '+l.split()[1]+' '+l.split()[2] for l in p.read_text().splitlines() if len(l.split())>=3 and not l.startswith('#')]
assert lines
Path('work/hostkeys/'+sys.argv[1]+'/known_hosts').write_text('\n'.join(lines)+'\n')
PY
python3 tools/diagnostics/check_socket_paths.py --socket "$run/qmp.sock" "$run/vnc.sock" /run/user/1000/putgd/session.sock > "$name-sockets.json"
uptime > "$name-load.txt"; free -b > "$name-ram.txt"
python3 tools/lab/lab.py launch --profile omarchy-hyprland --golden /home/patrick/work/put.gd/work/lab-images/omarchy-hyprland-20261108/image.qcow2 --run "$run" --bootstrap-key /home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity --known-hosts "work/hostkeys/$name/known_hosts" --ssh-port 22592 --vnc-display 92 --heads 2 --layout 1280x800+0+0,1024x768+1280+0 --timeout 300 > "$name-launch.json"
python3 tools/lab/lab.py install --run "$run" --appimage "$appimage" > "$name-install.json"
