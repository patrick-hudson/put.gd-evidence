import sys,subprocess,pathlib,json,os
root=pathlib.Path('/home/lab/b1364f');an=root/'an/squashfs-root';rows=[]
for tag in sys.argv[1:]:
 d=root/'r'/tag;x=json.loads((d/'results.json').read_text())
 for e in x['rounds']:
  for kind,c in e.get('clips',{}).items():
   checks=c.get('clickCheck') or {};rings=checks.get('rings') or []
   clip=pathlib.Path(c.get('path',''))
   if not clip.is_file():
    paths=list((d/('out' if kind=='export' else 'working')).glob('*.mp4'))
    if len(paths)!=1: continue
    clip=paths[0]
   spans=[f"{max(0,r['firstMs']-1200)},{r['firstMs']+1500},90,240" for r in rings if r.get('seen')]
   if not spans:continue
   raw=subprocess.run([str(an/'usr/bin/putgd-record'),'--click-check',str(clip),*spans],capture_output=True,text=True,check=True,env=dict(os.environ,APPDIR=str(an)))
   effects=json.loads(raw.stdout)['watches']
   for i,(ring,effect) in enumerate(zip([r for r in rings if r.get('seen')],effects),1):
    rows.append(dict(tag=tag,kind=kind,click=i,ringMs=ring['firstMs'],effectMs=effect.get('firstMs'),delayMs=ring['firstMs']-effect['firstMs'] if effect.get('seen') else None,dx=ring.get('dx'),dy=ring.get('dy'),oldPointerDelayMs=ring.get('delayMs'),effect=effect))
(root/'ring-effect.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=1))
