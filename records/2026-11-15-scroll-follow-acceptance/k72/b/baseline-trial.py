#!/usr/bin/env python3
"""Issue #1531 (from #1514's driver, record 2026-11-14-scroll-pointer-release-1514): a second input device takes the pointer during a
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
import shutil
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
        port=int(os.environ.get('SF7_VNC',str(port)))
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

    def pointer(self, x, y, buttons=0):
        self.sock.sendall(struct.pack('>BBHH', 5, buttons, max(0, int(x)), max(0, int(y))))


def cli(path, method, params):
    out = subprocess.run([path, method, json.dumps(params)], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {'error': {'code': 'cli', 'message': out.stdout + out.stderr}}


def x11_profile():
    text=subprocess.check_output(['xinput','list-props','putgd-lab relative mouse with wheel'],text=True)
    m=re.search(r'libinput Accel Profile Enabled \(\d+\):\s*([^\n]+)',text)
    if not m:raise RuntimeError('no libinput acceleration profile for the lab mouse')
    return [int(v.strip()) for v in m.group(1).split(',')]


def x11_bar(logtext):
    bars=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',logtext))
    if not bars:raise RuntimeError('no bar rectangle')
    expected=list(map(int,bars[-1].groups()))
    pids=subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.split()
    for pid in pids:
        ids=subprocess.run(['xdotool','search','--onlyvisible','--pid',pid],capture_output=True,text=True).stdout.split()
        for wid in ids:
            out=subprocess.run(['xwininfo','-id',wid],capture_output=True,text=True).stdout
            def n(label):
                m=re.search(label+r':\s*(-?\d+)',out)
                return int(m.group(1)) if m else None
            rect=[n('Absolute upper-left X'),n('Absolute upper-left Y'),n('Width'),n('Height')]
            if rect[2:]==expected[2:] and 'IsViewable' in out:return expected,rect,wid
    raise RuntimeError('cannot locate the visible bar in X11')


def flat():
    # No pointer acceleration for the lab mouse, so its units are pixels.
    name = 'putgd-lab relative mouse with wheel'
    if os.environ.get('XDG_CURRENT_DESKTOP', '').upper().endswith('GNOME'):
        # Set for all mice by the run script (saved and restored there).
        return
    if os.environ.get('XDG_SESSION_TYPE') == 'x11':
        values=x11_profile();props=subprocess.check_output(['xinput','list-props',name],text=True)
        available=re.search(r'libinput Accel Profiles Available \(\d+\):\s*([^\n]+)',props)
        if not available:raise RuntimeError('no available libinput profile vector')
        count=len(available.group(1).split(','));wanted=[0,1]+[0]*max(0,count-2)
        if values!=wanted:subprocess.run(['xinput','set-prop',name,'libinput Accel Profile Enabled',*map(str,wanted)],check=True)
        subprocess.run(['xinput','set-prop',name,'libinput Accel Speed','0'],check=True)
        for _ in range(20):
            values=x11_profile()
            if values==wanted:return values
            time.sleep(.05)
        raise RuntimeError('the lab mouse did not retain flat acceleration')
    out = subprocess.run([shutil.which('qdbus-qt6') or shutil.which('qdbus6') or 'qdbus', 'org.kde.KWin', '/org/kde/KWin/InputDevice', 'org.kde.KWin.InputDeviceManager.devicesSysNames'], capture_output=True, text=True).stdout.split()
    for sysname in out:
        path = f'/org/kde/KWin/InputDevice/{sysname}'
        got = subprocess.run(['busctl', '--user', 'get-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'name'], capture_output=True, text=True).stdout
        if name in got:
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAccelerationProfileFlat', 'b', 'true'], capture_output=True)
            subprocess.run(['busctl', '--user', 'set-property', 'org.kde.KWin', path, 'org.kde.KWin.InputDevice', 'pointerAcceleration', 'd', '0'], capture_output=True)
            return


def native_pointer():
    if os.environ.get('XDG_CURRENT_DESKTOP','').upper().endswith('KDE'):
        global _kwin_witness
        if '_kwin_witness'not in globals():
            import importlib.util
            from pathlib import Path
            spec=importlib.util.spec_from_file_location('kwin_witness',Path(__file__).with_name('kwin-pointer-witness.py'));_kwin_witness=importlib.util.module_from_spec(spec);spec.loader.exec_module(_kwin_witness)
        return _kwin_witness.get()
    # Independent, read-only Shell observer; no production signal/input hooks.
    global _pointer_bus
    from gi.repository import Gio,GLib
    if '_pointer_bus' not in globals():_pointer_bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    value=_pointer_bus.call_sync('org.gnome.Shell','/org/putgd/PointerWitness','org.putgd.PointerWitness','Get',None,GLib.VariantType('(s)'),Gio.DBusCallFlags.NONE,1000,None).unpack()[0]
    v=json.loads(value);return [v['x'],v['y']]

def now_ms():
    return time.monotonic() * 1000.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cli', required=True)
    ap.add_argument('--driver', choices=['user','putgd'], default='putgd')
    ap.add_argument('--rect', required=True)
    ap.add_argument('--stop', required=True)
    ap.add_argument('--log', required=True)
    ap.add_argument('--vnc', type=int, default=5900)
    ap.add_argument('--label', default='')
    ap.add_argument('--start', type=float, default=2.0)
    ap.add_argument('--jitter', type=float, default=0.0, help='add a random 0..JITTER s to --start')
    ap.add_argument('--speed', type=float, default=600.0)
    ap.add_argument('--rel', action='store_true', help='move with a relative uinput mouse after a VNC jump to the middle')
    ap.add_argument('--scale', type=float, default=1.0, help='VNC pixels per logical pixel')
    a = ap.parse_args()
    mouse = None
    if a.rel:
        mouse = subprocess.Popen(['sudo', '-n', 'python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'umouse.py')],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if not mouse.stdout.readline().startswith('ready'):
            print(json.dumps({'label': a.label, 'error': 'no uinput mouse'}))
            return 1
        try:flat()
        except BaseException:
            mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
            raise
    rect = [int(v) for v in a.rect.split(',')]
    stop = [int(v) for v in a.stop.split(',')] if a.stop != 'auto' else None
    offset = os.path.getsize(a.log) if os.path.exists(a.log) else 0
    rfb = Rfb(a.vnc)
    # Auto-scroll from the start: the pause is what is tried (#1515's capture waits for the user otherwise).
    
    if mouse:
        rfb.pointer(rfb.width//2,rfb.height//2) # before prepare/start only
        time.sleep(.1)
    if mouse and os.environ.get('SFA_NATIVE_POINTER')=='1':native_pointer() # warm connection before capture
    prepared = cli(a.cli, 'scroll.prepare', {'rect': rect, 'driver': a.driver})
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
    if a.stop == 'auto':
        # Done, where the Shell put the bar (the helper's debug log, #1531 lab line).
        stop = None
        for _ in range(60):
            with open(a.log, 'rb') as f:
                f.seek(offset)
                for line in f.read().decode('utf-8', 'replace').splitlines():
                    m = re.search(r'the Shell put the bar at .*; done (-?\d+),(-?\d+) (\d+)x(\d+)', line)
                    if m:
                        x, y, w, h = map(int, m.groups())
                        stop = [round((x + w / 2) * a.scale), round((y + h / 2) * a.scale)]
            if stop:
                break
            time.sleep(0.05)
        if not stop:
            print(json.dumps({'label': a.label, 'id': sid, 'error': 'no bar position in the helper log'}))
            cli(a.cli, 'scroll.cancel', {'id': sid})
            return 1
    import random
    due=t_start+(a.start+random.uniform(0,a.jitter))*1000
    bar_screen=None;profile_before=None
    if mouse and os.environ.get('XDG_SESSION_TYPE')=='x11':
        time.sleep(max(0,(due-now_ms()-400)/1000))
        with open(a.log,'rb') as f:
            f.seek(offset);bar_text=f.read().decode('utf-8','replace')
        profile_before=x11_profile()
        available=re.search(r'libinput Accel Profiles Available \(\d+\):\s*([^\n]+)',subprocess.check_output(['xinput','list-props','putgd-lab relative mouse with wheel'],text=True))
        expected=[0,1]+[0]*(len(available.group(1).split(','))-2)
        if profile_before!=expected:
            cli(a.cli,'scroll.cancel',{'id':sid});mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
            raise RuntimeError('lab mouse acceleration changed before motion')
        before_rect,bar_screen,wid=x11_bar(bar_text)
        stop=[stop[0]+bar_screen[0]-before_rect[0],stop[1]+bar_screen[1]-before_rect[1]]
    time.sleep(max(0,(due-now_ms())/1000))
    sx, sy = rfb.width // 2, rfb.height // 2
    if mouse:
        # Start from the helper's last requested position. Never reposition with
        # an absolute VNC pointer during an active capture: that pauses first.
        with open(a.log, 'rb') as f:
            f.seek(offset)
            before_motion=f.read().decode('utf-8','replace')
        points=list(re.finditer(r'scroll inject: t=\d+ pointer (-?\d+),(-?\d+) sent',before_motion))
        if not points and a.driver=='putgd':
            raise RuntimeError('no injected pointer position before relative motion')
        if points:
            px,py=map(int,points[-1].groups())
            sx,sy=round((rect[0]+px)*a.scale),round((rect[1]+py)*a.scale)
    start_estimate=[sx,sy]
    t_first=None;first_vector=None
    if mouse and (os.environ.get('XDG_SESSION_TYPE')=='x11' or os.environ.get('SFA_NATIVE_POINTER')=='1'):
        # Make the first real relative motion before sampling its resulting
        # position. A capture visit before this marker cannot stale the origin.
        first_vector=[6 if stop[0]>=sx else -6,0]
        t_first=now_ms();mouse.stdin.write(f'm {first_vector[0]} 0\n');mouse.stdin.flush();time.sleep(.01)
        if os.environ.get('SFA_NATIVE_POINTER')=='1':sx,sy=native_pointer()
        else:
            actual=dict(x.split('=',1) for x in subprocess.check_output(['xdotool','getmouselocation','--shell'],text=True).splitlines() if '=' in x)
            sx,sy=int(actual['X']),int(actual['Y'])
    dist = ((stop[0] - sx) ** 2 + (stop[1] - sy) ** 2) ** 0.5
    steps = max(1, int(dist / (a.speed * 0.010)))
    tick = now_ms()
    sent = [0.0, 0.0]
    for i in range(steps + 1):
        f = i / steps
        x, y = sx + (stop[0] - sx) * f, sy + (stop[1] - sy) * f
        if mouse:
            dx, dy = round(x - sx - sent[0]), round(y - sy - sent[1])
            sent[0] += dx
            sent[1] += dy
            if t_first is None and (dx or dy):t_first=now_ms()
            mouse.stdin.write(f'm {dx} {dy}\n')
            mouse.stdin.flush()
        else:
            rfb.pointer(x, y)
        if t_first is None and not mouse:
            t_first = now_ms()
        tick += 10
        delay = (tick - now_ms()) / 1000.0
        if delay > 0:
            time.sleep(delay)
    time.sleep(0.05)
    cursor_after=None;bar_after=None
    if mouse and os.environ.get('SFA_NATIVE_POINTER')=='1':cursor_after=native_pointer()
    if mouse and os.environ.get('XDG_SESSION_TYPE')=='x11':
        actual=dict(x.split('=',1) for x in subprocess.check_output(['xdotool','getmouselocation','--shell'],text=True).splitlines() if '=' in x)
        cursor_after=[int(actual['X']),int(actual['Y'])]

    before_click=cli(a.cli,'scroll.inspect',{'id':sid}).get('result',{})
    with open(os.path.join(os.path.dirname(a.log),'before-click.jsonl'),'a') as proof:proof.write(json.dumps({'label':a.label,'id':sid,'beforeClick':before_click})+'\n')
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
    # Done keeps the image: state done, whatever the end reason says (#1515: done, lost_track, ...).
    stopped = view.get('state') == 'done'
    ended_by_click = view.get('state') in ('done', 'failed', 'cancelled')
    if not ended_by_click:
        try:
            import rfb as shot_rfb
            from pathlib import Path
            v=shot_rfb.RFB(a.vnc);v.screenshot(Path(a.log).parent/('click-miss-'+a.label+'.png'));v.close()
        except Exception:pass
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
    put_back = 0
    shell_watch = False
    seen_by = None
    for line in text.splitlines():
        if 'pointer put back' in line:
            put_back += 1
        if 'the Shell watches the pointer' in line:
            shell_watch = True
        m = re.search(r'scroll: pointer at -?[\d.]+,-?[\d.]+ (on the watch|on the rest surface) \(([^)]*)\)', line)
        if m and seen_by is None:
            seen_by = m.group(1) + ': ' + m.group(2)
        m = re.search(r'paused by pointer at t=(\d+)', line)
        if m and paused_at is None:
            paused_at = int(m.group(1))
        m = re.search(r'scroll inject: t=(\d+) pointer -?\d+,-?\d+ sent', line)
        if m:
            moves += 1
            t = int(m.group(1))
            if (t-first_mod)%1000000 < 600000:
                moves_after += 1
    pause_raw = None if paused_at is None else ((paused_at-first_mod+500000)%1000000)-500000
    paused_ms = None if pause_raw is None else max(0.0,pause_raw)
    injections_after=[]
    for line in text.splitlines():
        m=re.search(r'scroll inject: t=(\d+) .*sent',line)
        if m and (int(m.group(1))-first_mod)%1000000<600000:
            injections_after.append(line)
    from pathlib import Path
    (Path(a.log).parent/('trial-'+a.label+'.log')).write_text(text)
    print(json.dumps({'label': a.label, 'relativeOnly': bool(mouse), 'firstMotionVector':first_vector, 'originSampledAfterFirstMotion':first_vector is not None, 'startPoint': [sx,sy], 'injectedStartEstimate': start_estimate, 'barScreenRect':bar_screen, 'flatProfileBeforeMotion':profile_before, 'cursorBeforeClick':cursor_after, 'barScreenAfterMotion':bar_after, 'target': stop, 'id': sid, 'pausedMs': paused_ms, 'pauseRawMs': pause_raw, 'clockResolutionMs': 1, 'movesAfter': moves_after, 'injectionsAfter': injections_after, 'movesTotal': moves,
                      'stoppedByClick': stopped, 'putBack': put_back, 'shellWatch': shell_watch, 'seenBy': seen_by, 'state': view.get('state'), 'endReason': view.get('endReason'),
                      'height': view.get('height'), 'motionMs': round(t_click - t_first), 'startMs': round(t_first - t_start)}),flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
