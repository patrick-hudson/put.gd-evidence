#!/bin/bash
# accaur.sh : aurora, before (#1809 AppImage 609c8a6) and after (#1812 AppImage 54e1aed), alternating twice; corpus, dense x3, 4K x5 each.
W=$HOME/work/i1812; cd ~/work/r1805; H=aurora-amd; M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
IDS=m74-monitor-light-125,m74-monitor-dark-125,gnome4k-monitor-light,gnome4k-monitor-dark
one(){ L=$1; ROOT=$W/pkg/$2/squashfs-root; REF=$3
  bash $W/harness/acc.sh $L $ROOT "usr/lib:$ROOT/usr/lib/putgd" $REF
  # 4K captures x5 through the same packaged resident
  R=$W/res-$L; CLI=$W/cli-$L.sh
  LD_LIBRARY_PATH=$ROOT/usr/lib:$ROOT/usr/lib/putgd python3 -I $W/harness/fileocr.py start $R $CLI $ROOT/usr/bin/putgd --background >> runs/$H/$L.start 2>&1
  python3 -I tools/bench.py $M --label $L-4k --out runs/$H/$L-4k --ids $IDS --repeat 5 -- python3 -I $W/harness/fileocr.py recognize $R $CLI {image} > runs/$H/$L-4k.log 2>&1
  python3 -I $W/harness/fileocr.py stop $R $CLI >> runs/$H/$L.start 2>&1; sleep 3; }
one pkga-before-1 before
one pkga-after-1 after pkga-before-1
one pkga-before-2 before pkga-before-1
one pkga-after-2 after pkga-before-1
echo ACCAUR_DONE >> $W/dense-pkg.txt
