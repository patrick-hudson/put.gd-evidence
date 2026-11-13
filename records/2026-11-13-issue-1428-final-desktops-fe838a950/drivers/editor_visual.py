import time,json,subprocess
from pathlib import Path

def extra(r):
 out=r.receipt['editorVisual']={};base=Path(r.args.fixture[-1]).parent
 ident=r.cli('editor.open',{'source':'file','path':str(base/'text.png')})['result']['operationId'];time.sleep(2)
 r.cli('editor.view',{'id':ident,'action':'tool','tool':'copyText'})
 data=r.wait(lambda:(lambda x:x if x.get('text',{}).get('state')=='completed' else None)(r.cli('editor.inspect',{'id':ident})['result']),'editor text');result=data['text']['result'];r.cli('editor.selectText',{'id':ident,'result':result,'from':0,'to':2});r.copy_sentinel('editor-visual-sentinel');out['copy']=r.cli('editor.copyText',{'id':ident,'result':result});out['paste']=r.paste()
 # A compositor-confirmed foreground window; no script touches another app.
 def bus(*a):return subprocess.run(['dbus-send','--session','--print-reply','--dest=org.kde.KWin',*a],env=r.env,capture_output=True,text=True)
 script=r.root/'raise-editor.js';script.write_text('for (const w of workspace.windowList()) {if (w.resourceClass == "putgd-ui" && w.caption.indexOf("Edit") >= 0) { workspace.activeWindow=w; }}')
 import re
 load=bus('/Scripting','org.kde.kwin.Scripting.loadScript','string:'+str(script),'string:a1428-editor-visual');n=re.search(r'int32 (\d+)',load.stdout)
 if n:
  bus('/Scripting/Script'+n.group(1),'org.kde.kwin.Script.run');bus('/Scripting','org.kde.kwin.Scripting.unloadScript','string:a1428-editor-visual')
 time.sleep(1);subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'editor-visible.png')],check=True);print('EDITOR-FRAME '+str(r.root/'editor-visible.png'),flush=True)
 r.wait(lambda:Path('/home/patrick/work/a1428/editor-go.txt').exists(),'visual editor confirmation',900)
 out['quick']=r.cli('editor.apply',{'id':ident,'commands':[{'op':'redactText','categories':['email']}]});time.sleep(1);subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'editor-redact-visible.png')],check=True)
 r.cli('editor.cancel',{'id':ident});print(json.dumps({'editorVisual':out}),flush=True)
 from history_qr import extra as history
 history(r)
 print('QR-FRAME '+str(r.root/'history-qr-dialog.png'),flush=True)
