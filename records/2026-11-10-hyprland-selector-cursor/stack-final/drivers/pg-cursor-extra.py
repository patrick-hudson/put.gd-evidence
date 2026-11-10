import sys,json,time
from pathlib import Path
from PIL import Image,ImageChops
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
name,label=sys.argv[1:];r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept'/label;o.mkdir(exist_ok=True)
def shell(s):return lab.guest_session(r,s)
def start(action,delay=0):
 p={'action':action}
 if delay:p['delaySeconds']=delay
 return lab.cli(r,'action.invoke',p)['operationId']
def wait(oid):
 for _ in range(150):
  op=lab.cli(r,'operation.inspect',{'id':oid})
  if op['state'] in ('completed','failed','cancelled'):return op
  time.sleep(.1)
 raise RuntimeError('Operation did not settle')
rows=[];(o/'version.json').write_text(shell('putgd-cli --version-json'))
for i in range(10):
 oid=start('region',3);time.sleep(.8);shell('python3 /tmp/wayland_pointer.py drag 300 300 600 500 --extent 2304 800 --steps 8');region=wait(oid);assert region['state']=='completed',region['error']
 # Repeat immediately with the pointer still at release: no grace period and
 # no cursor-corner exemption. Only then move away for the independent reference.
 repeat=wait(start('repeat'));assert repeat['state']=='completed',repeat['error']
 for kind,op in [('delayed-region',region),('repeat',repeat)]:
  (o/f'{kind}-op-{i}.json').write_text(json.dumps(op,indent=2));lab.get(r,op['items'][0]['local']['path'],o/f'{kind}-{i}.png')
 shell('python3 /tmp/wayland_pointer.py move 950 650 --extent 2304 800; sleep .3; grim /tmp/reference.png');lab.get(r,'/tmp/reference.png',o/f'reference-{i}.png')
 reference=Image.open(o/f'reference-{i}.png').convert('RGB').crop((300,300,600,500))
 for kind in ('delayed-region','repeat'):
  image=Image.open(o/f'{kind}-{i}.png').convert('RGB');assert image.size==(300,200)
  d=ImageChops.difference(image,reference);box=d.getbbox();d.save(o/f'{kind}-diff-{i}.png')
  row={'run':i,'kind':kind,'differentPixels':sum(x!=(0,0,0) for x in d.getdata()),'differenceBox':box};rows.append(row);print(json.dumps(row),flush=True)
 (o/'results.json').write_text(json.dumps(rows,indent=2))
summary={k:{'n':sum(x['kind']==k for x in rows),'affected':sum(x['kind']==k and x['differentPixels']>0 for x in rows)} for k in ('delayed-region','repeat')}
(o/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True);assert all(x['affected']==0 for x in summary.values()),summary
