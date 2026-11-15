import accept as A,json,time,subprocess,importlib.util
from pathlib import Path
import rfb,trial_relative as T
P=A.P;L=A.L;T.os.environ.update(A.E);rows=[];sid=None
spec=importlib.util.spec_from_file_location("relative_control",P/"relative-control-native.py");RC=importlib.util.module_from_spec(spec);spec.loader.exec_module(RC)
def rec(label,value):
 rows.append({'label':label,'value':value});(P/'keyboard-capture-probe.json').write_text(json.dumps(rows,indent=1));print(label,json.dumps(value),flush=True)
def page():return b.js('return {y:scrollY,h:document.documentElement.scrollHeight,focused:document.hasFocus(),tag:document.activeElement.tagName,keys:JSON.parse(document.documentElement.getAttribute("data-sfa-keys")||"[]")};')
def key(label,*keys):
 keyboard.stdin.write(' '.join(map(str,keys))+'\n');keyboard.stdin.flush();time.sleep(1);rec(label,page())
def shot(label):
 v=rfb.RFB(5900);v.screenshot(P/(label+'.png'));v.close()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();C=RC.Control(A,mouse);C.rect=[240,200,1440,820]
 keyboard=subprocess.Popen(['sudo','-n','python3',str(P/'ukey-ready.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert keyboard.stdout.readline().startswith('ready');time.sleep(2)
 b.js('document.documentElement.setAttribute("data-sfa-keys","[]");document.addEventListener("keydown",e=>{const a=JSON.parse(document.documentElement.getAttribute("data-sfa-keys"));a.push({key:e.key,code:e.code,ctrl:e.ctrlKey,shift:e.shiftKey,trusted:e.isTrusted});document.documentElement.setAttribute("data-sfa-keys",JSON.stringify(a));});return 0;')
 for driver in (['putgd'] if A.os.environ.get('SFA_BASELINE')=='1' else ['user','putgd']):
  C.anchor_before_prepare(1800,900);C.click();rec(driver+'-before',page());key(driver+'-preflight-End',107);key(driver+'-preflight-Home',102)
  offset=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0;params={'rect':C.rect}
  if A.os.environ.get('SFA_BASELINE')!='1':params['driver']=driver
  sid=A.rpc('scroll.prepare',params)['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1);rec(driver+'-capturing-before-key',page())
  key(driver+'-during-End',107);rec(driver+'-inspect-End',A.rpc('scroll.inspect',{'id':sid}));shot('keyboard-'+driver+'-during-End')
  key(driver+'-during-CtrlEnd',29,107);key(driver+'-during-Home',102)
  if driver=='user':
   C.move(1650,990);mouse.stdin.write('w 3\n');mouse.stdin.flush();time.sleep(1);rec(driver+'-during-wheel',page());rec(driver+'-inspect-wheel',A.rpc('scroll.inspect',{'id':sid}))
  state=A.rpc('scroll.inspect',{'id':sid});rec(driver+'-cancel',A.rpc('scroll.cancel',{'id':sid}) if state.get('state')in['capturing','ready','preparing'] else state);time.sleep(.5);key(driver+'-after-End',107);shot('keyboard-'+driver+'-after-End');key(driver+'-after-Home',102)
  (P/('keyboard-'+driver+'-capture-helper.log')).write_bytes((P/'helper.log').read_bytes()[offset:]);sid=None
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')in['capturing','ready','preparing']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 for n in ['mouse','keyboard']:
  if n in globals():
   q=globals()[n];q.stdin.write('q\n');q.stdin.flush();q.wait(5)
 L.browser_stop()
