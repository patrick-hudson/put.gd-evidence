# Fixture controls of fix round 7, on the tester's driver (pass2.py, fix6.py) and fixtures:
#   ruler from its end x2, Qt text x1, GTK 4 text x1, browser ruler from top x1 (fix6.py controls),
#   sticky header + footer x1, the FIX-6 committed-resize fixture x1 (an honest end is the pass),
#   the minimap fixture x1 (an honest end with the first viewport is the pass).
import json, os, sys, time, traceback, subprocess
from pathlib import Path
import pass2 as p, fix6 as f
P = p.P
out = json.loads((P / 'controls7-repeat.json').read_text()) if os.environ.get('SF7_REVERIFY') else {}
def note(name, value):
    out[name] = value
    (P / 'controls7-repeat.json').write_text(json.dumps(out, indent=1))
    print(json.dumps({name: value})[:600], flush=True)
def summary(r):
    c = (r or {}).get('capture', {}) if isinstance(r, dict) else {}
    res = c.get('result', c)
    return {'state': c.get('state'), 'endReason': res.get('endReason'), 'height': res.get('height'), 'note': res.get('note'), 'pass': (r or {}).get('pass') if isinstance(r, dict) else None,
            'verification': {k: v for k, v in ((r or {}).get('verification') or {}).items() if k in ('pass', 'lines', 'rows', 'badCells', 'mismatches', 'first_bad', 'bands', 'distinct')} if isinstance(r, dict) else None}
def run(name, call):
    try:
        note(name, summary(call()))
    except Exception:
        note(name, {'error': traceback.format_exc()[-800:]})
which = sys.argv[1:] or ['ruler', 'text', 'browser', 'sticky', 'resize', 'minimap']
if 'ruler' in which:
    for i in range(2):
        run('ruler-end-%d' % i, lambda: f.control('ruler-end-%d' % i, 600, ['python3', str(P / 'qt_fixture.py'), '--rows', '600', '--start', '23400'], maxh=30000))
if 'text' in which:
    for kind in ('qtfull', 'gtkfull'):
        try:
            p.batch(kind, 1)
            r = json.loads((P / (kind + '-00') / 'result.json').read_text())
            note(kind, summary(r))
        except Exception:
            note(kind, {'error': traceback.format_exc()[-800:]})
if 'browser' in which:
    ff = P / 'ffprofile'; ff.mkdir(exist_ok=True)
    (ff / 'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
    run('firefox-top-0', lambda: f.control('firefox-top-0', 60, ['firefox', '--no-remote', '--profile', str(ff), '--kiosk', (P / 'ruler.html').as_uri()], wait=18))
if 'sticky' in which:
    run('sticky-0', lambda: f.with_fixture('sticky', ['python3', str(P / 'review_fixture.py'), '--rows', '600', '--sticky'], lambda: p.capture('sticky-0', 600, 30000, header=40, footer=40)))
if 'resize' in which:
    def resize():
        r = f.resize_case('mid-viewport-0', 'resize_mid_fixture.py', 3, SC_MODE='viewport', SC_AT='6000')
        return {'capture': r.get('capture'), 'pass': str(r.get('verdict', '')).startswith('honest'), 'verification': r.get('verification')}
    run('mid-viewport-0', resize)
if 'minimap' in which:
    def minimap():
        if os.environ.get('SF7_REVERIFY'):  # the capture is there already: only compare again (no desktop)
            r = json.loads((P / 'editor-1' / 'result.json').read_text())
        else:
            r = f.with_fixture('editor', ['python3', str(P / 'editor_fixture.py'), '--rows', '600', '--start', '23400'], lambda: p.capture('editor-1', 600, 30000))
        c = r.get('capture', {}); res = c.get('result', c)
        png = P / 'editor-1' / 'capture.png'
        v = None
        if png.exists():
            import numpy as np
            from PIL import Image
            im = np.asarray(Image.open(png).convert('RGB')).astype('int16'); h = im.shape[0]; y = np.arange(h)
            mini = np.stack([30 + (y * 17) % 190, 40 + (y * 23) % 180, 50 + (y * 31) % 170], axis=1)
            bad = int(np.count_nonzero(np.any(im[:, 860:] != mini[:, None, :], axis=2)))
            # The main column: the ruler's cells left of the strip (14 of its 16 columns), every scanline.
            def bits(r, l):
                if l < 2: return 65535
                if l < 30: return r
                x = (r * 2654435761 + l * 40503 + 0x9e3779b9) & 0xffffffff; x ^= x >> 15; x = x * 0x2c1b3c6d & 0xffffffff; x ^= x >> 12; x = x * 0x297a2d39 & 0xffffffff; x ^= x >> 15
                b = x & 65535
                return b if b not in (0, 65535) else 0x5a5a ^ l
            cells = 0
            for yy in range(h):
                b = bits(yy // 40, yy % 40)
                for col in range(14):
                    cells += int((int(im[yy, 64 + col * 55 + 27].sum()) < 384) != bool(b & (0x8000 >> col)))
            v = {'height': h, 'minimapMismatchPixels': bad, 'mainColumn': {'pass': cells == 0, 'badCells': cells}}
        ok = res.get('endReason') == 'lost_track' and v is not None and v['minimapMismatchPixels'] == 0 and v['mainColumn'].get('pass')
        return {'capture': c, 'pass': bool(ok), 'verification': {'pass': bool(ok), 'rows': v and v['height'], 'mismatches': v and v['minimapMismatchPixels'], 'badCells': v and v['mainColumn']['badCells']}}
    run('editor-1', minimap)
if not os.environ.get('SF7_REVERIFY'):
    (P / 'controls7-repeat.done').write_text('done')
