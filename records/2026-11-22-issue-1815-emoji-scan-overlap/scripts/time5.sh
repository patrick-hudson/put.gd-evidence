#!/bin/bash
cd ~/work/r1805; H=aurora-amd; M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
B=$HOME/work/i1812/src/build/dev; export QT_QPA_PLATFORM=offscreen
cd ~/work/i1812/src && touch src/ocr/Recognize.cpp && toolbox run -c putgd-build cmake --build build/dev -j 4 --target bench_ocr_method putgd-ocr test_ocr_run -- -l10 > $HOME/work/i1812/build5.log 2>&1; cd ~/work/r1805
L=i1815-dev-e8; O=runs/$H/$L; { date -u +%FT%TZ; uptime; } > $O.load
python3 -I tools/bench.py $M --label $L --out $O --reference runs/$H/i1812-dev4-e8 -- $B/test_ocr_run --helper $B/putgd-ocr --text {image} > $O.log 2>&1
uptime >> $O.load; echo TIME5_DONE >> $O.log
