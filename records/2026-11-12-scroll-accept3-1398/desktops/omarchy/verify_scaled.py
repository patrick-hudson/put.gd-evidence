# The ruler page captured at a fractional scale: every physical scanline must
# decode to the ruler line at its place, within one physical pixel (a toolkit
# rounds the edges of scaled one-pixel lines), and every row's index must be
# at its centre. After the acceptance round's fractional_verify.py.
import sys, json
from PIL import Image
def pattern(r, l):
    if l < 2: return 65535
    if l < 30: return r
    x = (r * 2654435761 + l * 40503 + 0x9e3779b9) & 0xffffffff; x ^= x >> 15; x = x * 0x2c1b3c6d & 0xffffffff; x ^= x >> 12; x = x * 0x297a2d39 & 0xffffffff; x ^= x >> 15
    b = x & 65535
    return b if b not in (0, 65535) else 0x5a5a ^ l
def verify(path, scale, rows):
    im = Image.open(path).convert('RGB'); px = im.load(); errors = []
    want = (round(960 * scale), round(rows * 40 * scale))
    if im.size != want: errors.append('dimensions %s, expected %s' % (im.size, want))
    def code(y):
        b = 0
        for c in range(16):
            rgb = px[int((64 + (c + .5) * 55) * scale), y]
            b = b << 1 | (sum(rgb) < 384)
        return b
    for row in range(rows):
        y = round((row * 40 + 15) * scale)
        if y >= im.height or code(y) != row: errors.append('row centre %d' % row)
        if len(errors) > 20: break
    bad = 0
    for y in range(im.height):
        got = code(y)
        if not any(got == pattern(*divmod(max(0, int((y + s) / scale)), 40)) for s in (-1, 0, 1)):
            bad += 1
            if bad <= 5: errors.append('scanline %d' % y)
    return {'ok': not errors, 'size': list(im.size), 'badScanlines': bad, 'errors': errors[:8]}
if __name__ == '__main__':
    print(json.dumps(verify(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]))))
