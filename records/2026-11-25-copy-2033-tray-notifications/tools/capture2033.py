#!/usr/bin/env python3
"""#2033 tray, status and notification text: one capture run on m74 (Cinnamon, X11).

Run it on the desktop's host with the desktop lock held (desktop_lock.py run ...). It starts a
PRIVATE resident of the build under test (own XDG folders and runtime folder, session-only
credentials, nothing of the desktop user's configuration or keyring) on the real display, drives it
through putgd-cli, and saves uncropped frames of the whole desktop with ImageMagick `import`.

  python3 capture2033.py --build DIR --run DIR --label before|after --fixture FILE

Three scenes, all against loopback receivers on this host (synthetic PNGs only, no credentials):
  1. an upload to a port nothing listens on fails; the tray icon is then hovered for its tooltip,
     and the tooltip text is also read from the icon's StatusNotifierItem on the session bus;
  2. `diagnostics.bundle` with notify=true raises the "Diagnostics saved" notification;
  3. History after a failed upload, a cancelled upload (a receiver that never answers) and an
     upload whose reply was lost (the scripted fixture stores the file and drops the reply).
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after'])
parser.add_argument('--fixture', required=True)
options = parser.parse_args()

HOME = Path.home()
BUILD = Path(options.build)
R = Path(options.run)
LABEL = options.label
FRAMES = R / 'frames'
UID = os.getuid()
RT = Path('/run/user/%d/pg2033' % UID)
for folder in (R, FRAMES, R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'own', R / 'diag'):
    folder.mkdir(parents=True, exist_ok=True)
os.chmod(R, 0o700)
RT.mkdir(mode=0o700, exist_ok=True)
BUS = 'unix:path=/run/user/%d/bus' % UID
ENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS, XDG_SESSION_TYPE='x11',
           XDG_CURRENT_DESKTOP='X-Cinnamon', XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'), XDG_STATE_HOME=str(R / 'state'),
           XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
XENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS=BUS)
log = open(R / 'capture2033.log', 'a')
W, H = 1240, 1000
facts = {'label': LABEL}


def say(*parts):
    print(*parts, flush=True)
    print(*parts, file=log, flush=True)


def cli(method, params=None, timeout=120):
    out = subprocess.run([str(BUILD / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=ENV, timeout=timeout)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:200]}, 'result': {}}


def x(*args):
    return subprocess.run(list(args), capture_output=True, text=True, env=XENV).stdout.strip()


def until(check, seconds=30, step=0.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = check()
        if value:
            return value
        time.sleep(step)
    return None


def geometry(window):
    values = dict(line.split('=') for line in x('xdotool', 'getwindowgeometry', '--shell', window).splitlines() if '=' in line)
    try:
        return int(values['X']), int(values['Y']), int(values['WIDTH']), int(values['HEIGHT'])
    except (KeyError, ValueError):
        return None


def window(pid):
    best, area = None, 0
    for candidate in x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split():
        g = geometry(candidate)
        if g and g[2] * g[3] > area:
            best, area = candidate, g[2] * g[3]
    return best


def frame(name):
    """The whole desktop, uncropped."""
    path = FRAMES / ('%s-%s-full.png' % (LABEL, name))
    time.sleep(0.5)
    subprocess.run(['import', '-window', 'root', str(path)], env=XENV)
    say('frame', path.name, Image.open(path).size)
    return path


def park():
    x('xdotool', 'mousemove', '1900', '500')


def toast_showing():
    """Cinnamon's notification box has a saturated strip along its top edge; the wallpaper is grey."""
    subprocess.run(['import', '-window', 'root', '-crop', '40x1+1700+11', '+repage', str(R / 'toast-probe.png')], env=XENV)
    r, g, b = Image.open(R / 'toast-probe.png').convert('RGB').getpixel((20, 0))
    return max(r, g, b) - min(r, g, b) > 50


def clear_toasts(limit=60):
    """Dismiss every notification Cinnamon is showing or still has queued, with a press on its close button."""
    count = 0
    while count < limit and toast_showing():
        x('xdotool', 'mousemove', '1700', '80')
        time.sleep(0.5)
        x('xdotool', 'mousemove', '1877', '36')
        time.sleep(0.5)
        x('xdotool', 'mousedown', '1')
        time.sleep(0.15)
        x('xdotool', 'mouseup', '1')
        time.sleep(0.9)
        count += 1
    park()
    time.sleep(0.8)
    say('dismissed notifications:', count, 'still showing:', toast_showing())
    return count


procs = {}
servers = []


def hang_server():
    """A loopback receiver that takes the request and never answers, so an upload can be cancelled."""
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(8)
    held = []

    def run():
        while True:
            try:
                connection, _ = listener.accept()
            except OSError:
                return
            held.append(connection)
            facts['hangConnections'] = len(held)

    threading.Thread(target=run, daemon=True).start()
    servers.append((listener, held))
    return listener.getsockname()[1]


def free_port():
    probe = socket.socket()
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
    probe.close()  # nothing listens here afterwards
    return port


