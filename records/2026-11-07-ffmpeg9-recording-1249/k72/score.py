from pathlib import Path
import os,subprocess,json,statistics,sys
from PIL import Image,ImageChops,ImageStat
r=Path.home()/'work/f9t';results={}
for name in sys.argv[1:]:
 p=r/name/'results.json'
 if not p.exists():continue
 s=json.loads(p.read_text());rows=[]
 for row in s.get('rounds',[]):
  b=row['build'];fmt=row['format'];clip=r/name/'out'/f'{b}-{fmt}-1.{fmt}'
  if not clip.exists():continue
  dur=row.get('durationUs',0);start=1000000;end=max(start,dur-150000);times=[round(start+(end-start)*i/7) for i in range(8)];frames=[]
  if fmt in ['gif','webp']:
   im=Image.open(clip);seq=[];t=0
   for i in range(im.n_frames):
    im.seek(i);f=im.convert('L').copy();seq.append((t,f));t+=im.info.get('duration',1000/15)*1000
   for x in times:frames.append(next((f for at,f in reversed(seq) if at<=x),seq[0][1]))
  else:
   ad=r/('analyzer' if b=='candidate' else 'p/appdir-nightly')/'squashfs-root'
   for i,t in enumerate(times):
    f=r/name/'frames'/f'{b}-{fmt}-stable-{i}.png'
    z=subprocess.run([str(ad/'usr/bin/putgd-record'),'--preview',str(clip),str(t),str(f)],env=dict(os.environ,APPDIR=str(ad)),capture_output=True)
    if z.returncode==0:frames.append(Image.open(f).convert('L').copy())
  score=statistics.mean(ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(frames,frames[1:])) if len(frames)>1 else None
  rows.append({'build':b,'format':fmt,'score':round(score,3) if score is not None else None,'sampleTimesUs':times,'decodedFrames':len(frames),'afterResumeMotion':round(ImageStat.Stat(ImageChops.difference(frames[-2],frames[-1])).mean[0],3) if len(frames)>1 else None})
 results[name]=rows
(r/'stable-motion.json').write_text(json.dumps(results,indent=1)+'\n');print(json.dumps(results))
