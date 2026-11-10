import sys,json,time
from pathlib import Path
sys.argv=['checks','ah7','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland']
exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'<checks>','exec'))
E=Path(ROOT)/'work/acceptance-1363/ah7';E.mkdir(parents=True,exist_ok=True)
print('FRAMES',WORK,flush=True)
rows=[]
for n in range(6):
 head=1;ox,oy=ORIGIN[head];move(ox+500,400);time.sleep(.3);reference=dump(head)
 op,_=start('desktop',10);time.sleep(1.5);during=dump(head)
 record={'id':op,'active':cli('operation.inspect',{'id':op})}
 try: box=countdown_box(reference,during,head,'hit-%d'%n)
 except Exception:
  (E/('hit-%d-operation.json'%n)).write_text(json.dumps(record,indent=2));raise
 x=(box[0]+box[2])//2;y=(box[1]+box[3])//2 if n<5 else box[3]+8
 record.update(box=box,click=[ox+x,oy+y],hit=n<5)
 click(ox+x,oy+y);r=wait(op,25);record['result']=cli('operation.inspect',{'id':op});rows.append(record)
 (E/'hits.json').write_text(json.dumps(rows,indent=2));dump(head).save(E/('hit-%d-after.png'%n))
 ok=(r['state']=='cancelled' and not r['path']) if n<5 else r['state']=='completed' and bool(r['path'])
 print('HIT' if n<5 else 'MISS',n,box,[ox+x,oy+y],r['state'],'PASS' if ok else 'FAIL',flush=True)
 if not ok: raise RuntimeError('Demonstrable pill click failure; see frames and operation record')
 if n==5:fetch(r['path']).save(E/'deliberate-miss-capture.png')
print('5/5 hits cancelled; 1/1 deliberate miss completed',flush=True)
