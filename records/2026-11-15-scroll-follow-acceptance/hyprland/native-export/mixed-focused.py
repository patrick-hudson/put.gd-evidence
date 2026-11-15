import accept as A,time,json,subprocess,importlib.util,re,hashlib,shutil
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E);sid=None;R=[];pins=[]
spec=importlib.util.spec_from_file_location("relative_control",P/"relative-control-native.py");RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(k,v):
 R.append({'label':k,'value':v});(P/'mixed-focused-results.json').write_text(json.dumps(R,indent=1));print(k,json.dumps(v),flush=True)
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def sample():
 v=b.js('const e=[];for(const q of document.querySelectorAll("*")){const s=getComputedStyle(q);if(!["sticky","fixed"].includes(s.position)||s.display==="none"||s.visibility==="hidden")continue;const r=q.getBoundingClientRect();if(r.width>0&&r.height>0)e.push({rect:[r.x,r.y,r.width,r.height],position:s.position,what:(q.tagName+"."+String(q.className)).slice(0,120)});}return {y:scrollY,e};')
 out=[]
 for e in v['e']:
  x,y,w,h=e['rect'];x-=240;y-=200-view[1];x0=max(0,x);y0=max(0,y);x1=min(1440,x+w);y1=min(820,y+h)
  if x1>x0 and y1>y0:out.append(dict(e,rect=[x0,y0,x1-x0,y1-y0]))
 pins.append({'position':{'y':v['y']},'elements':out})
def run_for(seconds):
 end=time.time()+seconds
 while time.time()<end:sample();time.sleep(.25)
def click_auto():
 text=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*autoScroll (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x,y,w,h=map(int,m.groups());x+=w//2;y+=h//2
 if A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME'):
  q=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];s=list(re.finditer(r'the Shell put the bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x+=int(s[1])-int(q[1]);y+=int(s[2])-int(q[2])
 elif A.E.get('XDG_SESSION_TYPE')=='x11':
  old,actual,_=T.x11_bar(text);x+=actual[0]-old[0];y+=actual[1]-old[1]
 C.move(x,y);C.click()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(15)
 view=json.loads((P/'viewport.json').read_text())['rect'];assert view[2:]==[1920,963] if A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME') else True
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820];C.anchor_before_prepare(1800,900);C.click()
 before=b.js(L.INFO);offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',{'rect':C.rect,'driver':'putgd','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid});run_for(2)
 mouse.stdin.write('m 80 0\n');mouse.stdin.flush();time.sleep(.5);v=inspect();rec('paused-by-real-move',v);assert v.get('pausedBy')=='pointer',v
 C.move(1650,990);mouse.stdin.write('w 3\n');mouse.stdin.flush();run_for(1)
 click_auto();run_for(2);v=inspect();rec('resumed-by-real-Auto',v);assert v.get('driver')=='putgd' and v.get('activity')=='autoScrolling',v
 run_for(3);v=A.rpc('scroll.stop',{'id':sid});rec('end',v);assert v.get('scrolledBy')=='both',v
 import find_history;r=find_history.find_operation(A,sid);f=Path(r['local']['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(f,P/'mixed-focused-capture.png')
 after=b.js(L.INFO);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2);sample();b.shot_full(P/'mixed-focused-reference.png')
 (P/'mixed-focused-pinned.json').write_text(json.dumps(pins,indent=1));(P/'mixed-focused-reference-info.json').write_text(json.dumps({'before':before,'after':after,'viewport':json.loads((P/'viewport.json').read_text()),'capture':v,'pinSampling':'Actual visible fixed/sticky DOM rectangles sampled every250ms during the capture and clipped to the selected region. Original reference unchanged.'},indent=1));(P/'mixed-focused-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if inspect().get('state')in['capturing','ready','preparing']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 if 'mouse'in globals():mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
