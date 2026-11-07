import json,os,sys,subprocess,statistics
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
root=Path.home()/'work/f9t'; reports={}
def diff(a,b):return round(statistics.mean(ImageStat.Stat(ImageChops.difference(a.convert('L'),b.convert('L'))).mean),3)
for name in sys.argv[1:]:
 run=root/name
 if not (run/'results.json').exists():continue
 s=json.loads((run/'results.json').read_text()); extra=[]
 for row in s.get('rounds',[]):
  b=row['build'];fmt=row['format'];clip=run/'out'/f'{b}-{fmt}-1.{fmt}'
  if not clip.exists():continue
  helper=run/f'appdir-{b}/squashfs-root'
  if not helper.exists():helper=root/('analyzer' if b=='candidate' else 'p/appdir-nightly')/'squashfs-root'
  env=dict(os.environ,APPDIR=str(helper))
  e={'build':b,'format':fmt};dur=row.get('durationUs',0)
  if fmt in ['gif','webp']:
   im=Image.open(clip);n=im.n_frames;im.seek(max(0,n-22));a=im.convert('RGB').copy();im.seek(n-2);c=im.convert('RGB').copy();e['postResumeMotion']=diff(a,c)
  else:
   frames=[]
   for i,t in enumerate([max(0,dur-1500000),max(0,dur-200000)]):
    p=run/'frames'/f'{b}-{fmt}-post-{i}.png'
    r=subprocess.run([str(helper/'usr/bin/putgd-record'),'--preview',str(clip),str(t),str(p)],env=env,capture_output=True)
    if r.returncode==0:frames.append(Image.open(p).copy())
   if len(frames)==2:e['postResumeMotion']=diff(*frames)
   p=run/'frames'/f'{b}-{fmt}-poster.png'
   with clip.open('rb') as src,p.open('wb') as out:
    r=subprocess.run([str(helper/'usr/bin/putgd-record'),'--poster','100000000'],stdin=src,stdout=out,stderr=subprocess.PIPE,env=env)
   e['posterExit']=r.returncode
   if r.returncode==0:
    im=Image.open(p);e['posterSize']=im.size;e['posterDurationMs']=im.info.get('putgd-duration-ms')
   else:p.unlink()
  extra.append(e)
 reports[name]=extra
(root/'analysis.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports))
