#!/bin/bash
# change GECOS full name, run capture, always restore
OUT=$HOME/work/qr1618/state/out
getent passwd patrick > $OUT/gecos-original-line.txt
getent passwd patrick | cut -d: -f5 > $OUT/gecos-original.txt
echo "original GECOS: [$(cat $OUT/gecos-original.txt)]"
restore(){ sudo -n chfn -f "$(cat $OUT/gecos-original.txt)" patrick; echo "--- restored; getent passwd patrick:"; getent passwd patrick | tee $OUT/gecos-restored-line.txt; getent passwd patrick | cut -d: -f5 > $OUT/gecos-restored.txt; if cmp -s $OUT/gecos-original-line.txt $OUT/gecos-restored-line.txt; then echo "RESTORE-IDENTICAL"; else echo "RESTORE-DIFFERS"; fi; }
trap restore EXIT
sudo -n chfn -f "Patrick Hudson" patrick; echo "chfn rc=$?"
getent passwd patrick | tee $OUT/gecos-changed-line.txt
python3 - <<'P'
import sys;sys.path.insert(0,"/home/patrick/work/qr1618/bin")
from qrlib import *
rep,ins=capture_redact('r3b-fullname',['name'])
print(json.dumps({'counts':(rep['apply'] or {}).get('counts'),'ok':rep['ok']}))
for c in rep['covered']: print(c['rect'],c['words'])
P
