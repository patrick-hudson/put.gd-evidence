import sys,os,json,shutil,subprocess,hashlib
from pathlib import Path
sys.argv=['x',"save('final-diagnostics',cli('diagnostics'));save('final-settings',cli('settings.get'));save('guest-identity',guest('cat /etc/os-release; loginctl show-session 1 -p Type -p Desktop -p Active; dpkg-query -W putgd plasma-workspace kwin-wayland libqt6core6t64'))"]
exec(Path('/tmp/ap6-drive.py').read_text())
for n in ['state.json','package.json','qmp-features.json']:
 if (Path(RUN)/n).exists():shutil.copy2(Path(RUN)/n,E/n)
for n in ['install2','start']:
 shutil.copy2('/tmp/ap6-'+n+'.log',E/(n+'.log'))
for p in Path('/tmp/ap6-checks').rglob('*.png'):shutil.copy2(p,E/('driver-'+p.name))
for p in Path('/tmp').glob('p1363-checks-*'):
 if p.is_dir():
  # Only transport directories created by this worker are under /tmp/ap6-checks.
  pass
for n in ['tray-result','window-final','immediate-result']:
 h=json.loads((E/(n+'.json')).read_text());h=h.get('history',h);r=h['records'][0];save(n+'-operation',cli('operation.inspect',{'id':r['operationId']}))
(E/'driver.py').write_text(Path('/tmp/p1363-checks.py').read_text())
(E/'gui-driver.py').write_text(Path('/tmp/ap6-drive.py').read_text())
print('export prepared')
