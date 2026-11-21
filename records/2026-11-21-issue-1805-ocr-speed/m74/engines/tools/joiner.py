"""Reading-order joiner shared by the box-returning engines (#1805 research)."""


def join_lines(items):
    """items: list of (x0, y0, x1, y1, text). Bands top-to-bottom, left-to-right within a band.

    A box joins the current band when its vertical centre lies inside the band's
    vertical extent and their overlap is at least half the smaller height.
    """
    items = [i for i in items if i[4] and i[4].strip()]
    items.sort(key=lambda b: ((b[1] + b[3]) / 2, b[0]))
    bands = []
    for b in items:
        cy = (b[1] + b[3]) / 2
        h = b[3] - b[1]
        placed = False
        for band in reversed(bands[-3:]):
            top, bot = band['top'], band['bot']
            ov = min(bot, b[3]) - max(top, b[1])
            if top <= cy <= bot and ov >= 0.5 * min(h, bot - top):
                band['items'].append(b)
                band['top'] = min(top, b[1]); band['bot'] = max(bot, b[3])
                placed = True
                break
        if not placed:
            bands.append(dict(top=b[1], bot=b[3], items=[b]))
    bands.sort(key=lambda bd: (bd['top'] + bd['bot']) / 2)
    return '\n'.join(' '.join(x[4] for x in sorted(bd['items'], key=lambda x: x[0])) for bd in bands)


def hwm_kib():
    rss = hwm = 0
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmHWM:'):
                hwm = int(line.split()[1])
            elif line.startswith('VmRSS:'):
                rss = int(line.split()[1])
    return rss, hwm


def _gaps(spans, lo, hi):
    """Free intervals in [lo, hi] not covered by spans; returns (start, end) list."""
    spans = sorted(spans)
    out, cur = [], lo
    for s, e in spans:
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < hi:
        out.append((cur, hi))
    return out


def _vcuts(items, lh):
    """Vertical gutters of at least three line heights with boxes on both sides."""
    x0 = min(b[0] for b in items); x1 = max(b[2] for b in items)
    return [g for g in _gaps([(b[0], b[2]) for b in items], x0, x1) if g[1] - g[0] >= 3 * lh and g[0] > x0 and g[1] < x1]


def _xy(items, lh):
    if len(items) < 2:
        return [items]
    v = _vcuts(items, lh)
    if v:
        cols, edges = [], [g[0] for g in v] + [float('inf')]
        lo = float('-inf')
        for i, g in enumerate(v + [(float('inf'), float('inf'))]):
            part = [b for b in items if lo <= (b[0] + b[2]) / 2 < g[0]]
            if part:
                cols.append(part)
            lo = g[1] if g[1] != float('inf') else lo
        out = []
        for c in cols:
            out += _xy(c, lh)
        return out
    # Horizontal cut kept only when a part on either side is then cut down.
    y0 = min(b[1] for b in items); y1 = max(b[3] for b in items)
    for g in _gaps([(b[1], b[3]) for b in items], y0, y1):
        if g[0] <= y0 or g[1] >= y1:
            continue
        top = [b for b in items if (b[1] + b[3]) / 2 < g[0]]
        bot = [b for b in items if (b[1] + b[3]) / 2 >= g[0]]
        if top and bot and (_vcuts(top, lh) or _vcuts(bot, lh)):
            return _xy(top, lh) + _xy(bot, lh)
    return [items]


def join_layout(items, width, height):
    """As the helper does: screens of at least 4 MP are cut into panels (XY cut over boxes,
    gutters >= 3 line heights), panels joined in order; smaller inputs are one panel."""
    items = [i for i in items if i[4] and i[4].strip()]
    if not items:
        return ''
    if width * height < 4_000_000:
        return join_lines(items)
    hs = sorted(b[3] - b[1] for b in items)
    lh = max(4.0, hs[len(hs) // 2])
    return '\n\n'.join(join_lines(p) for p in _xy(items, lh))


class Sampler:
    """Samples this process's RSS every 5 ms; ms spent above a threshold (default 128 MiB)."""
    def __init__(self, limit_kib=128 * 1024):
        import threading, os
        self.limit, self.above, self.stop = limit_kib, 0.0, False
        self.page = os.sysconf('SC_PAGE_SIZE') // 1024
        self.t = threading.Thread(target=self.run, daemon=True); self.t.start()
    def run(self):
        import time
        last = time.monotonic()
        while not self.stop:
            time.sleep(0.005)
            now = time.monotonic()
            with open('/proc/self/statm') as f:
                rss = int(f.read().split()[1]) * self.page
            if rss > self.limit:
                self.above += now - last
            last = now
    def done(self):
        self.stop = True; self.t.join()
        return round(self.above * 1000)
