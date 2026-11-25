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

LAB = Path.home() / 'work/x2064/lab'
os.environ['SF7'] = str(LAB)
sys.path.insert(0, str(Path.home() / 'work/scroll-session/lab/tools'))
import live7 as L  # noqa: E402
import rfb  # noqa: E402

DRIVER = os.environ['LAB_DRIVER']
HELPER = os.environ['LAB_HELPER']
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
        cmd = [DRIVER, '--helper', HELPER, '--rect', ','.join(map(str, rect)), '--out', str(self.stage),
               '--max-height', os.environ.get('LAB_MAX', '60000'), '--driver', 'putgd' if mode == 'auto' else 'user', '--stop-file', str(self.stop)]
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


TICK = os.sysconf('SC_CLK_TCK')


def ticks(pid):
    try:
        f = Path('/proc/%d/stat' % pid).read_text().rsplit(')', 1)[1].split()
        return int(f[11]) + int(f[12])
    except (OSError, IndexError, ValueError):
        return None


def status(pid, key):
    try:
        for line in Path('/proc/%d/status' % pid).read_text().splitlines():
            if line.startswith(key + ':'):
                return int(line.split()[1])
    except OSError:
        return None
    return None


class Meter:
    """CPU of the helper (putgd-record, the driver's child) and of Xorg, and
    the helper's resident memory, while the capture runs."""

    def __init__(self, driver):
        self.driver, self.helper, self.samples = driver, None, []
        self.xorg = next((int(p.name) for p in Path('/proc').iterdir() if p.name.isdigit() and (p / 'comm').exists()
                          and (p / 'comm').read_text().strip() == 'Xorg'), None)
        self.stop = False
        self.t = threading.Thread(target=self.loop, daemon=True)
        self.t.start()

    def find(self):
        for p in Path('/proc').iterdir():
            if not p.name.isdigit():
                continue
            try:
                st = (p / 'stat').read_text()
                if st.rsplit(')', 1)[1].split()[1] == str(self.driver) and 'putgd-record' in (p / 'comm').read_text():
                    return int(p.name)
            except (OSError, IndexError):
                pass
        return None

    def loop(self):
        while not self.stop:
            if self.helper is None:
                self.helper = self.find()
            if self.helper:
                h = ticks(self.helper)
                if h is None:
                    # A helper that left (a short-lived first one): the next one is the capture's.
                    if self.samples and self.samples[-1][5] == self.helper and len([x for x in self.samples if x[5] == self.helper]) > 8:
                        self.stop = True
                        break
                    self.samples = [x for x in self.samples if x[5] != self.helper]
                    self.helper = None
                    continue
                self.samples.append((time.time(), h, ticks(self.xorg) if self.xorg else None, status(self.helper, 'VmRSS'), status(self.helper, 'VmHWM'), self.helper))
            time.sleep(0.25)

    def done(self):
        self.stop = True
        self.t.join(2)
        s = self.samples
        if len(s) < 2:
            return None
        dt = s[-1][0] - s[0][0]
        out = {'seconds': round(dt, 2), 'helperCpuS': round((s[-1][1] - s[0][1]) / TICK, 2),
               'peakRssMiB': round(max(x[4] or 0 for x in s) / 1024, 1), 'meanRssMiB': round(sum(x[3] or 0 for x in s) / len(s) / 1024, 1)}
        out['helperCpuPct'] = round(100 * out['helperCpuS'] / dt, 1) if dt > 0 else None
        if s[0][2] is not None and s[-1][2] is not None:
            out['xorgCpuS'] = round((s[-1][2] - s[0][2]) / TICK, 2)
            out['xorgCpuPct'] = round(100 * out['xorgCpuS'] / dt, 1) if dt > 0 else None
        return out


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
        if os.environ.get('LAB_PACE') == 'brisk':
            wheel('w %d' % rng.choice([3, 4, 5, 6, 6, 8]))
            time.sleep(rng.uniform(0.8, 1.4) if rng.random() < 0.05 else rng.uniform(0.06, 0.2))
        else:
            wheel('w %d' % rng.choice([1, 2, 3, 3, 4, 5]))
            time.sleep(rng.uniform(1.2, 2.2) if rng.random() < 0.06 else rng.uniform(0.15, 0.45))
    d.stop.touch()


def desk(path):
    v = rfb.RFB(5900)
    v.screenshot(path)
    v.close()


