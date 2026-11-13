import json,time,re,subprocess
from pathlib import Path
EXPECTED='ALPHA BRAVO CHARLIE\nSYNTHETIC TEXT 1428\nhello@example.test'
def extra(r):
 base=Path(r.args.fixture[-1]).parent
 out=r.receipt['extra']={}
 def task(name,fn):
  try:out[name]=fn()
  except Exception as e:out[name]={'error':str(e),'passed':False}
  print(json.dumps({name:out[name]}),flush=True)
 def frame(name):
  if r.args.rfb!='none':subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/(name+'.png'))],check=True,timeout=20)
 def editor():
  ed=r.cli('editor.open',{'source':'file','path':str(base/'text.png')})['result'];ident=ed['operationId'];time.sleep(3)
  r.cli('editor.view',{'id':ident,'action':'tool','tool':'copyText'})
  data=r.wait(lambda:(lambda d:d if d.get('text',{}).get('state')=='completed' else None)(r.cli('editor.inspect',{'id':ident})['result']),'editor recognition',30)
  layer=data['text'];result=layer['result'];r.copy_sentinel('editor-sentinel')
  select=r.cli('editor.selectText',{'id':ident,'result':result,'from':0,'to':2});copied=r.cli('editor.copyText',{'id':ident,'result':result});time.sleep(.5);paste=r.paste();frame('editor-selection')
  quick=r.cli('editor.apply',{'id':ident,'commands':[{'op':'redactText','categories':['email']}]});frame('editor-quick-redact')
  r.cli('editor.cancel',{'id':ident});return {'opened':ed,'recognized':data,'selection':select,'copy':copied,'paste':paste,'quickRedact':quick,'passed':paste=='ALPHA BRAVO CHARLIE'}
 def qr():
  (base/'mode').write_text('qr');time.sleep(1);previous=r.args.expect;r.args.expect=re.escape('https://example.test/acceptance/1428')
  try:ok=r.trigger('qr-region',lambda:r.input.chord(r.args.keys));return {'passed':ok,'expected':'https://example.test/acceptance/1428'}
  finally:r.args.expect=previous;(base/'mode').write_text('text')
 def sources():
  rows={};cap=r.cli('capabilities')['result']['text']['sources']
  for source in ('window','monitor','desktop','clipboard','file','region'):
   r.input.click(r.args.screen[0]//2,r.args.screen[1]//2);time.sleep(.3)
   sentinel='source-sentinel-'+source;r.copy_sentinel(sentinel)
   if source=='clipboard':subprocess.run(['wl-copy','--type','image/png'],input=(base/'text.png').read_bytes(),env=r.env,check=True);sentinel=None
   p={'source':source,'copy':False}
   if source=='file':p['path']=str(base/'text.png')
   start=r.cli('text.recognize',p,check=False);row={'capability':cap.get(source),'start':start};rows[source]=row
   if start['ok']:
    ident=start['result']['operationId']
    if source=='region':time.sleep(1);r.input.drag(r.args.region[:2],r.args.region[2:])
    state=r.wait(lambda:(lambda d:d if d.get('state') in ('completed','failed','cancelled') else None)(r.cli('text.inspect',{'id':ident})['result']),source+' end',45);row['record']=state
   if sentinel is not None:row['clipboardUnchanged']=r.paste()==sentinel
  return rows
 task('qr',qr);task('sources',sources);task('editor',editor)
