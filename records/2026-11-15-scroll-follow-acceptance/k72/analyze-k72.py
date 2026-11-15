import sys,json,re,shutil
from pathlib import Path
import numpy as np
from PIL import Image
P=Path('/home/patrick/work/sfa15');sys.path.insert(0,str(P));import score as S
Image.MAX_IMAGE_PIXELS=None
O=P/'analysis';O.mkdir(exist_ok=True)
scores=[];protocol=[];last=[];inside=[]
for d in sorted((P/'runs').iterdir()):
 if not(d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r.get('capture')or{};text=(d/'helper.log').read_text()
 protocol.append({'name':d.name,'result':c,'secondsPer10000px':c.get('stats',{}).get('elapsedMs',0)*10/c['height']if c.get('height')else None,'manualInjectLines':re.findall(r'^.*scroll inject:.*$',text,re.M),'manualStepLines':re.findall(r'^.*scroll step:.*$',text,re.M),'freshFrameLines':re.findall(r'^.*scroll fresh frame:.*$',text,re.M),'doneFreshFrameLines':re.findall(r'^.*Done.s fresh frame.*$',text,re.M)})
 if '-inside'not in d.name:
  try:scores.append(S.one(d))
  except Exception as e:scores.append({'name':d.name,'error':repr(e)})
 if r.get('mode')=='user'and(d/'saving.png').exists()and(d/'pre-done-pinned.json').exists()and'-inside'not in d.name:
  x,y,w,h=r['rect'];im=Image.open(d/'capture.png').convert('RGB');native=Image.open(d/'saving.png').convert('RGB')
  ref=S.S.Reference.__new__(S.S.Reference);ref.pixels=np.asarray(native.crop((x,y,x+w,y+h)),dtype=np.int16);ref.dx=0;ref.reachable=None;ref.rects=[]
  v=json.loads((d/'pre-done-viewport-info.json').read_text());bias=r['viewport']['rect'][1]-r['viewport']['info']['y'];top=v['y']+bias-y
  if top>0:ref.rects.append((0,0,w,top))
  for e in json.loads((d/'pre-done-pinned.json').read_text()):
   xx,yy,ww,hh=e['rect'];yy+=top;ref.rects.append((max(0,int(xx)-12),max(0,int(yy)-12),min(w,int(xx+ww+1)+12),min(h,int(yy+hh+1)+12)))
  bars=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))
  if bars:
   bx,by,bw,bh=map(int,bars[-1].groups());ref.rects.append((bx-x-4,by-y-4,bx+bw-x+4,by+bh-y+4))
  a=np.asarray(im.crop((0,im.height-h,w,im.height)),dtype=np.int16);last.append({'name':d.name,'nativeBandsEqualTotal':S.tolerant(ref,a),'browserUiTopRows':top,'rowsAtDone':c.get('rowsAtDone'),'method':'Actual native Saving framebuffer at selected region; native initial top bias retained, actual current fixed/sticky rectangles +12px and bar masked. No vertical translation.'})
 if '-inside'in d.name:
  dst=O/(d.name+'-body');dst.mkdir(exist_ok=True);im=Image.open(d/'capture.png').convert('RGB');im.crop((0,86,1920,im.height-40)).save(dst/'capture.png')
  for n in ['reference.png','pinned.json']:shutil.copyfile(d/n,dst/n)
  rr=dict(r,rect=[0,86,1920,954],comparisonTransform={'nativeTop':86,'nativePanel':40,'reference':'Own same-run full-page reference; not borrowed between runs with different fundraiser layout.'});(dst/'result.json').write_text(json.dumps(rr));scores.append(S.one(dst))
  a=np.asarray(im);bartext=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+) inside',text));bx,by,bw,bh=map(int,bartext[-1].groups());dark=a[:,bx:bx+bw].max(2)<70;hits=[]
  for yy,row in enumerate(dark):
   diff=np.diff(np.r_[0,row.astype(np.int8),0]);starts=np.flatnonzero(diff==1);ends=np.flatnonzero(diff==-1)
   if len(starts)and(ends-starts).max()>150:hits.append(yy)
  inside.append({'name':d.name,'hiddenCells':c.get('hiddenCells'),'hiddenRows':c.get('hiddenRows'),'bar':[bx,by,bw,bh],'allDarkRows':hits,'bodyDarkRows':[yy for yy in hits if 86<=yy<im.height-40]});im.crop((0,max(0,im.height-800),im.width,im.height)).save(dst/'native-tail.png')
for name,data in [('scores',scores),('protocol',protocol),('native-last-screen',last),('inside-bar',inside)]: (O/(name+'.json')).write_text(json.dumps(data,indent=1))
print(json.dumps({'scores':scores,'nativeDone':last,'inside':inside}),flush=True)
