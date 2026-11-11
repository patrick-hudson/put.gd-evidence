import sys,time,subprocess,shlex,json
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k='k';o=B/'v3evidence'/k;r=B/'repo/work/lab-runs/k3'
while not (o/'postcap.console').exists():time.sleep(2)
time.sleep(2)
code="""from pathlib import Path
p=Path('/tmp/v3/cases')
for d in list(p.iterdir()):
 if d.name.startswith(('clean','mcp','gtk','qt')):d.rename(d.with_name('harness-prewall-'+d.name))
"""
lab.guest_session(r,'python3 -c '+shlex.quote(code));old=o/'prewall';old.mkdir(exist_ok=True)
for f in list(o.iterdir()):
 if f.is_file() and f.name.startswith(('clean','mcp','gtk','qt')):f.rename(old/f.name)
for args in [['v3visual.py','user',k],['v3host.py','browser',k],['v3host.py','repeat',k],['v3mcps.py',k],['v3host.py','text',k],['v3host.py','export',k]]:
 print('RETAKE',' '.join(args),'START',flush=True);p=subprocess.run(['python3',str(B/args[0])]+args[1:],capture_output=True,text=True);(o/('retake-'+'-'.join(args)+'.log')).write_text(p.stdout+p.stderr);print('RETAKE',' '.join(args),'END',p.returncode,flush=True)
