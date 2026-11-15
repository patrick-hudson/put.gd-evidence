import accept as A,json,time,subprocess,sys,re,threading
from pathlib import Path
P=A.P;L=A.L
import rfb
import trial_relative
trial_relative.os.environ.update(A.E)
R=[];sid=None

def rec(label,value):
 R.append({'label':label,'value':value});(P/'extra-results.json').write_text(json.dumps(R,indent=1));print(label,json.dumps(value),flush=True)
def shot(label):
 v=rfb.RFB(5900);v.screenshot(P/(label+'.png'));v.close()
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def waitstate(wanted,timeout=20):
 t=time.time();v={}
 while time.time()-t<timeout:
  v=inspect()
  if v.get('activity') in wanted or v.get('state') in wanted:return v
  time.sleep(.1)
 return v
def begin(driver='user',rect=[240,200,1440,820]):
 global sid
 sid=A.rpc('scroll.prepare',{'rect':rect,'driver':driver,'maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(.5);return inspect()
def end(cancel=False):
 return A.rpc('scroll.cancel' if cancel else 'scroll.stop',{'id':sid})
def wheel(n):mouse.stdin.write(f'w {n}\n');mouse.stdin.flush()
def key(*keys):keyboard.stdin.write(' '.join(map(str,keys))+'\n');keyboard.stdin.flush();time.sleep(.3)
def top():b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(.8)
def point(x,y):
 v=rfb.RFB(5900);v.pointer(x,y);v.close();time.sleep(.2)
def relclick(button):
 log=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*'+button+r' (-?\d+),(-?\d+) (\d+)x(\d+)',log))[-1];x,y,w,h=map(int,m.groups());x+=w//2;y+=h//2
 sx,sy=960,540
 if A.E.get('XDG_SESSION_TYPE')=='x11':
  old,actual,wid=trial_relative.x11_bar(log);x+=actual[0]-old[0];y+=actual[1]-old[1]
  at=dict(l.split('=',1) for l in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=A.E,text=True).splitlines());sx,sy=int(at['X']),int(at['Y'])
 else:point(960,540)
 steps=150
 for i in range(1,steps+1):
  dx=round((x-sx)*i/steps)-round((x-sx)*(i-1)/steps);dy=round((y-sy)*i/steps)-round((y-sy)*(i-1)/steps)
  mouse.stdin.write(f'm {dx} {dy}\n');mouse.stdin.flush();time.sleep(.01)
 mouse.stdin.write('d\n');mouse.stdin.flush();time.sleep(.06);mouse.stdin.write('u\n');mouse.stdin.flush();time.sleep(.4)
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
 import trial_relative; trial_relative.flat()
 keyboard=subprocess.Popen(['sudo','-n','python3',str(P/'ukey.py')],stdin=subprocess.PIPE,text=True);time.sleep(1)
 top();rec('waiting',begin());shot('bar-waiting');point(960,540);wheel(3);time.sleep(1);rec('following',inspect());shot('bar-following')
 key(107);time.sleep(1);rec('lost',waitstate(['lost']));shot('bar-lost')
 key(102);time.sleep(1);rec('found-user',waitstate(['following']));shot('bar-found-user');rec('done-user',end())
 top();rec('auto',begin('putgd'));shot('bar-auto');time.sleep(2);mouse.stdin.write('m 80 0\n');mouse.stdin.flush();rec('paused-pointer',waitstate(['paused']));shot('bar-paused-pointer');point(960,540);wheel(3);time.sleep(1);relclick('autoScroll');rec('resumed-mixed',inspect());time.sleep(3);rec('done-mixed',end())
 # Keyboard shortcut names itself and finishes the same running session.
 settings=A.rpc('settings.get');d=settings['document'];old=d['actions']['scroll']['shortcut'];d['actions']['scroll']['shortcut']='Ctrl+Shift+F7';A.rpc('settings.save',{'document':d,'expectedRevision':settings['metadata']['observedRevision']});A.rpc('settings.reload')
 top();rec('key-start',begin());shot('bar-key');key(29,42,65);rec('key-end',waitstate(['done','failed']))
 if inspect().get('state')=='capturing':end(True)
 settings=A.rpc('settings.get');d=settings['document'];d['actions']['scroll']['shortcut']=old;A.rpc('settings.save',{'document':d,'expectedRevision':settings['metadata']['observedRevision']});A.rpc('settings.reload')
 # Cinnamon's Escape must also reach the page.
 if A.E.get('XDG_SESSION_TYPE')=='x11':
  top();b.js('document.documentElement.setAttribute("data-sfa-esc","0");document.addEventListener("keydown",e=>{if(e.key==="Escape"){let d=document.documentElement;d.setAttribute("data-sfa-esc",String(+d.getAttribute("data-sfa-esc")+1));}});return 0;')
  rec('esc-start',begin());key(1);rec('esc-end',waitstate(['done','failed']));rec('esc-reaches-page',{'events':b.js("return document.documentElement.getAttribute('data-sfa-esc')")})
  if inspect().get('state')=='capturing':end(True)
 # Inside corner, both drivers; Done and Cancel are pressed with the relative mouse.
 for driver,cancel in [('user',False),('putgd',False),('user',True),('putgd',True)]:
  top();rec('inside-'+driver+str(cancel),begin(driver,[0,0,1920,1080]));shot('inside-'+driver+str(cancel));time.sleep(2)
  if cancel:rec('inside-cancel',end(True))
  else:
   relclick('done');rec('inside-done-click',waitstate(['done','failed']))
   if inspect().get('state')=='capturing':rec('inside-forced-stop',end())
 # Agent control on the live page, then MCP through the official SDK.
 top();before=A.rpc('history.list');begin();rec('agent-inspect',inspect());rec('agent-on',A.rpc('scroll.autoScroll',{'id':sid,'on':True}));rec('agent-off',A.rpc('scroll.autoScroll',{'id':sid,'on':False}));rec('agent-cancel',end(True));rec('agent-history-before',before);rec('agent-history-after',A.rpc('history.list'));rec('agent-staging', [str(x.relative_to(P/'d')) for x in (P/'d').rglob('*') if '/scroll/' in str(x)])
 top();p=subprocess.run(([A.os.environ['SFA_MCP_PYTHON'],str(P/'mcptest.py')] if 'SFA_MCP_PYTHON' in A.os.environ else ['toolbox','run','-c','putgd-build',str(P/'tools/mcp/.venv/bin/python'),str(P/'mcptest.py')]),capture_output=True,text=True);rec('mcp-process',{'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 # Blank page's documented limit, both drivers.
 b.navigate('file://'+str(P/'blank.html'));time.sleep(2)
 top();begin('putgd');rec('blank-auto',waitstate(['done','failed'],90));shot('blank-auto-end')
 if inspect().get('state')=='capturing':rec('blank-forced-end',end())
 rec('blank-history',A.rpc('history.list'))
 top();begin();point(960,540);wheel(35);time.sleep(3);rec('blank-user',inspect());shot('blank-user-lost');rec('blank-user-end',end())
finally:
 if sid:
  try:
   if inspect().get('state')=='capturing':end(True)
  except Exception:pass
 for name in ['mouse','keyboard']:
  if name in globals():
   q=globals()[name];q.stdin.write('q\n');q.stdin.flush();q.wait(5)
 L.browser_stop()
