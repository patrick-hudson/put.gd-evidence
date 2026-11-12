import sys,json,time,hashlib,shutil,traceback,threading
from pathlib import Path
P=Path('/home/patrick/work/sl25');sys.path.insert(0,str(P));from live25 import Marionette;import pass2 as p,rfb
m=Marionette()
assert m.info()['user']=='' and m.info()['signedOut'],m.info()
(P/'live-site').mkdir(exist_ok=True)
for column in ['A','B']:
 for kind,i in [('half',0),('half',1),('top',0),('max',0)]:
  name=column+'-'+kind+'-'+str(i);d=P/'live-site'/name;d.mkdir()
  try:
   for _ in range(4):
    m.wheel(-200000)
    if m.info()['scrollY']==0:break
   time.sleep(1);inf=m.info()
   if kind=='max' and inf['docHeight']<=30000:
    (d/'result.json').write_text(json.dumps({'notApplicable':'page below 30000','dom':inf},indent=2));continue
   if kind=='half':m.wheel((inf['docHeight']-inf['h'])//2)
   time.sleep(1);before=m.info();assert before['user']=='' and before['signedOut'];(d/'dom-before.json').write_text(json.dumps(before,indent=2));m.shot(d/'reference-before.png')
   # MaximizeWindow and DOM geometry identify the page viewport, below all browser chrome.
   width=min(round(before['clientWidth']),round(before['w'])-16) if column=='A' else round(before['w']);rect=[round(before['x']),round(before['y']),width,round(before['h'])]
   s=p.rpc('settings.get');doc=s['document'];doc['preferences']['scrollCaptureFromTop']=kind!='top';doc['preferences']['scrollCaptureMaxHeight']=60000 if kind=='max' else 30000;p.rpc('settings.save',{'document':doc,'expectedRevision':s['metadata']['observedRevision']})
   off=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0;start=time.time();v=p.rpc('scroll.prepare',{'rect':rect});ident=v['id'];states=[]
   while v['state']!='ready':time.sleep(.1);v=p.rpc('scroll.inspect',{'id':ident})
   time.sleep(.3);p.rpc('scroll.start',{'id':ident});started=time.time();captureAt=None;upstate=None
   while True:
    v=p.rpc('scroll.inspect',{'id':ident});states.append({'at':time.time(),'capture':v})
    if captureAt is None and v['state']=='capturing':captureAt=time.time()
    if v['state'] in ['done','failed','cancelled']:break
    if time.time()-start>300:raise TimeoutError(name)
    time.sleep(.12)
   end=time.time();after=m.info();sha=v.get('result',{}).get('sha256');found=None
   for _ in range(100):
    for f in (P/'archive').rglob('*.png'):
     if hashlib.sha256(f.read_bytes()).hexdigest()==sha:found=f;break
    if found or not sha:break
    time.sleep(.1)
   if found:shutil.copyfile(found,d/'capture.png')
   (d/'helper.log').write_bytes((P/'helper.log').read_bytes()[off:]);(d/'states.json').write_text(json.dumps(states));(d/'dom-after.json').write_text(json.dumps(after,indent=2));m.shot(d/'reference-after.png')
   result={'name':name,'rect':rect,'fromTop':kind!='top','maxHeight':60000 if kind=='max' else 30000,'capture':v,'totalSeconds':end-start,'startToEndSeconds':end-started,'wayUpSecondsObserved':captureAt-started if captureAt else None,'sha256':sha,'domBeforeHeight':before['docHeight'],'domAfterHeight':after['docHeight'],'signedOut':True}
   (d/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
  except Exception:
   (d/'harness-error.txt').write_text(traceback.format_exc());print(name,'ERROR',traceback.format_exc(),flush=True)
   try:p.rpc('scroll.cancel',{'id':ident})
   except Exception:pass
(P/'live-site/done').write_text('done')
