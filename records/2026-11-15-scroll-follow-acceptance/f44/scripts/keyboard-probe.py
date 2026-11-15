import accept as A,subprocess,time,json,importlib.util
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E);R=[]
spec=importlib.util.spec_from_file_location("relative_control",P/"relative-control-native.py");RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse)
 keyboard=subprocess.Popen(['sudo','-n','python3',str(P/'ukey-ready.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert keyboard.stdout.readline().startswith('ready');time.sleep(2)
 C.anchor_before_prepare(1800,900);C.click()
 b.js('document.documentElement.setAttribute("data-sfa-keys","[]");document.addEventListener("keydown",e=>{const a=JSON.parse(document.documentElement.getAttribute("data-sfa-keys"));a.push({key:e.key,code:e.code,ctrl:e.ctrlKey,shift:e.shiftKey,defaultPrevented:e.defaultPrevented});document.documentElement.setAttribute("data-sfa-keys",JSON.stringify(a));});return 0;')
 for label,keys in [('end',[107]),('ctrl-end',[29,107]),('home',[102]),('ctrl-home',[29,102])]:
  before=b.js('return {y:scrollY,focused:document.hasFocus(),tag:document.activeElement.tagName,h:document.documentElement.scrollHeight};')
  keyboard.stdin.write(' '.join(map(str,keys))+'\n');keyboard.stdin.flush();time.sleep(1)
  after=b.js('return {y:scrollY,focused:document.hasFocus(),tag:document.activeElement.tagName,keys:JSON.parse(document.documentElement.getAttribute("data-sfa-keys"))};')
  R.append({'label':label,'before':before,'after':after});(P/'keyboard-probe.json').write_text(json.dumps(R,indent=1));print(json.dumps(R[-1]),flush=True)
finally:
 for n in ['mouse','keyboard']:
  if n in globals():
   q=globals()[n];q.stdin.write('q\n');q.stdin.flush();q.wait(5)
 L.browser_stop()
