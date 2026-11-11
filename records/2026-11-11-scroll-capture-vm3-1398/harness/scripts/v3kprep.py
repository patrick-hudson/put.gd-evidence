import sys,json,shlex,subprocess
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/k3';o=B/'v3evidence/k'
code="""from pathlib import Path
p=Path('/tmp/v3/cases')
for d in list(p.iterdir()):
 if d.name.startswith('clean') or d.name=='user':d.rename(d.with_name('harness-wall-restart-'+d.name))
"""
lab.guest_session(r,'python3 -c '+shlex.quote(code))
for args in [['v3visual.py','user','k']]:
 p=subprocess.run(['python3',str(B/args[0])]+args[1:],capture_output=True,text=True);(o/'user-corrected.log').write_text(p.stdout+p.stderr);print('user',p.returncode,flush=True)
lab.guest_session(r,'kill '+(o/'browser.pid').read_text().strip()+' || true')
p=subprocess.run(['python3',str(B/'v3host.py'),'browser','k'],capture_output=True,text=True);print('browser ready',p.returncode,flush=True)
