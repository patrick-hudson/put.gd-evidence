import sys,time,json,subprocess,concurrent.futures,traceback
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398')
s=Path('/home/patrick/work/sf1398/qt_fixture.py').read_text().replace('960','640').replace('600','400').replace('* 55','* 35').replace(', 55,',', 35,')
f=base/'v2fraction-fixture.py';f.write_text(s)
def run(k):
 r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
 def cmd(c):return lab.guest_session(r,c,timeout=300)
 def scale(v):
  c={'o':f'hyprctl keyword monitor Virtual-1,1280x800@74.99,0x0,{v}','b':f'wlr-randr --output Virtual-1 --scale {v}','n':f'kscreen-doctor output.1.scale.{v}','k':f'kscreen-doctor output.1.scale.{v}'}[k]
  (o/('scale-'+v+'.log')).write_text(cmd(c));time.sleep(3)
 try:
  lab.put(r,f,'/home/lab/v2fraction-fixture.py');scale('1.25')
  pid=int(cmd('nohup python3 /home/lab/v2fraction-fixture.py > /tmp/v2/fraction.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4)
  Image.open(lab.screenshot(r,'v2-fraction-ready')['path']).save(o/'fraction-ready.png')
  (o/'fraction.console').write_text(cmd('python3 /home/lab/v2guest.py case fraction 100,100,640,400'))
  Image.open(lab.screenshot(r,'v2-fraction-end')['path']).save(o/'fraction-end.png');cmd('kill '+str(pid));print(k,'fraction END',flush=True)
 except Exception:(o/'fraction-error.txt').write_text(traceback.format_exc())
 finally:scale('1')
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(run,sys.argv[1] if len(sys.argv)>1 else 'obnk'))
