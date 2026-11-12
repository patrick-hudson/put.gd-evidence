# FIX-6 desktop cases for PR #1398 on d69 (Plasma) and f44 (GNOME), on the
# tester's driver (pass2.py) and fixtures.
#   fix6.py resize    the tester's resize-window case x3 (the window is resized 5 s after the fixture starts)
#   fix6.py mid       the same change after rows were committed: window, viewport, narrower, shorter, x3 each
#   fix6.py before    (the previous head's package) the change after rows were committed, each kind once
#   fix6.py controls  ruler from its end x2, Qt text x1, GTK 4 text x1, browser ruler from top x1
#   fix6.py cancel    stop then cancel 1 ms later x5, stop then cancel 50 ms later x3, next capture
import pass2 as p, subprocess, time, json, threading, hashlib, shutil, re, sys, os, argparse, traceback
from pathlib import Path
import rfb
P = p.P
PORT = 5901 if os.uname().nodename == 'fedora' else 5900

def env(**more):
    e = json.loads((P / 'env.json').read_text()); e.update(more); return e

def bits(r, l):
    if l < 2: return 65535
    if l < 30: return r
    x = (r * 2654435761 + l * 40503 + 0x9e3779b9) & 0xffffffff; x ^= x >> 15; x = x * 0x2c1b3c6d & 0xffffffff; x ^= x >> 12; x = x * 0x297a2d39 & 0xffffffff; x ^= x >> 15; b = x & 65535
    return b if b not in (0, 65535) else 0x5a5a ^ l

