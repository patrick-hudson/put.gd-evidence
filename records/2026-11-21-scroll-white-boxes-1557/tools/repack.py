#!/usr/bin/env python3
"""repack.py RUNDIR...: re-save each tee frame as PNG compress_level 6 (lossless), in place via a temp file and rename."""
import os, sys
from multiprocessing import Pool
from PIL import Image
def one(path):
    if os.path.getsize(path) < 1_500_000: return 0
    tmp = path + '.tmp.png'
    Image.open(path).save(tmp, compress_level=6)
    os.replace(tmp, path)
    return 1
if __name__ == '__main__':
    os.nice(10)
    for run in sys.argv[1:]:
        d = os.path.join(run, 'tee', 'run0')
        files = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith('.png') and not f.endswith('.tmp.png'))
        with Pool(3) as p: n = sum(p.map(one, files, chunksize=16))
        print(run, len(files), 'repacked', n, flush=True)
