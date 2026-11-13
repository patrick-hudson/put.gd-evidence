from pathlib import Path
import time,json,subprocess

def locked(r):
 marker=Path('/home/lab/a1428-unlocked.txt')
 if marker.exists():raise RuntimeError('unlock marker already exists')
 sentinel='locked-screen-sentinel-1428';r.copy_sentinel(sentinel)
 r.input.chord(['meta_l','l']);time.sleep(2)
 row=r.receipt['lockedScreen']={}
 row['start']=r.cli('text.recognize',{'source':'monitor','copy':True},check=False)
 if row['start']['ok']:
  op=row['start']['result']['operationId'];row['terminal']=r.wait(lambda:(lambda x:x if x.get('state') in ('failed','completed','cancelled') else None)(r.cli('text.inspect',{'id':op})['result']),'locked screen operation')
 subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'locked.png')],check=True)
 print('LOCKED-FRAME '+str(r.root/'locked.png'),flush=True)
 print(json.dumps({'lockedScreenBeforeUnlock':row}),flush=True)
 r.wait(marker.exists,'visibly verified console unlock',900)
 row['pasteAfterUnlock']=r.paste();row['helpersAfter']=subprocess.run(['pgrep','-x','putgd-ocr'],capture_output=True,text=True).stdout.split()
 error=row.get('terminal',row['start']).get('error',{}).get('code');row['passed']=error=='session_locked' and row['pasteAfterUnlock']==sentinel and not row['helpersAfter']
 print(json.dumps({'lockedScreen':row}),flush=True)
