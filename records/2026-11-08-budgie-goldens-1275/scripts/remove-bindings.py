from pathlib import Path
import os,subprocess,ast,time,json
out=Path('/tmp/aprobe')
env=json.loads((out/'environment.json').read_text());os.environ.update({k:v for k,v in env.items() if v})
schema='org.buddiesofbudgie.settings-daemon.plugins.media-keys'
paths=ast.literal_eval((out/'bindings-original.txt').read_text().removeprefix('@as '))
for digit in '123':
 path='/org/buddiesofbudgie/settings-daemon/plugins/media-keys/custom-keybindings/customputgda'+digit+'/'
 target=schema+'.custom-keybinding:'+path
 for k in ['binding','command']:subprocess.run(['gsettings','set',target,k,''],check=True)
subprocess.run(['gsettings','set',schema,'custom-keybindings',repr(paths)],check=True)
for digit in '123':
 path='/org/buddiesofbudgie/settings-daemon/plugins/media-keys/custom-keybindings/customputgda'+digit+'/'
 subprocess.run(['gsettings','reset-recursively',schema+'.custom-keybinding:'+path],check=True)
time.sleep(12)
config=(Path.home()/'.config/budgie-desktop/labwc/rc.xml').read_text();(out/'rc-after.xml').write_text(config)
result={'removedCleanly':'customputgda' not in config,'originalPathsPreserved':subprocess.check_output(['gsettings','get',schema,'custom-keybindings'],text=True).strip()==(out/'bindings-original.txt').read_text(),'realKeyboardDigits':{d:Path('/tmp/putgd-a-digit'+d).exists() for d in '123'}}
(out/'shortcut-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
