"""Native End/Home state probe after verified actual document movement; settled UI picture and complete resumed image."""
import accept as A,json,time,subprocess,re,importlib.util,shutil
from pathlib import Path
import rfb,trial_relative as T,shlex
P=A.P;L=A.L;T.os.environ.update(A.E);sid=None;mouse=None;rows=[];pins=[];b=None;keyboard=None
spec=importlib.util.spec_from_file_location('control',P/'relative-control-native.py');RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(k,v):
 rows.append({'label':k,'value':v});(P/'h3-native-auto-recovery-results.json').write_text(json.dumps(rows,indent=1));print(k,json.dumps(v),flush=True)
def shot(k):
 v=rfb.RFB(5943);v.screenshot(P/(k+'.png'));v.close()
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def samplepins():
 v=b.js("const e=[];for(const q of document.querySelectorAll('*')){let s=getComputedStyle(q);if(!['sticky','fixed'].includes(s.position)||s.display==='none'||s.visibility==='hidden')continue;let r=q.getBoundingClientRect();if(r.width>0&&r.height>0)e.push({rect:[r.x,r.y,r.width,r.height]});}return {scrollY,x:mozInnerScreenX,y:mozInnerScreenY,e};")
 nx=v['x']+view['rect'][0]-view['info']['x'];ny=v['y']+view['rect'][1]-view['info']['y'];elements=[]
 for e in v['e']:
  x,y,w,h=e['rect'];x+=nx-rect[0];y+=ny-rect[1];x0=max(0,x);x1=min(rect[2],x+w);y0=max(0,y);y1=min(rect[3],y+h)
  if x1>x0 and y1>y0:elements.append({'rect':[x0,y0,x1-x0,y1-y0]})
 pins.append({'position':{'y':v['scrollY']},'elements':elements})
def wait(predicate,seconds):
 end=time.time()+seconds
 while time.time()<end:
  v=inspect();samplepins()
  if predicate(v):return v
  time.sleep(.2)
 return inspect()
try:
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(12)
 view=json.loads((P/'viewport.json').read_text());before=b.js(L.INFO);rect=list(view['rect']);rect[0]+=round(before['x']-view['info']['x']);rect[1]+=round(before['y']-view['info']['y']);rect[3]=min(rect[3],before['h'])
 mouse=subprocess.Popen(['python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=rect;C.anchor_before_prepare(1800,900);C.click()
 keyboard=subprocess.Popen([*A.SSH,shlex.join(['python3',A.GP+'/ukey-native.py'])],stdin=subprocess.PIPE,text=True);time.sleep(1.3)
 offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',{'rect':rect,'driver':'putgd','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid})
 ready=False;deadline=time.time()+45;pre=[]
 while time.time()<deadline:
  v=inspect();position=b.js('return {scrollY,doc:document.documentElement.scrollHeight,viewport:innerHeight};');pre.append({'state':v,'page':position})
  if v.get('activity')=='autoScrolling'and v.get('placed',0)>=3 and position['scrollY']>400:ready=True;break
  if v.get('driver')=='user' or v.get('state') in ['done','failed']:break
  time.sleep(.2)
 rec('auto-movement-precondition',{'pass':ready,'samples':pre});assert ready
 rec('native-End-before',b.js("window.__sfaKeys=[];window.addEventListener('keydown',e=>__sfaKeys.push({key:e.key,trusted:e.isTrusted,y:scrollY}));return {scrollY};"));keyboard.stdin.write('107\n');keyboard.stdin.flush();time.sleep(.6);rec('native-End-after',b.js('return {scrollY,events:window.__sfaKeys};'))
 v=wait(lambda v:v.get('driver')=='user'and v.get('pausedBy')=='lost',45);rec('handback',v);time.sleep(1);shot('h3-native-auto-lost');assert v.get('driver')=='user'and v.get('pausedBy')=='lost'
 keyboard.stdin.write('102\n');keyboard.stdin.flush();time.sleep(.6);rec('native-Home-after',b.js('return {scrollY,events:window.__sfaKeys};'))
 v=wait(lambda v:v.get('activity')=='paused'and v.get('pausedBy')=='lost',20);rec('found-immediate',v);shot('h3-native-auto-found-immediate');time.sleep(2);v=inspect();rec('found-settled-two-seconds',v);shot('h3-native-auto-found-settled');assert v.get('activity')=='paused'and v.get('pausedBy')=='lost'
 text=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x,y,w,h=map(int,m.groups());C.move(x+w//2,y+h//2);C.click()
 v=wait(lambda v:v.get('activity')=='autoScrolling',5);rec('resumed-by-real-Auto',v);shot('h3-native-auto-resumed');assert v.get('driver')=='putgd'and v.get('activity')=='autoScrolling'
 v=wait(lambda v:v.get('state')in ['done','failed'],180);rec('end-after-native-recovery',v);assert v.get('state')=='done'and v.get('reachedEnd'),v
 rec('end',v);f=A.sync_artifact(sid);shutil.copyfile(f,P/'h3-native-auto-recovery-capture.png')
 after=b.js(L.INFO);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1);b.shot_full(P/'h3-native-auto-recovery-reference.png');(P/'h3-native-auto-recovery-reference-info.json').write_text(json.dumps({'before':before,'after':after,'viewport':view,'rect':rect},indent=1))
 (P/'h3-native-auto-recovery-pinned.json').write_text(json.dumps(pins,indent=1))
 (P/'h3-native-auto-recovery-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if inspect().get('state')in ['capturing','ready','preparing']:
    v=A.rpc('scroll.stop',{'id':sid});rec('cleanup-done',v)
    if v.get('state')=='done':A.sync_artifact(sid)
  except Exception as e:rec('cleanup-error',str(e))
 if keyboard:keyboard.stdin.write('q\n');keyboard.stdin.flush();keyboard.wait(5)
 if mouse:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
