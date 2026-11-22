"""Operate only test-owned transient services on a locked physical lab desktop."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time

import capture
from fixtures import THEMES

root = Path(sys.argv[1]).resolve()
host = sys.argv[2]
build = sys.argv[3]
scenes = sys.argv[4:]
unit_prefix = 'qr1920-' + root.name.split('.')[-1]
runtime = f'/run/user/{os.getuid()}'
live = Path(tempfile.mkdtemp(prefix='r-', dir=root))
out = root / 'results' / build
out.mkdir(parents=True, exist_ok=True)

def exe(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)

def env_from(pid):
    entries = Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
    return dict(p.decode().split('=', 1) for p in entries if b'=' in p)

def session_env():
    compositor = 'cinnamon' if host == 'm74' else 'plasmashell'
    pids = exe('pgrep', '-u', str(os.getuid()), '-x', compositor, capture_output=True).stdout.split()
    sessions = []
    for pid in pids:
        env = env_from(pid)
        if (host == 'm74' and env.get('DISPLAY') == ':0' and env.get('XAUTHORITY')
                or host == 'k72' and env.get('WAYLAND_DISPLAY')):
            sessions.append(env)
    if len(sessions) != 1:
        raise RuntimeError(f'Expected one physical {compositor} session, got {len(sessions)}')
    env = sessions[0]
    keys = ('DISPLAY', 'XAUTHORITY', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 'WAYLAND_DISPLAY')
    env = {key: env.get(key, '') for key in keys}
    if env['WAYLAND_DISPLAY']:
        env['WAYLAND_DISPLAY'] = str(Path(runtime) / env['WAYLAND_DISPLAY'])
    if host == 'm74':
        env['WAYLAND_DISPLAY'] = ''
        env['XDG_SESSION_TYPE'] = 'x11'
    env['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path={runtime}/bus'
    return env

def check_sockets(session):
    paths = [live / 'putgd/session.sock', root / 'off' / 'putgd/session.sock',
             Path(runtime) / 'bus', Path(runtime) / 'pipewire-0', Path(runtime) / 'pulse/native']
    if session['WAYLAND_DISPLAY']:
        paths.append(Path(session['WAYLAND_DISPLAY']))
    if session['DISPLAY'].startswith(':'):
        paths.append(Path('/tmp/.X11-unix') / ('X' + session['DISPLAY'][1:].split('.')[0]))
    for path in paths:
        length = len(os.fsencode(path.resolve()))
        if length > 107:
            raise RuntimeError(f'Unix socket over 107 bytes: {path} ({length})')
        print(f'Socket preflight: {path} ({length} bytes)', flush=True)

def manager_env():
    return {**os.environ, 'XDG_RUNTIME_DIR': runtime}

def launch(name, env, *args):
    command = ['systemd-run', '--user', '--collect', f'--unit={unit_prefix}-{name}']
    command += [f'--setenv={k}={v}' for k, v in env.items()]
    exe(*command, *args, env=manager_env())

def stop(name):
    service = f'{unit_prefix}-{name}.service'
    state = subprocess.run(['systemctl', '--user', 'is-active', service], capture_output=True, text=True, env=manager_env())
    if state.stdout.strip() in ('active', 'activating', 'deactivating', 'reloading'):
        exe('systemctl', '--user', 'stop', service, env=manager_env())
    subprocess.run(['journalctl', '--user', '--no-pager', '-u', service],
                   stdout=(out / f'{name}.journal').open('a'), text=True, check=False)

def konsole_profile(theme):
    profiles = root / 'konsole-data' / 'konsole'
    profiles.mkdir(parents=True, exist_ok=True)
    bg, fg, _, _ = THEMES[theme]
    def channels(s):
        return ','.join(str(ch) for ch in bytes.fromhex(s))
    scheme = 'Solarized' if theme == 'solarized' else 'QuickRedactFixture'
    if theme != 'solarized':
        (profiles / f'{scheme}.colorscheme').write_text(
            '[General]\nDescription=Quick redact fixture\nOpacity=1\n'
            f'[Background]\nColor={channels(bg)}\n[Foreground]\nColor={channels(fg)}\n')
    (profiles / 'QuickRedactFixture.profile').write_text(
        '[General]\nName=QuickRedactFixture\nParent=FALLBACK/\n'
        f'[Appearance]\nColorScheme={scheme}\nFont=DejaVu Sans Mono,11,-1,5,400,0,0,0,0,0\n'
        '[Scrolling]\nScrollBarPosition=2\n')

def show(scene, env):
    surface, *modifiers, theme = scene.split('-')
    env = {**env, 'XDG_RUNTIME_DIR': runtime}
    if surface == 'browser':
        firefox = root / 'firefox'
        firefox.mkdir(exist_ok=True)
        (firefox / 'user.js').write_text(
            'user_pref("browser.aboutwelcome.enabled", false);\n'
            'user_pref("browser.shell.checkDefaultBrowser", false);\n'
            'user_pref("browser.sessionstore.resume_from_crash", false);\n'
            'user_pref("browser.startup.homepage_override.mstone", "ignore");\n'
            'user_pref("datareporting.policy.firstRunURL", "");\n'
            'user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);\n'
            'user_pref("browser.tabs.warnOnClose", false);\n')
        page = f'{theme}-blur.html' if modifiers == ['blur'] else f'{theme}.html'
        launch(scene, {**env, 'MOZ_ENABLE_WAYLAND': '1' if host == 'k72' else '0'}, '/usr/bin/firefox',
               '--new-instance', '--no-remote', '--profile', str(firefox), '--kiosk',
               (root / 'fixture' / page).as_uri())
        return 7
    if host == 'm74':
        launch(scene, {**env, 'XDG_CONFIG_HOME': str(root / 'gconfig'), 'GDK_BACKEND': 'x11', 'GIO_USE_VFS': 'local'},
               str(root / 'scripts/gnome.sh'), str(root), theme)
    else:
        konsole_profile(theme)
        launch(scene, {**env, 'XDG_DATA_HOME': str(root / 'konsole-data'), 'QT_QPA_PLATFORM': 'wayland'},
               '/usr/bin/konsole', '--nofork', '--fullscreen', '--hide-menubar',
               '--profile', 'QuickRedactFixture', '-e', str(root / 'scripts/term.sh'),
               str(root / 'fixture' / f'{theme}.txt'))
    return 6 if host == 'm74' else 2

def main():
    session = session_env()
    check_sockets(session)
    for name in ('live', 'config', 'data', 'cache', 'state'):
        (root / name).mkdir(mode=0o700, exist_ok=True)
    cap_env = {**session, 'XDG_RUNTIME_DIR': str(live), 'PIPEWIRE_RUNTIME_DIR': runtime,
               'PULSE_SERVER': f'unix:{runtime}/pulse/native',
               'QT_QPA_PLATFORM': 'xcb' if host == 'm74' else 'wayland'}
    for name in ('config', 'data', 'cache', 'state'):
        cap_env[f'XDG_{name.upper()}_HOME'] = str(root / name)
    os.environ.update(cap_env)
    if host == 'm74':
        # Back up the original branch. Terminal writes run on a distinct bus with private config.
        proc = exe('/usr/bin/dconf', 'dump', '/org/gnome/terminal/',
                   env={**os.environ, **session, 'XDG_RUNTIME_DIR': runtime,
                        'XDG_CONFIG_HOME': str(Path.home() / '.config')}, capture_output=True)
        original = proc.stdout
        (root / 'gnome-terminal.dconf.backup').write_text(original)
    launch('resident', cap_env, '/usr/bin/putgd', '--background')
    try:
        for i in range(60):
            if (live / 'putgd/session.sock').is_socket():
                time.sleep(.3)
                break
            time.sleep(.25)
        diagnostics = capture.cli('diagnostics')
        capture.cli('capabilities')
        settings = capture.cli('settings.get')
        (root / 'archive').mkdir(mode=0o700, exist_ok=True)
        capture.cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(root / 'archive')}},
                                       'expectedRevision': settings['metadata']['observedRevision']})
        identity = diagnostics['build']
        expected = {'nightly': '65df546861260bcb92f41ce3f24d3130e90e0c11',
                    'candidate': '667738ff4495562fd1dc4be3315683ae841ce63d'}[build]
        if identity['gitTree'] != expected:
            raise RuntimeError(f'Wrong build installed: {identity}')
        version = exe('/usr/bin/putgd', '--version', capture_output=True).stdout.strip()
        package = exe('dpkg-query', '-W', 'putgd', capture_output=True).stdout.strip()
        capture.write_json(out / 'identity.json', {'build': identity, 'display': session['XDG_SESSION_TYPE'],
                                                  'versionOutput': version, 'installedPackage': package})
        print(host, build, version, identity['gitTree'], flush=True)
        failures = []
        for name in (scenes or ['terminal-solarized', 'terminal-github', 'terminal-monokai',
                               'browser-solarized', 'browser-github', 'browser-monokai']):
            if (out / f'{name}-verify.json').exists():
                continue
            try:
                delay = show(name, session)
                time.sleep(delay)
                capture.run(out, name)
                capture.analyze(out, name, root / 'fixture')
            except Exception as error:
                failed = out / 'failed' / (name + '-' + str(time.time_ns()))
                failed.mkdir(parents=True)
                for path in out.glob(name + '-*'):
                    path.rename(failed / path.name)
                failures.append((name, str(error)))
                print(f'{name} attempt failed: {error}', flush=True)
            finally:
                stop(name)
        if failures:
            raise RuntimeError(f'Scenes failed: {failures}')
    finally:
        stop('resident')
        if host == 'm74':
            current = exe('/usr/bin/dconf', 'dump', '/org/gnome/terminal/',
                          env={**os.environ, **session, 'XDG_RUNTIME_DIR': runtime,
                               'XDG_CONFIG_HOME': str(Path.home() / '.config')}, capture_output=True)
            if current.stdout != original:
                raise RuntimeError('Real gnome-terminal dconf changed; investigate before release')
            print('Original gnome-terminal dconf verified unchanged', flush=True)

if __name__ == '__main__':
    main()
