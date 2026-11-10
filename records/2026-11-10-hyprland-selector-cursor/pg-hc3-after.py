import sys,json,time,shlex,subprocess
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
from PIL import Image,ImageChops
run='/home/patrick/work/pg-cd/work/lab-runs/hc3';out=Path(run)/'repro-after';out.mkdir(exist_ok=True)
def shell(s):return lab.guest_session(run,s)
def cli(m,p={}):return lab.cli(run,m,p)
def fetch(src,dst):
 s=lab.state(run);subprocess.run(['scp','-q','-i',run+'/identity','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+run+'/known_hosts','-P',str(s['ssh_port']),'lab@127.0.0.1:'+src,str(dst)],check=True)
rows=[]
for i in range(30):
 result=cli('action.invoke',{'action':'region'});oid=result['operationId'];time.sleep((.4,.8,2.5)[i%3])
 shell('python3 /tmp/wayland_pointer.py drag 300 300 600 500 --extent 2304 800 --steps 8')
 end=time.monotonic()+15
 while time.monotonic()<end:
  op=next(o for o in cli('operation.recent')['operations'] if o['id']==oid)
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.1)
 (out/f'op-{i}.json').write_text(json.dumps(op,indent=2))
 if op['state']!='completed':raise RuntimeError(op)
 src=op['items'][0]['local']['path'];fetch(src,out/f'capture-{i}.png')
 shell('python3 /tmp/wayland_pointer.py move 950 650 --extent 2304 800; sleep .3; grim /tmp/reference.png')
 fetch('/tmp/reference.png',out/f'reference-{i}.png')
 a=Image.open(out/f'capture-{i}.png').convert('RGB');b=Image.open(out/f'reference-{i}.png').convert('RGB').crop((300,300,600,500))
 diff=ImageChops.difference(a,b);box=diff.getbbox();diff.save(out/f'diff-{i}.png')
 row={'run':i,'size':a.size,'differenceBox':box,'differentPixels':sum(p!=(0,0,0) for p in diff.getdata())};rows.append(row);print(row,flush=True)
 (out/'results.json').write_text(json.dumps(rows,indent=2))
