from pathlib import Path
import subprocess,time,json,os
P=Path('/home/patrick/work/s3a')
while not (P/'accept3-campaign.done').exists():time.sleep(2)
env=dict(os.environ,SF7=str(P));out=[]
for n in ['strict-live-allcolumns.py','verify-live-all.py']:
 with (P/(n+'.console')).open('w') as f:r=subprocess.run(['python3',str(P/n)],env=env,stdout=f,stderr=subprocess.STDOUT)
 out.append({'script':n,'exitCode':r.returncode});print(out[-1],flush=True)
(P/'analysis-status.json').write_text(json.dumps(out,indent=2));(P/'analysis.done').write_text('done')
