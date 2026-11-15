"""State probe: establish actual document movement before an instant jump."""
import accept as A,json,time,subprocess,re,importlib.util,shutil
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E);sid=None;mouse=None;rows=[];b=None
spec=importlib.util.spec_from_file_location('control',P/'relative-control-native.py');RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(k,v):
 rows.append({'label':k,'value':v});(P/'h2-valid-auto-recovery-results.json').write_text(json.dumps(rows,indent=1));print(k,json.dumps(v),flush=True)
def shot(k):
 v=rfb.RFB(5942);v.screenshot(P/(k+'.png'));v.close()
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def wait(predicate,seconds):
 end=time.time()+seconds
 while time.time()<end:
  v=inspect()
  if predicate(v):return v
  time.sleep(.2)
 return inspect()
try:
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(12)
 view=json.loads((P/'viewport.json').read_text());before=b.js(L.INFO);rect=list(view['rect']);rect[0]+=round(before['x']-view['info']['x']);rect[1]+=round(before['y']-view['info']['y']);rect[3]=min(rect[3],before['h'])
 mouse=subprocess.Popen(['python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=rect;C.anchor_before_prepare(1800,900);C.click()
 offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',{'rect':rect,'driver':'putgd','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid})
 ready=False;deadline=time.time()+45;pre=[]
 while time.time()<deadline:
  v=inspect();position=b.js('return {scrollY,doc:document.documentElement.scrollHeight,viewport:innerHeight};');pre.append({'state':v,'page':position})
  if v.get('activity')=='autoScrolling'and v.get('placed',0)>=3 and position['scrollY']>400:ready=True;break
  if v.get('driver')=='user' or v.get('state') in ['done','failed']:break
  time.sleep(.2)
 rec('auto-movement-precondition',{'pass':ready,'samples':pre});assert ready
 jump=b.js('let before=scrollY;window.scrollBy({top:3000,behavior:"instant"});return {before,after:scrollY};');rec('actual-jump',jump);assert jump['after']-jump['before']>=2900
 v=wait(lambda v:v.get('driver')=='user'and v.get('pausedBy')=='lost',45);rec('handback',v);shot('h2-valid-auto-lost');assert v.get('driver')=='user'and v.get('pausedBy')=='lost'
 rec('actual-return',b.js('window.scrollTo({top:0,behavior:"instant"});return {scrollY};'))
 v=wait(lambda v:v.get('activity')=='paused'and v.get('pausedBy')=='lost',20);rec('found',v);shot('h2-valid-auto-found');assert v.get('activity')=='paused'and v.get('pausedBy')=='lost'
 text=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x,y,w,h=map(int,m.groups());C.move(x+w//2,y+h//2);C.click()
 v=wait(lambda v:v.get('activity')=='autoScrolling',5);rec('resumed-by-real-Auto',v);shot('h2-valid-auto-resumed');assert v.get('driver')=='putgd'and v.get('activity')=='autoScrolling'
 time.sleep(3);rec('intentional-partial-stop',{'purpose':'State-transition probe; whole-page runs and standard-crop continued recovery are retained separately.'})
 v=A.rpc('scroll.stop',{'id':sid});rec('end',v);f=A.sync_artifact(sid);shutil.copyfile(f,P/'h2-valid-auto-recovery-capture.png')
 after=b.js(L.INFO);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1);b.shot_full(P/'h2-valid-auto-recovery-reference.png');(P/'h2-valid-auto-recovery-reference-info.json').write_text(json.dumps({'before':before,'after':after,'viewport':view,'rect':rect},indent=1))
 (P/'h2-valid-auto-recovery-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if inspect().get('state')in ['capturing','ready','preparing']:
    v=A.rpc('scroll.stop',{'id':sid});rec('cleanup-done',v)
    if v.get('state')=='done':A.sync_artifact(sid)
  except Exception as e:rec('cleanup-error',str(e))
 if mouse:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
