from pathlib import Path
import json,re,hashlib,numpy as np
from PIL import Image
import scroll_run
P=Path('/home/patrick/work/sa2');out={}
for d in sorted(P.iterdir()):
 if not d.is_dir() or not (d/'result.json').exists():continue
 a=json.loads((d/'result.json').read_text());c=a.get('capture',{});f=d/'capture.png';n=d.name;v={}
 if f.exists():
  im=np.asarray(Image.open(f).convert('RGB')).astype(np.int16);h,w,_=im.shape
  if n.startswith(('gtk','qt')):
   gray=np.asarray(Image.open(f).convert('L')).astype(np.int16);part=gray[:,:int(w*.6)];ink=np.abs(part-int(np.median(part)))>60;rows=ink.any(axis=1);delta=np.diff(np.r_[False,rows,False].astype(int));starts=np.where(delta==1)[0];ends=np.where(delta==-1)[0];keys=[hashlib.sha256(np.packbits(ink[x:y]).tobytes()).hexdigest() for x,y in zip(starts,ends)];pitch=np.unique(np.diff(starts)).tolist();v={'bands':len(keys),'distinct':len(set(keys)),'pitch':pitch,'ok':len(keys)==1500 and len(set(keys))==1500 and len(pitch)==1}
  else:
   expected=24000 if n.startswith(('long','postcap','mcp')) else 12000 if n=='half-off' else 2000 if n=='cap' else 600 if n.startswith('stop') else 2400
   first=12000 if n=='half-off' else a.get('viewportFirstPixelCandidates',[0])[0] if n.startswith('stop') else 0
   codes=np.array([scroll_run.pattern(*divmod(y,40)) for y in range(first,first+h)],dtype=np.uint32);bad=0
   for col in range(16):
    want=np.where((codes>>(15-col))&1,16,250);bad+=int(np.count_nonzero(np.any(np.abs(im[:,64+col*55:64+(col+1)*55]-want[:,None,None])>12,axis=2)))
   bad+=int(np.count_nonzero(np.any(np.abs(im[:,944:]-250)>12,axis=2)));v={'ok':bad==0 and h==expected,'fullCellAndMarginMismatchPixels':bad,'firstPixel':first,'height':h,'expectedHeight':expected}
  if n.startswith(('gtk','qt')):
   part=im[:,max(int(w*.8),420):];bg=np.median(part.reshape(-1,3),axis=0);bad=int(np.count_nonzero(np.any(np.abs(part-bg)>12,axis=2)));v['rightBackgroundMismatchPixels']=bad
   expectedEdge=bool(n.startswith('qt') and bad==h and np.all(im[:,-1,:]==[211,212,212]) and np.all(np.abs(part[:,:-1]-bg)<=12))
   v['expectedFixtureRightEdgePixels']=h if expectedEdge else 0;v['ok']=v['ok'] and (bad==0 or expectedEdge)
  v['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 log=(d/'helper.log').read_text() if (d/'helper.log').exists() else ''
 expectedEnd='stopped' if n.startswith('stop') else 'height_cap' if n=='cap' else 'end_of_content'
 status='exact' if v.get('ok') and c.get('endReason')==expectedEnd else 'wrong image' if f.exists() and c.get('endReason') in ['end_of_content','height_cap'] else 'blocked'
 if n.startswith('stop'):
  positions=re.findall(r'position (\d+)',(P/(n+'-fixture.log')).read_text());v['fixtureLast']=int(positions[-1]) if positions else 23400;v['viewportMatches']=v.get('firstPixel')==v['fixtureLast'];v['topReachedFalse']=c.get('topReached',c.get('result',{}).get('topReached')) is False;status='honest early stop' if v.get('ok') and v['viewportMatches'] and v['topReachedFalse'] else 'blocked'
 out[n]={'status':status,'state':c.get('state'),'endReason':c.get('endReason'),'topReached':c.get('topReached',c.get('result',{}).get('topReached')),'verification':v,'source':re.findall(r'scroll: source[^\n]*',log),'wayUp':re.findall(r'scroll: way to the top[^\n]*',log),'error':a.get('error') or c.get('error'),'id':c.get('id')}
(P/'analysis.json').write_text(json.dumps(out,indent=2));print({s:sum(a['status']==s for a in out.values()) for s in sorted(set(a['status'] for a in out.values()))})
