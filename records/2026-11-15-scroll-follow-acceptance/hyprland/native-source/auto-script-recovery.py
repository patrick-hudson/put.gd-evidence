import accept as A,time,json,subprocess,re
from pathlib import Path
import rfb
import trial_relative
import importlib.util
spec=importlib.util.spec_from_file_location("relative_control",A.P/"relative-control-native.py");RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
trial_relative.os.environ.update(A.E)
P=A.P;L=A.L;rows=[];sid=None

def log(n,v):rows.append({'label':n,'value':v});(P/'auto-script-recovery-results.json').write_text(json.dumps(rows,indent=1));print(n,v,flush=True)
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
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(15)
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');trial_relative.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820];C.anchor_before_prepare(1800,900);C.click();focus_before=b.js('return {focused:document.hasFocus(),tag:document.activeElement.tagName,scrollY};');log('content-focus-before',focus_before);assert focus_before['focused']
 before_info=b.js(L.INFO);b.shot_full(P/'auto-script-recovery-before-reference.png')
 sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820],'driver':'putgd','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(2)
 log('stimulus',{'method':'Live page-script scrollBy(3000, instant); native End suppression is tested separately, not replaced as a pass.'});b.js('window.scrollBy({top:3000,behavior:"instant"});return 0;')
 v=wait(lambda v:v.get('driver')=='user' and v.get('pausedBy')=='lost',45);log('handback',v);shot('bar-js-auto-lost');assert v.get('driver')=='user' and v.get('pausedBy')=='lost',v
 b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');v=wait(lambda v:v.get('activity')=='paused' and v.get('pausedBy')=='lost',20);log('found',v);shot('bar-js-auto-found');assert v.get('activity')=='paused' and v.get('pausedBy')=='lost',v
 # The capture is paused by lost; all pointer motion here is relative.
 m=list(re.finditer(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1];x,y,w,h=map(int,m.groups());x+=w//2;y+=h//2
 if A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME'):
  text=(P/'helper.log').read_text();q=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];sh=list(re.finditer(r'the Shell put the bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x+=int(sh[1])-int(q[1]);y+=int(sh[2])-int(q[2])
 if A.E.get('XDG_SESSION_TYPE')=='x11':
  old,actual,wid=trial_relative.x11_bar((P/'helper.log').read_text());x+=actual[0]-old[0];y+=actual[1]-old[1]
 C.move(x,y);C.click();time.sleep(2);v=inspect();log('resumed',v);shot('bar-js-auto-resumed');assert v.get('driver')=='putgd' and v.get('activity')=='autoScrolling',v
 log('end',wait(lambda v:v.get('state') in ['done','failed'],150))
 if inspect().get('state')=='capturing':log('forced-end',A.rpc('scroll.stop',{'id':sid}))
 after_info=b.js(L.INFO);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2);b.shot_full(P/'auto-script-recovery-reference.png');(P/'auto-script-recovery-reference-info.json').write_text(json.dumps({'before':before_info,'after':after_info,'viewport':json.loads((P/'viewport.json').read_text())},indent=1))
finally:
 if sid:
  try:
   if inspect().get('state')=='capturing':A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 for name in ['keyboard','mouse']:
  if name in globals():p=globals()[name];p.stdin.write('q\n');p.stdin.flush();p.wait(5)
 L.browser_stop()
