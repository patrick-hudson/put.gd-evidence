#!/bin/sh
# runall.sh PREFIX BROWSERS : a private resident of the installed package, the live-site campaign, the controls.
cd ~/work/sf7 || exit 1
export SF6_P=$PWD SF7=$PWD SF7_NOVERIFY=1
touch active
python3 rmowned.py c d s cache r archive > rmowned.log 2>&1
python3 -c "import pass2; pass2.setup()" > setup-$1.log 2>&1 || { echo "setup failed" > $1-campaign.done; rm -f active; exit 1; }
sleep 2
# The private resident's own window process, by its pid.
python3 - <<'PY'
import os
from pathlib import Path
P = Path.home() / 'work/sf7'
for proc in Path('/proc').iterdir():
    if proc.name.isdigit():
        try:
            if (proc / 'comm').read_text().strip() == 'putgd-ui' and ('XDG_CONFIG_HOME=' + str(P / 'c')).encode() in (proc / 'environ').read_bytes().split(b'\0'):
                os.kill(int(proc.name), 15)
        except OSError:
            pass
PY
sleep 1
python3 live7.py campaign $1 $2 ${3:-pr,wiki,py,mdn,repo} ${4:-half,top} > $1.console 2>&1
if [ "${5:-controls}" = controls ]; then python3 controls7.py > $1-controls.console 2>&1; fi
kill $(cat resident.pid) 2>/dev/null
sleep 2
rm -f active
echo finished > $1-all.done
