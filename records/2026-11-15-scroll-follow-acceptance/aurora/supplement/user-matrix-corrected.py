import subprocess,os,time,json,shutil
from pathlib import Path
P=Path.cwd();rows=[]
def run(label,args,extra={}):
 with(P/(label+'.log')).open('w')as f:r=subprocess.run(['python3','-u',*args],env=dict(os.environ,**extra),stdout=f,stderr=subprocess.STDOUT)
 row={'label':label,'exit':r.returncode,'finished':time.time()};rows.append(row);(P/'user-matrix-corrected-results.json').write_text(json.dumps(rows,indent=1));print(json.dumps(row),flush=True)
 for name in ['putgd-record','firefox','chrome']:assert not subprocess.run(['pgrep','-x',name],capture_output=True,text=True).stdout.strip(),name
for page in ['github','python','news']:
 run('chromium-'+page+'-user-calibration-retry',['pages-relative.py','chromium',page,'user'],{'LAB_TAG':'native-retry'})
 if rows[-1]['exit']:
  shutil.copyfile(P/'calibration.png',P/('calibration-failed-'+page+'.png'))
p=P/'profile-firefox'
if p.exists():p.rename(P/(p.name+'-before-default-'+str(time.time_ns())))
run('default-blank-corrected',['default-blank-proof.py'],{'SFA_NATIVE_POINTER':'1'})

