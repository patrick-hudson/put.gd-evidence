#!/usr/bin/env python3
"""Scrolling capture's new session (#1515) on real pages, both drivers, against
the browser's own full-page picture. Runs on aurora-amd in the desktop session,
with the baseline's browsers and browser control (scroll-baseline/tools/live7.py).

  sess.py BROWSER SITE[,SITE...] MODE[,MODE...]     MODE: user | auto

user: a relative mouse through /dev/uinput turns the wheel at a person's pace
(bursts, pauses, one way back up) to the end of the page, then Done.
auto: auto-scroll from the bar's start, left alone to the end.
Only windows opened here; local save only (the lab driver, no resident).
"""
import json, os, random, shutil, subprocess, sys, threading, time
from pathlib import Path

LAB = Path.home() / 'work/scroll-session/lab'
os.environ['SF7'] = str(LAB)
sys.path.insert(0, str(LAB / 'tools'))
import live7 as L  # noqa: E402
import rfb  # noqa: E402

BUILD = Path.home() / 'work/scroll-session/repo/build/dev'
# Cinnamon X11 (m74): no uinput for this user, so the wheel is XTest from this
# separate client (xdotool), which X11 applications take as any mouse's wheel.
X11 = os.environ.get('LAB_X11') == '1'
if X11:
    def x11_env():
        env = dict(os.environ)
        env.update(DISPLAY=':0', XAUTHORITY=str(Path.home() / '.Xauthority'), XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon',
                   DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/%d/bus' % os.getuid(), QT_QPA_PLATFORM='xcb')
        env.pop('WAYLAND_DISPLAY', None)
        return env, 'Cinnamon X11'
    L.session_env = x11_env
PAGES = {
    'search': {'chromium': 'https://www.google.com/search?q=codex+cli+fedora&cs=1', 'firefox': 'https://www.bing.com/search?q=codex+cli+fedora'},
    'guide': 'https://app.put.gd/userguide/',
    'wiki': 'https://en.wikipedia.org/wiki/Linux',
    'mdn': 'https://developer.mozilla.org/en-US/docs/Web/CSS/position',
    'github': 'https://github.com/patrick-hudson/put.gd-desktop/pull/1398',
    'python': 'https://docs.python.org/3/library/stdtypes.html',
    'hn': 'https://news.ycombinator.com/',
    'hnthread': 'https://news.ycombinator.com/item?id=50489641',
    'stackoverflow': 'https://stackoverflow.com/questions/11227809',
    'news': 'https://www.aljazeera.com/news/2026/11/14/un-says-25-seafarers-killed-in-around-hormuz-since-february',
}
POS = 'return [Math.round(scrollY), innerHeight, document.documentElement.scrollHeight];'


class Driver:
    """The lab driver: one capture through the production backend and helper."""

    def __init__(self, rect, out, mode, env):
        self.stage = out / 'stage'
        self.stage.mkdir(mode=0o700)
        self.stop = out / 'stop'
        cmd = [str(BUILD / 'test_scroll_capture_driver'), '--helper', str(BUILD / 'putgd-record'), '--rect', ','.join(map(str, rect)), '--out', str(self.stage),
               '--max-height', '60000', '--driver', 'putgd' if mode == 'auto' else 'user', '--stop-file', str(self.stop)]
        self.lines = []
        self.p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=open(out / 'driver.err', 'w'), text=True)
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.p.stdout:
            self.lines.append(line.rstrip('\n'))

    def events(self):
        out = []
        for line in list(self.lines):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
        return out

    def capturing(self):
        return any(e.get('prepare', {}).get('state') == 'capturing' for e in self.events())

    def running(self):
        return self.p.poll() is None


def person(b, d, wheel, seed):
    """Wheel bursts of 1 to 5 notches with short gaps, a few pauses, one way
    back up a little past the middle, to the end of the page; then Done."""
    rng = random.Random(seed)
    went_up = False
    at_end_since = None
    began = time.time()
    while d.running() and time.time() - began < 480:
        y, h, doc = b.js(POS)
        if y + h >= doc - 2:
            at_end_since = at_end_since or time.time()
            if time.time() - at_end_since > 2.5:
                break
            wheel('w 2')
            time.sleep(0.6)
            continue
        at_end_since = None
        # The bar says "Lost the page: Scroll back a little": a reader does that.
        progress = [e for e in d.events() if e.get('event') == 'progress']
        if progress and progress[-1].get('state') == 'lost':
            wheel('w -2')
            time.sleep(0.7)
            continue
        if not went_up and doc - h > 3000 and y > 0.45 * (doc - h):
            wheel('w -5')
            went_up = True
            time.sleep(1.2)
            continue
        wheel('w %d' % rng.choice([1, 2, 3, 3, 4, 5]))
        time.sleep(rng.uniform(1.2, 2.2) if rng.random() < 0.06 else rng.uniform(0.15, 0.45))
    d.stop.touch()


