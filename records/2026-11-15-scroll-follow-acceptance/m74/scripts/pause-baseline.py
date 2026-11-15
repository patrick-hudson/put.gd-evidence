import accept as A,json,time,sys,os
from pathlib import Path
import trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E)
def rpc(m,p):
 p=dict(p)
 if m=='scroll.prepare':p.pop('driver',None)
 return {'ok':True,'result':A.rpc(m,p)}
T.cli=lambda path,method,params:rpc(method,params)
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 sid=rpc('scroll.prepare',{'rect':[240,200,1440,820]})['result']['id'];rpc('scroll.start',{'id':sid});time.sleep(1);rpc('scroll.cancel',{'id':sid})
 import re
 for typ in ['fixed','random']:
  for i in range(10):
   b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1)
   m=list(re.finditer(r'scroll: bar at .*done (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1]
   x,y,w,h=map(int,m.groups());sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop',f'{x+w//2},{y+h//2}','--log',str(P/'helper.log'),'--rel','--label',f'{typ}-{i+1}','--start','2' if typ=='fixed' else '1','--jitter','0' if typ=='fixed' else '5'];T.main()
finally:L.browser_stop()
