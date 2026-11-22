#!/bin/bash
# time.sh : dev helper at 4/6/8 engines (taskset 0-3, 0-5, all 12), dense page x3 + corpus, sequential
cd ~/work/r1805; H=$(cat host); M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
B=$HOME/work/i1812/src/build/dev; export QT_QPA_PLATFORM=offscreen
for cfg in e4:0-3 e6:0-5 e8:0-11; do L=i1812-dev-${cfg%%:*}; C=${cfg#*:}; O=runs/$H/$L
  { date -u +%FT%TZ; uptime; } > $O.load
  for i in 1 2 3; do taskset -c $C $B/test_ocr_run --helper $B/putgd-ocr --text synth/dense24.png | python3 -c "import json,sys;d=json.loads([l for l in sys.stdin if l.startswith(\"{\")][-1]);print(\"$L dense\",{k:d.get(k) for k in (\"totalMs\",\"recognizeMs\",\"peakRssKiB\",\"truncated\",\"error\")},len(d.get(\"text\",\"\")))" >> $HOME/work/i1812/dense.txt; done
  taskset -c $C python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/helper -- $B/test_ocr_run --helper $B/putgd-ocr --text {image} > $O.log 2>&1
  uptime >> $O.load
done
for e in 4 6 8; do $B/bench_ocr_method --budget 16000 --memory 320 --threads $e synth/dense24.png | python3 -c "import json,sys;d=json.loads(sys.stdin.read());print(\"bench threads $e\",d.get(\"threads\"),d.get(\"engineTasks\"),d.get(\"peakKiB\"),d.get(\"totalMs\"))" >> $HOME/work/i1812/dense.txt; done
echo TIME_DONE >> $HOME/work/i1812/dense.txt
