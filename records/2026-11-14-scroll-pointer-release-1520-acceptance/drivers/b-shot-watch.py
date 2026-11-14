from pathlib import Path
import sys,time,json,hashlib,base64
from PIL import Image
sys.path.insert(0,str(Path.home()/'work/s52/tools/lab'));import lab
r=Path.home()/'work/s52/work/lab-runs/b1';root=Path.home()/'work/s1520';seen=set()
while not (root/'b-shot-watch.stop').exists():
 try:
  raw=lab.ssh(str(r),"cat ~/work/s1520/shot-request.json 2>/dev/null || true",timeout=5).strip()
  if raw:
   req=json.loads(raw);seq=req['seq']
   if seq not in seen:
    label=req['label'];name=req['name'];assert label in ['a','b'] and name.replace('-','').isalnum()
    p=root/('b-shot-'+str(seq));ppm=p.with_suffix('.ppm');png=p.with_suffix('.png')
    with lab.QMP(r/'qmp.sock') as q:q.execute('screendump',{'filename':str(ppm)})
    Image.open(ppm).save(png);lab.put(str(r),str(png),'/home/lab/work/s1520/'+label+'/'+name+'.png')
    lab.ssh(str(r),'touch /home/lab/work/s1520/shot-'+str(seq)+'.done',timeout=5);seen.add(seq)
 except Exception as e:print(type(e).__name__,str(e),flush=True)
 time.sleep(.15)
