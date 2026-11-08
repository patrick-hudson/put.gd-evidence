#!/bin/bash
# d69: selector press sweep with the pointer already at the start point. selsweep.sh RUN OUTPUTS W H LOG DELAYS...
cd ~/work/d1275; R=$1; N=$2; W=$3; H=$4; L=$5; shift 5
PREPOS=${PREPOS:-1} timeout 540 python3 selbench.py $R $N $W $H ${COORDS:-300 200 700 500} ${TRIALS:-6} "$@" 2>&1 | grep -v '"kind": "map"' | cut -c1-400 > $L
python3 - "$L" <<'PY'
import json,statistics,sys
rows=[json.loads(l) for l in open(sys.argv[1]) if l.startswith("{")]
ds=[r for r in rows if r.get("kind")=="drag"]
for r in rows:
    if r.get("kind")=="map-summary": print("map", r)
med=lambda v:("%.3f"%statistics.median(v)) if v else "n/a"
for d in sorted({r["delay"] for r in ds}):
    x=[r for r in ds if r["delay"]==d]; px=[r["pixels"]["diffPx"] for r in x if r.get("pixels")]
    print("delay",d,"press",med([r["pressedAfter"] for r in x]),"catcher",med([r["catcherAfter"] for r in x if r.get("catcherAfter")]),"selector",med([r["mappedAfter"] for r in x if r["mappedAfter"]]),{o:[r["outcome"] for r in x].count(o) for o in {r["outcome"] for r in x}},"diffPx max",max(px) if px else "n/a","(n=%d)"%len(px))
PY
