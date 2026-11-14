set -eu
cd "$HOME/work/s5202"
. ./session.env
python3 - <<'PY'
from pathlib import Path
import json
l=Path.home()/'work/s5202/a'
for mode in ['fixed','random','steer']:
 v=[json.loads(x) for x in (l/('tries-'+mode+'.jsonl')).read_text().splitlines()];assert len(v)==10
 print(mode,sum(x['stoppedByClick'] for x in v))
PY
python3 other-window.py >a/terminal-check.log 2>&1
