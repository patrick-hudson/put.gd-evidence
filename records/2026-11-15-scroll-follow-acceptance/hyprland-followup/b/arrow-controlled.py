"""Same native pointer precondition for candidate and published nightly."""
import accept as A,sys,json,time,os,hashlib,shutil,importlib.util
from pathlib import Path
import rfb
P=A.P;L=A.L;sid=None;rows=[]
def rec(k,v):
 rows.append({'label':k,'value':v});(P/'arrow-controlled-results.json').write_text(json.dumps(rows,indent=1));print(k,json.dumps(v),flush=True)
def shot(k):
 v=rfb.RFB(int(A.E['SF7_VNC']));v.screenshot(P/(k+'.png'));v.close()
try:
 rec('diagnostics-build',A.rpc('diagnostics')['build'])
 L.browser_start('firefox');b,_=L.connect();rec('native-viewport',json.loads((P/'viewport.json').read_text()))
 rec('flat',A.remote('flat'));rec('control-anchor',A.remote('anchor','1840','960'));point=A.remote('pointer');rec('control-pointer',point);shot('arrow-native-control')
 b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(12)
 rec('page',b.js(L.INFO));rec('capture-anchor',A.remote('anchor','1840','960'));rec('pointer-before-prepare',A.remote('pointer'));shot('arrow-before-prepare')
 params={'rect':[0,0,1920,1080],'maxHeight':60000}
 if os.environ.get('SFA_BASELINE')!='1':params['driver']='putgd'
 rec('prepare-parameters',params);offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',params)['id'];A.rpc('scroll.start',{'id':sid});time.sleep(3)
 rec('before-done',A.rpc('scroll.inspect',{'id':sid}));shot('arrow-before-done');rec('end',A.rpc('scroll.stop',{'id':sid}))
 f=A.sync_artifact(sid);shutil.copyfile(f,P/'arrow-controlled-capture.png');rec('verified-artifact',{'operationId':sid,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'path':str(f)})
 (P/'arrow-controlled-helper.log').write_bytes((P/'helper.log').read_bytes()[offset:])
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')in['capturing','ready','preparing']:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 L.browser_stop()
