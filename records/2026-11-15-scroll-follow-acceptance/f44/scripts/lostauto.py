import accept as A,time,json,subprocess,re
from pathlib import Path
import rfb
import trial_relative
trial_relative.os.environ.update(A.E)
P=A.P;L=A.L;rows=[];sid=None

def log(n,v):rows.append({'label':n,'value':v});(P/'lostauto-results.json').write_text(json.dumps(rows,indent=1));print(n,v,flush=True)
def shot(n):v=rfb.RFB(5900);v.screenshot(P/(n+'.png'));v.close()
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def wait(f,seconds):
 t=time.time()
 while time.time()-t<seconds:
  v=inspect()
  if f(v):return v
  time.sleep(.2)
 return inspect()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 keyboard=subprocess.Popen(['sudo','-n','python3',str(P/'ukey.py')],stdin=subprocess.PIPE,text=True)
 sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820],'driver':'putgd','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(2)
 keyboard.stdin.write('107\n');keyboard.stdin.flush()
 log('handback',wait(lambda v:v.get('driver')=='user' and v.get('pausedBy')=='lost',45));shot('bar-auto-lost')
 keyboard.stdin.write('102\n');keyboard.stdin.flush();log('found',wait(lambda v:v.get('activity')=='paused' and v.get('pausedBy')=='lost',20));shot('bar-auto-found')
 # Real relative mouse to the bar's Auto-scroll, starting from centre via VNC.
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
 import trial_relative; trial_relative.flat()
 m=list(re.finditer(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1];x,y,w,h=map(int,m.groups());x+=w//2;y+=h//2
 sx,sy=960,540
 if A.E.get('XDG_SESSION_TYPE')=='x11':
  old,actual,wid=trial_relative.x11_bar((P/'helper.log').read_text());x+=actual[0]-old[0];y+=actual[1]-old[1]
  at=dict(l.split('=',1) for l in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=A.E,text=True).splitlines());sx,sy=int(at['X']),int(at['Y'])
 else:
  v=rfb.RFB(5900);v.pointer(sx,sy);v.close()
 for i in range(1,151):
  dx=round((x-sx)*i/150)-round((x-sx)*(i-1)/150);dy=round((y-sy)*i/150)-round((y-sy)*(i-1)/150);mouse.stdin.write(f'm {dx} {dy}\n');mouse.stdin.flush();time.sleep(.01)
 mouse.stdin.write('d\n');mouse.stdin.flush();time.sleep(.06);mouse.stdin.write('u\n');mouse.stdin.flush();time.sleep(2);log('resumed',inspect());shot('bar-auto-resumed')
 log('end',wait(lambda v:v.get('state') in ['done','failed'],150))
 if inspect().get('state')=='capturing':log('forced-end',A.rpc('scroll.stop',{'id':sid}))
finally:
 if sid:
  try:
   if inspect().get('state')=='capturing':A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 for name in ['keyboard','mouse']:
  if name in globals():p=globals()[name];p.stdin.write('q\n');p.stdin.flush();p.wait(5)
 L.browser_stop()
