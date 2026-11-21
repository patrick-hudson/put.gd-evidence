cd ~/work/r1805
set -o noclobber
{ echo "engines worker GPU vs CPU since $(date -u +%FT%TZ)" > TIMING.lock; } 2>/dev/null || { echo "lock exists: $(cat TIMING.lock)"; exit 1; }
set +o noclobber
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
E=$PWD/engines; R=runs/d69; mkdir -p $R
snap() { echo "== $1 $(date +%T) $(uptime)"; ps -eo pid,pcpu,etime,comm --sort=-pcpu | sed -n 2,5p; }
run() { L=$1; shift; mkdir -p $R/$L; snap "before $L"; python3 -I $E/tools/bench2.py $M --label $L --out $R/$L --only monitor,editor-code -- "$@" > $R/$L/log 2>&1; snap "after $L"; }
export OMP_NUM_THREADS=4
run g-cpu $E/rapidocr/venv/bin/python -I $E/tools/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 4
run g-webgpu $E/ort-webgpu/venv/bin/python -I $E/tools/run_rapidocr.py {image} --det-type tiny --rec-type tiny --threads 4 --ep webgpu
rm -f TIMING.lock
echo GPU_DONE
