#!/bin/bash
cd ~/work/r1805; H=$(cat host); M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
L=${LABEL:-i1812-helper}; O=runs/$H/$L
{ date -u +%FT%TZ; uptime; } > $O.load
QT_QPA_PLATFORM=offscreen python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/i1808-after2 -- $HOME/work/i1812/src/build/dev/test_ocr_run --helper $HOME/work/i1812/src/build/dev/putgd-ocr --text {image} > $O.log 2>&1
uptime >> $O.load; echo CHECK_DONE >> $O.log