def revision():
    return cli('settings.get')['result']['metadata']['observedRevision']


def sxcu(name, url):
    path = R / 'own' / (name + '.sxcu')
    path.write_text(json.dumps({'Version': '17.0.0', 'Name': name, 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': url,
                                'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    path.chmod(0o600)
    return path


def add_destination(profile, url):
    added = cli('settings.importUploader', {'path': str(sxcu(profile, url)), 'expectedRevision': revision(), 'profileId': profile, 'credentialMode': 'session', 'allowInsecureHttp': False})
    say('destination', profile, url, added['ok'], added['error'].get('code'))
    assert added['ok'], added


def png(name, color):
    path = R / 'own' / name
    image = Image.new('RGB', (480, 270), color)
    ImageDraw.Draw(image).text((24, 24), 'put.gd #2033 synthetic ' + name, fill=(255, 255, 255))
    image.save(path)
    return path


def start(profile, path):
    accepted = until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(path)], 'profileId': profile})), 20, 0.5)
    assert accepted and accepted['ok'], accepted
    return accepted['result']['operationId']


def settled(operation, seconds=60):
    return until(lambda: cli('operation.inspect', {'id': operation})['result'].get('state') in ('completed', 'partial', 'failed', 'cancelled', 'interrupted'), seconds)


def record_of(operation):
    return next((entry for entry in cli('history.list', {'limit': 30})['result']['records'] if entry['operationId'] == operation), None)


def tray_item_tooltip(pid):
    """The tooltip the tray icon offers its host, read from the icon's StatusNotifierItem."""
    names = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus', '--object-path', '/org/freedesktop/DBus', '--method', 'org.freedesktop.DBus.ListNames'],
                           capture_output=True, text=True, env=XENV).stdout
    found = []
    for token in names.replace("'", ' ').replace(',', ' ').split():
        if token.startswith('org.kde.StatusNotifierItem-%d-' % pid):
            reply = subprocess.run(['gdbus', 'call', '--session', '--dest', token, '--object-path', '/StatusNotifierItem', '--method', 'org.freedesktop.DBus.Properties.Get',
                                    'org.kde.StatusNotifierItem', 'ToolTip'], capture_output=True, text=True, env=XENV)
            found.append({'name': token, 'tooltip': reply.stdout.strip(), 'error': reply.stderr.strip()})
    return found


def cleanup():
    cli('ui.quit')
    time.sleep(1)
    for listener, held in servers:
        listener.close()
        for connection in held:
            connection.close()
    for process in procs.values():
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(8)
            except subprocess.TimeoutExpired:
                process.kill()
    for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user'):
        leftover.unlink(missing_ok=True)
    for folder in (RT / 'putgd', RT / 'dconf', RT):
        try:
            folder.rmdir()
        except OSError:
            pass
    say('cleanup done; runtime folder gone:', not RT.exists())
    (R / 'facts.json').write_text(json.dumps(facts, indent=1))


