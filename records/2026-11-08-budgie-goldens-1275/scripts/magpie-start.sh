python3 - <<'PY'
from pathlib import Path
import os,json,subprocess
out=Path('/tmp/magpie-a2');out.mkdir(mode=0o700,exist_ok=False)
env=json.loads(Path('/tmp/aprobe/environment.json').read_text());os.environ.update({k:v for k,v in env.items() if v})
config=Path.home()/'.config/budgie-desktop/magpierc'
if config.exists():
 (out/'magpierc-original').write_bytes(config.read_bytes())
config.write_text('[Keybinds]\n'+''.join('probe'+k+'=Ctrl+Shift+'+k+',A1275 probe,/usr/bin/touch,/tmp/magpie-a-'+k+'\n' for k in ['F9','1','2','3']))
(out/'magpierc').write_text(config.read_text())
os.environ['QT_QPA_PLATFORM']='offscreen';os.environ['WAYLAND_DISPLAY']='wayland-77'
args=[str(Path.home()/'magpie-probe'),'--platform-display-libs','mir:wayland','--console-provider','none','--wayland-host','wayland-0','--wayland-surface-title','A1275-Magpie-Mir229','--input-report','log','--app','/usr/bin/foot -a a1275-magpie -T A1275-Magpie-witness -e /usr/bin/tee /tmp/magpie-physical-input']
with (out/'compositor.log').open('w') as log:p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
(out/'pid').write_text(str(p.pid));(out/'launch.json').write_text(json.dumps({'args':args,'pid':p.pid,'qtPlatform':'offscreen (internal Qt config only); Mir output nested visible Wayland','socketBytes':len('/run/user/1000/wayland-77'.encode())},indent=2));print(p.pid)
PY
