import record_run,subprocess,json
from pathlib import Path
p=Path('/home/patrick/work/sa2');e,_=record_run.session_environment();v={}
for k,f in [('enabled-extensions','extensions-before.txt'),('disabled-extensions','disabled-extensions-before.txt')]:
 before=(p/f).read_text().strip();subprocess.run(['gsettings','set','org.gnome.shell',k,before],env=e,check=True);after=subprocess.check_output(['gsettings','get','org.gnome.shell',k],env=e,text=True).strip();v[k]={'match':before==after,'before':before,'after':after}
(p/'extension-restoration.json').write_text(json.dumps(v,indent=2));print(v)
