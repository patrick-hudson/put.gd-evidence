import sys,json,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc5';out=Path(r)/'accept';out.mkdir(exist_ok=True)
if len(sys.argv)==1:
 (out/'install.json').write_text(json.dumps(lab.install(r,appimage='/tmp/pg-c-final.AppImage'),indent=2))
 (out/'start.json').write_text(json.dumps(lab.start(r),indent=2))
for src,dst in [('/home/patrick/work/pg-cd/tools/lab/wayland_toplevels.py','/tmp/wayland_toplevels.py'),('/tmp/pg-env.py','/tmp/pg-env.py'),('/tmp/pg-frame-probe.py','/tmp/pg-frame-probe.py')]:lab.put(r,src,dst)
caps=lab.cli(r,'capabilities');(out/'capabilities.json').write_text(json.dumps(caps,indent=2))
v=lab.guest_session(r,'putgd-cli --version-json');(out/'version.json').write_text(v)
assert json.loads(v)['gitTree']=='03f2f3cde95cc4af4e1c39e4e8f7aada13e33b96'
paths=lab.ssh(r,"python3 - <<'CHECK'\nfrom pathlib import Path\nimport json\np=['/run/user/1000/putgd/session.sock','/run/user/1000/bus']+[str(p) for p in Path('/run/user/1000').glob('wayland-*') if not p.name.endswith('.lock')]\nassert all(len(s.encode())<=107 for s in p)\nprint(json.dumps({s:len(s.encode()) for s in p}))\nCHECK")
(out/'socket-paths.json').write_text(paths)
s=lab.cli(r,'settings.get');lab.cli(r,'settings.patch',{'expectedRevision':s['metadata']['acceptedRevision'],'patch':{'actions':{a:{'destination':'local','shortcut':''} for a in ('region','window','desktop','clipboard','edit')},'profiles':[],'archive':{'root':'/home/lab/pg-evidence/captures','keepUploads':True},'preferences':{'notifications':False}}})
def capture(name):
 oid=lab.cli(r,'action.invoke',{'action':'desktop'})['operationId']
 for _ in range(120):
  op=next(o for o in lab.cli(r,'operation.recent')['operations'] if o['id']==oid)
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.1)
 (out/(name+'.json')).write_text(json.dumps(op,indent=2));print(name,op['state'],op.get('error'),flush=True)
 return op
def shot(name):
 p=lab.screenshot(r,name)['path'];Image.open(p).save(out/(name+'.png'))
if len(sys.argv)>1 and sys.argv[1]=='after-unlock':
 op=capture('unlocked-after');assert op['state']=='completed';shot('unlocked-after');sys.exit()
if '--locked-only' not in sys.argv:
 op=capture('unlocked-before');assert op['state']=='completed'
(out/'probe-unlocked.json').write_text(lab.guest_session(r,'python3 /tmp/pg-frame-probe.py'))
lab.guest_session(r,'busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock Lock');time.sleep(1)
shot('locked')
(out/'locked-state.txt').write_text(lab.guest_session(r,'loginctl show-session 1 -p LockedHint; busctl --user introspect org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock; busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.freedesktop.DBus.Properties GetAll s org.buddiesofbudgie.BudgieScreenlock; python3 /tmp/pg-frame-probe.py'))
before=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort')
for i in range(3):
 op=capture('locked-'+str(i));assert op['state']=='failed' and op['error']['code']=='session_locked' and not op['items']
after=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort');assert before==after
(out/'locked-no-new-files.json').write_text(json.dumps({'before':before.splitlines(),'after':after.splitlines(),'unchanged':True},indent=2))
