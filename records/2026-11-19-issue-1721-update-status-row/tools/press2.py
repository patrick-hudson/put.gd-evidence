import sys, os, time, json, subprocess
sys.path.insert(0, os.path.expanduser('~/work/w1721/drv'))
import rfb, drv_lib
X0, X1 = 1140, 1225  # strip inside the Check now button, same column every time
def strip(c, y0, y1):
    w = c.width; p = c.pixels
    return [bytes(p[(y * w + X0) * 4:(y * w + X1) * 4]) for y in range(y0, y1)]
def locate(c, tmpl):
    c.frame(); best = None
    h = len(tmpl)
    rows = strip(c, 0, c.height)
    for y in range(240, c.height - h - 120):
        d = 0
        for k in range(0, h, 2):
            a, b = rows[y + k], tmpl[k]
            d += sum(abs(a[i] - b[i]) for i in range(0, len(a), 12))
            if best and d >= best[0]: break
        if best is None or d < best[0]: best = (d, y)
    return best
name, cli, tx, ty, count, wait, prefix = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
c = rfb.RFB(drv_lib.PORT); c.frame(); tmpl = strip(c, ty - 14, ty + 14); c.close()
for i in range(count):
    c = rfb.RFB(drv_lib.PORT); d, y = locate(c, tmpl); by = y + 14
    c.click(1182, by); time.sleep(0.2); c.pointer(5, 5); c.close()
    time.sleep(wait)
    st = json.loads(drv_lib.cli(name, cli, 'update.status') or '{}').get('result') or {}
    drv_lib.shot('%s-%02d.png' % (prefix, i + 1))
    print(i + 1, 'clicked y', by, 'diff', d, 'checking', st.get('checking'), 'checkedAt', st.get('checkedAt'), flush=True)
