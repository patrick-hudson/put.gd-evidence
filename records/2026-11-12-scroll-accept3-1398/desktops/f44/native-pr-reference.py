# Independent native CDP full-document screenshots: no CSS position mutation.
from pathlib import Path
import json,time,base64,hashlib,traceback,os
import livenative as l,rfb
P=l.P
try:l.browser_start('chromium')
except Exception:
 (P/'native-reference-start.error').write_text(traceback.format_exc());raise
try:
 b,_=l.connect()
 for d in sorted((P/'runs').glob('accept3-cr-pr-*')):
  if not (d/'result.json').exists():continue
  r=json.loads((d/'result.json').read_text());meta={'method':'CDP Page.captureScreenshot captureBeyondViewport true, clip browser document dimensions, no CSS or DOM modifications'}
  try:
   b.navigate(r['url']);time.sleep(6);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2);info=l.wait_loaded(b,15);meta['before']=info
   assert info['clientWidth']==r['before']['clientWidth'] and info['dpr']==r['before']['dpr']
   assert info['docHeight']<=40000,'bounded native full-snapshot preflight (f44 only)'
   v=rfb.RFB(int(os.environ.get('SF7_VNC','5901')));v.pointer(100,20);v.close();time.sleep(.5)
   meta['layoutMetrics']=b.cmd('Page.getLayoutMetrics')
   result=b.cmd('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':True,'clip':{'x':0,'y':0,'width':info['clientWidth'],'height':info['docHeight'],'scale':1}})
   f=d/'reference-nativefull.png';f.write_bytes(base64.b64decode(result['data']));meta['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();meta['after']=b.js(l.INFO);assert meta['after']['docHeight']==info['docHeight'] and meta['after']['clientWidth']==info['clientWidth']
   print('NATIVE_REFERENCE',d.name,info['docHeight'],flush=True)
  except Exception:meta['error']=traceback.format_exc();print('NATIVE_REFERENCE_ERROR',d.name,meta['error'][-300:],flush=True)
  (d/'native-reference.json').write_text(json.dumps(meta,indent=2))
 b.s.close()
finally:l.browser_stop()
