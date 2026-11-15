import accept as A,trial_relative as T,time,json,subprocess,re,os
from pathlib import Path
import rfb
P=A.P;L=A.L;os.environ.update(A.E);R=[];sid=None
assert A.E['XDG_SESSION_TYPE']=='x11'
def rec(v):R.append(v);(P/'inside-click-results.json').write_text(json.dumps(R,indent=1));print(json.dumps(v),flush=True)
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def at():return {k:int(v) for k,v in (x.split('=',1) for x in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=A.E,text=True).splitlines())}
def shot(n):v=rfb.RFB(5900);v.screenshot(P/(n+'.png'));v.close()
def move(x,y):
 a=at();sx,sy=a['X'],a['Y'];steps=max(1,int(((x-sx)**2+(y-sy)**2)**.5/6))
 for i in range(1,steps+1):
  dx=round((x-sx)*i/steps)-round((x-sx)*(i-1)/steps);dy=round((y-sy)*i/steps)-round((y-sy)*(i-1)/steps);mouse.stdin.write(f'm {dx} {dy}\n');mouse.stdin.flush();time.sleep(.01)
 time.sleep(.1)
def click():
 mouse.stdin.write('d\n');mouse.stdin.flush();time.sleep(.06);mouse.stdin.write('u\n');mouse.stdin.flush()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 mouse=subprocess.Popen(['sudo','-n','python3',str(Path(__file__).parent/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat()
 for driver in (['putgd'] if os.environ.get('SFA_BASELINE')=='1' else ['user','putgd']):
  for button in ['done','cancel']:
   label=driver+'-'+button;b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(.6)
   v=rfb.RFB(5900);v.pointer(960,540);v.close();time.sleep(.2)
   params={'rect':[0,0,1920,1080]}
   if os.environ.get('SFA_BASELINE')!='1':params['driver']=driver
   sid=A.rpc('scroll.prepare',params)['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1)
   if driver=='putgd':
    mouse.stdin.write('m 80 0\n');mouse.stdin.flush()
    for _ in range(100):
     if inspect().get('paused'):break
     time.sleep(.05)
   log=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*'+button+r' (-?\d+),(-?\d+) (\d+)x(\d+)',log))[-1];x,y,w,h=map(int,m.groups());old,actual,wid=T.x11_bar(log);x+=actual[0]-old[0];y+=actual[1]-old[1]
   for targetLabel,target in [('centre',[x+w//2,y+h//2]),('upper',[x+w//2,y+3])]:
    before=inspect()
    if before.get('state')!='capturing':break
    move(*target);cursor=at();props=subprocess.run(['xprop','-id',str(cursor['WINDOW']),'WM_CLASS','_NET_WM_PID','_NET_WM_WINDOW_TYPE'],capture_output=True,text=True).stdout
    shot('inside-probe-'+label+'-'+targetLabel+'-before');click()
    for _ in range(30):
     after=inspect()
     if after.get('state')!='capturing':break
     time.sleep(.1)
    shot('inside-probe-'+label+'-'+targetLabel+'-after');rec({'label':label,'operationId':sid,'targetLabel':targetLabel,'target':target,'cursorBeforeClick':cursor,'windowProperties':props,'barClientRect':actual,'flatProfile':T.x11_profile(),'before':before,'after':after})
   if inspect().get('state')=='capturing':rec({'label':label,'forcedCancel':A.rpc('scroll.cancel',{'id':sid})})
finally:
 if sid:
  try:
   if inspect().get('state')=='capturing':A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 if 'mouse'in globals():mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
