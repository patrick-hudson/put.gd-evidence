"""Measure actual client-visible flashes first, then each ring. Never require pointer arrival."""
import json,subprocess,math
from pathlib import Path
base=Path.home()/'work/s1364s2';all=[]
for name in ['click-monitor-corrected','click-region','click-window-corrected','click-off-corrected']:
 root=base/'runs'/name;p=root/'results.json'
 if not p.exists():continue
 for e in json.loads(p.read_text()).get('rounds',[]):
  for kind,clip in e.get('clips',{}).items():
   checks=clip.get('clickCheck',{});presses=checks.get('presses',[])
   if not presses:continue
   filename=str(root/('out' if kind=='export' else 'working')/clip['file'])
   # Broad disjoint windows locate each real flash; wall/call time only selects the search interval.
   spans=[f"{max(0,checks['startCallMs']+p['s']*1000-1800):.0f},{checks['startCallMs']+p['s']*1000+1800:.0f},90,240" for p in presses]
   def watch(spans):
    r=subprocess.run(['/usr/bin/putgd-record','--click-check',filename,*spans],capture_output=True,text=True,check=True)
    return json.loads(r.stdout)['watches']
   effects=watch(spans)
   for i,(press,effect) in enumerate(zip(presses,effects),1):
    row=dict(case=name,clip=kind,click=i,effect=effect,oldPointer=checks.get('pointer',[None]*3)[i-1],oldRing=checks.get('rings',[None]*3)[i-1])
    if not effect.get('seen'):row.update(error='client flash not seen');all.append(row);continue
    ms=effect['firstMs'];ring=watch([f"{max(0,ms-300)},{ms+1000},{press['x']},{press['y']}"])[0]
    row.update(ring=ring,seen=bool(ring.get('seen')),effectMs=ms,ringMs=ring.get('firstMs'),ringMinusEffectMs=ring['firstMs']-ms if ring.get('seen') else None,positionError=round(math.hypot(ring.get('dx',0),ring.get('dy',0)),2) if ring.get('seen') else None)
    all.append(row)
(base/'ring-effect.json').write_text(json.dumps(all,indent=1)+'\n');print(json.dumps(all,indent=1))
