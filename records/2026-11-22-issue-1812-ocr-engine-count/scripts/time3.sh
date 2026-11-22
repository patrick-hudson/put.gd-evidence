#!/bin/bash
cd ~/work/r1805; H=aurora-amd; M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
B=$HOME/work/i1812/src/build/dev; export QT_QPA_PLATFORM=offscreen; IDS=m74-monitor-light-125,m74-monitor-dark-125,gnome4k-monitor-light,gnome4k-monitor-dark
: > $HOME/work/i1812/dense3.txt
for cfg in e4:0-3 e6:0-5 e8:0-11; do e=${cfg%%:*}; C=${cfg#*:}; L=i1812-dev3-$e; O=runs/$H/$L
  { date -u +%FT%TZ; uptime; } > $O.load
  for i in 1 2 3; do taskset -c $C $B/test_ocr_run --helper $B/putgd-ocr --text synth/dense24.png | python3 -c "import json,sys;d=json.loads([l for l in sys.stdin if l.startswith(\"{\")][-1]);print(\"$L dense\",{k:d.get(k) for k in (\"totalMs\",\"peakRssKiB\",\"truncated\",\"error\")},len(d.get(\"text\",\"\")))" >> $HOME/work/i1812/dense3.txt; done
  taskset -c $C python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/helper -- $B/test_ocr_run --helper $B/putgd-ocr --text {image} > $O.log 2>&1
  taskset -c $C python3 -I tools/bench.py $M --label i1812-4k3-$e --out runs/$H/i1812-4k3-$e --ids $IDS --repeat 5 -- $B/test_ocr_run --helper $B/putgd-ocr --text {image} > runs/$H/i1812-4k3-$e.log 2>&1
  uptime >> $O.load
done
echo TIME3_DONE >> $HOME/work/i1812/dense3.txt
