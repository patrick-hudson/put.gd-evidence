import accept as A,json,time,subprocess,sys
from pathlib import Path
import rfb,trial_relative as T
import importlib.util
P=A.P;L=A.L;sid=None;mouse=None;rows=[]
spec=importlib.util.spec_from_file_location('rc',P/'relative-control-native.py');RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(label,value):rows.append({'label':label,'value':value});(P/'blank-user-crossing.json').write_text(json.dumps(rows,indent=1));print(label,json.dumps(value),flush=True)
try:
 L.browser_start('firefox');b,_=L.connect();b.navigate('file://'+A.GP+'/blank.html');time.sleep(2)
 mouse=subprocess.Popen(['python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820];C.anchor_before_prepare(960,540);C.click()
 geometry=b.js("let e=document.querySelector('div[style*=\"height:2600\"]');return {start:e.getBoundingClientRect().top+scrollY,end:e.getBoundingClientRect().bottom+scrollY,scrollY,viewport:innerHeight,doc:document.documentElement.scrollHeight,focused:document.hasFocus()};");rec('fixture',geometry)
 sid=A.rpc('scroll.prepare',{'rect':C.rect,'driver':'user'})['id'];A.rpc('scroll.start',{'id':sid});offset=(P/'helper.log').stat().st_size
 for i in range(100):
  mouse.stdin.write('w 5\n');mouse.stdin.flush();time.sleep(.4);y=b.js('return scrollY;');v=A.rpc('scroll.inspect',{'id':sid});rec('wheel-'+str(i),{'scrollY':y,'activity':v.get('activity'),'height':v.get('height')})
  if v.get('activity')=='lost':
   s=rfb.RFB(5940);s.screenshot(P/'blank-user-proved-lost.png');s.close()
  if y>geometry['end']+50:break
 else:raise RuntimeError('Input did not cross the blank stretch')
 time.sleep(2);v=A.rpc('scroll.inspect',{'id':sid});rec('past-blank',v);rec('end',A.rpc('scroll.stop',{'id':sid}));(P/'blank-user-crossing-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')=='capturing':A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 if mouse:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
# Run the stop/toggle race only at a newly opened test browser.
try:
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 subprocess.run([sys.executable,str(P/'race.py')],check=True)
finally:L.browser_stop()
