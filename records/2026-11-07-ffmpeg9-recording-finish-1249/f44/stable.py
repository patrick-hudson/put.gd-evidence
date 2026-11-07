from pathlib import Path
import os,subprocess,json,statistics,sys
from PIL import Image,ImageChops,ImageStat
r=Path.home()/'work/r9b';results={}
for name in sys.argv[1:]:
 s=json.loads((r/name/'results.json').read_text());rows=[]
 for row in s.get('rounds',[]):
  b=row['build'];fmt=row['format'];clip=r/name/'out'/f'{b}-{fmt}-1.{fmt}'
  if not clip.exists():continue
  start=2000000;end=max(start,row.get('durationUs',0)-150000);times=[round(start+(end-start)*i/7) for i in range(8)];frames=[]
  if fmt in ['gif','webp']:
   im=Image.open(clip);seq=[];t=0
   for i in range(im.n_frames):
    im.seek(i);seq.append((t,im.convert('L').copy()));t+=im.info.get('duration',1000/15)*1000
   frames=[next((f for at,f in reversed(seq) if at<=x),seq[0][1]) for x in times]
  else:
   ad=r/'extract'/f'appdir-{b}'/'squashfs-root'
   for i,t in enumerate(times):
    f=r/name/'frames'/f'{b}-{fmt}-stable-{i}.png'
    z=subprocess.run([str(ad/'usr/bin/putgd-record'),'--preview',str(clip),str(t),str(f)],env=dict(os.environ,APPDIR=str(ad)),capture_output=True)
    if z.returncode==0:frames.append(Image.open(f).convert('L').copy())
  score=statistics.mean(ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(frames,frames[1:])) if len(frames)>1 else None
  rows.append({'build':b,'format':fmt,'motion':round(score,3) if score is not None else None,'sampleTimesUs':times,'decodedFrames':len(frames)})
 results[name]=rows
(r/'stable-motion.json').write_text(json.dumps(results,indent=1)+'\n');print(json.dumps(results))
