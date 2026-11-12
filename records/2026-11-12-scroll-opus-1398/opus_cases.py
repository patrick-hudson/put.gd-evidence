# The tester's late_fixture cases (latecases.py of accept3), three runs each:
# `counter` (a fixed counter in a bottom bar: "new-fixed") and `nonfixed`
# (a non-fixed patch repainted in the bottom of the viewport, the whole picture
# rebuilt on every wheel event: the case that ended end_of_content early).
import pass2 as p, fix6 as f, json, shutil, sys
from PIL import Image
import numpy as np
kinds = sys.argv[1:] or ['nonfixed', 'counter']
for kind in kinds:
    for i in range(3):
        name = 'new-' + kind + '-' + str(i)
        r, o = f.with_fixture(name, ['python3', str(p.P / 'late_fixture.py'), kind], lambda: f.cap(name, maxh=30000))
        if not (o / 'capture.png').exists():
            r['oracle'] = {'imageAbsent': True}; f.save(r, o); continue
        for suffix in ['-generator.png', '-footer.png']:
            source = p.P / (kind + suffix)
            if source.exists(): shutil.copyfile(source, o / ('reference' + suffix))
        im = np.asarray(Image.open(o / 'capture.png').convert('RGB')); ref = np.asarray(Image.open(p.P / (kind + '-generator.png')).convert('RGB')); h = len(im)
        if kind == 'counter':
            ref = np.concatenate([ref, np.asarray(Image.open(p.P / (kind + '-footer.png')).convert('RGB'))])
        nh = min(h, len(ref)); diff = np.any(im[:nh] != ref[:nh], axis=2)
        c = r.get('capture', {}); res = c.get('result', c)
        rows = np.where(diff.any(axis=1))[0]
        r['oracle'] = {'height': h, 'expectedHeight': len(ref), 'pixelExact': h == len(ref) and not diff.any(), 'mismatchPixels': int(diff.sum()),
                       'firstBadRow': int(rows[0]) if len(rows) else None, 'badRows': [int(rows[0]), int(rows[-1])] if len(rows) else None,
                       'maxDelta': int(np.abs(im[:nh].astype(int) - ref[:nh].astype(int)).max()) if diff.any() else 0}
        r['falseEnd'] = res.get('endReason') == 'end_of_content' and h != len(ref)
        f.save(r, o)
