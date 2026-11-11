from pathlib import Path
import subprocess,time,sys
P=Path('/home/patrick/work/sr8');host=sys.argv[1]
for _ in range(1200):
 if (P/'campaign-complete').exists():break
 time.sleep(1)
else:raise TimeoutError('campaign completion')
steps=[]
if host=='m74':steps.append(['extras3.py','mint'])
steps += [['scale3.py',host],['extras3.py','cap',host]]
if host!='d69':steps.append(['special.py','user'])
for step in steps:
 r=subprocess.run(['python3']+step,cwd=P,stdout=open(P/('-'.join(step)+'.log'),'w'),stderr=subprocess.STDOUT)
 print(step,r.returncode,flush=True)
(P/'follow-complete').write_text('done')