def main():
    version = json.loads(subprocess.run([str(BUILD / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
    facts['build'] = version
    say('build', version.get('version'), version.get('gitCommit'))
    # The panel before the resident starts: its tray icon is found as the difference.
    facts['dismissedBeforeStart'] = clear_toasts()
    frame('panel-before-start')
    (RT / 'putgd').mkdir(exist_ok=True)
    (RT / 'putgd/session.sock').unlink(missing_ok=True)
    procs['resident'] = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    facts['residentPid'] = procs['resident'].pid
    assert until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(5)
    document = cli('settings.get')['result']['document']
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}  # no global shortcuts from this private resident
    patch = {'actions': actions}
    if 'updates' in document.get('preferences', {}):
        patch['preferences'] = {'updates': dict(document['preferences']['updates'], check=False)}
    patched = cli('settings.patch', {'patch': patch, 'expectedRevision': revision()})
    say('patched', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))

    port_dead = free_port()
    port_hang = hang_server()
    procs['fixture'] = subprocess.Popen([sys.executable, options.fixture], stdout=subprocess.PIPE, text=True)
    base = 'http://127.0.0.1:' + procs['fixture'].stdout.readline().strip()
    add_destination('lab-refused', 'http://127.0.0.1:%d/upload' % port_dead)
    add_destination('lab-hang', 'http://127.0.0.1:%d/upload' % port_hang)
    add_destination('lab-lost', base + '/upload/json')
    import urllib.request
    urllib.request.urlopen(urllib.request.Request(base + '/__rules', data=json.dumps({'rules': [{'call': 'upload', 'store': True, 'drop': True}]}).encode(),
                                                  headers={'Content-Type': 'application/json'}, method='POST'), timeout=10).read()

    # History's window, sized and placed once.
    assert cli('ui.show', {'view': 'history'})['ok']
    pid = until(lambda: cli('ui.snapshot')['result'].get('diagnostics', {}).get('ui', {}).get('pid'), 20)
    w = until(lambda: window(pid), 20)
    assert w, 'no put.gd window'
    x('xdotool', 'windowsize', w, str(W), str(H))
    x('xdotool', 'windowmove', w, '120', '20')
    time.sleep(1.5)
    facts['historyWindow'] = geometry(window(pid))
    say('history window', facts['historyWindow'])

    # The tray icon is where the panel gained something since before the resident started (the clock changes by
    # itself, so only the first cluster of changed columns counts). Found now, while the tray is idle: the failure
    # badge and its tooltip last only 8 seconds.
    park()
    idle = frame('panel-idle')
    base_img = Image.open(FRAMES / ('%s-panel-before-start-full.png' % LABEL)).convert('RGB')
    now_img = Image.open(idle).convert('RGB')
    columns = []
    for xx in range(1500, 1920):
        if sum(1 for yy in range(1040, 1080) if sum(abs(a - b) for a, b in zip(base_img.getpixel((xx, yy)), now_img.getpixel((xx, yy)))) > 60) > 3:
            columns.append(xx)
    cluster = []
    for xx in columns:
        if cluster and xx - cluster[-1] > 6:
            break
        cluster.append(xx)
    icon = ((cluster[0] + cluster[-1]) // 2, 1060) if cluster else None
    facts['trayIconCentre'] = icon
    say('tray icon at', icon)

    # Scene 3's data and scene 1: a queued upload cancelled before it is sent, one cancelled after it was sent
    # (a receiver that never answers), a lost reply, then the refused upload last.
    first_op = start('lab-hang', png('sent-then-cancelled.png', (60, 90, 150)))
    until(lambda: facts.get('hangConnections'), 20, 0.3)
    second_op = start('lab-hang', png('queued-then-cancelled.png', (90, 60, 150)))
    time.sleep(1.0)
    for op in (second_op, first_op):
        cancelled = cli('operation.cancel', {'id': op})
        say('cancel', op, cancelled['ok'], cancelled['error'].get('code'))
        settled(op)
    # Cancelled the moment it is accepted, before anything is sent.
    third_op = start('lab-hang', png('cancelled-at-once.png', (150, 90, 60)))
    cancelled = cli('operation.cancel', {'id': third_op})
    say('cancel', third_op, cancelled['ok'], cancelled['error'].get('code'))
    settled(third_op)
    lost_op = start('lab-lost', png('lost-reply.png', (120, 70, 60)))
    settled(lost_op)
    facts['dismissedBeforeFailure'] = clear_toasts()
    failed_op = start('lab-refused', png('refused-upload.png', (40, 110, 80)))
    settled(failed_op)
    time.sleep(0.8)
    frame('toast-failure')
    if icon:
        x('xdotool', 'mousemove', str(icon[0] - 8), '1058')
        time.sleep(0.4)
        x('xdotool', 'mousemove', str(icon[0]), '1060')
        time.sleep(1.8)
        frame('tooltip')
        park()
    facts['trayItems'] = tray_item_tooltip(procs['resident'].pid)
    for name, op in (('atOnceCancelled', third_op), ('sentCancelled', first_op), ('queuedCancelled', second_op), ('lost', lost_op), ('refused', failed_op)):
        entry = record_of(op) or {}
        facts[name] = {'uploadStatus': entry.get('uploadStatus'), 'state': cli('operation.inspect', {'id': op})['result'].get('state'), 'id': entry.get('id'), 'operationId': op}
        say(name, facts[name])
    facts['historyList'] = [{'title': e.get('title') or e.get('name'), 'uploadStatus': e.get('uploadStatus'), 'id': e.get('id')} for e in cli('history.list', {'limit': 30})['result']['records']]
    say('history list', facts['historyList'])

    # Scene 2: the notification whose title changed. The failure toasts come first; clear them.
    facts['dismissedBeforeDiagnostics'] = clear_toasts()
    # diagnostics.bundle saves a redacted package (names hashed, nothing uploaded) and notifies.
    saved = cli('diagnostics.bundle', {'operation': failed_op, 'output': str(R / 'diag'), 'notify': True}, timeout=180)
    say('diagnostics', saved['ok'], saved['error'].get('code'), str(saved['result'].get('path', ''))[-40:])
    facts['diagnostics'] = {'ok': saved['ok'], 'error': saved['error'].get('code')}
    time.sleep(1.4)
    frame('notification')
    time.sleep(1.5)
    frame('notification-late')

    # Scene 3: History.
    x('xdotool', 'windowactivate', w)
    time.sleep(1.0)
    x('xdotool', 'windowmove', w, '120', '20')
    cli('ui.show', {'view': 'settings'})
    time.sleep(1.5)
    cli('ui.show', {'view': 'history'})
    time.sleep(2.0)
    for key in ('atOnceCancelled', 'sentCancelled', 'lost', 'refused'):
        if not facts[key]['id']:
            continue
        cli('ui.history', {'action': 'select', 'ids': [facts[key]['id']]})
        time.sleep(1.5)
        park()
        frame('history-' + key)
    x('xdotool', 'windowminimize', w)


try:
    main()
finally:
    cleanup()
