import sys,json,time,subprocess,shlex
from pathlib import Path
from PIL import Image,ImageChops
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
name,label,count=sys.argv[1],sys.argv[2],int(sys.argv[3]);r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept'/label;o.mkdir(exist_ok=True)
def shell(s):return lab.guest_session(r,s)
def action(action,delay=0):
 p={'action':action}
 if delay:p['delaySeconds']=delay
 return lab.cli(r,'action.invoke',p)['operationId']
def wait(oid):
 for _ in range(100):
  op=lab.cli(r,'operation.inspect',{'id':oid})
  if op['state'] in ('completed','failed','cancelled'):return op
  time.sleep(.1)
 raise RuntimeError('Operation timeout')
(o/'version.json').write_text(shell('putgd-cli --version-json'));rows=[]
for i in range(count):
 oid=action('region');time.sleep((.4,.8,2.5)[i%3]);shell('python3 /tmp/wayland_pointer.py drag 300 300 600 500 --extent 2304 800 --steps 8');op=wait(oid);(o/f'operation-{i}.json').write_text(json.dumps(op,indent=2));assert op['state']=='completed',op['error']
 lab.get(r,op['items'][0]['local']['path'],o/f'capture-{i}.png')
 shell('python3 /tmp/wayland_pointer.py move 950 650 --extent 2304 800; sleep .3; grim /tmp/reference.png');lab.get(r,'/tmp/reference.png',o/f'reference-{i}.png')
 a=Image.open(o/f'capture-{i}.png').convert('RGB');b=Image.open(o/f'reference-{i}.png').convert('RGB').crop((300,300,600,500));assert a.size==(300,200)
 diff=ImageChops.difference(a,b);box=diff.getbbox();diff.save(o/f'diff-{i}.png')
 row={'run':i,'differenceBox':box,'differentPixels':sum(p!=(0,0,0) for p in diff.getdata()),'cornerOnly':bool(box and box[0]>=284 and box[1]>=184),'delaySeconds':0};rows.append(row);(o/'results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
summary={'n':len(rows),'affected':sum(x['differentPixels']>0 for x in rows),'cornerAffected':sum(x['cornerOnly'] for x in rows),'otherDifferences':sum(x['differentPixels']>0 and not x['cornerOnly'] for x in rows)};(o/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
