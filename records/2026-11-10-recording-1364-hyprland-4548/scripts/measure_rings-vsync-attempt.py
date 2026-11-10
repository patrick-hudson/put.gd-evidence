"""Ring-vs-client-flash from recorded pixels, robust to a moving arrow.
A full ring must change at least three quadrants outside radius4; an arrow at
its hotspot occupies one quadrant. Fit the ring centre to the other quadrants.
"""
import pathlib,subprocess,json,math,os
H=pathlib.Path.home();root=H/'n'
def decoded(clip,x,y,box):
 width=2*box
 cmd=['ffmpeg','-v','error','-i',str(clip),'-vf',f'crop={width}:{width}:{x-box}:{y-box}','-vsync','0','-pix_fmt','rgb24','-f','rawvideo','-']
 raw=subprocess.run(cmd,capture_output=True,check=True).stdout
 times=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(clip)]))['frames']
 stamps=[float(f['best_effort_timestamp_time'])*1000 for f in times if 'best_effort_timestamp_time' in f]
 size=width*width*3;assert len(raw)//size==len(stamps),(len(raw)//size,len(stamps))
 zero=stamps[0]
 return [(round(t-zero),raw[i*size:(i+1)*size]) for i,t in enumerate(stamps)]
def solve3(m,b):
 m=[list(row)+[value] for row,value in zip(m,b)]
 for col in range(3):
  pivot=max(range(col,3),key=lambda r:abs(m[r][col]));m[col],m[pivot]=m[pivot],m[col];d=m[col][col]
  if abs(d)<1e-8:return None
  m[col]=[v/d for v in m[col]]
  for row in range(3):
   if row!=col:
    d=m[row][col];m[row]=[a-d*b for a,b in zip(m[row],m[col])]
 return [r[3] for r in m]
def shape(pixels):
 points=[];quads=[0]*4
 for y in range(64):
  for x in range(64):
   dx=x-32;dy=y-32;r=dx*dx+dy*dy
   if not 16<=r<=27*27:continue
   at=(y*64+x)*3;red,g,blue=pixels[at:at+3]
   # Every ring has visible green over the magenta ground; the moving cursor alone is not a ring.
   if g<35:continue
   q=(2 if dy>=0 else 0)+(1 if dx>=0 else 0);quads[q]+=1
   if not(dx>=-2 and dy>=-2):points.append((dx,dy))
 seen=sum(q>=5 for q in quads)>=3
 if not seen:return dict(seen=False,quadrants=quads)
 sx=sum(x for x,y in points);sy=sum(y for x,y in points);n=len(points)
 sxx=sum(x*x for x,y in points);syy=sum(y*y for x,y in points);sxy=sum(x*y for x,y in points)
 v=solve3([[sxx,sxy,sx],[sxy,syy,sy],[sx,sy,n]],[sum(x*(x*x+y*y) for x,y in points),sum(y*(x*x+y*y) for x,y in points),sxx+syy])
 return dict(seen=True,quadrants=quads,pixels=sum(quads),dx=round(v[0]/2,2) if v else None,dy=round(v[1]/2,2) if v else None)
summary=[]
for name in ('m-still','m-sweep','r-still','r-sweep','off','h'):
 run=root/name;data=json.loads((run/'results.json').read_text());entry=data['rounds'][0];clip=next((run/'out').glob('*.mp4'))
 a=list(data['rect']) if data['target']=='region' else [0,0,1280,800]
 flashes=decoded(clip,90-a[0],300-a[1],24)
 # White client effect fills this watch; the central marker never intersects it.
 ons=[t for t,b in flashes if sum(b[1::3])/len(b[1::3])>100]
 clusters=[]
 for t in ons:
  if not clusters or t-clusters[-1][-1]>100:clusters.append([t])
  else:clusters[-1].append(t)
 effects=[c[0] for c in clusters];assert len(effects)==3,(name,effects)
 checks=[]
 for i,((x,y),effect) in enumerate(zip([(200,100),(640,100),(900,100)],effects),1):
  frames=decoded(clip,x-a[0],y-a[1],32);hits=[]
  for t,pixels in frames:
   if effect-300<=t<=effect+900:
    hit=shape(pixels)
    if hit['seen']:hits.append(dict(hit,ms=t))
  first=hits[0] if hits else None;peak=max(hits,key=lambda z:z['pixels']) if hits else None
  checks.append(dict(click=i,effectMs=effect,seen=bool(hits),firstMs=first['ms'] if first else None,ringMinusEffectMs=first['ms']-effect if first else None,peak=peak))
 ok=all(not c['seen'] for c in checks) if name=='off' else all(c['seen'] and -70<=c['ringMinusEffectMs']<=250 and abs(c['peak']['dx'])<=4 and abs(c['peak']['dy'])<=4 for c in checks)
 result=dict(name=name,ok=ok,reference='visible client flash',checks=checks,audioMedianMs=entry['clips']['export'].get('medianMs'),motion=entry['clips']['export'].get('motion'))
 (run/'ring-effect.json').write_text(json.dumps(result,indent=1));summary.append(result);print(name,ok,[c['ringMinusEffectMs'] for c in checks],flush=True)
 if name!='off' and checks[0]['peak']:
  subprocess.run(['/usr/bin/putgd-record','--preview',str(clip),str(checks[0]['peak']['ms']*1000),str(run/'frames/corrected-click.png')],env=dict(os.environ,QT_QPA_PLATFORM='offscreen'),check=True,capture_output=True)
(root/'ring-effects.json').write_text(json.dumps(summary,indent=1))
