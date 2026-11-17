from pathlib import Path
import os,json,subprocess,time
P=Path.cwd();rows=[]
for label,args in [('auto-retry',['retry-auto.py']),('blank-retry',['default-blank-proof.py']),('pause',['controls.py','pause'])]:
 with(P/(label+'.log')).open('w')as f:r=subprocess.run(['python3','-u',*args],env=dict(os.environ,**({'SFA_NATIVE_POINTER':'1'}if label=='pause'else{})),stdout=f,stderr=subprocess.STDOUT)
 if label=='blank-retry':
  d=P/'runs/B5-1';d.mkdir(exist_ok=True,parents=True)
  for f in P.glob('blank-default-*'):
   if f.is_file():f.rename(d/f.name)
  (d/'process.json').write_text(json.dumps({'exit':r.returncode}))
 rows.append({'label':label,'exit':r.returncode,'time':time.time()});(P/'control-process-results.json').write_text(json.dumps(rows,indent=1));print(rows[-1],flush=True)
