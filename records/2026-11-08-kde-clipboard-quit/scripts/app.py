import sys,json,time,subprocess,hashlib,shlex
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
n,label,pkg=sys.argv[1:];r=S/'work/lab-runs'/n;o=Path.home()/'work/kq/evidence'/n/label;o.mkdir(parents=True,exist_ok=True)
def g(s):return lab.guest_session(r,'export PATH=$HOME/putgd-lab/bin:$PATH\n'+s,timeout=200)
def c(m,p={}):return json.loads(g('putgd-cli '+shlex.quote(m)+' '+shlex.quote(json.dumps(p))))['result']
def shot(t):
 from PIL import Image
 Image.open(lab.screenshot(r,label+'-'+t)['path']).save(o/(t+'.png'))
receipt=lab.install_appimage(r,pkg);(o/'package.json').write_text(json.dumps(receipt,indent=2));(r/'package.json').write_text(json.dumps(receipt))
print(receipt['version'],flush=True)
subprocess.run([sys.executable,str(S/'tools/diagnostics/check_socket_paths.py'),'--socket','/run/user/1000/putgd/session.sock'],check=True)
def start():
 g('(setsid -f putgd-launcher --background > ~/kq-app.log 2>&1 < /dev/null); true');time.sleep(3)
 print(c('capabilities')['source']['adapter'],flush=True)
def quit():
 c('ui.quit');time.sleep(2);print(g('pgrep -ax putgd || true; pgrep -ax putgd-clipboard || true'),flush=True)
def sha():return g('(timeout 8 wl-paste -t image/png 2>/dev/null || true) | sha256sum').split()[0]
def paste(t):
 g('(setsid -f kolourpaint > ~/kq-paint.log 2>&1 < /dev/null); true');time.sleep(2);lab.key(r,['ctrl','v']);time.sleep(1);shot(t);g('for p in $(pgrep -x kolourpaint); do kill "$p"; done; true')
start();setting=c('settings.get');print(c('settings.patch',{'patch':{'archive':{'keepUploads':True},'captureDefaults':{'destination':'local','profileId':None,'publicationMode':'default'},'actions':{'desktop':{'destination':'local','profileId':None,'publicationMode':'default'}}},'expectedRevision':setting['metadata']['observedRevision']}),flush=True)
results=[]
for mode in ['stock','save-images']:
 g('kwriteconfig6 --file ~/.config/klipperrc --group General --key SaveImages '+('true' if mode=='save-images' else 'false')+'; qdbus6 org.kde.klipper /klipper reloadConfig');time.sleep(1)
 if n=='k1':g('kwriteconfig6 --file ~/.config/klipperrc --group General --key IgnoreImages '+('false' if mode=='save-images' else 'true')+'; qdbus6 org.kde.klipper /klipper reloadConfig')
 if mode!='stock':start()
 op=c('action.invoke',{'action':'desktop'});print('invoke',op,flush=True);time.sleep(4)
 ops=c('operation.recent');(o/(mode+'-operations.json')).write_text(json.dumps(ops,indent=2))
 before=sha();assert before!=hashlib.sha256(b'').hexdigest(), 'image missing before quit';shot(mode+'-before');quit();after=sha();results.append(dict(mode=mode,action='auto-copy',before=before,after=after,kept=before==after));print(results[-1],flush=True);paste(mode+'-auto-paste')
 start();records=c('history.list',{'limit':5});(o/(mode+'-history.json')).write_text(json.dumps(records,indent=2));rid=records['records'][0]['id'];print(c('history.copyImage',{'id':rid}),flush=True);time.sleep(2);before=sha();quit();after=sha();results.append(dict(mode=mode,action='history-copy-image',before=before,after=after,kept=before==after));print(results[-1],flush=True);paste(mode+'-history-paste')
(o/'results.json').write_text(json.dumps(results,indent=2));g('kwriteconfig6 --file ~/.config/klipperrc --group General --key SaveImages false; qdbus6 org.kde.klipper /klipper reloadConfig');print('DONE',flush=True)
