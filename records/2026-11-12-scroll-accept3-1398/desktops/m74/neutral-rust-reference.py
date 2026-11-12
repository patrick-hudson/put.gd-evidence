from pathlib import Path
import os,json,time,traceback,hashlib
import livenative as l,rfb
P=l.P;l.browser_start('firefox')
try:
 b,_=l.connect()
 for d in sorted((P/'runs').glob('accept3-ff-rust-*')):
  if not (d/'result.json').exists():continue
  r=json.loads((d/'result.json').read_text());meta={'method':'Browser full-document snapshot, same width, own pointer parked in browser toolbar before reference; original capture and references retained'}
  try:
   b.navigate(r['url']);time.sleep(6);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1);info=l.wait_loaded(b,15);meta['before']=info;assert info['clientWidth']==r['before']['clientWidth']
   v=rfb.RFB(int(os.environ.get('SF7_VNC','5900')));v.pointer(100,20);v.close();time.sleep(1)
   f=d/'reference-neutral.png';b.shot_full(f,limit=10000);meta['after']=b.js(l.INFO);meta['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();print('NEUTRAL_REFERENCE',d.name,flush=True)
  except Exception:meta['error']=traceback.format_exc();print('NEUTRAL_REFERENCE_ERROR',d.name,meta['error'][-300:],flush=True)
  (d/'neutral-reference.json').write_text(json.dumps(meta,indent=2))
 b.cmd('WebDriver:DeleteSession');b.s.close()
finally:l.browser_stop()
