from pathlib import Path
import os,subprocess,json,hashlib,statistics
from PIL import Image,ImageChops,ImageStat
root=Path.home()/'work/f9t';p=root/'vaapi2';p.mkdir(mode=0o700);s=json.loads((root/'p6/results.json').read_text());out=[]
for b in ['candidate','nightly']:
 row=next(r for r in s['rounds'] if r['build']==b and r['format']=='mp4');src=root/'p6/working'/row['clips']['working']['file'];ad=root/('analyzer' if b=='candidate' else 'p/appdir-nightly')/'squashfs-root'
 for codec,enc in [('h264','h264_vaapi'),('h265','hevc_vaapi')]:
  dst=p/f'{b}-{codec}.mp4';env=dict(os.environ,APPDIR=str(ad),PUTGD_RECORD_EXPORT_ENCODERS=enc)
  r=subprocess.run([str(ad/'usr/bin/putgd-record'),'--export',str(src),str(dst),'--codec',codec],env=env,capture_output=True,text=True,timeout=120)
  e={'build':b,'codec':codec,'forcedEncoder':enc,'returncode':r.returncode,'log':r.stdout+r.stderr}
  if r.returncode==0:
   e['sha256']=hashlib.sha256(dst.read_bytes()).hexdigest()
   rr=subprocess.run(['ffmpeg','-v','error','-i',str(dst),'-vf','fps=1,scale=320:180','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True)
   n=320*180;frames=[Image.frombytes('L',(320,180),rr.stdout[i:i+n]) for i in range(0,len(rr.stdout)-n+1,n)]
   e['decodedFrames']=len(frames);e['motion']=statistics.mean(ImageStat.Stat(ImageChops.difference(a,b)).mean[0] for a,b in zip(frames,frames[1:]));frames[len(frames)//2].save(p/f'{b}-{codec}.png')
  out.append(e);(root/'vaapi2.json').write_text(json.dumps(out,indent=1)+'\n')
print(json.dumps(out))
