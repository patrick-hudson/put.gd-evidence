import sys,json,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc3';out=Path(r)/'accept';out.mkdir(exist_ok=True)
(out/'install.json').write_text(json.dumps(lab.install(r,appimage='/tmp/pg-c-head.AppImage'),indent=2))
(out/'start.json').write_text(json.dumps(lab.start(r),indent=2))
(out/'version.json').write_text(lab.guest_session(r,'putgd-cli --version-json'))
assert json.loads((out/'version.json').read_text())['gitTree']=='3fb37294ecc722ed18098894c73c32c70eebefcb'
s=lab.cli(r,'settings.get');lab.cli(r,'settings.patch',{'expectedRevision':s['metadata']['acceptedRevision'],'patch':{'actions':{a:{'destination':'local','shortcut':''} for a in ('region','window','desktop','clipboard','edit')},'profiles':[],'archive':{'root':'/home/lab/pg-evidence/captures','keepUploads':True},'preferences':{'notifications':False}}})
rows=[]
for i in range(10):
 if i:
  lab.cli(r,'ui.quit');time.sleep(.5);lab.guest_session(r,'setsid -f putgd-launcher --background > /tmp/pg-cold-'+str(i)+'.log 2>&1 < /dev/null');time.sleep(.5)
  for _ in range(40):
   try:lab.cli(r,'capabilities');break
   except Exception:time.sleep(.1)
 start=time.monotonic();oid=lab.cli(r,'action.invoke',{'action':'desktop'})['operationId']
 for _ in range(120):
  op=next(o for o in lab.cli(r,'operation.recent')['operations'] if o['id']==oid)
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.1)
 row={'restart':i,'milliseconds':round((time.monotonic()-start)*1000),'operation':op};rows.append(row)
 (out/'cold-start-results.json').write_text(json.dumps(rows,indent=2));print(i,op['state'],op['error'],row['milliseconds'],flush=True)
 if op['state']!='completed':
  p=lab.screenshot(r,'cold-failure-'+str(i))['path'];Image.open(p).save(out/('cold-failure-'+str(i)+'.png'))
  (out/('display-'+str(i)+'.txt')).write_text(lab.guest_session(r,'wlopm'))
  break
Image.open(lab.screenshot(r,'cold-final')['path']).save(out/'cold-final.png')
