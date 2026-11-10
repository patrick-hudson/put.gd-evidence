#!/usr/bin/env python3
"""#1393: what a user sees for a reply that was cut off. No physical desktop.

A private X display (Xvfb), a private resident of the build under test on it (own XDG
folders, own session bus, session credentials), the scripted receiver on loopback, and
one upload whose reply is short of its Content-Length. History is shown with that item
selected and the display is captured with PIL. The receiver's token is its synthetic
one and is never on screen.

  python3 picture1393.py --build DIR --fixture FILE --run DIR
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageGrab

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--fixture', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--display', default=':93')
options = parser.parse_args()
BUILD, R, DISPLAY = Path(options.build), Path(options.run), options.display
for folder in (R, R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'rt', R / 'own', R / 'shots'):
    folder.mkdir(parents=True, exist_ok=True)
for private in (R, R / 'rt', R / 'own'):
    os.chmod(private, 0o700)
if Path('/tmp/.X11-unix/X' + DISPLAY.lstrip(':')).exists():
    sys.exit('display %s is in use' % DISPLAY)
ENV = {k: v for k, v in os.environ.items() if k not in ('WAYLAND_DISPLAY', 'XAUTHORITY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_CURRENT_DESKTOP')}
ENV.update(DISPLAY=DISPLAY, XDG_SESSION_TYPE='x11', QT_QPA_PLATFORM='xcb', XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'),
           XDG_STATE_HOME=str(R / 'state'), XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(R / 'rt'))
W, H = 1240, 1000
procs = {}


def cli(method, params=None):
    out = subprocess.run([str(BUILD / 'putgd-cli'), '--params-stdin', method], input=json.dumps(params or {}), capture_output=True, text=True, env=ENV, timeout=120)
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {'ok': False, 'error': {'code': 'no_reply', 'message': (out.stdout + out.stderr)[:200]}, 'result': {}}


def x(*args):
    return subprocess.run(list(args), capture_output=True, text=True, env=ENV).stdout.strip()


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


def revision():
    return cli('settings.get')['result']['metadata']['observedRevision']


def main():
    procs['x'] = subprocess.Popen(['Xvfb', DISPLAY, '-screen', '0', '1400x1100x24', '-nolisten', 'tcp'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert until(lambda: Path('/tmp/.X11-unix/X' + DISPLAY.lstrip(':')).exists(), 10), 'the X display did not start'
    procs['resident'] = subprocess.Popen(['dbus-run-session', '--', str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    assert until(lambda: (R / 'rt/putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(4)
    version = json.loads(subprocess.run([str(BUILD / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
    document = cli('settings.get')['result']['document']
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}  # no global shortcuts from this resident
    cli('settings.patch', {'patch': {'actions': actions}, 'expectedRevision': revision()})

    procs['fixture'] = subprocess.Popen([sys.executable, options.fixture], stdout=subprocess.PIPE, text=True)
    base = 'http://127.0.0.1:' + procs['fixture'].stdout.readline().strip()
    sxcu = R / 'own/receiver.sxcu'
    sxcu.write_text(json.dumps({'Version': '17.0.0', 'Name': 'Scripted receiver', 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': base + '/upload/json',
                                'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    sxcu.chmod(0o600)
    added = cli('settings.importUploader', {'path': str(sxcu), 'expectedRevision': revision(), 'profileId': 'scripted', 'credentialMode': 'session'})
    print('import', added['ok'], added['error'].get('code'))
    png = R / 'own/putgd-cut-reply-check.png'
    image = Image.new('RGB', (640, 360), (24, 26, 30))
    ImageDraw.Draw(image).text((40, 160), 'put.gd #1393 synthetic upload', fill=(244, 196, 48))
    image.save(png)
    # The receiver stores the file and answers with a whole link in a reply that promises 64 bytes more.
    request = urllib.request.Request(base + '/__rules', data=json.dumps({'rules': [{'call': 'upload', 'store': True, 'cut': 'length'}]}).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(request, timeout=10).read()
    accepted = until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(png)], 'profileId': 'scripted'})), 20, 0.5)
    operation = accepted['result']['operationId']
    until(lambda: cli('operation.inspect', {'id': operation})['result'].get('state') in ('completed', 'partial', 'failed'), 60)
    record = next(entry for entry in cli('history.list', {'limit': 30})['result']['records'] if entry['operationId'] == operation)
    detail = cli('history.detail', {'id': record['id']})['result']
    with urllib.request.urlopen(base + '/__state', timeout=10) as reply:
        stored = len([f for f in json.loads(reply.read())['files'].values() if not f['deleted']])
    result = {'build': version, 'uploadStatus': record['uploadStatus'], 'error': (record.get('error') or {}).get('code'), 'message': (record.get('error') or {}).get('message'),
              'linkRecorded': bool((record.get('receipt') or {}).get('directUrl')), 'storedOnTheReceiver': stored,
              'tokenInTheRecord': 'putgd-synthetic-uploader-token-not-real' in json.dumps(detail) + json.dumps(record)}
    (R / 'shots/result.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))

    assert cli('ui.show', {'view': 'history'})['ok']
    pid = until(lambda: cli('ui.snapshot')['result'].get('diagnostics', {}).get('ui', {}).get('pid'), 20)
    w = until(lambda: window(pid), 20)
    assert w, 'no put.gd window'
    x('xdotool', 'windowmove', w, '40', '30')
    x('xdotool', 'windowsize', w, str(W), str(H))
    time.sleep(1.5)
    cli('ui.history', {'action': 'select', 'ids': [record['id']]})
    time.sleep(2)
    x('xdotool', 'mousemove', '1390', '1090')
    time.sleep(0.5)
    frame = geometry(window(pid))
    print('window', frame)
    shot = ImageGrab.grab(xdisplay=DISPLAY).crop((frame[0], frame[1], frame[0] + frame[2], frame[1] + frame[3]))
    shot.save(R / 'shots/cut-reply-history.png')
    print('shot', shot.size)


def cleanup():
    cli('ui.quit')
    time.sleep(1)
    for name in ('fixture', 'resident', 'x'):
        process = procs.get(name)
        if process and process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(8)
            except subprocess.TimeoutExpired:
                process.kill()
    print('cleanup done; display gone:', not Path('/tmp/.X11-unix/X' + DISPLAY.lstrip(':')).exists())


try:
    main()
finally:
    cleanup()
