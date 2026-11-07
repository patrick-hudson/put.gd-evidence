"""Side-by-side sheet of every council proposal on the same crops and colours."""
import sys, os, importlib.util
sys.dont_write_bytecode = True
ROOT = '/home/patrick/work/i1237-council'
sys.path.insert(0, ROOT + '/proposals/opus')
import numpy as np
from PIL import Image, ImageDraw
import hl_research as H
import opus_hl as O

def exec_head(path, stop):
    src = open(path).read().split('\n')
    end = next(i for i, l in enumerate(src) if l.startswith(stop))
    ns = {'__file__': path}
    exec('\n'.join(src[:end]), ns)
    return ns
SOL = exec_head(ROOT + '/proposals/sol/render.py', 'def round2')
AST = exec_head(ROOT + '/proposals/astra/render.py', 'def round2')

def tile_modes(region, m):
    seg = H.segment(region)
    cov, bg, distinct, frac = seg
    out = {}
    out['today'] = O.mode_today(region, m)
    out['round 2'] = O.mode_round2(region, m, seg=seg)
    idx = np.argmin(np.linalg.norm(bg[..., None, :] - distinct[None, None, :, :], axis=-1), axis=-1)
    solseg = (cov, distinct[idx], distinct, frac)
    out['sol'] = SOL['candidate'](region.astype(float), np.array(m, float), solseg).astype(float)
    a, _ = AST['proposed'](region, cov, bg, frac, np.array(m, dtype=np.int64))
    out['astra'] = np.clip(np.rint(a), 0, 255).astype(float)
    out['opus'] = O.mode_opus(region, m, seg=seg)
    extra = globals().get('EXTRA_MODES', {})
    for k, fn in extra.items():
        out[k] = fn(region, m, seg)
    return out

MODES = ['today', 'round 2', 'sol', 'astra', 'opus']
def render_crop(name, m):
    px = O.load(name)
    outs = {k: px.copy() for k in MODES + list(globals().get('EXTRA_MODES', {}))}
    for (x0, y0, x1, y1) in O.SCENES[name][1]:
        r = tile_modes(px[y0:y1, x0:x1], m)
        for k, v in r.items():
            outs[k][y0:y1, x0:x1] = v
    vx0, vy0, vx1, vy1 = O.VIEW[name]
    return {k: v[vy0:vy1, vx0:vx1] for k, v in outs.items()}

def label(im, text):
    t = Image.new('RGB', (im.width, im.height + 22), '#e9e6e0')
    t.paste(im, (0, 22))
    ImageDraw.Draw(t).text((4, 4), text, fill='#222', font=O.font(13, bold=False))
    return t

def sheet(crops, colours, path, title, zoom=2):
    modes = MODES + list(globals().get('EXTRA_MODES', {}))
    rows = []
    for name in crops:
        for cname, m in colours:
            r = render_crop(name, m)
            tiles = []
            for k in modes:
                im = Image.fromarray(r[k].astype(np.uint8))
                im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
                tiles.append(label(im, f'{name} · {cname} · {k}'))
            rows.append(tiles)
    colw = [max(t[i].width for t in rows) for i in range(len(modes))]
    W = sum(colw) + 12 * (len(modes) + 1)
    Hh = sum(max(t.height for t in row) + 12 for row in rows) + 40
    sh = Image.new('RGB', (W, Hh), '#d4d4d0')
    ImageDraw.Draw(sh).text((12, 10), title, fill='#222', font=O.font(16))
    y = 40
    for row in rows:
        x = 12
        for i, t in enumerate(row):
            sh.paste(t, (x, y)); x += colw[i] + 12
        y += max(t.height for t in row) + 12
    sh.save(path)
    return path

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else ROOT + '/compare'
    os.makedirs(out, exist_ok=True)
    pal = dict(O.PALETTE)
    yr = [('yellow', pal['yellow']), ('red', pal['red'])]
    dark = ['dark-table', 'dark-notify', 'kde-notify', 'dark-settings-top', 'syn-syntax', 'syn-button']
    light = ['light-paragraph', 'light-menu', 'light-popup']
    print(sheet(dark, yr, out + '/overview-dark.png', 'Dark pages, yellow and red: today · round 2 · Sol · Astra · Opus (2x)'))
    print(sheet(light, yr, out + '/overview-light.png', 'Light pages, yellow and red (2x)'))
    print(sheet(['photo', 'kde-wallpaper-text', 'accent'], yr, out + '/overview-fallback.png', 'No-paper fallbacks (2x)'))
    for crop in ['dark-table', 'dark-notify', 'kde-notify', 'light-paragraph']:
        print(sheet([crop], O.PALETTE, out + f'/colours-{crop}.png', f'{crop}: every palette colour (2x)'))
