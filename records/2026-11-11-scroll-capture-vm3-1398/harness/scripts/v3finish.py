import sys,subprocess,time,concurrent.futures,json
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
keys=sys.argv[1]
def go(k):
 o=B/'v3evidence'/k;r=B/'repo/work/lab-runs'/(k+'3')
 while not (o/'clean20.console').exists():time.sleep(2)
 time.sleep(2)
 for f,n in [(B/'v3guest.py','v3guest.py'),(Path('/home/patrick/work/sf1398/qt_fixture.py'),'v3ruler.py')]:lab.put(r,f,'/home/lab/'+n)
 for args in [['v3mcps.py',k],['v3host.py','text',k],['v3host.py','extras',k],['v3visual.py','fraction',k],['v3visual.py','user',k],['v3host.py','export',k]]:
  print(k,' '.join(args),'START',flush=True)
  p=subprocess.run(['python3',str(B/args[0])]+args[1:],capture_output=True,text=True);(o/('-'.join(args)+'.log')).write_text(p.stdout+p.stderr);print(k,' '.join(args),'END',p.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(2) as ex:list(ex.map(go,keys))
