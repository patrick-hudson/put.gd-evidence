import pathlib,json,subprocess,os
root=pathlib.Path.home()/'f';results=[]
for name in ('monitor-on','h'):
 d=root/name
 if not (d/'results.json').exists():continue
 x=json.loads((d/'results.json').read_text())
 for entry in x['rounds']:
  if 'clips' not in entry:continue
  clip=d/'out'/('pr-mp4-%d.mp4'%entry['round'])
  if not clip.exists():
   results.append(dict(name=name,error='clip deleted by driver frame gate; not reclassified'));continue
  rings=entry['clips']['export']['clickCheck']['rings']
  spans=[f"{max(0,r['firstMs']-1200)},{r['firstMs']+1500},90,300" for r in rings if r.get('seen')]
  raw=subprocess.run(['/usr/bin/putgd-record','--click-check',str(clip),*spans],capture_output=True,text=True,check=True,env=dict(os.environ,QT_QPA_PLATFORM="offscreen"))
  effects=json.loads(raw.stdout)['watches']
  results.append(dict(name=name,round=entry['round'],clicks=[dict(ring=r,effect=e,ringMinusEffectMs=r['firstMs']-e['firstMs'] if e.get('seen') else None) for r,e in zip(rings,effects)]))
(root/'ring-effects.json').write_text(json.dumps(results,indent=1))
