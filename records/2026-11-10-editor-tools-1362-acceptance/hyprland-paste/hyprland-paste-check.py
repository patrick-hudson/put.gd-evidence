import sys,time,json,shlex
from pathlib import Path
sys.path.insert(0,'tools/lab');import lab
run=Path('work/lab-runs/h62p').resolve();root='/tmp/e1362';op=json.loads((run/'real-input.json').read_text())['operationId'];result={'operationId':op}
def guest(code):return lab.ssh(run,"cd /home/lab/e1362\npython3 - <<'P'\n"+code+'P\n')
def call(m,p={}):
 code="import json,subprocess\nfrom pathlib import Path\ne=json.loads(Path('/tmp/e1362/env.json').read_text());e['LD_LIBRARY_PATH']='/home/lab/e1362/squashfs-root/usr/lib'\nr=subprocess.run(['/home/lab/e1362/squashfs-root/usr/bin/putgd-cli','--socket','/tmp/e1362/runtime/putgd/session.sock','--params-stdin',"+repr(m)+"],input="+repr(json.dumps(p))+",env=e,capture_output=True,text=True);print(r.stdout)\n"
 v=json.loads(guest(code));assert v['ok'],v;return v['result']
def native(cmd):
 return guest("import subprocess,json\nfrom record_run import session_environment\ne,_=session_environment();print(subprocess.check_output("+repr(cmd)+",env=e,text=True))\n")
def clients():return json.loads(native(['hyprctl','-j','clients']))
def browser():
 rows=[w for w in clients()if w.get('class','').lower() in ('chromium','chromium-browser')];assert len(rows)==1,[(w.get('class'),w.get('title'))for w in clients()];return rows[0]
def click(x,y):lab.pointer(run,round(x),round(y),1280,800,down=True);lab.pointer(run,round(x),round(y),1280,800,down=False)
def paste(label,sha):
 b=browser();x,y=b['at'];click(x+75,y+230);lab.key(run,['ctrl','v'])
 for i in range(50):
  b=browser()
  if sha in b.get('title',''):break
  time.sleep(.1)
 assert sha in b.get('title',''),b
 result[label]={'sha256':sha,'browserTitle':b['title'],'browserAddress':b['address'],'at':b['at'],'size':b['size']};lab.screenshot(run,label)
# First verify the shortcut action, then paste its exact bytes in Chromium.
before=call('history.list');saved=call('editor.saveCopy',{'id':op,'path':'/tmp/e1362/action-expected.png','overwrite':True});sha=saved['sha256']
def seed_clipboard():
 guest("import subprocess\nfrom record_run import session_environment\ne,_=session_environment();subprocess.run(['wl-copy'],input=b'clipboard action probe',env=e,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n")
seed_clipboard();lab.key(run,['ctrl','shift','c']);time.sleep(.3);state=call('editor.inspect',{'id':op});assert state['phase']=='editing';assert call('history.list')==before
lab.put(run,Path('paste.html').resolve(),'/home/lab/e1362/paste.html')
print(guest("import subprocess\nfrom pathlib import Path\nfrom record_run import session_environment\ne,_=session_environment();p=Path('/tmp/e1362/paste-once');p.mkdir(mode=0o700);args=['chromium','--user-data-dir='+str(p),'--no-first-run','file:///home/lab/e1362/paste.html'];c=subprocess.Popen(args,env=e,stdout=open('paste-once.log','w'),stderr=subprocess.STDOUT,start_new_session=True);Path('paste-once.pid').write_text(str(c.pid));print(c.pid)\n"));time.sleep(2);paste('shortcut-paste',sha)
# The original geometry changed when the browser tiled. Resolve current editor bounds.
editor=[w for w in clients()if w.get('class','')=='putgd-ui'];assert len(editor)==1,clients();w=editor[0];x,y=w['at'];width,height=w['size'];result['editorAtButton']={'at':w['at'],'size':w['size']}
# At the minimum width the footer wraps; use the observed editor's Copy image area.
seed_clipboard();click(x+130,y+height-28);time.sleep(.3);state=call('editor.inspect',{'id':op});assert state['phase']=='editing';assert state['view']['lastCopy']['status']=='copied';assert call('history.list')==before;lab.screenshot(run,'button-copy-visible')
# Empty the paste surface with a fresh navigation in the same real browser window.
b=browser();x,y=b['at'];click(x+75,y+230);lab.key(run,['ctrl','r']);time.sleep(.5)
assert 'Pasted PNG' not in browser()['title'];paste('button-paste',sha)
result['historyUnchanged']=True;result['editorOpen']=True;result['ok']=True;(run/'clipboard-paste-verified.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
