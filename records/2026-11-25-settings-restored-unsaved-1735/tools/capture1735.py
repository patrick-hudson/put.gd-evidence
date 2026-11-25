#!/usr/bin/env python3
"""#1735 pictures: the issue's sequence on m74 (Cinnamon, X11) under the desktop lock.

  python3 capture1735.py --build DIR --run DIR --label before|after|probe [--points points.json]

A PRIVATE resident of the build (own XDG folders, XDG_RUNTIME_DIR /run/user/UID/pg1735) with one S3 destination
(the development template; nothing is uploaded) and no Updates object in the configuration. Then:
  1. Settings > Destinations: the destination's name is retyped and, before the 600 ms typing pause sends it, the
     put.gd window process (putgd-ui, this run's own PID only) is killed, so the resident keeps the checkpoint taken
     mid-rename at the configuration's own revision.
  2. Settings opens again and restores that checkpoint; the rename is finished (one more letter, then Tab).
  3. General: daily update checks are turned off, then back on.
  4. Upload clipboard in the window's command band. Before the fix put.gd refuses it with "Some changes in Settings
     aren't saved yet"; with it, the text is kept as a local copy (the clipboard action goes to no destination).
Frames are uncropped 1920x1080 desktop frames (ImageMagick import).
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from lib1735 import Run

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after', 'probe'])
parser.add_argument('--skip-updates', action='store_true', help='builds without a package identity have no daily-check control')
parser.add_argument('--points', default=os.path.join(os.path.dirname(__file__), 'points.json'))
o = parser.parse_args()
P = json.loads(Path(o.points).read_text()) if Path(o.points).exists() else {}
r = Run(o.build, o.run, o.label)
WIN = (100, 20, 1160, 1000)
NAME = 'Team photo'


def doc():
    return r.cli('settings.get')['result']


def label():
    profiles = doc()['document'].get('profiles', [])
    return profiles[0].get('label') if profiles else None


def updates():
    return doc()['document'].get('preferences', {}).get('updates', '(absent)')


def show_settings():
    shown = r.cli('ui.show', {'view': 'settings'})
    r.say('ui.show', shown['ok'], shown['error'])
    ws = r.until(lambda: r.windows(), 20)
    assert ws, 'no Settings window'
    r.place(ws[0][0], *WIN)
    return ws[0][0]


try:
    r.start(check_updates_off=False)
    got = doc()
    imported = r.cli('settings.importDevelopment', {'expectedRevision': got['metadata']['observedRevision']})
    r.say('importDevelopment', imported['ok'], imported['error'])
    got = doc()
    document = got['document']
    actions = document['actions']
    # Upload clipboard keeps a local copy only, so the "after" action needs no network.
    actions['clipboard'] = dict(actions['clipboard'], destination='local', profileId=None)
    archive = dict(document['archive'], keepUploads=True, root=str(r.run / 'keep'))
    patched = r.cli('settings.patch', {'patch': {'actions': {'clipboard': actions['clipboard']}, 'archive': archive}, 'expectedRevision': got['metadata']['observedRevision']})
    r.say('clipboard local', patched['ok'], patched['error'])
    # No Updates object, as in a configuration from before it existed: edit the file, then reload it.
    files = [p for p in (r.run / 'cfg').rglob('*.json') if '"profiles"' in p.read_text()]
    r.say('config files', files)
    cfg = json.loads(files[0].read_text())
    cfg.get('preferences', {}).pop('updates', None)
    files[0].write_text(json.dumps(cfg, indent=2))
    reloaded = r.cli('settings.reload')
    r.say('reload', reloaded['ok'], reloaded['error'], 'updates:', updates(), 'label:', label())
    r.facts['start'] = {'label': label(), 'updates': updates()}

    window = show_settings()
    r.click(*P.get('tab_destinations', (680, 48)), settle=1.5)
    r.park()
    r.frame('destinations')
    if o.label == 'probe':
        r.click(*P.get('tab_settings', (796, 48)), settle=1.5)
        r.click(*P.get('rail_general', (185, 206)), settle=1.5)
        r.park()
        r.frame('general')
        raise SystemExit(0)

    # 1. Mid-rename checkpoint: type, wait past the 250 ms checkpoint, kill before the 600 ms typing pause.
    revision = doc()['metadata']['observedRevision']
    r.click(*P['label_field'], settle=0.6)
    r.x('xdotool', 'key', 'ctrl+a')
    r.x('xdotool', 'type', '--delay', '15', NAME)
    time.sleep(0.4)
    pids = r.ui_pids()
    for pid in pids:
        os.kill(pid, signal.SIGKILL)
    r.say('killed putgd-ui', pids)
    time.sleep(1.5)
    r.facts['checkpoint'] = {'label': label(), 'sameRevision': doc()['metadata']['observedRevision'] == revision}
    r.say('after kill', r.facts['checkpoint'])

    # 2. Restored window; finish the rename.
    window = show_settings()
    r.click(*P.get('tab_destinations', (680, 48)), settle=1.5)
    r.park()
    r.frame('restored')
    r.click(*P['label_field_restored'], settle=0.6)
    r.x('xdotool', 'key', 'End')
    r.x('xdotool', 'type', '--delay', '15', 's')
    r.x('xdotool', 'key', 'Tab')
    r.until(lambda: label() == NAME + 's', 10)
    r.facts['renamed'] = label()
    r.say('renamed', label())
    r.park()
    r.frame('renamed')

    # 3. Daily update checks off, then on.
    r.click(*P.get('tab_settings', (796, 48)), settle=1.5)
    r.click(*P.get('rail_general', (185, 206)), settle=1.5)
    for want in (() if o.skip_updates else (False, True)):
        r.click(*P['update_check'], settle=0.4)
        r.until(lambda: updates() != '(absent)' and updates().get('check', True) == want, 10)
        r.say('updates after click', updates())
    time.sleep(1.5)
    r.facts['updates'] = updates()
    r.park()
    r.frame('toggled')

    # 4. Upload clipboard from the command band.
    subprocess.run(['xclip', '-selection', 'clipboard'], input='put.gd #1735 check', text=True, env=r.xenv, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r.facts['xclip'] = r.x('pgrep', '-u', str(os.getuid()), '-x', 'xclip')
    r.click(*P['band_clipboard'], settle=2.5)
    r.park()
    r.frame('action', settle=0.3)
    time.sleep(2)
    r.frame('action-later', settle=0.1)
    r.facts['windows'] = r.windows()
    r.facts['history'] = r.cli('history.list', {'limit': 3}).get('result')
finally:
    for pid in r.x('pgrep', '-u', str(os.getuid()), '-x', '-f', 'xclip -selection clipboard').split():
        os.kill(int(pid), signal.SIGTERM)
    r.cleanup()
