#!/bin/bash
# acc.sh : #1808 acceptance on this builder: packaged helper (after) and today's helper (before), full corpus.
cd ~/work/r1805
H=$(cat host); export OMP_THREAD_LIMIT=1
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
HELPER=${HELPER:-/usr/bin/putgd-ocr}
run(){ L=$1; P=$2; O=runs/$H/$L; [ -f $O/summary.json ] && return
  { date -u +%FT%TZ; uptime; } > $O.load
  python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/helper -- src/build/dev/test_ocr_run --helper $P --text {image} > $O.log 2>&1
  uptime >> $O.load; }
run i1808-after "$HELPER"
run i1808-before "$PWD/src/build/dev/putgd-ocr"
run i1808-after2 "$HELPER"
echo ACC_DONE > runs/$H/i1808.done
