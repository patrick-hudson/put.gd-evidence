import json,time,subprocess
from pathlib import Path
def extra(r):
 out=r.receipt['supplement']={}
 archive=r.root/'archive';archive.mkdir()
 revision=r.cli('settings.get')['result']['metadata']['acceptedRevision']
 r.cli('settings.patch',{'patch':{'archive':{'keepUploads':True,'root':str(archive)}},'expectedRevision':revision})
 out['capture']=r.region_capture('region',r.args.region)
 rows=r.cli('history.list')['result'];out['historyList']=rows
 ident=rows['records'][0]['id'];r.copy_sentinel('history-sentinel')
 job=r.cli('history.copyText',{'id':ident,'keepResult':True})['result']['operationId']
 out['historyText']=r.wait(lambda:(lambda x:x if x.get('state') in ('failed','completed') else None)(r.cli('text.inspect',{'id':job})['result']),'history copy')
 out['historyPaste']=r.paste();out['historyPassed']=out['historyPaste']=='ALPHA BRAVO CHARLIE\nSYNTHETIC TEXT 1428\nhello@example.test'
 detail=r.cli('history.detail',{'id':ident});out['detail']=detail
 # This is the owned capture's exact local copy, never a pre-existing user file.
 paths=list(archive.rglob('*.png'))
 out['ownedLocalFiles']=[str(p) for p in paths]
 if len(paths)==1:
  saved=paths[0].with_suffix('.held');paths[0].rename(saved)
  try:
   r.copy_sentinel('missing-history-sentinel');start=r.cli('history.copyText',{'id':ident},check=False);out['missingHistoryStart']=start
   if start['ok']:
    op=start['result']['operationId'];out['missingHistoryResult']=r.wait(lambda:(lambda x:x if x.get('state') in ('failed','completed') else None)(r.cli('text.inspect',{'id':op})['result']),'missing history end')
   out['missingHistoryClipboard']=r.paste()
  finally:saved.rename(paths[0])
 out['qrWithLink']={'state':'not_run','reason':'local-only capture has no link; no isolated upload destination configured in this session'}
 # A real GNOME resize gesture. The application enforces its own minimum.
 r.cli('ui.show',{'view':'history'});time.sleep(1);r.input.chord(['alt','tab']);time.sleep(1);r.input.chord(['alt','f8'])
 for i in range(140):r.input.chord(['left'])
 r.input.chord(['ret']);time.sleep(1)
 subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'band-minimum.png')],check=True)
 print(json.dumps({'supplement':out}),flush=True)
