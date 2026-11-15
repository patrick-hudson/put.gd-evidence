"""Published nightly comparison: actual native Stop button, same relative first-motion driver.
Old nightly has no user driver or bar-position debug line. Read its visible X11 window,
locate the light primary button in the native framebuffer, and retain that calibration.
An inspect BEFORE the click distinguishes an earlier automatic end from a click stop.
"""
import accept as A,json,time,sys,subprocess,re,importlib.util
from pathlib import Path
import rfb
import numpy as np
from PIL import Image
P=A.P;source=Path(__file__).parent;L=A.L;latest_sid=None

def nativebar():
 for pid in subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.split():
  for wid in subprocess.run(['xdotool','search','--onlyvisible','--pid',pid],env=A.E,capture_output=True,text=True).stdout.split():
   out=subprocess.run(['xwininfo','-id',wid],env=A.E,capture_output=True,text=True).stdout
   def n(label):
    m=re.search(label+r':\s*(-?\d+)',out);return int(m[1]) if m else 0
   rect=[n('Absolute upper-left X'),n('Absolute upper-left Y'),n('Width'),n('Height')]
   if 250<rect[2]<1200 and 25<rect[3]<150 and 'IsViewable'in out:return rect,wid,out
 raise RuntimeError('native old Stop bar not visible')

src=(source/'trial_relative.py').read_text();needle="    if mouse:\n        mouse.stdin.write('d\\n')"
assert src.count(needle)==1
src=src.replace(needle,"    before_click=cli(a.cli,'scroll.inspect',{'id':sid}).get('result',{})\n    with open(os.path.join(os.path.dirname(a.log),'before-click.jsonl'),'a') as proof:proof.write(json.dumps({'label':a.label,'id':sid,'beforeClick':before_click})+'\\n')\n"+needle)
(P/'baseline-trial.py').write_text(src);(P/'umouse.py').write_bytes((source/'umouse.py').read_bytes())
spec=importlib.util.spec_from_file_location('baseline_trial',P/'baseline-trial.py');T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T);T.os.environ.update(A.E)
def rpc(m,p):
 global latest_sid
 p=dict(p)
 if m=='scroll.prepare':p.pop('driver',None)
 result=A.rpc(m,p)
 if m=='scroll.prepare':latest_sid=result['id']
 return {'ok':True,'result':result}
T.cli=lambda path,m,p:rpc(m,p)
def bar_adapter(text):
 r,w,_=nativebar();return r,r,w
T.x11_bar=bar_adapter
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 sid=rpc('scroll.prepare',{'rect':[240,200,1440,820]})['result']['id'];rpc('scroll.start',{'id':sid});time.sleep(1)
 rect,wid,info=nativebar();v=rfb.RFB(5900);v.screenshot(P/'pointer-calibration.png');v.close();x,y,w,h=rect;a=np.asarray(Image.open(P/'pointer-calibration.png').convert('RGB'))[y:y+h,x:x+w]
 light=(a.min(axis=2)>150)&(a.max(axis=2)-a.min(axis=2)<18);col=light.sum(axis=0)>=16;edges=np.diff(np.r_[False,col,False].astype(int));spans=[(int(s),int(e)) for s,e in zip(np.nonzero(edges==1)[0],np.nonzero(edges==-1)[0]) if e-s>=40]
 if spans:
  lo,hi=spans[-1];target=[x+(lo+hi)//2,y+h//2]
 else:
  assert [w,h]==[447,52],('unexpected old bar layout',rect)
  lo,hi=266,352;target=[x+309,y+26] # Stop centre measured in retained native 447x52 calibration picture
 (P/'pointer-calibration.json').write_text(json.dumps({'nativeBar':rect,'window':wid,'xwininfo':info,'primaryButtonColumns':[lo,hi],'target':target,'method':'Read actual framebuffer light primary button, no fabricated helper log.'},indent=1));rpc('scroll.cancel',{'id':sid})
 for typ in ['fixed','random']:
  for i in range(10):
   b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1)
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop',','.join(map(str,target)),'--log',str(P/'helper.log'),'--rel','--label',f'{typ}-{i+1}','--start','2' if typ=='fixed' else '1','--jitter','0' if typ=='fixed' else '5'];T.main()
finally:
 if latest_sid:
  try:
   if A.rpc('scroll.inspect',{'id':latest_sid}).get('state') in ['ready','preparing','capturing','finishing','selecting']:A.rpc('scroll.cancel',{'id':latest_sid})
  except Exception:pass
 L.browser_stop()
