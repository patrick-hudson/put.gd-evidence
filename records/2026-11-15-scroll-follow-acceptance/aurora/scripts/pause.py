import accept as A,json,time,subprocess,sys
from pathlib import Path
P=A.P;L=A.L
sys.path.insert(0,str(Path.home()/'work/scroll-session/gnome'))
# Reuse the evidence trial, copied beside this driver by setup.
import trial
trial.cli=lambda path,method,params: {'ok':True,'result':A.rpc(method,params)}
orig=trial.flat
trial.os.environ.update(A.E)
def run(b):
 rows=[]
 for typ in ['fixed','random']:
  for i in range(10):
   b.js('window.scrollTo({top:0,behavior:"instant"}); return 0;');time.sleep(1)
   # Position from a prior helper log line is fixed for the same rectangle.
   import re
   m=list(re.finditer(r'scroll: bar at .*done (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1]
   x,y,w,h=map(int,m.groups());stop=f'{x+w//2},{y+h//2}'
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop',stop,'--log',str(P/'helper.log'),'--rel','--label',f'{typ}-{i+1}','--start','2' if typ=='fixed' else '1','--jitter','0' if typ=='fixed' else '5']
   trial.main()
if __name__=='__main__':
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 try:
  L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
  sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1);A.rpc('scroll.cancel',{'id':sid})
  run(b)
 finally:L.browser_stop()