def verify_layout(path):
    """The image as a rectangle larger than the page's viewport shows it: the
    window's gray above, below and beside the ruler; every ruler row once."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path).convert('L'); W, H = im.size; d = im.tobytes(); gray = bytes([102]) * W
    row = lambda y: d[y * W:(y + 1) * W]
    t = 0
    while t < H and row(t) == gray: t += 1
    b = 0
    while b < H - t and row(H - 1 - b) == gray: b += 1
    probe = row(min(H - 1, t + 100)); l = 0
    while l < W and probe[l] == 102: l += 1
    r = W - 1
    while r > l and probe[r] == 102: r -= 1
    bad = 0; first = None; cells = 0
    for y in range(H - t - b):
        rr, ll = divmod(y, 40); bb = bits(rr, ll); rw = row(t + y)
        for ci in range(16):
            x0 = l + 64 + ci * 55; x1 = x0 + 55
            if x1 > r + 1: break
            want = bool(bb & (0x8000 >> ci)); seg = rw[x0 + 2:x1 - 2]; cells += 1
            if not (all(v < 60 for v in seg) if want else all(v > 200 for v in seg)):
                bad += 1
                if first is None: first = [y, ci]
        if r + 1 < W and any(v != 102 for v in rw[r + 2:]):
            bad += 1
            if first is None: first = [y, 'right of the viewport']
    return {'size': [W, H], 'grayRowsAbove': t, 'grayRowsBelow': b, 'viewportColumns': [l, r], 'rulerRows': H - t - b, 'cellsChecked': cells, 'badCells': bad, 'firstBad': first}

def verify_prefix(path, height):
    """Every scanline is the 960 px ruler's row of that number (the tester's oracle)."""
    import scroll_run
    a = argparse.Namespace(scale=1, height=height, rows=600, first_pixel=0, header=0, footer=0, code_width=960, format='fixture', scrollbar=0)
    return scroll_run.verify(path, a)

def cap(name, rect=(100, 200, 960, 600), maxh=40000):
    out = P / name; out.mkdir(); log = P / 'helper.log'; offset = log.stat().st_size if log.exists() else 0
    done = threading.Event()
    def frames():
        try:
            v = rfb.RFB(PORT)
            for i in range(200):
                if done.is_set(): break
                v.screenshot(out / ('screen-%03d.png' % i)); done.wait(2)
            v.sock.close()
        except Exception as ex: (out / 'visual-error.txt').write_text(str(ex))
    th = threading.Thread(target=frames); result = {'name': name}
    try:
        v = p.rpc('scroll.prepare', {'rect': list(rect), 'maxHeight': maxh}); ident = v['id']; result['id'] = ident
        while v['state'] != 'ready': time.sleep(.1); v = p.rpc('scroll.inspect', {'id': ident})
        time.sleep(.8); th.start(); p.rpc('scroll.start', {'id': ident}); start = time.monotonic()
        while True:
            v = p.rpc('scroll.inspect', {'id': ident})
            if v['state'] in ['done', 'failed', 'cancelled']: break
            if time.monotonic() - start > 250: raise TimeoutError('capture')
            time.sleep(.15)
        result['capture'] = v; sha = v.get('result', {}).get('sha256'); found = None
        for i in range(80):
            for f in (P / 'archive').rglob('*.png'):
                if hashlib.sha256(f.read_bytes()).hexdigest() == sha: found = f; break
            if found or not sha: break
            time.sleep(.2)
        if found: shutil.copyfile(found, out / 'capture.png')
    except Exception as ex:
        result['error'] = traceback.format_exc()
        try: p.rpc('scroll.cancel', {'id': ident})
        except Exception: pass
    finally:
        done.set()
        if th.is_alive(): th.join(15)
        txt = log.read_bytes()[offset:].decode(errors='replace') if log.exists() else ''
        (out / 'helper.log').write_text(txt); result['endLines'] = re.findall(r'scroll: (?:ended|source fresh|way to the top) .*', txt)
        result['steps'] = [m for m in re.findall(r'scroll step: (\S+ offset \S+ hint \S+ notches \S+ score \S+ evidence \S+ appended \S+ fixed \S+)', txt)][-6:]
    return result, out

def with_fixture(name, cmd, call, wait=3, **more):
    f = subprocess.Popen(cmd, env=env(**more), stdout=open(P / (name + '-fixture.log'), 'w'), stderr=subprocess.STDOUT)
    try:
        time.sleep(wait)
        if f.poll() is not None:raise RuntimeError("Fixture exited before capture: "+str(cmd)+" exit="+str(f.returncode))
        if any(Path(x).name in ("adversarial.py","late_fixture.py") for x in cmd):
            ready_log=P/(name+"-fixture.log")
            deadline=time.monotonic()+20
            while "\"ready\": true" not in ready_log.read_text():
                if f.poll() is not None or time.monotonic()>deadline:raise RuntimeError("Fixture readiness missing: "+name)
                time.sleep(.1)
        return call()
    finally:
        f.terminate()
        try: f.wait(15)
        except Exception: f.kill()

def save(result, out):
    (out / 'result.json').write_text(json.dumps(result, indent=2))
    c = result.get('capture', {})
    print(json.dumps({'name': result['name'], 'state': c.get('state'), 'endReason': c.get('endReason'), 'height': c.get('height'), 'note': c.get('note') or c.get('result', {}).get('note'), 'verdict': result.get('verdict'), 'verification': {k: v for k, v in result.get('verification', {}).items() if k != 'errors'}, 'errors': result.get('verification', {}).get('errors', [])[:2], 'error': result.get('error')}), flush=True)

def resize_case(name, fixture, wait, **more):
    def run():
        result, out = cap(name)
        c = result.get('capture', {}); png = out / 'capture.png'
        log = (P / (name + '-fixture.log')).read_text()
        result['fixtureChange'] = re.findall(r'changed .*', log)
        if png.exists():
            if c.get('endReason') == 'end_of_content':
                # Complete: either the plain ruler, or the layout the capture saw from its first frame on.
                plain = verify_prefix(png, 24000) if c.get('height') == 24000 else None
                result['verification'] = plain if plain and plain['pass'] else verify_layout(png)
                ok = (plain and plain['pass']) or (result['verification'].get('badCells') == 0 and result['verification'].get('rulerRows') == 24000)
                result['verdict'] = 'exact' if plain and plain['pass'] else ('exact for the layout on screen during the whole capture' if ok else 'WRONG')
            else:
                result['verification'] = verify_prefix(png, c.get('height'))
                result['verdict'] = 'honest, exact prefix' if result['verification']['pass'] and c.get('truncated') else 'WRONG'
        else: result['verdict'] = 'honest, no image' if c.get('state') in ('failed', 'cancelled') else 'WRONG'
        save(result, out); return result
    return with_fixture(name, ['python3', str(P / fixture), '--rows', '600', '--start', '23400'], run, wait, **more)

def control(name, rows, cmd, wait=3, **kw):
    r = with_fixture(name, cmd, lambda: p.capture(name, rows, **kw), wait)
    return r

def cancel_case(name, gap):
    d = P / name; d.mkdir(); off = (P / 'helper.log').stat().st_size
    v = p.rpc('scroll.prepare', {'rect': [100, 200, 960, 600]}); ident = v['id']
    while v['state'] != 'ready': time.sleep(.05); v = p.rpc('scroll.inspect', {'id': ident})
    replies = {}
    def send(m):
        try: replies[m] = subprocess.run(['putgd-cli', '--socket', str(P / 'r/putgd/session.sock'), 'scroll.' + m, json.dumps({'id': ident})], env=env(), text=True, capture_output=True, timeout=75).stdout
        except Exception as ex: replies[m] = {'exception': str(ex)}
    send('start'); time.sleep(.2)
    t = threading.Thread(target=send, args=('stop',)); t.start(); time.sleep(gap); send('cancel'); t.join(75)
    for k in list(replies):
        try: replies[k] = json.loads(replies[k])
        except Exception: pass
    final = p.rpc('scroll.inspect', {'id': ident}); time.sleep(2)
    rfb.RFB(PORT).screenshot(d / 'screen-2s-later.png')
    txt = (P / 'helper.log').read_bytes()[off:].decode(errors='replace'); (d / 'helper.log').write_text(txt)
    result = {'name': name, 'gapSeconds': gap, 'id': ident, 'replies': replies, 'final': final, 'helperOrder': re.findall(r'scroll (?:command|result) (?:stop|cancel).*', txt),
              'shell': subprocess.getoutput('pgrep -x gnome-shell'), 'archivePngs': len(list((P / 'archive').rglob('*.png'))), 'pass': final['state'] == 'cancelled'}
    (d / 'result.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'name': name, 'state': final['state'], 'error': final.get('error'), 'stopReply': (replies.get('stop') or {}).get('error') if isinstance(replies.get('stop'), dict) else replies.get('stop'), 'cancelOk': (replies.get('cancel') or {}).get('ok') if isinstance(replies.get('cancel'), dict) else None, 'helperOrder': result['helperOrder'], 'shell': result['shell']}), flush=True)
    return result

if __name__ == '__main__':
    what = sys.argv[1]
    try:
        if what == 'resize':
            for i in range(3): resize_case('resize-window-%d' % i, 'resize_window_fixture.py', 1)
        elif what == 'mid':
            for mode in ('window', 'viewport', 'narrower', 'shorter'):
                for i in range(3): resize_case('mid-%s-%d' % (mode, i), 'resize_mid_fixture.py', 3, SC_MODE=mode, SC_AT='6000')
        elif what == 'before':
            for mode in ('viewport', 'shorter', 'window'): resize_case('mid-%s-0' % mode, 'resize_mid_fixture.py', 3, SC_MODE=mode, SC_AT='6000')
        elif what == 'narrower':
            resize_case('mid-narrower-0', 'resize_mid_fixture.py', 3, SC_MODE='narrower', SC_AT='6000')
        elif what == 'controls':
            for i in range(2): control('ruler-end-%d' % i, 600, ['python3', str(P / 'qt_fixture.py'), '--rows', '600', '--start', '23400'], maxh=40000)
            p.batch('qtfull', 1); p.batch('gtkfull', 1)
            ff = P / 'ffprofile'; ff.mkdir(exist_ok=True); (ff / 'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
            control('firefox-top-0', 60, ['firefox', '--no-remote', '--profile', str(ff), '--kiosk', (P / 'ruler.html').as_uri()], wait=18)
        elif what == 'cancel':
            before = len(list((P / 'archive').rglob('*.png')))
            def run():
                rs = [cancel_case('cancel-stop-%d' % i, .001) for i in range(5)] + [cancel_case('stop-cancel-%d' % i, .05) for i in range(3)]
                return rs
            rs = with_fixture('cancel', ['python3', str(P / 'qt_fixture.py'), '--rows', '600'], run)
            after = len(list((P / 'archive').rglob('*.png')))
            nxt = with_fixture('after-cancels', ['python3', str(P / 'qt_fixture.py')], lambda: p.capture('after-cancels', 60, 40000))
            (P / 'cancel-summary.json').write_text(json.dumps({'states': [r['final']['state'] for r in rs], 'failed': sum(r['final']['state'] == 'failed' for r in rs), 'cancelled': sum(r['final']['state'] == 'cancelled' for r in rs), 'imagesAdmitted': after - before, 'nextCapturePass': bool(nxt.get('pass'))}, indent=2))
            print((P / 'cancel-summary.json').read_text())
    except Exception:
        (P / (what + '.error')).write_text(traceback.format_exc()); traceback.print_exc()
    (P / (what + '.done')).write_text('done')
