from pathlib import Path
import json,sys,tarfile,hashlib,re
import numpy as np
from PIL import Image
sys.path.insert(0,'/home/patrick/work/sf1398');from verify_text import verify as textverify
base=Path('/home/patrick/work/svm1398/v2evidence')
def pattern(r,l):
 if l<2:return 65535
 if l<30:return r
 x=(r*2654435761+l*40503+0x9e3779b9)&0xffffffff;x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15;b=x&65535;return b if b not in [0,65535] else 0x5a5a^l
codes=np.array([pattern(*divmod(y,40)) for y in range(60000)],dtype=np.uint32)
def ruler(f,expected,first=0,scale=1,codewidth=None):
 im=np.asarray(Image.open(f).convert('RGB'));h,w,_=im.shape;cw=codewidth or round(w/scale);cell=(cw-76)//16
 xs=np.array([int((64+(c+.5)*cell)*scale) for c in range(16)])
 if xs.max()>=w:return {'ok':False,'size':[w,h],'expectedSize':[round(cw*scale),round(expected*scale)] if expected else None,'error':'capture width smaller than logical rectangle times output scale'}
 got=np.sum((im[:,xs,:].sum(axis=2)<384).astype(np.uint32)<<(np.arange(15,-1,-1,dtype=np.uint32)),axis=1)
 if first is None:
  first=next((i for i in range(len(codes)-min(40,h)) if np.array_equal(got[:min(40,h)],codes[i:i+min(40,h)])), -1)
 if first<0:return {'ok':False,'error':'no unique start','size':[w,h]}
 if scale==1:bad=np.nonzero(got!=codes[first:first+h])[0]
 else:
  bad=np.nonzero(~np.logical_or.reduce([got==codes[np.clip(((np.arange(h)+d)/scale).astype(int)+first,0,len(codes)-1)] for d in [-1,0,1]]))[0]
 unexpected=0
 if scale==1:
  for c in range(16):
   lo=int(64+(c+.12)*cell);hi=min(w,int(64+(c+.88)*cell));want=np.where((codes[first:first+h]>>(15-c))&1,16,250).astype(np.int16)
   unexpected+=int(np.count_nonzero(np.any(np.abs(im[:,lo:hi,:].astype(np.int16)-want[:,None,None])>12,axis=2)))
 return {'unexpectedPixels':unexpected,'ok':len(bad)==0 and unexpected==0 and (expected is None or h==round(expected*scale)),'size':[w,h],'firstPixel':first,'expectedHeight':None if expected is None else round(expected*scale),'badScanlines':len(bad),'firstBad':bad[:8].tolist()}
out=json.loads((base/'analysis.json').read_text()) if (base/'analysis.json').exists() else {}
for k in sys.argv[1] if len(sys.argv)>1 else 'obnk':
 p=base/k
 if (p/'export.tgz').exists() and not (p/'initial').exists():
  (p/'initial').mkdir();tarfile.open(p/'export.tgz').extractall(p/'initial',filter='data')
 root=p/('final' if (p/'final').exists() else 'initial');results={}
 for d in sorted((root/'cases').iterdir()):
  if not d.is_dir() or not (d/'result.json').exists():continue
  r=json.loads((d/'result.json').read_text());f=d/'capture.png';v=None
  if f.exists():
   n=d.name
   if n.startswith(('gtk','qt')):v=textverify(str(f),1500);v['ok']=v['ok'] and v['lines']==1500 and len(v['pitch'])==1
   elif n.startswith('fraction'):v=ruler(f,2400,scale=1.25,codewidth=r.get('capture',{}).get('rect',[0,0,640])[2])
   else:
    expected=24000 if n.startswith(('long','half-on')) else 12000 if n.startswith('half-off') else 2000 if n.startswith('cap') else None if n=='stop' else 2400
    v=ruler(f,expected,first=12000 if n.startswith('half-off') else None if n=='stop' else 0,codewidth=960 if n.startswith(('long','half','cap-notify')) else None)
  log=(d/'helper.log').read_text() if (d/'helper.log').exists() else ''
  results[d.name]={'state':r.get('capture',{}).get('state'),'endReason':r.get('capture',{}).get('endReason'),'error':r.get('error') or r.get('capture',{}).get('error'),'verification':v,'source':re.findall(r'scroll: source[^\n]*',log),'pngSha256':hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None}
 out[k]=results
 print(k,json.dumps({n:{'end':r['endReason'],'verify':r['verification']} for n,r in results.items() if not n.startswith('harness')}),flush=True)
(base/'analysis.json').write_text(json.dumps(out,indent=2))
