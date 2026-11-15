import accept as A,json,time,subprocess,hashlib,shutil,importlib.util
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E)
spec=importlib.util.spec_from_file_location("relative_control",P/"relative-control-native.py");RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
rows=[];sid=None
def rec(label,value):
 rows.append({'label':label,'value':value});(P/'user-script-recovery-results.json').write_text(json.dumps(rows,indent=1));print(label,json.dumps(value),flush=True)
def shot(name):
 v=rfb.RFB(5900);v.screenshot(P/(name+'.png'));v.close()
def inspect():return A.rpc('scroll.inspect',{'id':sid})
def wait(activity):
 until=time.time()+20
 while time.time()<until:
  v=inspect()
  if v.get('activity')==activity:return v
  time.sleep(.1)
 return inspect()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(15)
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820]
 C.anchor_before_prepare(1800,900);C.click()
 focus=b.js('return {focused:document.hasFocus(),tag:document.activeElement.tagName,scrollY};');rec('content-focus-before',focus);assert focus['focused']
 before=b.js(L.INFO);offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',{'rect':C.rect,'driver':'user','maxHeight':60000})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(.5)
 rec('focus-before-End',b.js('return {focused:document.hasFocus(),tag:document.activeElement.tagName,scrollY};'))
 C.move(1650,990);mouse.stdin.write('w 3\n');mouse.stdin.flush();time.sleep(1);rec('before-jump',inspect());rec('stimulus',{'method':'Live page-script scrollBy(3000, instant); native End suppression is tested separately, not replaced as a pass.'});b.js('window.scrollBy({top:3000,behavior:"instant"});return 0;');v=wait('lost');rec('lost',v);shot('bar-js-user-lost');assert v.get('activity')=='lost',v
 b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');v=wait('following');rec('found',v);shot('bar-js-user-found');assert v.get('activity')=='following',v
 C.move(1650,990);mouse.stdin.write('w 3\n');mouse.stdin.flush();time.sleep(1)
 v=A.rpc('scroll.stop',{'id':sid});rec('end',v)
 import find_history;r=find_history.find_operation(A,sid);f=Path(r['local']['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(f,P/'user-script-recovery-capture.png')
 after=b.js(L.INFO);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2);b.shot_full(P/'user-script-recovery-reference.png')
 (P/'user-script-recovery-reference-info.json').write_text(json.dumps({'before':before,'after':after,'viewport':json.loads((P/'viewport.json').read_text()),'capture':v},indent=1))
 (P/'user-script-recovery-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if inspect().get('state') in ['capturing','preparing','ready']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 for name in ['mouse','keyboard']:
  if name in globals():
   q=globals()[name];q.stdin.write('q\n');q.stdin.flush();q.wait(5)
 L.browser_stop()
