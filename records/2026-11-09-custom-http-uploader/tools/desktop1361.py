#!/usr/bin/env python3
"""#1361 custom HTTP uploader: the picture set on an X11 desktop (written for m74, Cinnamon).

Run on the desktop's own host, inside nothing: it finds the session itself. Hold the desktop
lock first. It starts a PRIVATE resident of the build under test (own XDG folders, session
credentials, nothing of the desktop user's configuration or keyring), drives it through
putgd-cli as an agent would, makes a few real pointer clicks with xdotool where a click is the
thing shown, and captures put.gd's window with ImageMagick `import`.

  python3 desktop1361.py --build DIR --run DIR --sxcu DIR --fixture FILE

  --build    folder with putgd and putgd-cli (a build tree, or /usr/bin for a package)
  --run      a new, empty private folder for this run (configuration, data, shots)
  --sxcu     folder with xbackbone.sxcu and zipline.sxcu from tools/lab/http_receivers
  --fixture  tests/fixtures/http_uploader_server.py of the same source
  --form-only  stop after the Settings form pictures (01 to 07)

Needs xdotool, wmctrl, ImageMagick, python3-pil and firefox. Every link opens in Firefox with a
throwaway profile through a temporary handler; ~/.config/mimeapps.list is restored byte for
byte. Links are copied to the desktop clipboard, as every put.gd upload does. Nothing is
printed or captured that holds a token: secret rows are shown masked and never revealed.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--sxcu', required=True)
parser.add_argument('--fixture', required=True)
parser.add_argument('--form-only', action='store_true', help='stop after the Settings form pictures (01 to 07)')
options = parser.parse_args()

HOME = Path.home()
BUILD = Path(options.build)
R = Path(options.run)
SXCU = Path(options.sxcu)
SHOTS = R / 'shots'
UID = os.getuid()
RT = Path('/run/user/%d/pg1361' % UID)
for folder in (R, SHOTS, R / 'cfg', R / 'data', R / 'state', R / 'cache', R / 'ff', R / 'own'):
    folder.mkdir(parents=True, exist_ok=True)
os.chmod(R, 0o700)
RT.mkdir(mode=0o700, exist_ok=True)
ENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'), DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/%d/bus' % UID,
           XDG_SESSION_TYPE='x11', XDG_CURRENT_DESKTOP='X-Cinnamon', XDG_CONFIG_HOME=str(R / 'cfg'), XDG_DATA_HOME=str(R / 'data'),
           XDG_STATE_HOME=str(R / 'state'), XDG_CACHE_HOME=str(R / 'cache'), XDG_RUNTIME_DIR=str(RT))
XENV = dict(os.environ, DISPLAY=':0', XAUTHORITY=str(HOME / '.Xauthority'))
log = open(R / 'desktop1361.log', 'a')
W, H = 1240, 1000


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


def window(name=None, pid=None):
    ids = x('xdotool', 'search', '--onlyvisible', '--name', name).split() if name else x('xdotool', 'search', '--onlyvisible', '--pid', str(pid)).split()
    best, area = None, 0
    for candidate in ids:
        g = geometry(candidate)
        if g and g[2] * g[3] > area:
            best, area = candidate, g[2] * g[3]
    return best


def shot(name, target=None, region=None):
    path = SHOTS / (name + '.png')
    time.sleep(0.6)
    if region is None and target is not None:
        region = geometry(target)
    command = ['import', '-window', 'root']
    if region:
        command += ['-crop', '%dx%d+%d+%d' % (region[2], region[3], region[0], region[1]), '+repage']
    subprocess.run(command + [str(path)], env=XENV)
    say('shot', path.name, Image.open(path).size)
    return path


def click(target, rx, ry):
    gx, gy, _, _ = geometry(target)
    x('xdotool', 'mousemove', str(gx + rx), str(gy + ry))
    time.sleep(0.2)
    x('xdotool', 'click', '1')


def wheel(target, clicks):
    """Scrolls the page with the pointer over its empty right margin, away from every control."""
    gx, gy, _, _ = geometry(target)
    x('xdotool', 'mousemove', str(gx + 1120), str(gy + 620))
    for _ in range(abs(clicks)):
        x('xdotool', 'click', '5' if clicks > 0 else '4')
        time.sleep(0.03)
    time.sleep(0.4)


def park():
    x('xdotool', 'mousemove', '1900', '1060')


def danger_button(path):
    """The centre of the outlined danger button in the lower right of a History capture."""
    image = Image.open(path).convert('RGB')
    pixels = image.load()
    xs, ys = [], []
    for yy in range(image.height - 200, image.height - 40):
        for xx in range(860, image.width - 8):
            r, g, b = pixels[xx, yy]
            if r > 140 and g < 110 and b < 110 and r - g > 70:
                xs.append(xx)
                ys.append(yy)
    return ((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2) if len(xs) > 40 else None


procs = {}
mime = HOME / '.config/mimeapps.list'
mime_before = mime.read_bytes() if mime.exists() else None
handler = HOME / '.local/share/applications/putgd1361-browser.desktop'


def own_browsers():
    found = []
    for pid in x('pgrep', '-x', 'firefox').split() + x('pgrep', '-x', 'firefox-bin').split():
        try:
            # Only the browser this run started: its command line names this run's profile folder.
            if str(R / 'ff') in Path('/proc/%s/cmdline' % pid).read_bytes().decode(errors='replace'):
                found.append(int(pid))
        except OSError:
            pass
    return found


def cleanup():
    cli('ui.quit')
    time.sleep(1)
    for process in procs.values():
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(8)
            except subprocess.TimeoutExpired:
                process.kill()
    if mime_before is None:
        mime.unlink(missing_ok=True)
    else:
        mime.write_bytes(mime_before)
    handler.unlink(missing_ok=True)
    for pid in own_browsers():
        os.kill(pid, signal.SIGTERM)
    for leftover in (RT / 'putgd/session.sock', RT / 'dconf/user'):
        leftover.unlink(missing_ok=True)
    for folder in (RT / 'putgd', RT / 'dconf', RT):
        try:
            folder.rmdir()
        except OSError:
            pass
    say('cleanup done; mimeapps restored:', (mime.read_bytes() if mime.exists() else None) == mime_before, 'runtime folder gone:', not RT.exists())


def revision():
    return cli('settings.get')['result']['metadata']['observedRevision']


def upload(path, profile):
    accepted = until(lambda: (lambda reply: reply if reply['ok'] or reply['error'].get('code') != 'initializing' else None)(cli('upload.files', {'paths': [str(path)], 'profileId': profile})), 20, 0.5)
    operation = accepted['result']['operationId']
    until(lambda: cli('operation.inspect', {'id': operation})['result'].get('state') in ('completed', 'partial', 'failed'), 60)
    return next(entry for entry in cli('history.list', {'limit': 30})['result']['records'] if entry['operationId'] == operation)


def main():
    version = json.loads(subprocess.run([str(BUILD / 'putgd-cli'), '--version-json'], capture_output=True, text=True).stdout)
    (SHOTS / 'build.json').write_text(json.dumps(version, indent=1))
    say('build', version.get('version'), version.get('gitCommit'))
    (RT / 'putgd').mkdir(exist_ok=True)
    (RT / 'putgd/session.sock').unlink(missing_ok=True)
    procs['resident'] = subprocess.Popen([str(BUILD / 'putgd'), '--background'], env=ENV, stdout=open(R / 'resident.log', 'w'), stderr=subprocess.STDOUT)
    assert until(lambda: (RT / 'putgd/session.sock').exists(), 20), 'resident did not start'
    time.sleep(4)  # the startup credential read
    assert cli('ui.show', {'view': 'destinations'})['ok']
    pid = until(lambda: cli('ui.snapshot')['result'].get('diagnostics', {}).get('ui', {}).get('pid'), 20)
    w = until(lambda: window(pid=pid), 20)
    assert w, 'no put.gd window'
    x('xdotool', 'windowsize', w, str(W), str(H))
    x('xdotool', 'windowmove', w, '120', '20')
    time.sleep(1.2)
    w = window(pid=pid)
    frame = geometry(w)
    say('window', w, frame)

    # 1. Add destination: the menu with the new type.
    click(w, 92, frame[3] - 74)
    time.sleep(0.8)
    shot('01-add-destination-menu', region=frame)
    x('xdotool', 'key', 'Escape')
    time.sleep(0.4)

    # 2. A destination of the new type, as Add destination leaves it; credentials for this session only.
    document = cli('settings.get')['result']['document']
    defaults = {'accepts': ['image', 'text', 'file'], 'allowInsecureHttp': False, 'arguments': [], 'body': 'multipart', 'connectTimeoutMs': 10000, 'data': '', 'dataSecret': False,
                'deletionUrl': '', 'errorMessage': '', 'fileFormName': 'file', 'headers': [], 'parameters': [], 'requestMethod': 'POST', 'requestTimeoutMs': 600000,
                'requestUrl': '', 'responseUrl': '', 'secrets': [], 'thumbnailUrl': ''}
    actions = {name: dict(action, shortcut='') for name, action in document['actions'].items()}  # no global shortcuts from this private resident
    patched = cli('settings.patch', {'patch': {'actions': actions, 'profiles': [{'id': 'lab-xbackbone', 'label': 'Custom uploader', 'provider': 'custom-http', 'settings': defaults,
                                                                                 'credentials': {'mode': 'session', 'reference': None}}]}, 'expectedRevision': revision()})
    say('new destination', patched['ok'], patched['error'].get('code'))
    time.sleep(2.5)
    cli('ui.customUploader', {'action': 'inspect', 'profileId': 'lab-xbackbone'})
    park()
    shot('02-new-custom-uploader', w)

    # 3. Import .sxcu: the dialog, then XBackBone's own file.
    cli('ui.customUploader', {'action': 'openImport'})
    if until(lambda: window(name='Import a ShareX custom uploader'), 10):
        shot('03-import-dialog', region=frame)
    cli('ui.customUploader', {'action': 'closeImport'})
    time.sleep(0.6)
    imported = cli('ui.customUploader', {'action': 'import', 'path': str(SXCU / 'xbackbone.sxcu')})
    say('import', imported['ok'], imported['error'].get('code'), imported['result'].get('typedSecrets'))
    time.sleep(1.5)
    park()
    shot('04-imported-plain-http-refused', w)

    # The file's address is plain HTTP on the lab network: tick the switch as a user does. The
    # label column holds nothing else that takes a click, so walk down it until the form says so.
    for ry in range(540, 760, 8):
        click(w, 272, ry)
        time.sleep(0.25)
        if cli('ui.customUploader', {'action': 'inspect'})['result'].get('allowInsecureHttp') is True:
            say('allow plain HTTP ticked at y', ry)
            break
    else:
        raise SystemExit('could not tick Allow plain HTTP')
    until(lambda: cli('ui.customUploader', {'action': 'inspect'})['result'].get('saved'), 15)
    park()
    shot('04b-imported-plain-http-allowed', w)
    wheel(w, 9)
    park()
    shot('05-imported-fields-masked', w)

    # 4. Store: the typed value becomes "stored".
    stored = cli('ui.customUploader', {'action': 'store'})
    say('store', stored['ok'], stored['error'].get('code'))
    until(lambda: 'stored' in cli('ui.customUploader', {'action': 'inspect'})['result'].get('storedHint', ''), 20)
    # Storing brings the Credentials card into view; go back to the rows the picture is about.
    wheel(w, -60)
    wheel(w, 9)
    park()
    shot('06-stored-masked', w)

    # 5. Test connection.
    tested = cli('ui.customUploader', {'action': 'test'})
    say('test', tested['ok'], tested['error'].get('code'))
    status = until(lambda: (lambda text: text if ('Connection' in text or 'failed' in text.lower()) and 'Testing' not in text else None)(cli('ui.customUploader', {'action': 'inspect'})['result'].get('status', '')), 60)
    say('test status:', status)
    wheel(w, 40)
    park()
    shot('07-test-connection-result', w)
    timeouts = cli('settings.get')['result']['document']['profiles'][0]['settings']
    say('timeouts after scrolling over them:', timeouts['connectTimeoutMs'], timeouts['requestTimeoutMs'])
    if options.form_only:
        return

    # 6. A real upload, in History, and its link in the real browser.
    png = R / 'own/lab-capture.png'
    picture = Image.new('RGB', (640, 360))
    for yy in range(360):
        for xx in range(640):
            picture.putpixel((xx, yy), (30 + xx * 180 // 640, 60 + yy * 150 // 360, 150 - xx * 80 // 640))
    ImageDraw.Draw(picture).text((24, 20), 'put.gd #1361 synthetic lab capture', fill=(255, 255, 255))
    picture.save(png)
    record = upload(png, 'lab-xbackbone')
    link = record['receipt'].get('directUrl')
    say('uploaded', record['uploadStatus'], link)
    (SHOTS / 'upload.json').write_text(json.dumps({'uploadStatus': record['uploadStatus'], 'link': link, 'historyId': record['id']}, indent=1))
    cli('ui.show', {'view': 'history'})
    time.sleep(1.5)
    cli('ui.history', {'action': 'select', 'ids': [record['id']]})
    time.sleep(1.5)
    park()
    shot('08-history-uploaded', w)
    # Firefox with a throwaway profile: nothing of the desktop user's own profile is opened.
    handler.parent.mkdir(parents=True, exist_ok=True)
    handler.write_text('[Desktop Entry]\nType=Application\nName=Firefox (put.gd lab profile)\nExec=firefox --profile %s --new-instance %%u\n'
                       'MimeType=x-scheme-handler/http;x-scheme-handler/https;\nNoDisplay=true\n' % (R / 'ff'))
    for scheme in ('http', 'https'):
        subprocess.run(['xdg-mime', 'default', handler.name, 'x-scheme-handler/' + scheme], env=XENV)
    opened = cli('history.openLink', {'id': record['id']})
    say('openLink', opened['ok'], opened['error'].get('code'), opened['result'])
    browser = until(lambda: window(name='Mozilla Firefox'), 40, 1.0)
    time.sleep(6)
    if browser:
        # Beside nothing else: the browser alone, clear of the desktop's notification corner.
        x('xdotool', 'windowsize', browser, '1240', '900')
        x('xdotool', 'windowmove', browser, '120', '20')
        x('xdotool', 'windowactivate', browser)
        time.sleep(1.5)
        x('xdotool', 'key', 'Escape')
        time.sleep(1.5)
        park()
        shot('09-browser-shows-upload', browser)
    else:
        say('NO BROWSER WINDOW')
    for own in own_browsers():
        os.kill(own, signal.SIGTERM)
    time.sleep(2)

    # 7. Prepared deletion: the confirmation as History shows it, then the deletion itself.
    x('xdotool', 'windowactivate', '--sync', w)
    time.sleep(1)
    cli('ui.history', {'action': 'select', 'ids': [record['id']]})
    time.sleep(1.2)
    park()
    spot = danger_button(shot('tmp-history', w))
    say('Delete from destination at', spot)
    if spot:
        click(w, spot[0], spot[1])
        if until(lambda: window(name='Delete from destination'), 10):
            time.sleep(1)
            park()
            shot('10-prepared-deletion', region=frame)
            x('xdotool', 'key', 'Escape')
            time.sleep(0.8)
    prepared = cli('delete.prepare', {'ids': [record['id']]})
    if prepared['ok']:
        cli('delete.confirm', {'ids': [record['id']], 'acknowledgement': prepared['result']['acknowledgement']})
        gone = until(lambda: cli('history.detail', {'id': record['id']})['result'].get('remoteStatus') == 'removed', 40)
        say('deleted from History:', bool(gone))
        time.sleep(1.5)
        cli('ui.history', {'action': 'select', 'ids': [record['id']]})
        time.sleep(1.2)
        park()
        shot('11-history-deleted', w)

    # 8. A receiver that gives no deletion URL (Zipline): History says why it offers no deletion.
    if (SXCU / 'zipline.sxcu').is_file():
        added = cli('settings.importUploader', {'path': str(SXCU / 'zipline.sxcu'), 'expectedRevision': revision(), 'profileId': 'lab-zipline', 'credentialMode': 'session', 'allowInsecureHttp': True})
        say('zipline import', added['ok'], added['error'].get('code'))
        if added['ok']:
            kept = upload(png, 'lab-zipline')
            say('zipline upload', kept['uploadStatus'])
            cli('ui.history', {'action': 'select', 'ids': [kept['id']]})
            time.sleep(1.5)
            park()
            shot('14-no-deletion-url', w)

    # 9. Duplicate on retry: a loopback receiver that stores the file and drops the reply.
    procs['fixture'] = subprocess.Popen([sys.executable, options.fixture], stdout=subprocess.PIPE, text=True)
    base = 'http://127.0.0.1:' + procs['fixture'].stdout.readline().strip()
    scripted = R / 'own/scripted.sxcu'
    scripted.write_text(json.dumps({'Version': '17.0.0', 'Name': 'Scripted receiver', 'DestinationType': 'ImageUploader, FileUploader', 'RequestMethod': 'POST', 'RequestURL': base + '/upload/json',
                                    'Headers': {'Authorization': 'Bearer putgd-synthetic-uploader-token-not-real'}, 'Body': 'MultipartFormData', 'FileFormName': 'file',
                                    'URL': '{json:files[0].url}', 'DeletionURL': '{json:files[0].delete}'}))
    scripted.chmod(0o600)
    added = cli('settings.importUploader', {'path': str(scripted), 'expectedRevision': revision(), 'profileId': 'scripted', 'credentialMode': 'session'})
    say('scripted import', added['ok'], added['error'].get('code'))
    import urllib.request

    def receiver(path, body=None):
        request = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(), headers={'Content-Type': 'application/json'}, method='GET' if body is None else 'POST')
        with urllib.request.urlopen(request, timeout=10) as reply:
            return json.loads(reply.read())

    receiver('/__rules', {'rules': [{'call': 'upload', 'store': True, 'drop': True}]})
    lost = upload(png, 'scripted')
    say('lost reply', lost['uploadStatus'], 'stored on the receiver:', len([f for f in receiver('/__state')['files'].values() if not f['deleted']]))
    cli('ui.history', {'action': 'select', 'ids': [lost['id']]})
    time.sleep(1.5)
    park()
    shot('12-retry-may-duplicate', w)
    receiver('/__rules', {'rules': []})
    retried = cli('operation.retry', {'id': lost['operationId']})
    say('retry', retried['ok'], retried['error'].get('code'))
    until(lambda: cli('history.detail', {'id': lost['id']})['result'].get('uploadStatus') == 'uploaded', 40)
    copies = len([f for f in receiver('/__state')['files'].values() if not f['deleted']])
    (SHOTS / 'retry.json').write_text(json.dumps({'copiesOnTheReceiverAfterRetry': copies, 'uploadStatus': cli('history.detail', {'id': lost['id']})['result'].get('uploadStatus')}, indent=1))
    say('after retry: copies on the receiver', copies)
    time.sleep(1.5)
    cli('ui.history', {'action': 'select', 'ids': [lost['id']]})
    time.sleep(1.5)
    park()
    shot('13-after-retry', w)
    (SHOTS / 'tmp-history.png').unlink(missing_ok=True)


try:
    main()
finally:
    cleanup()
