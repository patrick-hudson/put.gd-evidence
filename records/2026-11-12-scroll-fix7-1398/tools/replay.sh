#!/bin/sh
# replay.sh NAME : converts frames/NAME/*.png to raw and replays them
cd ~/work/sf7 && python3 - "$1" <<'PY'
import sys, json
from PIL import Image
import numpy as np
d = "frames/" + sys.argv[1]
m = json.load(open(d + "/meta.json"))
args = []
for i, p in enumerate(m["positions"]):
    a = np.asarray(Image.open("%s/f%03d.png" % (d, i)).convert("RGB"))
    raw = np.dstack([a[:, :, 2], a[:, :, 1], a[:, :, 0], np.full(a.shape[:2], 255, np.uint8)])
    raw.tofile("%s/f%03d.bgrx" % (d, i))
    args.append("%d:%s/f%03d.bgrx" % (p, d, i))
open(d + "/args.txt", "w").write("%d %d %s" % (m["size"][0], m["size"][1], " ".join(args)))
PY
./replay7 $(cat frames/$1/args.txt)
