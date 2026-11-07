"""Reference renderer of the converged rule, with the dark-page paper floor as a knob."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, '/home/patrick/work/i1237-council/proposals/opus'); sys.path.insert(0, '/home/patrick/work/i1237-council/compare')
import numpy as np
from PIL import Image, ImageDraw
import hl_research as H
import opus_hl as O

def lum(c):
    return float(H.luminance(np.array(c, float)))

def paper_for(m, dark, floor):
    m = np.array(m, int)
    if m.min() >= 240: return np.array([250]*3) if dark else np.array([232]*3)
    if m.max() <= 32: return np.array([149]*3)
    if not dark: return (m + 256) // 2
    for w in range(89, 255):
        q = ((255 - w) * m + 255 * w + 127) // 255
        if lum(q) >= floor: return q
    return np.array([255]*3)

def table_for(q, lb, steps=4095):
    a = np.arange(256)[:, None]
    ramp = (q[None, :] * (255 - a) + 127) // 255
    rl = H.luminance(ramp.astype(float))
    L = np.arange(steps + 1) / steps
    c = (np.maximum(L, lb) + 0.05) / (np.minimum(L, lb) + 0.05)
    wanted = (rl[0] + 0.05) / c - 0.05
    # first a with rl[a] <= wanted (rl decreasing)
    idx = np.searchsorted(-rl, -wanted - 1e-9, side='left').clip(0, 255)
    return ramp[idx]

def converged(px, m, seg, floor=0.78, dark_page=0.30):
    cov, bgpix, distinct, frac = seg
    m = np.array(m, int)
    if frac < 0.5:
        return ((184 * px + 71 * m + 127) // 255).astype(float)
    idx = np.argmin(np.linalg.norm(bgpix[..., None, :] - distinct[None, None, :, :], axis=-1), axis=-1)
    out = px.copy()
    L = H.luminance(px)
    li = np.clip((L * 4095 + 0.5).astype(int), 0, 4095)
    for k, b in enumerate(distinct):
        mask = idx == k
        if not mask.any(): continue
        lb = lum(b)
        q = paper_for(m, lb < dark_page, floor)
        t = table_for(q, lb)
        out[mask] = t[li[mask]]
    return out

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    floors = [0.45, 0.55, 0.65, 0.78]
    import compare as C
    C.MODES = ['today']
    C.EXTRA_MODES = {f'floor {f}': (lambda f: (lambda r, m, seg: converged(r, m, seg, floor=f)))(f) for f in floors}
    def only_today(region, m):
        seg = H.segment(region); o = {'today': O.mode_today(region, m)}
        for k, fn in C.EXTRA_MODES.items(): o[k] = fn(region, m, seg)
        return o
    C.tile_modes = only_today
    for crop in ['dark-table', 'dark-notify', 'kde-notify', 'syn-syntax', 'dark-settings-top']:
        print(C.sheet([crop], O.PALETTE, f'{out}/sweep-{crop}.png', f'{crop}: dark-page paper floor sweep (today · 0.45 · 0.55 · 0.65 · 0.78)'))
    print(C.sheet(['light-paragraph', 'light-menu'], O.PALETTE, f'{out}/sweep-light.png', 'light pages (floor has no effect): today · converged'))
