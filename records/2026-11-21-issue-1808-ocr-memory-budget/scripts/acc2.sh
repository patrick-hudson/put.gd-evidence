#!/bin/bash
# acc2.sh CLI : the corpus through the packaged resident's own helper (fileocr.py), twice.
cd ~/work/r1805; H=$(cat host); CLI=$1
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
R=$HOME/work/i1808/res-after
for L in i1808-pkg i1808-pkg2; do O=runs/$H/$L; [ -f $O/summary.json ] && continue
  { date -u +%FT%TZ; uptime; } > $O.load
  python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/helper -- python3 -I $HOME/work/i1808/fileocr.py recognize $R $CLI {image} > $O.log 2>&1
  uptime >> $O.load; done
echo ACC2_DONE > runs/$H/i1808-pkg.done
