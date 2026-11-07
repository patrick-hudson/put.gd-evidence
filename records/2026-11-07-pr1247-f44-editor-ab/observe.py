import pathlib,sys,os,json,time,shlex
home=pathlib.Path.home();root=home/'nd';sys.path.insert(0,str(root));os.chdir(root)
from tools.lab import lab
base=home/'work/f44-editor-ab-1247'
script='''python3 - <<'OBS'
import json,pathlib,subprocess,dbus,os
w=dbus.Interface(dbus.SessionBus().get_object('org.gnome.Shell','/org/putgd/LabWitness'),'org.putgd.LabWitness')
windows=json.loads(str(w.Windows(timeout=3)))
logs=[]
for root in pathlib.Path('/dev/shm').glob('a????????'):
 p=root/'app.log'
 if p.is_file():
  lines=[line for line in p.read_text(errors='replace').splitlines() if 'Resident started' in line]
  logs.append(dict(root=str(root),startup=lines))
print(json.dumps(dict(windows=windows,logs=logs)))
OBS
'''
seen=set()
for i in range(600):
 for label in ['c1','n1b','c2b','n2']:
  out=base/label
  if not (out/'identity.json').exists() or (out/'retirement.json').exists():continue
  for attempt in [1,2]:
   target=out/f'edit_upload-{attempt}'
   key=(label,attempt)
   if not target.exists() or key in seen or (target/'terminal.json').exists():continue
   run=json.loads((out/'identity.json').read_text())['run']
   # state stores run? use own run path from qmp field or locate id
   runs=[p.parent for p in (root/'work/lab-runs').glob('ab*/state.json') if json.loads(p.read_text())['id']==run['id']]
   if len(runs)!=1:continue
   try:
    d=json.loads(lab.guest_session(runs[0],script,timeout=10));d['at']=time.time()
    with (out/f'edit-{attempt}-observer.jsonl').open('a') as f:f.write(json.dumps(d)+'\n')
   except Exception:pass
   if (target/'terminal.json').exists():seen.add(key)
 if (base/'n2/retirement.json').exists():break
 time.sleep(3)