def come_back(d, out, rect, wheel):
    """Auto-scroll handed the page back lost (#1515 round 2): what a person
    sees, scrolling back until the bar no longer says lost, and the bar's own
    Auto-scroll button pressed again."""
    note = {'handedAt': time.time()}
    time.sleep(1.5)
    desk(out / 'handback.png')
    note['handbackState'] = [e for e in d.events() if e.get('event') == 'progress'][-1]
    v = rfb.RFB(5900)
    v.pointer(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
    v.close()
    time.sleep(0.5)
    notches = 0
    while notches < 60:
        last = [e for e in d.events() if e.get('event') == 'progress'][-1]
        if last.get('state') != 'lost':
            break
        wheel('w -2')
        notches += 2
        time.sleep(0.9)
    time.sleep(1.0)
    note['scrolledBackNotches'] = notches
    note['foundState'] = [e for e in d.events() if e.get('event') == 'progress'][-1]
    desk(out / 'found.png')
    import re
    at = None
    for line in (out / 'helper.log').read_text(errors='replace').splitlines():
        m = re.search(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)', line)
        if m:
            x, y, w, h = map(int, m.groups())
            at = (x + w // 2, y + h // 2)
    note['button'] = at
    if at:
        v = rfb.RFB(5900)
        v.click(*at)
        v.close()
        note['pressedAt'] = time.time()
        time.sleep(3)
        desk(out / 'resumed.png')
        note['afterPress'] = [e for e in d.events() if e.get('event') == 'progress'][-1]
    return note


def run(kind, site, mode, wheel):
    name = f'{kind}-{site}-{mode}' + (('-' + os.environ['LAB_TAG']) if os.environ.get('LAB_TAG') else '')
    out = LAB / 'runs' / name
    if (out / 'result.json').exists():
        return
    if out.exists():
        out.rename(out.with_name(name + '-incomplete-%d' % int(time.time())))
    out.mkdir(parents=True)
    b, _ = L.connect()
    view = json.loads((LAB / 'viewport.json').read_text())
    url = os.environ.get('LAB_URL') or (PAGES[site][kind] if isinstance(PAGES[site], dict) else PAGES[site])
    if os.environ.get('LAB_NAV_JS') == '1':
        # As if typed into the address bar: no wait for a load event that a page
        # full of ads never sends (Al Jazeera in Firefox timed out three times).
        b.js('window.location.href = %s; return 0;' % json.dumps(url))
        time.sleep(15)
    else:
        b.navigate(url)
    time.sleep(6)
    L.wait_loaded(b, 25)
    b.js('window.scrollTo({top:0,behavior:"instant"});return 0;')
    time.sleep(1.5)
    before = L.wait_loaded(b, 15)
    rect = list(view['rect'])
    rect[2] = min(rect[2], int(round(before['clientWidth'] * before['dpr'])))
    rect[3] = min(rect[3], int(round(before['h'] * before['dpr'])))
    if os.environ.get('LAB_RECT'):
        # A region of our choosing, such as the whole screen (#1519: no room for the bar outside).
        rect = [int(v) for v in os.environ['LAB_RECT'].split(',')]
    env, _ = L.session_env()
    env.update(PUTGD_RECORD_DEBUG_LOG=str(out / 'helper.log'), PIPEWIRE_RUNTIME_DIR='/run/user/%d' % os.getuid())
    for k in ('PUTGD_LAB_PACE', 'PUTGD_SCROLL_WATCH'):
        if os.environ.get(k):
            env[k] = os.environ[k]
    result = {'name': name, 'site': site, 'url': url, 'mode': mode, 'browser': kind, 'rect': rect, 'before': before, 'viewport': view}
    start = time.time()
    d = Driver(rect, out, mode, env)
    meter = Meter(d.p.pid)
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
        person(b, d, wheel, int(os.environ.get('LAB_SEED', '1')))
    # Auto-scroll that handed the page back waits for a person; after 15 s
    # this one presses Done, as a person who saw it stop would.
    began = time.time()
    handed = None
    resumed = 0
    while d.running() and time.time() - began < 600:
        progress = [e for e in d.events() if e.get('event') == 'progress']
        if (mode == 'auto' and os.environ.get('LAB_RESUME') == '1' and not resumed and progress and progress[-1].get('driver') == 'user'
                and progress[-1].get('pausedBy') == 'lost'):
            resumed = 1
            result['resume'] = come_back(d, out, rect, wheel)
            continue
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
    result['meter'] = meter.done()
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
        if os.environ.get('LAB_NOREF') == '1':
            raise RuntimeError('no reference asked')
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
                      'skipped': c.get('framesSkipped'), 'foundAgain': c.get('foundAgain'), 'fps': (c.get('stats') or {}).get('framesPerSecond'),
                      'source': (c.get('stats') or {}).get('sourceRate'), 'meter': result['meter'], 'by': c.get('scrolledBy'), 'seconds': result['seconds'], 'failed': result['failed']}), flush=True)


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
