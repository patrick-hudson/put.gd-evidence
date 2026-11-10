import json,sys,math
from pathlib import Path
base=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/'work/s1364s2'
rows=[]
for p in sorted((base/'runs').glob('*/results.json')):
 x=json.loads(p.read_text())
 if x.get('error'):rows.append({'case':p.parent.name,'error':x['error']})
 for r in x.get('rounds',[]):
  e=r.get('clips',{}).get('export',{});w=r.get('clips',{}).get('working',{});v={'case':p.parent.name,'build':r.get('build'),'format':r.get('format'),'round':r.get('round'),'pairs':e.get('pairs'),'exportMs':e.get('medianMs'),'workingMs':w.get('medianMs'),'target':abs(e.get('medianMs',9999))<=1000/30,'bound':-45<=e.get('medianMs',9999)<=125,'motion':e.get('motion'),'recordedS':r.get('recordedS'),'clipS':r.get('durationUs',0)/1e6,'pauseStepMs':r.get('captureStepMs'),'exportShiftMs':r.get('exportMinusWorkingMs'),'micLost':r.get('microphoneLostAtStop'),'error':r.get('error'),'problems':r.get('problems'),'tones':e.get('tones'),'readyFollow':r.get('readyFollow'),'afterOutputGone':r.get('afterOutputGone'),'delayedCaptures':r.get('delayedCaptures')}
  cc=e.get('clickCheck')
  if cc:v['rings']=[{k:z.get(k) for k in ['seen','dx','dy','delayMs','firstMs']} for z in cc['rings']]
  rows.append(v)
print(json.dumps(rows,indent=1));(base/'summary.json').write_text(json.dumps(rows,indent=1)+'\n')
