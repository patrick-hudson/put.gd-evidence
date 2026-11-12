# Full-page references, tiled; preserve the initial contemporaneous reference.
import livefull as l,json,time,shutil,datetime,traceback
from PIL import Image
from pathlib import Path
P=l.P
for kind,short in [('firefox','ff'),('chromium','cr')]:
 try:l.browser_start(kind)
 except Exception:
  (P/('reference-start-'+kind+'.error')).write_text(traceback.format_exc());continue
 try:
  b,_=l.connect()
  for out in sorted((P/'runs').glob('accept3-'+short+'-*')):
   if not (out/'result.json').exists():continue
   r=json.loads((out/'result.json').read_text())
   original=out/'reference.png';docheight=int(r.get('afterReference',r.get('after',r['before']))['docHeight']);size=Image.open(original).size if original.exists() else (0,0)
   if size[1]>=docheight:
    (out/'full-reference.json').write_text(json.dumps({'method':'original contemporaneous browser full-page reference retained','size':size,'documentHeight':docheight},indent=2));continue
   meta={'url':r['url'],'timestampUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'browser own screenshot, entire document; Firefox2500px tiles, Chromiumviewport tiles; original contemporaneous reference retained'}
   try:
    b.navigate(r['url']);time.sleep(6);b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2);info=l.wait_loaded(b,15);meta['before']=info
    if info['docHeight']>150000:raise RuntimeError('Full-reference preflight refuses >150000 rows; no allocation attempted')
    expected=int(round(r['before']['clientWidth']*r['before']['dpr']));actual=int(round(info['clientWidth']*info['dpr']));assert actual==expected,(actual,expected)
    dest=out/'reference-full.png';b.shot_full(dest,limit=2_000_000_000);meta['after']=b.js(l.INFO)
    if (out/'reference.png').exists() and not (out/'reference-initial.png').exists():shutil.copyfile(out/'reference.png',out/'reference-initial.png')
    shutil.copyfile(dest,out/'reference.png');print('FULL',out.name,info['docHeight'],flush=True)
   except Exception:meta['error']=traceback.format_exc();print('FULL-ERROR',out.name,meta['error'][-400:],flush=True)
   (out/'full-reference.json').write_text(json.dumps(meta,indent=2))
 finally:l.browser_stop()
