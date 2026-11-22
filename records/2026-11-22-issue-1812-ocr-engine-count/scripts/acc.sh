#!/bin/bash
# acc.sh LABEL ROOT LIBDIR [REFLABEL] : the corpus (and the dense page x3) through a packaged resident's own helper.
# ROOT: an extracted package or AppImage squashfs-root; LIBDIR: its private library dir (relative to ROOT).
cd ~/work/r1805; H=$(cat host); L=$1; ROOT=$2; LIB=$3; REF=${4:-}
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
W=$HOME/work/i1812; R=$W/res-$L; O=runs/$H/$L; CLI=$W/cli-$L.sh
printf '#!/bin/sh\nLD_LIBRARY_PATH=%s/%s exec %s/usr/bin/putgd-cli "$@"\n' $ROOT $LIB $ROOT > $CLI; chmod +x $CLI
mkdir -p $R
LD_LIBRARY_PATH=$ROOT/$LIB python3 -I $W/harness/fileocr.py start $R $CLI $ROOT/usr/bin/putgd --background > $O.start 2>&1
RP=$(cat $R/resident.pid); echo "resident $RP $(readlink /proc/$RP/exe)" >> $O.start
{ date -u +%FT%TZ; uptime; } > $O.load
python3 -I tools/bench.py $M --label $L --out $O ${REF:+--reference runs/$H/$REF} -- python3 -I $W/harness/fileocr.py recognize $R $CLI {image} > $O.log 2>&1
for i in 1 2 3; do python3 -I $W/harness/fileocr.py recognize $R $CLI $W/dense24.png | python3 -c "import json,sys;d=json.loads(sys.stdin.read());t=d.pop('text','');d['chars']=len(t);print('$L dense',json.dumps(d))" >> $W/dense-pkg.txt; done
uptime >> $O.load
python3 -I $W/harness/fileocr.py stop $R $CLI >> $O.start 2>&1
echo ACC_DONE >> $O.log
