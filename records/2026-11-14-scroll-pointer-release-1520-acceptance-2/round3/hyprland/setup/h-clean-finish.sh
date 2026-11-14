set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export PATH=$PWD/bin:$PATH LANG=C.UTF-8
python3 - <<'PY'
from pathlib import Path
import os,signal
l=Path.home()/'work/s5302';assert (l/'b/r12-received.txt').read_text()=='abc\n';p=int((l/'b/r12-terminal.pid').read_text());cmd=Path(f'/proc/{p}/cmdline').read_bytes();assert b'foot' in cmd and b'terminal-witness.py' in cmd;os.kill(p,signal.SIGTERM)
PY
hyprctl reload >b/final-input-restored.log
sleep 1
python3 - <<'PY'
from pathlib import Path
import json,subprocess
l=Path.home()/'work/s5302';bad=[p.read_text().strip() for p in Path('/sys/class/input').glob('event*/device/name') if 'putgd-lab' in p.read_text() or 'scroll-1520' in p.read_text()];assert not bad
layers=json.loads(subprocess.check_output(['hyprctl','layers','-j'],text=True));clients=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True));assert 'putgd-record' not in json.dumps(layers);assert not clients
procs=[int(p.name) for p in Path('/proc').iterdir() if p.name.isdigit() and (p/'comm').exists() and (p/'comm').read_text().strip().startswith('putgd')];assert not procs,procs
v={'witness':'abc','testDevices':bad,'putgdPids':procs,'clients':clients,'layers':layers,'restoredInput':subprocess.check_output(['hyprctl','getoption','input:accel_profile'],text=True)};(l/'b/cleanup.json').write_text(json.dumps(v,indent=2));print('final nightly cleanup',v['restoredInput'])
PY
mv evidence.tgz evidence-first-export-retained.tgz
python3 collect.py
