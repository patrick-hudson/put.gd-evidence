import sys,json,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc1';out=Path(r)/'repro';out.mkdir(exist_ok=True)
s=lab.cli(r,'settings.get');patch={'actions':{a:{'destination':'local','shortcut':''} for a in ('region','window','desktop','clipboard','edit')},'archive':{'root':'/home/lab/pg-evidence/captures','keepUploads':True},'preferences':{'notifications':False}}
lab.cli(r,'settings.patch',{'expectedRevision':s['metadata']['acceptedRevision'],'patch':patch})
(out/'capabilities.json').write_text(json.dumps(lab.cli(r,'capabilities'),indent=2))
(out/'probe-unlocked.json').write_text(lab.guest_session(r,'python3 /tmp/pg-frame-probe.py'))
lab.guest_session(r,'busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock Lock')
time.sleep(1)
(out/'locked-state.txt').write_text(lab.guest_session(r,'loginctl show-session 1 -p LockedHint; busctl --user introspect org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock; busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.freedesktop.DBus.Properties GetAll s org.buddiesofbudgie.BudgieScreenlock; python3 /tmp/pg-frame-probe.py'))
result=lab.cli(r,'action.invoke',{'action':'desktop'});oid=result['operationId']
for i in range(100):
 op=next(o for o in lab.cli(r,'operation.recent')['operations'] if o['id']==oid)
 if op['state'] in ('completed','failed','cancelled'):break
 time.sleep(.1)
(out/'locked-capture-operation.json').write_text(json.dumps(op,indent=2));print(op['state'],op['error'],flush=True)
if op['state']=='completed':lab.get(r,op['items'][0]['local']['path'],out/'locked-capture.png')
print((out/'locked-state.txt').read_text(),flush=True)
