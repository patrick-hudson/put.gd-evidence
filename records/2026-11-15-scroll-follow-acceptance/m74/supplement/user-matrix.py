import subprocess,json,os,time
from pathlib import Path
P=Path.cwd();rows=[]
def run(label,args,extra={}):
 for name in ['putgd-record','firefox','chrome']:assert not subprocess.run(['pgrep','-x',name],capture_output=True,text=True).stdout.strip(),name
 import rfb
 v=rfb.RFB(5900);v.pointer(100,300);v.close();time.sleep(6) # no capture/helper is running: release prior own-toast hover before calibration
 with(P/(label+'.log')).open('w')as f:r=subprocess.run(['python3','-u',*args],env=dict(os.environ,**extra),stdout=f,stderr=subprocess.STDOUT)
 row={'label':label,'exit':r.returncode,'finished':time.time()};rows.append(row);(P/'user-matrix-process-results.json').write_text(json.dumps(rows,indent=1));print(json.dumps(row),flush=True)
 for name in ['putgd-record','firefox','chrome']:assert not subprocess.run(['pgrep','-x',name],capture_output=True,text=True).stdout.strip(),name
for kind in ['firefox','chromium']:
 for page in ['wiki','stackoverflow','github','python','news']:
  run(kind+'-'+page+'-user',['pages-relative.py',kind,page,'user'],{'LAB_NAV_JS':'1'}if kind=='firefox'and page=='news'else{})
run('mixed-safe',['mixed-focused.py'])
run('default-blank',['default-blank-proof.py'])

