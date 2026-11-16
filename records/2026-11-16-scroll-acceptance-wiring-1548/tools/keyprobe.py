#!/usr/bin/env python3
"""Do trusted keys reach the page during a scrolling capture? (PR #1548, item 5)

keyprobe.py ROOT LABEL DRIVER [--click-bar]
A local page (served here on 127.0.0.1:8765) reports every keydown, focus and blur, and
its scroll position, to this server, which writes them to ROOT/LABEL-keys.jsonl. A fresh
Firefox opens it; a uinput keyboard (sudo -n) presses End and Home before, End, Ctrl+End
and Home during a capture of 240,200 1440x820 (DRIVER user or putgd), and End after.
--click-bar: during the capture, a uinput mouse also clicks the bar's label (Mutter
focuses a window it is clicked on), then End and Home again. Last, Done is clicked: the
capture must end with its image (a click on Done stays a click).
"""
import http.server, json, os, re, shlex, socketserver, subprocess, sys, threading, time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
label, driver = sys.argv[2], sys.argv[3]
click_bar = '--click-bar' in sys.argv
here = Path(__file__).resolve().parent
env = json.loads((root / 'env.json').read_text())
os.environ.update(env)
cli = json.loads((root / 'cli.json').read_text())
events = root / f'{label}-keys.jsonl'
marks = []

PAGE = '''<!doctype html><meta charset="utf-8"><title>keys</title>
<style>body{font:18px/1.5 sans-serif;margin:40px}#k{position:fixed;right:10px;top:10px;background:#ffd;padding:6px;font:14px monospace}</style>
<div id="k">no key</div>
''' + '\n'.join(f'<p>Paragraph {i}: ' + ' '.join(f'word{(i * 7 + j) % 97}' for j in range(10 + (i * 13) % 40)) + '</p>' for i in range(400)) + '''
<script>
const send=(o)=>{o.y=Math.round(scrollY);o.focus=document.hasFocus();o.t=Date.now();navigator.sendBeacon('/e',JSON.stringify(o));};
addEventListener('keydown',e=>{document.getElementById('k').textContent=e.key+' '+Math.round(scrollY);send({type:'keydown',key:e.key,ctrl:e.ctrlKey,trusted:e.isTrusted});});
addEventListener('focus',()=>send({type:'focus'}));addEventListener('blur',()=>send({type:'blur'}));
addEventListener('scroll',()=>{clearTimeout(window.__s);window.__s=setTimeout(()=>send({type:'scroll'}),150);});
send({type:'load'});
</script>'''


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGE.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(n) or b'{}')
        data['mark'] = marks[-1] if marks else None
        with events.open('a') as f:
            f.write(json.dumps(data) + '\n')
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(('127.0.0.1', 8765), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()


def rpc(m, p=None):
    r = subprocess.run([*cli, m, json.dumps(p or {})], capture_output=True, text=True, timeout=100)
    o = json.loads(r.stdout)
    if not o.get('ok'):
        raise RuntimeError(json.dumps(o))
    return o['result']


def mark(m):
    marks.append(m)
    print('mark', m, flush=True)


kb = subprocess.Popen(['sudo', '-n', 'python3', str(here / 'ukey.py')], stdin=subprocess.PIPE, text=True)
time.sleep(1.5)


def key(name, *codes):
    mark(name)
    kb.stdin.write(' '.join(map(str, codes)) + '\n')
    kb.stdin.flush()
    time.sleep(1.2)


prof = root / f'ff-profile-{label}'
prof.mkdir(parents=True, exist_ok=True)
(prof / 'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.aboutwelcome.enabled", false);\nuser_pref("datareporting.policy.dataSubmissionEnabled", false);\n')
ff = subprocess.Popen([os.environ.get('FF', 'firefox'), '--new-instance', '--no-remote', '--profile', str(prof), 'http://127.0.0.1:8765/'],
                      env=dict(os.environ, MOZ_DBUS_REMOTE='0'), stdout=open(root / 'firefox.log', 'w'), stderr=subprocess.STDOUT)
sid = None
result = {}
try:
    time.sleep(10)
    key('before-End', 107)
    key('before-Home', 102)
    offset = (root / 'helper.log').stat().st_size if (root / 'helper.log').exists() else 0
    mark('capture-start')
    sid = rpc('scroll.prepare', {'rect': [240, 200, 1440, 820], 'driver': driver})['id']
    rpc('scroll.start', {'id': sid})
    time.sleep(2)
    key('during-End', 107)
    key('during-CtrlEnd', 29, 107)
    key('during-Home', 102)
    text = (root / 'helper.log').read_bytes()[offset:].decode('utf-8', 'replace')
    m = list(re.finditer(r'the Shell put the bar at (-?\d+),(-?\d+) (\d+)x(\d+); done (-?\d+),(-?\d+) (\d+)x(\d+)', text))
    bar = list(map(int, m[-1].groups())) if m else None
    result['bar'] = bar
    if click_bar and bar:
        mouse = subprocess.Popen(['sudo', '-n', 'python3', str(here / 'umouse.py')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        assert mouse.stdout.readline().startswith('ready')
        time.sleep(0.5)
        # Where the pointer is cannot be asked on GNOME: drive it to the bottom-left corner first
        # (the top-left one opens Activities). The screen is 1920x1080.
        for _ in range(4):
            mouse.stdin.write('m -1000 1000\n')
            mouse.stdin.flush()
            time.sleep(0.05)
        label_point = [bar[0] + 60, bar[1] + bar[3] // 2]
        done_point = [bar[4] + bar[6] // 2, bar[5] + bar[7] // 2]
        mark('click-bar-label')
        mouse.stdin.write(f'm {label_point[0]} {label_point[1] - 1079}\nd\n')
        mouse.stdin.flush()
        time.sleep(0.15)
        mouse.stdin.write('u\n')
        mouse.stdin.flush()
        time.sleep(0.8)
        key('after-click-End', 107)
        key('after-click-Home', 102)
        mark('click-done')
        mouse.stdin.write(f'm {done_point[0] - label_point[0]} {done_point[1] - label_point[1]}\nd\n')
        mouse.stdin.flush()
        time.sleep(0.15)
        mouse.stdin.write('u\nq\n')
        mouse.stdin.flush()
        mouse.wait(5)
        time.sleep(3)
    v = rpc('scroll.inspect', {'id': sid})
    result['inspect'] = v
    if v.get('state') in ('capturing', 'ready', 'preparing'):
        rpc('scroll.cancel', {'id': sid})
    sid = None
    time.sleep(1)
    key('after-End', 107)
    (root / f'{label}-helper.log').write_text((root / 'helper.log').read_bytes()[offset:].decode('utf-8', 'replace'))
finally:
    if sid:
        try:
            rpc('scroll.cancel', {'id': sid})
        except Exception:
            pass
    kb.stdin.write('q\n')
    kb.stdin.flush()
    kb.wait(5)
    ff.terminate()
    ff.wait(10)
    srv.shutdown()
rows = [json.loads(l) for l in events.read_text().splitlines()] if events.exists() else []
summary = {}
for r in rows:
    if r.get('type') == 'keydown':
        summary.setdefault(r['mark'], []).append({'key': r['key'], 'ctrl': r['ctrl'], 'y': r['y'], 'focus': r['focus']})
result['keys'] = summary
result['blurFocus'] = [(r['type'], r['mark']) for r in rows if r.get('type') in ('blur', 'focus')]
(root / f'{label}-result.json').write_text(json.dumps(result, indent=1))
print(json.dumps(result)[:3000])
