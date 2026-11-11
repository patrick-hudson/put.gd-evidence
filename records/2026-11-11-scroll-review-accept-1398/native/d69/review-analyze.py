import json,hashlib,re
from pathlib import Path
import numpy as np
from PIL import Image
import scroll_run
P=Path('/home/patrick/work/sr8');out={}
for f in sorted(P.glob('*/result.json')):
 d=f.parent;n=d.name;a=json.loads(f.read_text());c=a.get('capture',{});png=d/'capture.png';v={}
 if n.startswith('cancel-'):
  out[n]={'status':'control-pass' if a.get('inspect',{}).get('state')=='cancelled' else 'control-failure','reply':a};continue
 if png.exists():
  im=np.asarray(Image.open(png).convert('RGB')).astype(np.int16);h,w,_=im.shape
  if n.startswith(('qtfull','gtkfull')):
   gray=np.asarray(Image.open(png).convert('L')).astype(np.int16);part=gray[:,:int(w*.6)];ink=np.abs(part-int(np.median(part)))>60;delta=np.diff(np.r_[False,ink.any(axis=1),False].astype(int));starts=np.where(delta==1)[0];ends=np.where(delta==-1)[0];keys=[hashlib.sha256(np.packbits(ink[x:y]).tobytes()).hexdigest() for x,y in zip(starts,ends)];pitch=np.unique(np.diff(starts)).tolist();part=im[:,max(int(w*.8),420):];bg=np.median(part.reshape(-1,3),axis=0);bad=int(np.count_nonzero(np.any(np.abs(part-bg)>12,axis=2)));edge=bool(n.startswith('qt') and bad==h and np.all(im[:,-1,:]==[211,212,212]) and np.all(np.abs(part[:,:-1]-bg)<=12));v={'bands':len(keys),'distinct':len(set(keys)),'pitch':pitch,'rightBackgroundMismatch':bad,'expectedFixtureEdge':edge,'ok':len(keys)==1500 and len(set(keys))==1500 and len(pitch)==1 and (bad==0 or edge)}
  else:
   expected=24000 if n.startswith(('long','postcap','mcp','resize')) else 12000 if n=='half-off' else 2000 if n in ['cap','busy-first','history-failure'] else int(n.split('-')[1]) if n.startswith('sticky-') else 600 if n.startswith('stop') else 2400
   first=12000 if n=='half-off' else a.get('viewportFirstPixelCandidates',[0])[0] if n.startswith('stop') else 0
   if n.startswith('switch'):expected=24000
   codes=np.array([scroll_run.pattern(*divmod(first+y,40)) for y in range(max(h,1))],dtype=np.uint32);bad=0
   if n.startswith('sticky-'):
    if expected<40:bad=int(np.count_nonzero(np.any(np.abs(im-[32,80,128])>12,axis=2)))
    else:
     bad=int(np.count_nonzero(np.any(np.abs(im[:40]-[32,80,128])>12,axis=2)))+int(np.count_nonzero(np.any(np.abs(im[-40:]-[128,96,32])>12,axis=2)))
     im=im[40:-40];codes=codes[:len(im)]
   for col in range(16):
    lo=64+col*55;hi=lo+55
    if n.startswith('switch'):
     lo=max(lo,720)
     if hi<=lo:continue
    if n.startswith('sticky-') and expected<40:continue
    want=np.where((codes[:len(im)]>>(15-col))&1,16,250);bad+=int(np.count_nonzero(np.any(np.abs(im[:,lo:hi]-want[:,None,None])>12,axis=2)))
   if not (n.startswith('sticky-') and expected<40):bad+=int(np.count_nonzero(np.any(np.abs(im[:,944:]-250)>12,axis=2)))
   if n.startswith('switch'):bad+=int(np.count_nonzero(np.any(np.abs(im[:,:720]-102)>12,axis=2)))
   v={'ok':bad==0 and h==expected,'fullCellAndMarginMismatchPixels':bad,'firstPixel':first,'height':h,'expectedHeight':expected}
  v['sha256']=hashlib.sha256(png.read_bytes()).hexdigest()
 end=c.get('endReason');status='exact' if v.get('ok') and end in ['end_of_content','height_cap'] else 'wrong' if png.exists() and end in ['end_of_content','height_cap'] else 'honest' if end in ['stopped','top_not_reached','lost_track','time_limit','layout_changed'] else 'not-run'
 if n.startswith('stop'):
  positions=re.findall(r'position (\d+)',(P/(n+'-fixture.log')).read_text());v['fixtureLast']=int(positions[-1]) if positions else 23400;v['viewportMatches']=v.get('firstPixel')==v['fixtureLast'];v['topReachedFalse']=c.get('topReached',c.get('result',{}).get('topReached')) is False
 out[n]={'status':status,'endReason':end,'verification':v,'id':c.get('id'),'error':a.get('error') or c.get('error')}
user=P/'user';f=user/'verification.json'
if f.exists():out['user']={'status':'exact' if json.loads(f.read_text()).get('pass') else 'wrong','verification':json.loads(f.read_text())}
(P/'review-analysis.json').write_text(json.dumps(out,indent=2));print({s:sum(a['status']==s for a in out.values()) for s in sorted(set(a['status'] for a in out.values()))})
