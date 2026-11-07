from pathlib import Path
import subprocess,json,os,hashlib,statistics
from PIL import Image,ImageChops,ImageStat
r=Path.home()/'work/f9t';o=r/'hevc-recheck';o.mkdir(mode=0o700);s=json.loads((r/'p6/results.json').read_text());row=next(x for x in s['rounds'] if x['build']=='candidate' and x['format']=='mp4');src=r/'p6/working'/row['clips']['working']['file'];report=[]
for i,b in enumerate(['candidate','nightly','candidate','nightly']):
 ad=r/('analyzer' if b=='candidate' else 'p/appdir-nightly')/'squashfs-root';dst=o/f'{i}-{b}.mp4';env=dict(os.environ,APPDIR=str(ad),PUTGD_RECORD_EXPORT_ENCODERS='hevc_vaapi')
 p=subprocess.run([str(ad/'usr/bin/putgd-record'),'--export',str(src),str(dst),'--codec','h265'],env=env,capture_output=True,text=True)
 e={'round':i,'build':b,'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'exportExit':p.returncode,'exportLog':p.stdout+p.stderr}
 if p.returncode==0:
  d=subprocess.run(['ffmpeg','-v','warning','-i',str(dst),'-vf','fps=1,scale=320:180','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True)
  e['decodeExit']=d.returncode;e['decodeLog']=d.stderr.decode(errors='replace');n=320*180;frames=[Image.frombytes('L',(320,180),d.stdout[j:j+n]) for j in range(0,len(d.stdout)-n+1,n)]
  e['motion']=statistics.mean(ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(frames,frames[1:]));e['frames']=len(frames)
  for j,im in enumerate(frames):im.save(o/f'{i}-{b}-{j}.png')
 report.append(e);(r/'hevc-recheck.json').write_text(json.dumps(report,indent=1)+'\n')
print(json.dumps([(e['build'],e.get('motion'),e.get('decodeLog')) for e in report]))
