#!/usr/bin/env python3
"""One try of the pause by the mouse (#1515 acceptance row 6, PR #1548).

Same protocol as the acceptance's trial_relative.py (from r3-gnome trial.py):
a capture with auto-scroll from the start, then after START (+ random 0..JITTER) s
a real relative uinput mouse moves from wherever the pointer is to Done at about
600 px/s, one event every 10 ms, and clicks. No absolute pointer during the capture.

Reports, from the helper's debug log (PUTGD_RECORD_DEBUG_LOG):
  pausedMs        first relative motion -> "paused by pointer"
  injectsAfter    every "scroll inject: ... sent" line after the first motion
                  (wheel, pointer, rest, put-back), and how many were put-backs
  late            "the hand was seen N ms late" lines (put-back skipped)
  stoppedByClick  the first click ended the capture with its image (state done)
  cursorBeforeClick the compositor's pointer before the click (Hyprland, X11)

ptrial.py --cli CMD --rect X,Y,W,H --log HELPER_LOG --label L [--start 2] [--jitter 0]
          [--mouse 'python3 umouse.py' | 'sudo -n python3 umouse.py'] [--target X,Y]
"""
import argparse, json, os, random, re, shlex, subprocess, sys, time

DEVICE = 'putgd-lab relative mouse with wheel'


def cli(cmd, method, params):
    out = subprocess.run([*shlex.split(cmd), method, json.dumps(params)], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {'ok': False, 'error': {'code': 'cli', 'message': (out.stdout + out.stderr)[-400:]}}


def desktop():
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        return 'hyprland'
    if os.environ.get('XDG_SESSION_TYPE') == 'x11':
        return 'x11'
    return 'other'


def cursor():
    kind = desktop()
    try:
        if kind == 'hyprland':
            d = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], text=True))
            return [int(d['x']), int(d['y'])]
        if kind == 'x11':
            v = dict(x.split('=', 1) for x in subprocess.check_output(['xdotool', 'getmouselocation', '--shell'], text=True).splitlines() if '=' in x)
            return [int(v['X']), int(v['Y'])]
    except Exception:
        return None
    return None


