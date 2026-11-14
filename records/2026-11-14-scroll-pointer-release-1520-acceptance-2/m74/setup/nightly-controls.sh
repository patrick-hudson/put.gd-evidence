set -eu
cd "$HOME/work/s5202"
. ./session.env
bin/cli-a ui.quit >a/quit-before-nightly.json
sleep 1
sudo -n apt-get --no-install-recommends --allow-downgrades install -y "$HOME/work/s5202/before.deb" >install-nightly-control.log 2>&1
for file in diagnostics.json build.json resident.log browser-ready.png helper.log; do cp "b/$file" "b/s1-$file"; done
sh start.sh b
python3 - <<'PY'
from pathlib import Path
import json
l=Path.home()/'work/s5202';v=json.loads((l/'b/build.json').read_text());assert v['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3';print(v)
PY
STOP=780,978 sh s2.sh b
python3 esc-check.py b >b/escape-driver.log 2>&1
