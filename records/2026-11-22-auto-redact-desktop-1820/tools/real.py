import sys, json, time
sys.path.insert(0, 'kit')
from orch import *
from PIL import Image, ImageDraw
import subprocess

def run_real(h, label, crop, cover=ALL):
    n0 = len(h.call('notifications'))
    oid = h.call('capture', label, 'monitor', 'agent', None, None)
    op = h.call('observe', oid, 'sensitive_text_found', 120)
    paused = op.get('phase') == 'sensitive_text_found'
    if paused:
        h.call('decide', oid, 'upload'); op = h.call('observe', oid, 'end', 120)
    col = h.call('collect', oid, label); time.sleep(1.5)
    f = h.pull(col['uploads'] + [x['to'] for x in col['original']])
    notes = [n['fields']['notificationText'] for n in h.call('notifications', n0)]
    up, orig = Image.open(f[0]).convert('RGB'), Image.open(f[1]).convert('RGB') if len(f) > 1 else None
    out = {'label': label, 'state': op['state'], 'paused': paused, 'sensitive': op.get('sensitive'), 'notifications': notes}
    if orig:
        # changed pixels all black?
        from PIL import ImageChops
        diff = ImageChops.difference(up, orig).convert('L').point(lambda v: 255 if v else 0)
        box = diff.getbbox()
        bad = sum(1 for (a, d) in zip(up.getdata(), diff.getdata()) if d and a != (0, 0, 0))
        out['changedBox'] = box; out['changedNotBlack'] = bad
        c = up.crop(crop); o = orig.crop(crop)
        im = Image.new('RGB', (c.width, c.height * 2 + 6), 'red'); im.paste(o, (0, 0)); im.paste(c, (0, c.height + 6))
        im.save(f'{h.res}/{label}-pair.png')
    h.record(out)
    return out