def run(kind, site, mode, wheel):
    name = f'{kind}-{site}-{mode}'
    out = LAB / 'runs' / name
    if (out / 'result.json').exists():
        return
    if out.exists():
        out.rename(out.with_name(name + '-incomplete-%d' % int(time.time())))
    out.mkdir(parents=True)
    b, _ = L.connect()
    view = json.loads((LAB / 'viewport.json').read_text())
    url = PAGES[site][kind] if isinstance(PAGES[site], dict) else PAGES[site]
    b.navigate(url)
    time.sleep(6)
    L.wait_loaded(b, 25)
    b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
    time.sleep(1.5)
    before = L.wait_loaded(b, 15)
    rect = list(view['rect'])
    rect[2] = min(rect[2], int(round(before['clientWidth'] * before['dpr'])))
    rect[3] = min(rect[3], int(round(before['h'] * before['dpr'])))
    env, _ = L.session_env()
    env.update(PUTGD_RECORD_DEBUG_LOG=str(out / 'helper.log'), PIPEWIRE_RUNTIME_DIR='/run/user/%d' % os.getuid())
    result = {'name': name, 'site': site, 'url': url, 'mode': mode, 'browser': kind, 'rect': rect, 'before': before, 'viewport': view}
    start = time.time()
    d = Driver(rect, out, mode, env)
    for _ in range(200):
        if d.capturing() or not d.running():
            break
        time.sleep(0.05)
    if mode == 'user' and d.running():
        # The pointer over the middle of the page, as a reader's is; then only the wheel.
        if X11:
            subprocess.run(['xdotool', 'mousemove', str(rect[0] + rect[2] // 2), str(rect[1] + rect[3] // 2)], env=env, check=True)
        else:
            v = rfb.RFB(5900)
            v.pointer(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
            v.close()
        time.sleep(0.6)
        person(b, d, wheel, hash(name) & 0xffff)
    # Auto-scroll that handed the page back waits for a person; after 15 s
    # this one presses Done, as a person who saw it stop would.
    began = time.time()
    handed = None
    while d.running() and time.time() - began < 600:
        progress = [e for e in d.events() if e.get('event') == 'progress']
        if mode == 'auto' and progress and progress[-1].get('driver') == 'user':
            handed = handed or time.time()
            if time.time() - handed > 15:
                result['handedBack'] = progress[-1].get('pausedBy')
                d.stop.touch()
                break
        else:
            handed = None
        time.sleep(0.5)
    try:
        d.p.wait(timeout=60 if d.stop.exists() else 1)
    except subprocess.TimeoutExpired:
        d.stop.touch()
        d.p.wait(timeout=60)
    result['seconds'] = round(time.time() - start, 2)
    events = d.events()
    (out / 'driver.log').write_text('\n'.join(d.lines))
    finished = next((e for e in events if e.get('event') == 'finished'), None)
    result['capture'] = finished
    result['failed'] = next((e for e in events if e.get('event') == 'failed'), None)
    if finished and Path(finished['path']).exists():
        shutil.copyfile(finished['path'], out / 'capture.png')
    for f in d.stage.iterdir():
        f.unlink()
    d.stage.rmdir()
    result['after'] = b.js(L.INFO)
    # The browser's own full-page picture at its top, and what the page keeps in place.
    try:
        b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
        time.sleep(2.0)
        pinned = b.js('''const r=[];for(const e of document.querySelectorAll('*')){const s=getComputedStyle(e);if(s.position!=='sticky'&&s.position!=='fixed')continue;
          if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0)continue;const q=e.getBoundingClientRect();if(q.width<1||q.height<1)continue;
          r.push({rect:[Math.round(q.x),Math.round(q.y),Math.round(q.width),Math.round(q.height)],position:s.position,what:(e.tagName+'.'+String(e.className||'')).slice(0,70)});}
          return {vw:innerWidth,vh:innerHeight,list:r.slice(0,80)};''')
        (out / 'pinned.json').write_text(json.dumps([{'position': {'y': 0}, 'elements': pinned['list']}], indent=1))
        b.shot_full(out / 'reference.png')
    except Exception as e:
        result['referenceError'] = str(e)
    (out / 'result.json').write_text(json.dumps(result, indent=1))
    c = finished or {}
    print(json.dumps({'name': name, 'end': c.get('endReason'), 'height': c.get('height'), 'doc': result['after']['docHeight'], 'placed': c.get('framesPlaced'),
                      'skipped': c.get('framesSkipped'), 'by': c.get('scrolledBy'), 'seconds': result['seconds'], 'failed': result['failed']}), flush=True)


def main():
    kind, sites, modes = sys.argv[1], sys.argv[2].split(','), sys.argv[3].split(',')
    if X11:
        env, _ = L.session_env()
        mouse = None

        def wheel(line):
            n = int(line.split()[1])
            subprocess.run(['xdotool', 'click', '--repeat', str(abs(n)), '--delay', '12', '5' if n > 0 else '4'], env=env, check=True)
    else:
        mouse = subprocess.Popen([sys.executable, str(LAB / 'umouse.py')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        assert mouse.stdout.readline().startswith('ready')

        def wheel(line):
            mouse.stdin.write(line + '\n')
            mouse.stdin.flush()

    def fresh():
        # A fresh browser per page: Chrome for Testing's renderer crashes now and
        # then (SIGSEGV in its seccomp sandbox), and its remote protocol hangs after.
        pid = LAB / 'browser.pid'
        if pid.exists() and Path('/proc/' + pid.read_text().strip()).exists():
            L.browser_stop()
        stale = LAB / ('profile-' + kind)
        if stale.exists():
            stale.rename(LAB / ('profile-%s-old-%d' % (kind, int(time.time() * 1000))))  # set aside, never deleted here
        L.browser_start(kind)

    try:
        for site in sites:
            for attempt in (1, 2):
                fresh()
                failed = False
                for mode in modes:
                    try:
                        run(kind, site, mode, wheel)
                    except Exception as e:
                        failed = True
                        print(json.dumps({'name': f'{kind}-{site}-{mode}', 'attempt': attempt, 'error': repr(e)}), flush=True)
                        break
                if not failed:
                    break
        L.browser_stop()
    finally:
        if mouse:
            wheel('q')
            mouse.wait(5)


if __name__ == '__main__':
    main()
