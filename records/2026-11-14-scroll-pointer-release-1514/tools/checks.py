#!/usr/bin/env python3
"""Issue #1514 hand checks, driven through the wall VNC server.

checks.py equal   --cli PATH --rect R --resume X,Y [--pause-after S]
    An unpaused capture of page.html, then one paused by the mouse halfway
    and resumed with the bar's Resume: both PNGs must be the same.
checks.py stoptop --cli PATH --rect R --stop X,Y
    The page at its end; Stop on the way to the top keeps the viewport.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trial import Rfb, cli  # noqa: E402

LAB = os.path.expanduser('~/work/scroll-1514-lab')


def open_page(anchor=''):
    subprocess.run(['firefox', '--profile', f'{LAB}/ff', f'file://{LAB}/page.html{anchor}'], capture_output=True)
    time.sleep(5)


def wait_end(c, sid, limit=240):
    deadline = time.monotonic() + limit
    view = {}
    while time.monotonic() < deadline:
        view = cli(c, 'scroll.inspect', {'id': sid}).get('result', {})
        if view.get('state') in ('done', 'failed', 'cancelled'):
            return view
        time.sleep(0.3)
    return view


def start(c, rect):
    sid = cli(c, 'scroll.prepare', {'rect': rect})['result']['id']
    cli(c, 'scroll.start', {'id': sid})
    return sid


def glide(rfb, frm, to, speed=600.0):
    dist = ((to[0] - frm[0]) ** 2 + (to[1] - frm[1]) ** 2) ** 0.5
    steps = max(1, int(dist / (speed * 0.01)))
    for i in range(steps + 1):
        f = i / steps
        rfb.pointer(frm[0] + (to[0] - frm[0]) * f, frm[1] + (to[1] - frm[1]) * f)
        time.sleep(0.01)


def click(rfb, at):
    rfb.pointer(at[0], at[1], 1)
    time.sleep(0.06)
    rfb.pointer(at[0], at[1], 0)


def summary(view):
    r = view.get('result', {})
    return {k: view.get(k) for k in ('state', 'endReason', 'height', 'topReached', 'note')} | {'sha256': r.get('sha256'), 'bytes': r.get('bytes')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode')
    ap.add_argument('--cli', required=True)
    ap.add_argument('--rect', required=True)
    ap.add_argument('--resume')
    ap.add_argument('--stop')
    ap.add_argument('--pause-after', type=float, default=3.5)
    a = ap.parse_args()
    rect = [int(v) for v in a.rect.split(',')]
    rfb = Rfb(5900)
    middle = (rfb.width // 2, rfb.height // 2)
    if a.mode == 'equal':
        open_page()
        plain = summary(wait_end(a.cli, start(a.cli, rect)))
        open_page()
        sid = start(a.cli, rect)
        time.sleep(a.pause_after)
        resume = [int(v) for v in a.resume.split(',')]
        glide(rfb, middle, resume)
        time.sleep(0.3)
        paused = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
        time.sleep(2.0)
        click(rfb, resume)
        paused_view = {k: paused.get(k) for k in ('state', 'paused', 'pausedBy', 'height')}
        resumed = summary(wait_end(a.cli, sid))
        print(json.dumps({'mode': 'equal', 'plain': plain, 'whilePaused': paused_view, 'resumed': resumed,
                          'same': plain['sha256'] is not None and plain['sha256'] == resumed['sha256']}))
    elif a.mode == 'stoptop':
        open_page('#end')
        sid = start(a.cli, rect)
        time.sleep(1.0)
        stop = [int(v) for v in a.stop.split(',')]
        glide(rfb, middle, stop)
        time.sleep(0.05)
        at = cli(a.cli, 'scroll.inspect', {'id': sid}).get('result', {})
        click(rfb, stop)
        view = wait_end(a.cli, sid, 30)
        print(json.dumps({'mode': 'stoptop', 'beforeClick': {k: at.get(k) for k in ('state', 'paused', 'pausedBy', 'height')}, 'end': summary(view)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
