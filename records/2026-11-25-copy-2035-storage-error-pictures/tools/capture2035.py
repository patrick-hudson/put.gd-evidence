#!/usr/bin/env python3
"""#2035 storage error wording: one capture run on d69 (Plasma 6, Wayland).

Run it on the desktop's host with the desktop lock held (desktop_lock.py run ...). It starts a
PRIVATE resident of the build under test (own XDG folders and runtime folder, session-only
credentials, nothing of the desktop user's configuration or keyring) on the real display, drives it
through putgd-cli and saves frames of the whole desktop from the host's loopback VNC (tools/lab/rfb.py).

  python3 capture2035.py --build DIR --run DIR --label before|after --rfb FILE [--vnc-port 5900]

Offline only, all against 127.0.0.1 ports nothing listens on, with synthetic PNGs and no credentials:
  1. a custom HTTP uploader whose Request URL is an unused port: the upload fails with http_connect_failed;
  2. an SFTP destination at an unused port: the upload fails with ssh_connection_refused.
History lists both failed uploads; each is selected in turn and the window is framed.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--label', required=True, choices=['before', 'after'])
parser.add_argument('--rfb', required=True)
parser.add_argument('--vnc-port', default='5900')
options = parser.parse_args()

BUILD = Path(options.build)
R = Path(options.run)
LABEL = options.label
FRAMES = R / 'frames'
UID = os.getuid()
RT = Path('/run/user/%d/pg2035' % UID)
for folder in (R, FRAMES, R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'own'):
    folder.mkdir(parents=True, exist_ok=True)
os.chmod(R, 0o700)
RT.mkdir(mode=0o700, exist_ok=True)
SOCKET = RT / 'putgd/session.sock'
assert len(str(SOCKET).encode()) <= 107, SOCKET
ENV = dict(os.environ, WAYLAND_DISPLAY='/run/user/%d/wayland-0' % UID, DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/%d/bus' % UID,
           XDG_SESSION_TYPE='wayland', XDG_CURRENT_DESKTOP='KDE', QT_QPA_PLATFORM='wayland',
           XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'), XDG_STATE_HOME=str(R / 'state'),
           XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
ENV.pop('DISPLAY', None)
log = open(R / 'capture2035.log', 'a')
facts = {'label': LABEL}
procs = {}


def say(*parts):
    print(*parts, flush=True)
    print(*parts, file=log, flush=True)


def cli(method, params=None, timeout=120):
    out = subprocess.run([str(BUILD / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=ENV, timeout=timeout)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:200]}, 'result': {}}


def until(check, seconds=30, step=0.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = check()
        if value:
            return value
        time.sleep(step)
    return None


def revision():
    return cli('settings.get')['result']['metadata']['observedRevision']


def free_port():
    probe = socket.socket()
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
    probe.close()  # nothing listens here afterwards
    return port


def park():
    """Move the pointer off put.gd's window and the toasts, with real pointer input through the host's own VNC tile."""
    sys.path.insert(0, str(Path(options.rfb).parent))
    from rfb import RFB
    client = RFB(int(options.vnc_port))
    client.pointer(1750, 300)
    time.sleep(0.3)
    client.pointer(1752, 302)
    client.close()


def frame(name):
    """The whole desktop, uncropped, from the host's loopback VNC."""
    path = FRAMES / ('%s-%s-full.png' % (LABEL, name))
    park()
    time.sleep(1.0)
    subprocess.run([sys.executable, options.rfb, options.vnc_port, str(path)], capture_output=True)
    say('frame', path.name, Image.open(path).size)
    return path


KWIN = R / 'place.js'


def kwin_place(x, y, w, h, tag):
    """A temporary KWin script: log the put.gd windows, then put the History window at x,y,w,h and keep it above."""
    KWIN.write_text("""
for (const w of workspace.windowList()) {
  if (String(w.resourceClass).indexOf('putgd') < 0 && String(w.caption).indexOf('put.gd') < 0) continue;
  print('PG2035 %(tag)s class=' + w.resourceClass + ' caption=' + w.caption + ' geo=' + JSON.stringify(w.frameGeometry) + ' min=' + w.minimized);
  if (String(w.resourceClass) !== 'putgd-ui') continue;
  w.minimized = false;
  w.frameGeometry = {x: %(x)d, y: %(y)d, width: %(w)d, height: %(h)d};
  w.keepAbove = true;
  workspace.activeWindow = w;
  print('PG2035 %(tag)s placed ' + JSON.stringify(w.frameGeometry));
}
""" % dict(x=x, y=y, w=w, h=h, tag=tag))
    name = 'pg2035-' + tag
    since = time.strftime('%Y-%m-%d %H:%M:%S')
    loaded = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.kde.KWin', '--object-path', '/Scripting', '--method', 'org.kde.kwin.Scripting.loadScript', str(KWIN), name],
                            capture_output=True, text=True, env=ENV).stdout.strip()
    number = loaded.strip('(),\n ').split(',')[0].strip()
    subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.kde.KWin', '--object-path', '/Scripting/Script' + number, '--method', 'org.kde.kwin.Script.run'], capture_output=True, text=True, env=ENV)
    time.sleep(1.0)
    subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.kde.KWin', '--object-path', '/Scripting', '--method', 'org.kde.kwin.Scripting.unloadScript', name], capture_output=True, text=True, env=ENV)
    seen = subprocess.run(['journalctl', '--user', '--since', since, '--no-pager', '-o', 'cat'], capture_output=True, text=True).stdout
    lines = [line for line in seen.splitlines() if 'PG2035 ' + tag in line]
    say('kwin', tag, loaded, lines)
    return lines


