#!/bin/sh
# runctl.sh PREFIX [probe SITE START BROWSER] : a private resident of the installed package, then either the fixture
# controls (earlier control directories are first moved into controls-before-PREFIX/), or one capture of SITE begun
# at START with screenshots of the screen taken all the while.
cd ~/work/sf7 || exit 1
export SF6_P=$PWD SF7=$PWD SF7_NOVERIFY=1
touch active
python3 rmowned.py c d s cache r archive > rmowned.log 2>&1
python3 -c "import pass2; pass2.setup()" > setup-$1.log 2>&1 || { echo "setup failed" > $1-all.done; rm -f active; exit 1; }
sleep 2
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
if [ "$2" = probe ]; then
  (python3 shots.py $1 ${6:-70} > shots-$1.log 2>&1 &)
  SF7_START=$4 python3 live7.py campaign $1 ${5:-firefox} $3 top > $1.console 2>&1
else
  mkdir controls-before-$1
  for d in ruler-end-0 ruler-end-1 qtfull-00 gtkfull-00 firefox-top-0 sticky-0 mid-viewport-0 editor-0; do [ -d $d ] && mv $d controls-before-$1/; done
  python3 controls7.py > $1-controls.console 2>&1
fi
kill $(cat resident.pid) 2>/dev/null
sleep 2
rm -f active
echo finished > $1-all.done
