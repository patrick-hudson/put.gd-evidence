"""Install one published nightly package on this builder, refusing any transaction beyond putgd (P6, #2025).

  install.py WORK PACKAGE PACKAGE_SHA256 HELPER_SHA256
Writes WORK/package-before.txt, install.log, package-check.json, package-after.txt, environment.json
and on GNOME gnome-before.json / gnome-active.json.
"""
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from proton_accept import desktop_environment, installed_helper

work, package, package_sha, helper_sha = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
desktop, session = desktop_environment()
env = dict(os.environ); env.update(session)
c = lambda args: subprocess.run(args, env=env, text=True, capture_output=True)
assert hashlib.sha256(package.read_bytes()).hexdigest() == package_sha, 'package bytes differ from SHA256SUMS'
rpm = package.suffix == '.rpm'
(work / 'package-before.txt').write_text((c(['rpm', '-q', 'putgd']) if rpm else c(['dpkg-query', '-W', 'putgd'])).stdout)
if desktop == 'gnome-shell':
    r = {k: c(['gsettings', 'get', 'org.gnome.shell', k]).stdout.strip() for k in ('enabled-extensions', 'disable-user-extensions')}
    r['putgd'] = c(['gnome-extensions', 'info', 'putgd@put.gd']).stdout
    r['appindicator'] = c(['gnome-extensions', 'info', 'appindicatorsupport@rgcjonas.gmail.com']).stdout
    (work / 'gnome-before.json').write_text(json.dumps(r, indent=2) + '\n')
# Read the transaction first: only putgd may change.
if rpm:
    plan = c(['sudo', '-n', 'dnf', '--assumeno', '--setopt=install_weak_deps=False', 'install', str(package)])
    text = plan.stdout + plan.stderr
    lines = [l for l in text.splitlines() if l.startswith(' ') and ('x86_64' in l or 'noarch' in l)]
    # dnf5 lists an upgrade's old package as an indented 'replacing NAME' line under it.
    names = sorted({(l.split()[1] if l.split()[0] == 'replacing' else l.split()[0]) for l in lines})
else:
    plan = c(['sudo', '-n', 'apt-get', '-s', '--no-install-recommends', 'install', str(package)])
    text = plan.stdout + plan.stderr
    names = sorted({l.split()[1] for l in text.splitlines() if l.startswith(('Inst ', 'Remv ', 'Purg '))})
(work / 'transaction-plan.txt').write_text(text)
assert names == ['putgd'], f'transaction would change more than putgd: {names}'
with (work / 'install.log').open('w') as log:
    args = (['sudo', '-n', 'dnf', '-y', '--setopt=install_weak_deps=False', 'install', str(package)] if rpm else
            ['sudo', '-n', 'env', 'DEBIAN_FRONTEND=noninteractive', 'apt-get', '-y', '--no-install-recommends', 'install', str(package)])
    subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True)
helper = installed_helper(helper_sha)
helper['identity'] = json.loads(subprocess.run([helper['path'], '--version'], capture_output=True, text=True, check=True).stdout)
catalog = Path(helper['path']).parent / 'redistribution/SOURCES.json'
helper['sourceCatalogSha256'] = hashlib.sha256(catalog.read_bytes()).hexdigest()
helper['manifestSha256'] = json.loads((Path(helper['path']).parent / 'manifest.json').read_text())['sha256']
assert helper['manifestSha256'] == helper_sha
(work / 'package-check.json').write_text(json.dumps({'package': package.name, 'packageSha256': package_sha, 'helper': helper}, indent=2) + '\n')
(work / 'package-after.txt').write_text((c(['rpm', '-q', 'putgd']) if rpm else c(['dpkg-query', '-W', 'putgd'])).stdout)
if desktop == 'gnome-shell':
    for action in ('disable', 'enable'):
        x = c(['gnome-extensions', action, 'putgd@put.gd']); print(action, x.returncode, x.stderr.strip())
    x = c(['gnome-extensions', 'info', 'putgd@put.gd'])
    (work / 'gnome-active.json').write_text(json.dumps({'info': x.stdout, 'exitCode': x.returncode}, indent=2) + '\n')
    print(x.stdout)
    assert 'State: ACTIVE' in x.stdout, 'putgd@put.gd is not ACTIVE after the upgrade; re-login needed'
    assert 'State: ACTIVE' in c(['gnome-extensions', 'info', 'appindicatorsupport@rgcjonas.gmail.com']).stdout, 'no tray host'
versions = c(['rpm', '-q', 'putgd', 'gnome-shell', 'qt6-qtbase']).stdout if rpm else c(['dpkg-query', '-W', 'putgd', 'cinnamon', 'plasma-workspace', 'kwin-wayland', 'libqt6core6t64', 'libqt6core6']).stdout
(work / 'environment.json').write_text(json.dumps({'kernel': os.uname().release, 'clockTicks': os.sysconf('SC_CLK_TCK'),
    'logicalCpus': os.cpu_count(), 'desktop': desktop, 'packageVersions': versions}, indent=2) + '\n')
print('installed', package.name, 'helper', helper)
