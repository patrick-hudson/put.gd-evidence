#!/usr/bin/env python3
"""Issue #1514 acceptance: a second input device takes the pointer during a
scrolling capture and clicks Stop.

Runs on the builder. Starts a capture of RECT through the running resident
(putgd-cli scroll.prepare + scroll.start), waits START s, then moves the
pointer through the desktop's wall VNC server (an independent input path, as a
real mouse) from the middle of the screen to STOP at about 600 px/s, one event
every 10 ms, and clicks there. Reports, from the helper's debug log:
  pausedMs   from the first VNC motion to the helper's "paused by pointer" line
  movesAfter pointer motions the helper sent after the first VNC motion
  stopped    the first click ended the capture as Stop (state done, endReason stopped)

trial.py --cli PATH --rect X,Y,W,H --stop X,Y (VNC pixels) --log HELPER_LOG
         [--vnc 5900] [--scale S (VNC pixels per logical pixel)] [--label TEXT] [--start 2.0]
"""
import argparse
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time


def recvn(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise RuntimeError('VNC server closed the connection')
        data += chunk
    return data


class Rfb:
    """The least of RFB 3.8 that sends pointer events: no auth, shared."""

    def __init__(self, port):
        self.sock = socket.create_connection(('127.0.0.1', port), timeout=10)
        recvn(self.sock, 12)
        self.sock.sendall(b'RFB 003.008\n')
        count = recvn(self.sock, 1)[0]
        types = recvn(self.sock, count)
        if 1 not in types:
            raise RuntimeError(f'VNC server offers no None security: {list(types)}')
        self.sock.sendall(bytes([1]))
        if struct.unpack('>I', recvn(self.sock, 4))[0] != 0:
            raise RuntimeError('VNC security failed')
        self.sock.sendall(bytes([1]))
        self.width, self.height = struct.unpack('>HH', recvn(self.sock, 4))
        recvn(self.sock, 16)
        recvn(self.sock, struct.unpack('>I', recvn(self.sock, 4))[0])

        # QEMU needs a pixel format and encoding negotiation before input.
        self.sock.sendall(struct.pack('>BxxxBBBBHHHBBBxxx', 0, 32, 24, 0, 1, 255, 255, 255, 16, 8, 0))
        self.sock.sendall(struct.pack('>BxHi', 2, 1, 0))

    def pointer(self, x, y, buttons=0):
        self.sock.sendall(struct.pack('>BBHH', 5, buttons, max(0, int(x)), max(0, int(y))))


def cli(path, method, params):
    out = subprocess.run([path, method, json.dumps(params)], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {'error': {'code': 'cli', 'message': out.stdout + out.stderr}}


def flat():
    # No pointer acceleration for the lab mouse, so its units are pixels.
    name = 'putgd-lab relative mouse'
    if os.environ.get('XDG_SESSION_TYPE') == 'x11':
        for values in (['0', '1', '0'], ['0', '1']):
            if subprocess.run(['xinput', 'set-prop', name, 'libinput Accel Profile Enabled', *values], capture_output=True).returncode == 0:
                break
        subprocess.run(['xinput', 'set-prop', name, 'libinput Accel Speed', '0'], capture_output=True)
        return
    if 'GNOME' in os.environ.get('XDG_CURRENT_DESKTOP', ''):
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.peripherals.mouse', 'accel-profile', 'flat'], check=True)
        return
    if 'Budgie' in os.environ.get('XDG_CURRENT_DESKTOP',''):
        return  # labwc XML accelProfile=flat and pointerSpeed=0 prepared and restored by this campaign
    if 'Hyprland' in os.environ.get('XDG_CURRENT_DESKTOP',''):
        subprocess.run(['hyprctl','eval','hl.config({input={accel_profile="flat",sensitivity=0}})'],check=True,stdout=subprocess.DEVNULL)
        return
    out = subprocess.run(['qdbus6', 'org.kde.KWin', '/org/kde/KWin/InputDevice', 'org.kde.KWin.InputDeviceManager.devicesSysNames'], capture_output=True, text=True).stdout.split()
    for sysname in out:
        path = f'/org/kde/KWin/InputDevice/{sysname}'
        got = subprocess.run(['busctl', '--user', 'get-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'name'], capture_output=True, text=True).stdout
        if name in got:
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAccelerationProfileFlat', 'b', 'true'], capture_output=True)
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAcceleration', 'd', '0'], capture_output=True)
            return


def now_ms():
    return time.monotonic() * 1000.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cli', required=True)
    ap.add_argument('--rect', required=True)
    ap.add_argument('--stop', required=True)
    ap.add_argument('--log', required=True)
    ap.add_argument('--vnc', type=int, default=5900)
    ap.add_argument('--label', default='')
    ap.add_argument('--start', type=float, default=2.0)
    ap.add_argument('--jitter', type=float, default=0.0, help='add a random 0..JITTER s to --start')
    ap.add_argument('--speed', type=float, default=600.0)
    ap.add_argument('--local-center', action='store_true', help='local initial uinput tablet placement; remaining motion uses relative device only')
    ap.add_argument('--native-center', action='store_true', help='Hyprland: initial placement through relative input using current compositor cursor position')
    ap.add_argument('--rel', action='store_true', help='move with a relative uinput mouse after a VNC jump to the middle')
    a = ap.parse_args()
    mouse = None
    if a.rel:
        mouse = subprocess.Popen(['sudo', '-n', 'python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'umouse.py')] + (['--with-tablet'] if a.local_center else []),
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if not mouse.stdout.readline().startswith('ready'):
            print(json.dumps({'label': a.label, 'error': 'no uinput mouse'}))
            return 1
        flat()
    rect = [int(v) for v in a.rect.split(',')]
    stop = [int(v) for v in a.stop.split(',')]
    offset = os.path.getsize(a.log) if os.path.exists(a.log) else 0
    if a.local_center:
        from geometry import output
        rfb=output()
    else: rfb = Rfb(a.vnc)
    prepared = cli(a.cli, 'scroll.prepare', {'rect': rect})
    if not prepared.get('ok'):
        print(json.dumps({'label': a.label, 'error': prepared.get('error')}))
        return 1
    sid = prepared['result']['id']
    started = cli(a.cli, 'scroll.start', {'id': sid})
    if not started.get('ok'):
        print(json.dumps({'label': a.label, 'id': sid, 'error': started.get('error')}))
        cli(a.cli, 'scroll.cancel', {'id': sid})
        return 1
    t_start = now_ms()
    import random
    time.sleep(a.start + random.uniform(0, a.jitter))
    sx, sy = rfb.width // 2, rfb.height // 2
    dist = ((stop[0] - sx) ** 2 + (stop[1] - sy) ** 2) ** 0.5
    steps = max(1, int(dist / (a.speed * 0.010)))
    t_first = None
    tick = now_ms()
    sent = [0.0, 0.0]
    for i in range(steps + 1):
        f = i / steps
        x, y = sx + (stop[0] - sx) * f, sy + (stop[1] - sy) * f
        if mouse and i > 0:
            dx, dy = round(x - sx - sent[0]), round(y - sy - sent[1])
            sent[0] += dx
            sent[1] += dy
            mouse.stdin.write(f'm {dx} {dy}\n')
            mouse.stdin.flush()
        elif mouse and a.local_center:
            mouse.stdin.write(f'a {sx} {sy} {rfb.width} {rfb.height}\n');mouse.stdin.flush()
        elif mouse and a.native_center:
            at = subprocess.check_output(['hyprctl','cursorpos'],text=True).strip().split(',')
            mouse.stdin.write(f'm {sx-int(at[0])} {sy-int(at[1])}\n');mouse.stdin.flush()
        else:
            rfb.pointer(x, y)
        if t_first is None:
            t_first = now_ms()
            if a.native_center: tick = t_first
        tick += 10
        delay = (tick - now_ms()) / 1000.0
        if delay > 0:
            time.sleep(delay)
    time.sleep(0.05)
    if mouse:
        mouse.stdin.write('d\n')
        mouse.stdin.flush()
        time.sleep(0.06)
        mouse.stdin.write('u\n')
        mouse.stdin.flush()
    else:
        rfb.pointer(stop[0], stop[1], 1)
        time.sleep(0.06)
        rfb.pointer(stop[0], stop[1], 0)
    t_click = now_ms()
    view = {}
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        view = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
        if view.get('state') in ('done', 'failed', 'cancelled'):
            break
        time.sleep(0.2)
    stopped = view.get('state') == 'done' and view.get('endReason') == 'stopped'
    ended_by_click = view.get('state') in ('done', 'failed', 'cancelled')
    if not ended_by_click:
        # The click did not end it: Stop through the session, then wait for the end.
        cli(a.cli, 'scroll.stop', {'id': sid})
        for _ in range(100):
            view = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
            if view.get('state') in ('done', 'failed', 'cancelled'):
                break
            time.sleep(0.3)
    if mouse:
        mouse.stdin.write('q\n')
        mouse.stdin.flush()
        mouse.wait(5)
    time.sleep(0.5)
    with open(a.log, 'rb') as f:
        f.seek(offset)
        text = f.read().decode('utf-8', 'replace')
    first_mod = t_first % 1000000
    paused_at = None
    moves_after = 0
    moves = 0
    for line in text.splitlines():
        m = re.search(r'scroll: paused by pointer at t=(\d+)', line)
        if m and paused_at is None:
            paused_at = int(m.group(1))
        m = re.search(r'scroll inject: t=(\d+) pointer -?\d+,-?\d+ sent', line)
        if m:
            moves += 1
            t = int(m.group(1))
            if t >= first_mod and t - first_mod < 600000:
                moves_after += 1
    paused_ms = None if paused_at is None else paused_at - first_mod
    print(json.dumps({'label': a.label, 'id': sid, 'pausedMs': paused_ms, 'movesAfter': moves_after, 'movesTotal': moves,
                      'stoppedByClick': stopped, 'state': view.get('state'), 'endReason': view.get('endReason'),
                      'height': view.get('height'), 'motionMs': round(t_click - t_first), 'startMs': round(t_first - t_start)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
