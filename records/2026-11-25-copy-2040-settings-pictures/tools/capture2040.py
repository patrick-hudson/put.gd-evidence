#!/usr/bin/env python3
"""#2040 Settings description pictures: one capture run on m74 (Cinnamon, X11), under the desktop lock.

  python3 capture2040.py --build DIR --run DIR --label before|after

Starts a PRIVATE resident of the build (own XDG folders, own XDG_RUNTIME_DIR /run/user/UID/pg2040), opens Settings
with `ui.show settings` and saves uncropped 1920x1080 frames of the real desktop. The Settings window is placed at
(100, 20) and sized 1160x1000. A local copy is kept (no destination, nothing uploads), so the "no output" banner
doesn't move the page rail. Nothing is uploaded; no credentials are used.

Scenes (frame names):
  limits-tooltip      Advanced > Resource limits (expanded), pointer rests on Memory for queued images: its tooltip
  region-help         Capture > Region selection, the info button next to While selecting opened
  debug-logging       Advanced > Diagnostics, the description under the debug logging checkbox
  sensitive-text      Capture > Text recognition, the description of the sensitive-text check
  largest-file-tooltip  Advanced > Resource limits, pointer rests on Largest file: its tooltip
"""
import argparse
import sys
import time
sys.path.insert(0, __import__('os').path.dirname(__file__))
from lib2040 import Run

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after', 'probe'])
parser.add_argument('--only', default='')
o = parser.parse_args()
r = Run(o.build, o.run, o.label)
WIN = (100, 20, 1160, 1000)
# Pointer positions that rest on a control (absolute desktop pixels), read from the -pre frames of a probe run.
HOVER = {'limits-tooltip': (608, 828), 'largest-file-tooltip': (608, 292)}
RAIL = {'general': (185, 206), 'capture': (185, 244), 'advanced': (185, 320)}
MARGIN = (1180, 600)  # empty page margin right of the cards: the wheel scrolls the page and never changes a control


def scroll(clicks):
    r.x('xdotool', 'mousemove', str(MARGIN[0]), str(MARGIN[1]))
    for _ in range(clicks):
        r.x('xdotool', 'click', '5')
        time.sleep(0.05)
    time.sleep(0.8)


def to_top():
    r.x('xdotool', 'mousemove', str(MARGIN[0]), str(MARGIN[1]))
    for _ in range(40):
        r.x('xdotool', 'click', '4')
    time.sleep(0.8)


def want(name):
    return not o.only or name in o.only.split(',')


try:
    r.start()
    shown = r.cli('ui.show', {'view': 'settings'})
    r.say('ui.show', shown['ok'], shown['error'])
    time.sleep(4)
    ws = r.windows()
    r.say('windows', ws)
    assert ws, 'no Settings window'
    r.place(ws[0][0], *WIN)

    # Advanced > Resource limits: open the disclosure once, it stays open.
    r.click(*RAIL['advanced'], settle=1.5)
    to_top()
    r.click(400, 496, 1.5)  # Resource limits
    r.park()
    r.frame('advanced-open-top')

    if want('debug-logging'):
        # The Diagnostics card is below Resource limits when it is open; collapse the disclosure for this frame.
        r.click(400, 496, 1.2)
        to_top()
        r.park()
        r.frame('debug-logging')
        r.click(400, 496, 1.2)  # open again

    for name, scrolled in (('limits-tooltip', 6), ('largest-file-tooltip', 6)):
        if not want(name):
            continue
        to_top()
        scroll(scrolled)
        r.park()
        r.frame(name + '-pre')
        # hover points are given by --probe frames; see HOVER below
        px, py = HOVER[name]
        r.hover(px, py, 2.4)
        r.frame(name, settle=0.2)
        r.park()

    if want('region-help') or want('sensitive-text'):
        r.click(*RAIL['capture'], settle=1.5)
        to_top()
        r.park()
        r.frame('capture-top')
    if want('region-help'):
        r.click(476, 622, 1.0)  # info button next to While selecting
        r.park()
        r.frame('region-help')
        r.click(476, 622, 0.6)
    if want('sensitive-text'):
        to_top()
        scroll(24)
        r.park()
        r.frame('sensitive-text-pre')
finally:
    r.cleanup()
