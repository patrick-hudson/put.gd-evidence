import json,subprocess
from pathlib import Path
base=Path.home()/'work/s1364s2';rows=[]
for p in sorted((base/'runs').glob('*/results.json')):
 x=json.loads(p.read_text())
 for r in x.get('rounds',[]):
  for kind,c in r.get('clips',{}).items():
   clip=p.parent/('out' if kind=='export' else 'working')/c['file']
   if not clip.is_file():continue
   result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,start_time,duration','-of','json',str(clip)],capture_output=True,text=True)
   rows.append({'case':p.parent.name,'build':r['build'],'format':r['format'],'round':r['round'],'kind':kind,'file':c['file'],'recordedS':r.get('recordedS'),'probe':json.loads(result.stdout) if result.stdout else None,'error':result.stderr,'rc':result.returncode})
(base/'container-probes.json').write_text(json.dumps(rows,indent=1)+'\n');print('Probed',len(rows),'clips')