def png(name, color):
    path = R / 'own' / name
    image = Image.new('RGB', (480, 270), color)
    ImageDraw.Draw(image).text((24, 24), 'put.gd #2035 synthetic ' + name, fill=(255, 255, 255))
    image.save(path)
    return path


def sxcu(name, url):
    path = R / 'own' / (name + '.sxcu')
    path.write_text(json.dumps({'Version': '17.0.0', 'Name': name, 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': url,
                                'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    path.chmod(0o600)
    return path


def start(profile, path):
    accepted = until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(path)], 'profileId': profile})), 20, 0.5)
    assert accepted and accepted['ok'], accepted
    return accepted['result']['operationId']


def settled(operation, seconds=90):
    return until(lambda: cli('operation.inspect', {'id': operation})['result'].get('state') in ('completed', 'partial', 'failed', 'cancelled', 'interrupted'), seconds)


def record_of(operation):
    return next((entry for entry in cli('history.list', {'limit': 30})['result']['records'] if entry['operationId'] == operation), None)


def cleanup():
    cli('ui.quit')
    time.sleep(1.5)
    process = procs.get('resident')
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(8)
        except subprocess.TimeoutExpired:
            process.kill()
    for leftover in (SOCKET, RT / 'dconf/user'):
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
    frame('desktop-before-start')
    (RT / 'putgd').mkdir(exist_ok=True)
    SOCKET.unlink(missing_ok=True)
    procs['resident'] = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    facts['residentPid'] = procs['resident'].pid
    assert until(lambda: SOCKET.exists(), 20), 'resident did not start'
    time.sleep(5)
    document = cli('settings.get')['result']['document']
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}  # no global shortcuts from this private resident
    patch = {'actions': actions}
    if 'updates' in document.get('preferences', {}):
        patch['preferences'] = {'updates': dict(document['preferences']['updates'], check=False)}
    patched = cli('settings.patch', {'patch': patch, 'expectedRevision': revision()})
    say('patched', patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))

    # 1. A custom HTTP uploader at a port nothing listens on.
    port_http = free_port()
    added = cli('settings.importUploader', {'path': str(sxcu('lab-http', 'http://127.0.0.1:%d/upload' % port_http)), 'expectedRevision': revision(), 'profileId': 'lab-http',
                                            'credentialMode': 'session', 'allowInsecureHttp': False})
    say('destination lab-http', port_http, added['ok'], added['error'].get('code'), added['error'].get('message', ''))
    assert added['ok'], added
    # 2. An SFTP destination at another port nothing listens on.
    port_sftp = free_port()
    profile = {'id': 'lab-sftp', 'label': 'Lab SFTP (closed port)', 'provider': 'sftp',
               'settings': {'server': '127.0.0.1:%d' % port_sftp, 'user': 'lab', 'folder': 'uploads', 'publicUrlBase': None, 'hostKeyFingerprint': None},
               'credentials': {'mode': 'session', 'reference': None}}
    document = cli('settings.get')['result']['document']
    profiles = list(document['profiles']) + [profile]
    patched = cli('settings.patch', {'patch': {'profiles': profiles}, 'expectedRevision': revision()})
    say('destination lab-sftp', port_sftp, patched['ok'], patched['error'].get('code'), patched['error'].get('message', ''))
    facts['ports'] = {'http': port_http, 'sftp': port_sftp}
    assert patched['ok'], patched

    http_op = start('lab-http', png('closed-port-http.png', (40, 110, 80)))
    settled(http_op)
    sftp_op = start('lab-sftp', png('closed-port-sftp.png', (60, 90, 150)))
    settled(sftp_op)
    for name, op in (('http', http_op), ('sftp', sftp_op)):
        entry = record_of(op) or {}
        inspected = cli('operation.inspect', {'id': op})['result']
        detail = cli('history.detail', {'id': entry['id']}) if entry.get('id') else {}
        facts[name] = {'id': entry.get('id'), 'operationId': op, 'uploadStatus': entry.get('uploadStatus'), 'state': inspected.get('state'), 'inspect': inspected, 'detail': detail}
        say(name, json.dumps(facts[name])[:1500])

    # History: place the window, select each failed upload, frame.
    assert cli('ui.show', {'view': 'history'})['ok']
    time.sleep(3)
    facts['kwin'] = kwin_place(40, 60, 1440, 900, 'a')
    time.sleep(1.5)
    for name in ('http', 'sftp'):
        if not facts[name]['id']:
            continue
        cli('ui.history', {'action': 'select', 'ids': [facts[name]['id']]})
        time.sleep(2.0)
        frame('history-' + name)
    facts['kwinAfter'] = kwin_place(40, 60, 1440, 900, 'b')
    cli('ui.hide', {'view': 'history'})


try:
    main()
finally:
    cleanup()
