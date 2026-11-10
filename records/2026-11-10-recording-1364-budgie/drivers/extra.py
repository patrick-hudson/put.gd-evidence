#!/usr/bin/env python3
"""budgie_extra.py APPIMAGE RUN: Budgie's click-highlight binds in rc.xml through a recording's life (#1364).

Prints one line per check: a window recording refused; the binds present while recording; put back after Budgie's
bridge rewrites the file; left by a killed resident and removed when put.gd starts again; the file identical at the end."""
import json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'lab'))
import record_run

appimage, run = sys.argv[1], Path(sys.argv[2]).resolve()
for name in ('config', 'data', 'cache', 'state', 'logs'):
    (run / name).mkdir(parents=True, exist_ok=True)
env, desktop = record_run.session_environment()
env.update(XDG_CONFIG_HOME=str(run / 'config'), XDG_DATA_HOME=str(run / 'data'), XDG_CACHE_HOME=str(run / 'cache'), XDG_STATE_HOME=str(run / 'state'))
build = record_run.Build('pr', appimage, run)
rc = Path.home() / '.config/budgie-desktop/labwc/rc.xml'
original = rc.read_bytes()
session = {'DBUS_SESSION_BUS_ADDRESS': env.get('DBUS_SESSION_BUS_ADDRESS', 'unix:path=/run/user/%d/bus' % os.getuid()), 'XDG_RUNTIME_DIR': env['XDG_RUNTIME_DIR'], 'HOME': os.environ['HOME'], 'PATH': os.environ['PATH']}
def binds():
    return rc.read_text(errors='replace').count('putgd="click-highlights"')
def cli(method, params=None, timeout=60, check=True):
    r = subprocess.run([build.cli, method, json.dumps(params or {})], env=env, capture_output=True, text=True, timeout=timeout)
    reply = json.loads(r.stdout)
    if check and not reply.get('ok'):
        raise RuntimeError('%s failed: %s' % (method, reply.get('error')))
    return reply if not check else (reply.get('result') or {})
def start():
    p = subprocess.Popen(build.launcher, env=env, stdin=subprocess.DEVNULL, stdout=open(run / 'logs' / 'resident.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.monotonic() + 60
    while True:
        try:
            cli('recording.capabilities', timeout=40); break
        except Exception:
            if time.monotonic() > deadline: raise
            time.sleep(0.5)
    s = cli('settings.get')
    if not ((s.get('document') or {}).get('archive') or {}).get('keepUploads'):
        cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(run / 'archive')}, 'preferences': {'notifications': False}}, 'expectedRevision': (s.get('metadata') or {}).get('observedRevision')})
    return p
def say(name, ok, detail=''):
    print('%s %s %s' % ('ok  ' if ok else 'FAIL', name, detail), flush=True)
def scroll(value):
    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.peripherals.mouse', 'natural-scroll', value], env=session, check=False)

p = start(); time.sleep(1); cli('ui.quit'); p.wait(20); time.sleep(1.5)   # the first start of a fresh configuration opens Settings
p = start()
try:
    say('no binds before a recording', binds() == 0, 'count %d' % binds())
    refused = cli('recording.prepare', {'target': {'kind': 'window'}, 'format': 'mp4', 'audio': {'system': False}, 'clickHighlights': True}, check=False)
    error = refused.get('error') or {}
    say('window recording with click highlights refused', not refused.get('ok') and error.get('code') == 'recording_unsupported' and (error.get('details') or {}).get('reason') == 'click_target_unsupported', json.dumps(error)[:260])
    rid = cli('recording.prepare', {'target': {'kind': 'monitor'}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}, 'clickHighlights': True})['recordingId']
    while cli('recording.inspect', {'id': rid}).get('state') != 'ready': time.sleep(0.3)
    say('no binds while ready', binds() == 0, 'count %d' % binds())
    cli('recording.start', {'id': rid}); time.sleep(1.5)
    say('binds while recording', binds() == 2, 'count %d' % binds())
    before = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.peripherals.mouse', 'natural-scroll'], env=session, capture_output=True, text=True).stdout.strip()
    scroll('false' if before == 'true' else 'true')
    seen = []
    for _ in range(30):
        seen.append(binds()); time.sleep(0.05)
    say("binds back after the bridge's rewrite", binds() == 2, 'counts in the 1.5 s after the setting changed: %s' % ''.join(str(n) for n in seen))
    scroll(before or 'false'); time.sleep(1.5)
    say('binds back after the second rewrite', binds() == 2, 'count %d' % binds())
    info = cli('recording.inspect', {'id': rid})
    say('recording still running, no click error', info.get('state') == 'recording' and not (info.get('progress') or {}).get('clickHighlightsError'), str((info.get('progress') or {}).get('clickHighlightsError')))
    cli('recording.stop', {'id': rid}, timeout=60); time.sleep(1.0)
    say('no binds after Stop', binds() == 0, 'count %d' % binds())
    cli('recording.cancel', {'id': rid})
    rid = cli('recording.prepare', {'target': {'kind': 'monitor'}, 'format': 'mp4', 'fps': 30, 'audio': {'system': False}, 'clickHighlights': True})['recordingId']
    while cli('recording.inspect', {'id': rid}).get('state') != 'ready': time.sleep(0.3)
    cli('recording.start', {'id': rid}); time.sleep(1.5)
    helpers = [int(x) for x in subprocess.run(['pgrep','-u',str(os.getuid()),'-x','putgd-record'],capture_output=True,text=True).stdout.split()]
    say('one owned recording helper', len(helpers)==1, str(helpers))
    if len(helpers)!=1: raise RuntimeError('ambiguous helper identity')
    os.kill(helpers[0], signal.SIGKILL)
    time.sleep(3)
    say('no binds after helper killed', binds()==0, 'count %d'%binds())
    cli('recording.cancel',{'id':rid},check=False)
    rid=cli('recording.prepare',{'target':{'kind':'monitor'},'format':'mp4','audio':{'system':False},'clickHighlights':True})['recordingId']
    while cli('recording.inspect',{'id':rid}).get('state')!='ready':time.sleep(.3)
    cli('recording.start',{'id':rid});time.sleep(1)
    cli('recording.cancel',{'id':rid});time.sleep(1)
    say('no binds after cancel during recording',binds()==0,'count %d'%binds())
    now = rc.read_bytes()
    detail = ''
    if now != original:
        import difflib
        detail = ' | '.join(list(difflib.unified_diff(original.decode(errors='replace').splitlines(), now.decode(errors='replace').splitlines(), lineterm='', n=0))[:8])
        time.sleep(3)
        detail += ' || after 3 s more: %s' % ('identical' if rc.read_bytes() == original else 'still different')
    say('rc.xml is byte for byte what it was', now == original, detail)
finally:
    try:
        cli('ui.quit', timeout=15)
    except BaseException:
        pass
    left = subprocess.run(['pgrep', '-u', str(os.getuid()), '-a', 'putgd'], capture_output=True, text=True).stdout.strip()
    print('left running:', left or 'nothing')
