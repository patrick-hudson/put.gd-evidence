from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,time,statistics,hashlib,sys
r=Path.home()/'work/r9b'/sys.argv[1];out=r/'stable-motion.json';rows=[]
for attempt in range(300):
 try:data=json.loads((r/'results.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):time.sleep(2);continue
 for row in data['rounds']:
  key=(row['build'],row['format'])
  if any((x['build'],x['format'])==key for x in rows):continue
  p=r/'out'/f"{key[0]}-{key[1]}-1.{key[1]}"
  if not p.exists():continue
  im=Image.open(p);seq=[];t=0
  for i in range(im.n_frames):
   im.seek(i);seq.append((t,im.convert('L').copy()));t+=im.info.get('duration',1000/15)*1000
  start=2000000;end=max(start,row['durationUs']-150000);times=[round(start+(end-start)*i/7) for i in range(8)]
  frames=[next((f for at,f in reversed(seq) if at<=x),seq[0][1]) for x in times]
  score=statistics.mean(ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(frames,frames[1:]))
  rows.append(dict(build=key[0],format=key[1],motion=round(score,3),sampleTimesUs=times,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),deletedExactExport=p.name))
  out.write_text(json.dumps(rows,indent=1)+'\n');p.unlink()
  w=r/'working'/row['clips']['working']['file'];w.unlink(missing_ok=True)
 if len(rows)>=4:break
 time.sleep(2)
print(json.dumps(rows))
