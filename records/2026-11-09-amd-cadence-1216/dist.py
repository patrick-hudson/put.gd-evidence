import sys
sys.path.insert(0, 'tools/lab')
import fluidity
clip = sys.argv[1]
strip = None; prev = None; rows = {}
first = None
for pts, w, h, stride, data in fluidity.decode_frames(clip):
    if first is None: first = pts
    if strip is None:
        strip = fluidity.find_strip(w, h, stride, data)
        if strip is None: continue
    c = fluidity.read_counter(w, stride, data, strip)
    if c is None: prev = None; continue
    sec = int((pts - first) / 1e9)
    r = rows.setdefault(sec, [0, 0, 0])
    if prev is not None:
        d = c - prev
        r[0] += 1
        if d == 0: r[1] += 1
        elif d == 2: r[2] += 1
    prev = c
print('second pairs repeats skip1')
for s in sorted(rows): print(s, *rows[s])