def flat():
    kind = desktop()
    if kind == 'hyprland':
        # Set once for the run by the setup (saved and restored there).
        return
    if kind == 'x11':
        props = subprocess.check_output(['xinput', 'list-props', DEVICE], text=True)
        avail = re.search(r'libinput Accel Profiles Available \(\d+\):\s*([^\n]+)', props)
        n = len(avail.group(1).split(',')) if avail else 2
        subprocess.run(['xinput', 'set-prop', DEVICE, 'libinput Accel Profile Enabled', *map(str, [0, 1] + [0] * max(0, n - 2))], check=True)
        subprocess.run(['xinput', 'set-prop', DEVICE, 'libinput Accel Speed', '0'], check=True)
        return
    qdbus = next((q for q in ('qdbus6', 'qdbus-qt6', 'qdbus') if subprocess.run(['which', q], capture_output=True).returncode == 0), None)
    if not qdbus:
        return
    for sysname in subprocess.run([qdbus, 'org.kde.KWin', '/org/kde/KWin/InputDevice', 'org.kde.KWin.InputDeviceManager.devicesSysNames'], capture_output=True, text=True).stdout.split():
        path = f'/org/kde/KWin/InputDevice/{sysname}'
        name = subprocess.run(['busctl', '--user', 'get-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'name'], capture_output=True, text=True).stdout
        if DEVICE in name:
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAccelerationProfileFlat', 'b', 'true'], capture_output=True)
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAcceleration', 'd', '0'], capture_output=True)


def tail(path, offset):
    with open(path, 'rb') as f:
        f.seek(offset)
        return f.read().decode('utf-8', 'replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cli', required=True)
    ap.add_argument('--rect', required=True)
    ap.add_argument('--log', required=True)
    ap.add_argument('--label', default='')
    ap.add_argument('--start', type=float, default=2.0)
    ap.add_argument('--jitter', type=float, default=0.0)
    ap.add_argument('--speed', type=float, default=600.0)
    ap.add_argument('--mouse', default='sudo -n python3 ' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'umouse.py'))
    ap.add_argument('--target', help='where to click instead of Done (X,Y screen)')
    ap.add_argument('--from', dest='origin', help='where the pointer starts when it cannot be asked (X,Y screen)')
    a = ap.parse_args()
    rect = [int(v) for v in a.rect.split(',')]
    mouse = subprocess.Popen(shlex.split(a.mouse), stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if not mouse.stdout.readline().startswith('ready'):
        print(json.dumps({'label': a.label, 'error': 'no uinput mouse'}), flush=True)
        return 1

    def send(line):
        mouse.stdin.write(line + '\n')
        mouse.stdin.flush()

    try:
        time.sleep(0.3)
        flat()
        offset = os.path.getsize(a.log) if os.path.exists(a.log) else 0
        prepared = cli(a.cli, 'scroll.prepare', {'rect': rect, 'driver': 'putgd'})
        if not prepared.get('ok'):
            print(json.dumps({'label': a.label, 'error': prepared.get('error')}), flush=True)
            return 1
        sid = prepared['result']['id']
        started = cli(a.cli, 'scroll.start', {'id': sid})
        if not started.get('ok'):
            cli(a.cli, 'scroll.cancel', {'id': sid})
            print(json.dumps({'label': a.label, 'id': sid, 'error': started.get('error')}), flush=True)
            return 1
        t_start = time.monotonic() * 1000
        target = [int(v) for v in a.target.split(',')] if a.target else None
        for _ in range(100):
            if target:
                break
            m = list(re.finditer(r'scroll: bar at .*?done (-?\d+),(-?\d+) (\d+)x(\d+)', tail(a.log, offset)))
            if m:
                x, y, w, h = map(int, m[-1].groups())
                sh = list(re.finditer(r'the Shell put the bar at .*?; done (-?\d+),(-?\d+) (\d+)x(\d+)', tail(a.log, offset)))
                if sh:
                    x, y, w, h = map(int, sh[-1].groups())
                target = [x + w // 2, y + h // 2]
            else:
                time.sleep(0.05)
        if not target:
            cli(a.cli, 'scroll.cancel', {'id': sid})
            print(json.dumps({'label': a.label, 'id': sid, 'error': 'no bar in the helper log'}), flush=True)
            return 1
        due = t_start + (a.start + random.uniform(0, a.jitter)) * 1000
        time.sleep(max(0.0, (due - time.monotonic() * 1000) / 1000))
        # Where the pointer is: the compositor's answer, else the capture's last motion (its rest).
        start = cursor()
        if start is None and a.origin:
            start = [int(v) for v in a.origin.split(',')]
        if start is None:
            pts = list(re.finditer(r'scroll inject: t=\d+ pointer (-?\d+),(-?\d+) sent', tail(a.log, offset)))
            start = [rect[0] + int(pts[-1].group(1)), rect[1] + int(pts[-1].group(2))] if pts else [rect[0] + rect[2] // 2, rect[1] + rect[3] // 2]
        sx, sy = start
        dist = ((target[0] - sx) ** 2 + (target[1] - sy) ** 2) ** 0.5
        steps = max(1, int(dist / (a.speed * 0.010)))
        sent = [0, 0]
        t_first = None
        tick = time.monotonic() * 1000
        for i in range(1, steps + 1):
            f = i / steps
            dx = round(sx + (target[0] - sx) * f - sx - sent[0])
            dy = round(sy + (target[1] - sy) * f - sy - sent[1])
            sent[0] += dx
            sent[1] += dy
            if dx or dy:
                if t_first is None:
                    t_first = time.monotonic() * 1000
                send(f'm {dx} {dy}')
            tick += 10
            d = (tick - time.monotonic() * 1000) / 1000
            if d > 0:
                time.sleep(d)
        time.sleep(0.05)
        before_click = cursor()
        send('d')
        time.sleep(0.06)
        send('u')
        t_click = time.monotonic() * 1000
        view = {}
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            view = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
            if view.get('state') in ('done', 'failed', 'cancelled'):
                break
            time.sleep(0.2)
        clicked = view.get('state') == 'done'
        if view.get('state') not in ('done', 'failed', 'cancelled'):
            cli(a.cli, 'scroll.stop', {'id': sid})
            for _ in range(100):
                view = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
                if view.get('state') in ('done', 'failed', 'cancelled'):
                    break
                time.sleep(0.3)
    finally:
        try:
            send('q')
            mouse.wait(5)
        except Exception:
            pass
    time.sleep(0.5)
    text = tail(a.log, offset)
    first = int(t_first) % 1000000
    after = lambda t: (t - first) % 1000000 < 600000
    paused = None
    injects, late, seen = [], [], None
    for line in text.splitlines():
        m = re.search(r'paused by pointer at t=(\d+)', line)
        if m and paused is None:
            paused = ((int(m.group(1)) - first + 500000) % 1000000) - 500000
        m = re.search(r'scroll inject: t=(\d+) (.*) sent$', line)
        if m and after(int(m.group(1))):
            injects.append({'dt': (int(m.group(1)) - first) % 1000000, 'what': m.group(2)})
        m = re.search(r'the hand was seen (\d+) ms late', line)
        if m:
            late.append(int(m.group(1)))
        m = re.search(r'scroll: pointer at \S+ (on the watch|on the rest surface) \(([^)]*)\)', line)
        if m and seen is None:
            seen = m.group(1) + ': ' + m.group(2)
    putbacks = [i for i in injects if 'put back' in i['what']]
    others = [i for i in injects if 'put back' not in i['what']]
    log_dir = os.path.dirname(os.path.abspath(a.log))
    with open(os.path.join(log_dir, f'trial-{a.label}.log'), 'w') as f:
        f.write(text)
    print(json.dumps({'label': a.label, 'id': sid, 'stoppedByClick': clicked, 'pausedMs': paused, 'injectsAfter': len(others), 'putBacks': len(putbacks),
                      'injectLines': injects, 'lateMs': late, 'seenBy': seen, 'start': start, 'target': target, 'cursorBeforeClick': before_click,
                      'state': view.get('state'), 'endReason': view.get('endReason'), 'height': view.get('height'),
                      'startMs': round(t_first - t_start), 'motionMs': round(t_click - t_first)}), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
