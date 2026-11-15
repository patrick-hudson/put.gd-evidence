# Run only with the desktop lease; resident must be stopped before the subsequent re-login.
import json,os,subprocess,sys,ast,hashlib
from pathlib import Path
P=Path.home()/'work/sfa15';D=Path.home()/'.local/share/gnome-shell/extensions/sfa15-pointer@lab'
E=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME']:E.pop(k,None)
if sys.argv[1]=='install':
 assert not D.exists();D.mkdir()
 (D/'extension.js').write_bytes((P/'pointer-witness.js').read_bytes());(D/'metadata.json').write_text(json.dumps({'uuid':'sfa15-pointer@lab','name':'Acceptance cursor observer','description':'Read-only native cursor coordinates for the relative-input test driver.','version':1,'shell-version':['50']}))
 before={k:hashlib.sha256((D/k).read_bytes()).hexdigest()for k in ['extension.js','metadata.json']};(P/'pointer-witness-installed.json').write_text(json.dumps(before,indent=1))
 raw=subprocess.check_output(['gsettings','get','org.gnome.shell','enabled-extensions'],env=E,text=True).strip();v=ast.literal_eval(raw.replace('@as ',''));v.append('sfa15-pointer@lab');subprocess.run(['gsettings','set','org.gnome.shell','enabled-extensions',str(v)],env=E,check=True);print('Installed observer; re-login required')
elif sys.argv[1]=='remove':
 expected=json.loads((P/'pointer-witness-installed.json').read_text());assert set(x.name for x in D.iterdir())==set(expected)
 for n,sha in expected.items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==sha
 for n in expected:(D/n).unlink()
 D.rmdir();print('Removed exact observer files; restore original extension lists and re-login')
