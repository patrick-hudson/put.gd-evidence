import sys,json,time
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r=Path('/home/patrick/work/pg-cd/work/lab-runs/bc9');o=r/'accept/C-final-extra'
oid=lab.cli(r,'action.invoke',{'action':'desktop'})['operationId']
for _ in range(100):
 op=lab.cli(r,'operation.inspect',{'id':oid})
 if op['state'] in ('completed','failed','cancelled'):break
 time.sleep(.1)
(o/'unlocked-after.json').write_text(json.dumps(op,indent=2));assert op['state']=='completed'
lab.get(r,op['items'][0]['local']['path'],o/'unlocked-after.png')
for h in (0,1):Image.open(lab.screenshot(r,'extra-unlocked',h)['path']).save(o/f'unlocked-after-head{h}.png')
print('C-final desktop capture after real gtklock unlock completed',flush=True)
