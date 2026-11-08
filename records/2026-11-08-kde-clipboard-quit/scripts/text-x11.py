import sys,json,time,shlex,subprocess
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
n,label=sys.argv[1:];r=S/'work/lab-runs'/n;o=Path.home()/'work/kq/evidence'/n/label;o.mkdir(parents=True,exist_ok=True)
def g(s):return lab.guest_session(r,'export QT_QPA_PLATFORM=xcb\nexport XDG_SESSION_TYPE=x11\nexport PATH=$HOME/putgd-lab/bin:$PATH\n'+s,timeout=60)
def c(m,p={}):return json.loads(g('/usr/bin/putgd-cli '+shlex.quote(m)+' '+shlex.quote(json.dumps(p))))['result']
g('(setsid -f /usr/bin/putgd-launcher --background > ~/text-app.log 2>&1 </dev/null); true');time.sleep(3)
s=c('settings.get');c('settings.patch',{'patch':{'actions':{'clipboard':{'destination':'local','profileId':None,'publicationMode':'default'}}},'expectedRevision':s['metadata']['observedRevision']})
url='https://example.invalid/kq-'+label
g('printf %s '+url+' | xclip -selection clipboard >/dev/null 2>&1');time.sleep(1);op=c('action.invoke',{'action':'clipboard'});time.sleep(3);copied=c('operation.copy',{'id':op['operationId']});(o/'text-operation.json').write_text(json.dumps(copied,indent=2))
before=g('timeout 8 xclip -selection clipboard -o');c('ui.quit');time.sleep(2);after=g('timeout 8 xclip -selection clipboard -o');print(dict(expected=url,before=before,after=after,kept=before==after),flush=True)
g('touch ~/kq-paste.txt; (setsid -f kate -n ~/kq-paste.txt > ~/kate.log 2>&1 </dev/null); true');time.sleep(3);lab.key(r,['ctrl','a']);lab.key(r,['ctrl','v']);lab.key(r,['ctrl','s']);time.sleep(1)
from PIL import Image
Image.open(lab.screenshot(r,label+'-text-paste')['path']).save(o/'text-paste.png')
actual=g('cat ~/kq-paste.txt');(o/'text-result.json').write_text(json.dumps(dict(expected=url,before=before,after=after,savedPaste=actual,kept=before==after,pasteMatches=actual.strip()==url),indent=2));print('saved',actual,flush=True);g('for p in $(pgrep -x kate); do kill "$p"; done; true')
