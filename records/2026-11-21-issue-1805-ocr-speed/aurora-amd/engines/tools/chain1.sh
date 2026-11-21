cd ~/work/r1805
export OMP_NUM_THREADS=4
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
P=$PWD/engines/rapidocr/venv/bin/python
T=$PWD/engines/tools
R=runs/aurora-amd
run() { L=$1; shift; O=""; if [ "$1" = "--only" ]; then O="--only $2"; shift 2; fi; mkdir -p $R/$L; python3 -I $T/bench2.py $M --label $L --out $R/$L --reference $R/helper $O -- "$@" > $R/$L/log 2>&1; echo "$L done $(date +%T)"; }
run rapidocr-v6tiny-xy --only monitor $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny
run rapidocr-v6tiny-det1920 --only monitor $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --det-limit-type max --det-limit 1920
run rapidocr-v6tiny-det960 $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --det-limit-type max --det-limit 960
run hybrid-v6tinydet $P -I $T/run_hybrid.py {image} --lib /usr/lib64/libtesseract.so.5.5
run hybrid-v6tinydet960 $P -I $T/run_hybrid.py {image} --lib /usr/lib64/libtesseract.so.5.5 --det-limit-type max --det-limit 960
run rapidocr-v5mobile $P -I $T/run_rapidocr.py {image} --version PP-OCRv5 --det-type mobile --rec-type mobile --det-lang ch --rec-lang en
echo CHAIN_DONE
