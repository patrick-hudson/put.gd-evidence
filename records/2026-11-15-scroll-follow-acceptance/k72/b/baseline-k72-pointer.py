import accept as A,json,time,sys,subprocess,importlib.util
from pathlib import Path
import rfb
import numpy as np
from PIL import Image
P=A.P;source=Path(__file__).parent;L=A.L;sid=None
src=(source/'trial_relative.py').read_text();needle="    if mouse:\n        mouse.stdin.write('d\\n')"
assert src.count(needle)==1
src=src.replace(needle,"    before_click=cli(a.cli,'scroll.inspect',{'id':sid}).get('result',{})\n    with open(os.path.join(os.path.dirname(a.log),'before-click.jsonl'),'a') as proof:proof.write(json.dumps({'label':a.label,'id':sid,'beforeClick':before_click})+'\\n')\n"+needle)
(P/'baseline-trial.py').write_text(src)
spec=importlib.util.spec_from_file_location('baseline_trial',P/'baseline-trial.py');T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T);T.os.environ.update(A.E)
def rpc(m,p):
 global sid
 p=dict(p)
 if m=='scroll.prepare':p.pop('driver',None)
 r=A.rpc(m,p)
 if m=='scroll.prepare':sid=r['id']
 return {'ok':True,'result':r}
T.cli=lambda path,m,p:rpc(m,p)
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 sid=rpc('scroll.prepare',{'rect':[240,200,1440,820]})['result']['id'];rpc('scroll.start',{'id':sid});time.sleep(1)
 v=rfb.RFB(5900);v.screenshot(P/'pointer-calibration.png');v.close()
 a=np.asarray(Image.open(P/'pointer-calibration.png').convert('RGB'));assert (a[148:180,510:590].max(axis=2)<80).mean()>.6
 (P/'pointer-calibration.json').write_text(json.dumps({'target':[550,164],'nativeBar':[240,138,447,52],'method':'Native Kubuntu screenshot visibly confirms the old dark Stop button at506,146 88x36; positive dark interior coverage check. Relative input to its actual centre.'},indent=1))
 rpc('scroll.cancel',{'id':sid})
 for typ in ['fixed','random']:
  for i in range(3):
   b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1)
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop','550,164','--log',str(P/'helper.log'),'--rel','--label',f'{typ}-{i+1}','--start','2' if typ=='fixed' else '1','--jitter','0' if typ=='fixed' else '5'];T.main()
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')in['ready','preparing','capturing','finishing']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 L.browser_stop()
