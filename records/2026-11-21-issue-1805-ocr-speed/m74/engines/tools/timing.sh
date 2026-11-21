# timing.sh HOST : CPU head-to-head under TIMING.lock (#1805 engines worker)
cd ~/work/r1805
H=$1
L=~/work/r1805/TIMING.lock
[ -e $L ] && { echo "lock exists: $(cat $L)"; exit 1; }
echo "engines worker (OCR candidates) since $(date -u +%FT%TZ)" > $L
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
P=$PWD/engines/rapidocr/venv/bin/python; T=$PWD/engines/tools; R=runs/$H
mkdir -p $R
snap() { echo "== $1 $(date +%T) $(uptime)"; ps -eo pid,pcpu,etime,comm --sort=-pcpu | sed -n 2,5p; }
run() { Lb=$1; shift; O=""; if [ "$1" = "--only" ]; then O="--only $2"; shift 2; fi; mkdir -p $R/$Lb; snap "before $Lb"; python3 -I $T/bench2.py $M --label $Lb --out $R/$Lb --reference $R/w-helper $O -- "$@" > $R/$Lb/log 2>&1; snap "after $Lb"; }
snap start
mkdir -p $R/w-helper; snap "before w-helper"
OMP_THREAD_LIMIT=1 python3 -I $T/bench2.py $M --label w-helper --out $R/w-helper -- $PWD/src/build/dev/test_ocr_run --helper $PWD/src/build/dev/putgd-ocr --text {image} > $R/w-helper/log 2>&1
snap "after w-helper"
export OMP_NUM_THREADS=4
run w-v6tiny $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 4
run w-v6tiny-det960 $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 4 --det-limit-type max --det-limit 960
OMP_NUM_THREADS=1 run w-v6tiny-1t --only monitor,terminal $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 1
run w-v6tiny-detonly --only monitor,terminal,editor-code $P -I $T/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 4 --det-only
rm -f $L
echo TIMING_DONE
