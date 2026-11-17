"""Default user driver and actual crossing of the supplied blank fixture."""
import accept as A,json,time,subprocess,importlib.util,shutil,os,hashlib
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E);sid=None;mouse=None;rows=[];guest=hasattr(A,'remote')
spec=importlib.util.spec_from_file_location('relative_control',P/'relative-control-native.py');RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(label,value):
 rows.append({'label':label,'value':value});(P/'blank-default-results.json').write_text(json.dumps(rows,indent=1));print(label,json.dumps(value),flush=True)
def shot(label):
 v=rfb.RFB(int(os.environ.get('SF7_VNC','5900')));v.screenshot(P/(label+'.png'));v.close()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-blank-retry-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('file://'+getattr(A,'GP',str(P))+'/blank.html');time.sleep(2)
 command=['python3',str(P/'umouse.py')]if guest else['sudo','-n','python3',str(P/'umouse.py')]
 mouse=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820];C.anchor_before_prepare(960,540);C.click()
 geometry=b.js("let e=document.querySelector('div[style*=\"height:2600\"]');return {start:e.getBoundingClientRect().top+scrollY,end:e.getBoundingClientRect().bottom+scrollY,scrollY,viewport:innerHeight,doc:document.documentElement.scrollHeight,focused:document.hasFocus()};");rec('fixture',geometry)
 offset=(P/'helper.log').stat().st_size;parameters={'rect':C.rect};rec('prepare-parameters',parameters)
 sid=A.rpc('scroll.prepare',parameters)['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1);v=A.rpc('scroll.inspect',{'id':sid});rec('default-waiting',v);assert v.get('driver')=='user'and v.get('activity')=='waiting',v;shot('blank-default-waiting')
 for i in range(100):
  mouse.stdin.write('w 5\n');mouse.stdin.flush();time.sleep(.4);y=b.js('return scrollY;');v=A.rpc('scroll.inspect',{'id':sid});rec('wheel-'+str(i),{'scrollY':y,'activity':v.get('activity'),'height':v.get('height')})
  if v.get('activity')=='lost':shot('blank-default-lost')
  if y+geometry['viewport']>=geometry['doc']-2:break
 else:raise RuntimeError('Real input did not cross the blank stretch')
 time.sleep(2);v=A.rpc('scroll.inspect',{'id':sid});rec('past-blank',v);shot('blank-default-past');rec('end',A.rpc('scroll.stop',{'id':sid}))
 end=A.rpc('scroll.inspect',{'id':sid});expected=end['result']['sha256']
 for _ in range(100):
  images=[f for f in(P/'archive').rglob('*.png')if f.stat().st_size==end['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==expected]
  if images:break
  time.sleep(.1)
 assert images,'exact admitted image not found';shutil.copyfile(images[0],P/'blank-default-capture.png');rec('verified-local-artifact',{'path':str(images[0]),'sha256':expected});rec('after-geometry',b.js(L.INFO));b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1);b.shot_full(P/'blank-default-reference.png');rec('reference-geometry',b.js(L.INFO))
 text=(P/'helper.log').read_bytes()[offset:];(P/'blank-default-helper.log').write_bytes(text);rec('manual-input-protocol',{'injectLines':[l for l in text.decode().splitlines()if'scroll inject:'in l],'stepLines':[l for l in text.decode().splitlines()if'scroll step:'in l]})
 if guest:
  f=A.sync_artifact(sid);shutil.copyfile(f,P/'blank-default-capture.png');rec('verified-artifact',{'path':str(f),'history':A.remote('artifact',sid)})
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')in['capturing','ready','preparing']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 if mouse:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
