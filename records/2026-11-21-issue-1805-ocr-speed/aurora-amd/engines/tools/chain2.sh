cd ~/work/r1805
while pgrep -f -x "bash engines/tools/chain1.sh" > /dev/null; do sleep 10; done
M=corpus/records/2026-11-13-issue-1428-corpus-index/manifest.json
P=$PWD/engines/rapidocr/venv/bin/python; T=$PWD/engines/tools; R=runs/aurora-amd
L=hybrid-v6tiny-tight; mkdir -p $R/$L
taskset -c 4,5,10,11 python3 -I $T/bench2.py $M --label $L --out $R/$L --reference $R/helper -- $P -I $T/run_hybrid.py {image} --lib /usr/lib64/libtesseract.so.5.5 --threads 2 --tess-threads 2 --unclip 1.3 --shrink 0.1 > $R/$L/log 2>&1
echo "$L done $(date +%T)"
