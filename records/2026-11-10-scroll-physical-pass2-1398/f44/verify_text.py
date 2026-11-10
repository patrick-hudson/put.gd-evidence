# Checks a stitched capture of a text view whose lines are all different
# ("Row 0000 ...", "Row 0001 ..."): the image is cut into text-line bands, and
# a correct stitch has every band once (no two bands with the same bitmap), a
# constant line pitch and, for a whole document, as many bands as lines.
import sys, json, hashlib
import numpy as np
from PIL import Image

def verify(path, expected=None, x1frac=0.6):
    im = np.asarray(Image.open(path).convert("L")).astype(np.int16)
    h, w = im.shape
    part = im[:, : int(w * x1frac)]
    bg = int(np.median(part))
    ink = np.abs(part - bg) > 60
    rows = ink.any(axis=1)
    bands, y = [], 0
    while y < h:
        if rows[y]:
            y0 = y
            while y < h and rows[y]: y += 1
            bands.append((y0, y))
        else: y += 1
    # A band cut by the image's top or bottom edge is not a whole line.
    whole = [b for b in bands if b[0] > 0 and b[1] < h]
    seen, dup = {}, []
    for (y0, y1) in whole:
        k = hashlib.sha1(np.packbits(ink[y0:y1]).tobytes() + bytes([min(255, y1 - y0)])).hexdigest()
        if k in seen: dup.append((seen[k], y0))
        else: seen[k] = y0
    tops = [b[0] for b in whole]
    pitch = {}
    for a, b in zip(tops, tops[1:]): pitch[b - a] = pitch.get(b - a, 0) + 1
    heights = {}
    for (y0, y1) in whole: heights[y1 - y0] = heights.get(y1 - y0, 0) + 1
    common = sorted(pitch, key=lambda k: -pitch[k])[:2]
    odd = sum(v for k, v in pitch.items() if not any(abs(k - c) <= 0 for c in common)) if pitch else 0
    ok = not dup and odd == 0 and len(heights) <= 2 and (expected is None or len(whole) in (expected, expected - 1, expected - 2))
    return {"ok": bool(ok), "width": w, "height": h, "lines": len(whole), "expected": expected, "duplicates": len(dup), "firstDuplicate": dup[:1],
            "pitch": {str(k): v for k, v in sorted(pitch.items())}, "oddPitch": odd, "bandHeights": {str(k): v for k, v in sorted(heights.items())}}

if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)))
