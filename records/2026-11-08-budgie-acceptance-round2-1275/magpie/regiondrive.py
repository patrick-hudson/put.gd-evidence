import json, os, subprocess, time, pathlib
S = pathlib.Path(os.environ['S']); B = pathlib.Path(os.environ['BUILD'])
log = open(S / 'result.log', 'w')
def say(*a): print(*a, file=log, flush=True)
def cli(m, p=None, timeout=30):
    r = subprocess.run([str(B / 'putgd-cli'), m, json.dumps(p or {})], capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'raw': r.stdout, 'err': r.stderr}
def wait(c, s, step=0.2):
    end = time.time() + s
    while time.time() < end:
        v = c()
        if v: return v
        time.sleep(step)
POINTER = ['/w/src/tools/lab/wayland_pointer.py']
EW, EH = (int(v) for v in os.environ.get('EXTENT', '1920x1080').split('x'))
env = dict(os.environ, QT_QPA_PLATFORM='wayland')
fixture = subprocess.Popen([str(B / 'putgd-labwc-fixture')], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
say('compositor', os.environ.get('COMP'), 'extent', EW, EH)
say('fixture', fixture.stdout.readline().strip())
w = subprocess.run(['wayland-info'], capture_output=True, text=True).stdout
say('virtual pointer global', 'zwlr_virtual_pointer_manager_v1' in w, 'layer shell', 'zwlr_layer_shell_v1' in w)
res = subprocess.Popen([str(B / 'putgd'), '--background'], stdout=open(S / 'resident.log', 'w'), stderr=subprocess.STDOUT)
sock = pathlib.Path(os.environ['XDG_RUNTIME_DIR']) / 'putgd/session.sock'
say('socket', bool(wait(lambda: sock.exists(), 20))); time.sleep(2)
def patch(p):
    rev = cli('settings.get').get('result', {}).get('metadata', {}).get('acceptedRevision')
    return cli('settings.patch', {'patch': p, 'expectedRevision': rev}).get('ok')
say('patch', patch({'archive': {'keepUploads': True, 'root': str(S / 'archive')}, 'actions': {'region': {'destination': 'local'}, 'desktop': {'destination': 'local'}}}))
from PIL import Image
time.sleep(3)
say('minimize ui', subprocess.run(['wlrctl', 'toplevel', 'minimize', 'app_id:putgd-ui'], capture_output=True, text=True).returncode)
time.sleep(1)
cli('action.invoke', {'action': 'desktop'}, timeout=20); time.sleep(3)
desk = Image.open(sorted((S / 'archive').rglob('*.png'), key=lambda p: p.stat().st_mtime)[-1]).convert('RGB')
red = (200, 40, 40)
def clean(x, y, w=200, h=150):
    return all(desk.getpixel((xx, yy)) == red for xx in range(x - 4, x + w + 4, 4) for yy in range(y - 4, y + h + 4, 4))
spot = next(((x, y) for y in range(80, 560, 20) for x in range(80, 1060, 20) if clean(x, y)), None)
say('desktop', desk.size, 'clean spot', spot)
X, Y = spot
def helper_running():
    return subprocess.run(['pgrep', '-x', 'putgd-region'], capture_output=True).returncode == 0
def region(mode, drag, button='left'):
    say('mode', mode, patch({'preferences': {'regionSelectionMode': mode}}))
    time.sleep(1)
    before = {o['id'] for o in cli('operation.recent').get('result', {}).get('operations', [])}
    cli('action.invoke', {'action': 'region'}, timeout=10)
    say('helper up', bool(wait(helper_running, 10)))
    time.sleep(3.0)
    r = subprocess.run(['python3', '-I'] + POINTER + ['drag'] + [str(v) for v in drag] + ['--extent', str(EW), str(EH), '--button', button], capture_output=True, text=True)
    say('drag', r.returncode, r.stderr.strip()[:200])
    if button == 'right' or drag[0] == drag[2]:
        pass
    op = wait(lambda: next((o for o in cli('operation.recent').get('result', {}).get('operations', []) if o['id'] not in before and o.get('state') in ('completed', 'failed', 'cancelled')), None), 20)
    say('op', op and op.get('state'), op and json.dumps(op.get('error'))[:200])
    say('helper gone', bool(wait(lambda: not helper_running(), 10)))
    return op
for mode in ('live', 'screenshot_first'):
    op = region(mode, (X, Y, X + 200, Y + 150))
    pngs = sorted((S / 'archive').rglob('*.png'), key=lambda p: p.stat().st_mtime)
    if op and op.get('state') == 'completed' and pngs:
        im = Image.open(pngs[-1]).convert('RGB')
        colours = {c for _, c in im.getcolors(1 << 20)}
        exact = im.size == (200, 150) and colours == {red}
        say('result', mode, im.size, 'distinct colours', len(colours), sorted(colours)[:4], 'pixels', im.size[0] * im.size[1], 'EXACT' if exact else 'MISMATCH')
# Position: the fixture's white 64x64 square sits at the output's (0,0). A drag
# from (32,32) to (232,182) must show exactly a 32x32 white block at the crop's top-left.
for mode in ('live', 'screenshot_first'):
    op = region(mode, (32, 32, 232, 182))
    pngs = sorted((S / 'archive').rglob('*.png'), key=lambda p: p.stat().st_mtime)
    if op and op.get('state') == 'completed' and pngs:
        im = Image.open(pngs[-1]).convert('RGB')
        white = [(x, y) for y in range(im.size[1]) for x in range(im.size[0]) if im.getpixel((x, y)) == (255, 255, 255)]
        redn = sum(1 for y in range(im.size[1]) for x in range(im.size[0]) if im.getpixel((x, y)) == red)
        bbox = (min(x for x, _ in white), min(y for _, y in white), max(x for x, _ in white), max(y for _, y in white)) if white else None
        exact = im.size == (200, 150) and len(white) == 1024 and bbox == (0, 0, 31, 31) and redn == 30000 - 1024
        say('corner', mode, im.size, 'white', len(white), 'bbox', bbox, 'red', redn, 'EXACT' if exact else 'MISMATCH')
# Escape cancels: press via virtual keyboard is not available; right-click cancels the selector.
op = region('live', (X + 10, Y + 10, X + 50, Y + 50), button='right')
say('archive', sorted(str(p.relative_to(S)) for p in (S / 'archive').rglob('*.png')))
fixture.terminate(); cli('ui.quit'); res.wait(30); say('DONE')
