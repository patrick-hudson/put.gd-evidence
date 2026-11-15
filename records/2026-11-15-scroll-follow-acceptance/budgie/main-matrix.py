import subprocess,json,os,time
from pathlib import Path
import accept as A
P=Path.cwd();(P/'main-master.json').write_text(json.dumps({'pid':os.getpid(),'start':time.time(),'pages':['wiki','stackoverflow','github','python','news'],'modes':['user','auto'],'nativeInput':'Guest real relative uinput; independent read-only compositor cursor observer; all-local AppImage resident.'},indent=1));rows=[]
for page in ['wiki','stackoverflow','github','python','news']:
 for mode in ['user','auto']:
  assert not A.remote('helper-pids')
  env=dict(os.environ)
  if page=='news':env['LAB_NAV_JS']='1'
  label=page+'-'+mode
  with(P/(label+'.log')).open('w')as f:r=subprocess.run(['python3','-u','pages-relative.py','firefox',page,mode],env=env,stdout=f,stderr=subprocess.STDOUT)
  row={'page':page,'mode':mode,'exit':r.returncode,'finished':time.time()};rows.append(row);(P/'main-process-results.json').write_text(json.dumps(rows,indent=1));print(json.dumps(row),flush=True)
  assert not A.remote('helper-pids'),'A capture did not clean up after '+label
