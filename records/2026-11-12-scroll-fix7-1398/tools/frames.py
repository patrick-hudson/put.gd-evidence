# Screenshots of a live page at given scroll positions (set through the browser, no input), cropped to the
# viewport rectangle: real frames for replaying the stitcher offline.
#   frames.py SITE NAME POS[,POS...]      or   frames.py SITE NAME START:STEP:COUNT
import sys, time, json
sys.path.insert(0, '/home/patrick/work/sf7'); sys.path.insert(0, '/home/patrick/work/sf7/tools')
import live7
from PIL import Image
site, name, spec = sys.argv[1], sys.argv[2], sys.argv[3]
if ':' in spec:
    a, s, n = map(int, spec.split(':')); pos = [a + s * i for i in range(n)]
else:
    pos = [int(x) for x in spec.split(',')]
b, kind = live7.connect()
view = json.loads((live7.P / 'viewport.json').read_text())['rect']
out = live7.P / 'frames' / name
out.mkdir(parents=True)
b.navigate(live7.SITES.get(site, site)); time.sleep(6); info = live7.wait_loaded(b, 20)
w = min(view[2], int(info['clientWidth']))
got = []
for i, p in enumerate(pos):
    b.js('window.scrollTo({top:%d,behavior:"instant"});return 0;' % p); time.sleep(1.2)
    y = b.js('return Math.round(scrollY)')
    live7.screen_png(out / 'screen.png')
    Image.open(out / 'screen.png').convert('RGB').crop((view[0], view[1], view[0] + w, view[1] + view[3])).save(out / ('f%03d.png' % i))
    got.append(y)
(out / 'screen.png').unlink()
(out / 'meta.json').write_text(json.dumps({'site': site, 'positions': got, 'size': [w, view[3]], 'browser': kind}))
print(name, got)
