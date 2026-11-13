from text_proof import session_environment
import subprocess,time,json,os
from pathlib import Path
E,_=session_environment(['gsd-power']);E['QT_QPA_PLATFORM']='wayland'
A=Path('/home/lab/ai2/squashfs-root');sock=Path(E['XDG_RUNTIME_DIR'])/'putgd/session.sock';assert len(str(sock).encode())<=107
p=subprocess.Popen(['/home/lab/candidate.AppImage','--background'],env=E,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
time.sleep(4)
C=dict(E,LD_LIBRARY_PATH=str(A/'usr/lib')+':'+str(A/'usr/lib/putgd'))
for method in ['capabilities','ui.quit']:
 r=subprocess.run([str(A/'usr/bin/putgd-cli'),'--socket',str(sock),method,'{}'],env=C,capture_output=True,text=True,timeout=30)
 if method=='capabilities':
  v=json.loads(r.stdout);print(json.dumps({'setup':v.get('result',{}).get('source',{}).get('helper',{}),'text':v.get('result',{}).get('text',{})}))
 else:print(r.stdout)
time.sleep(2)
if p.poll() is None:os.killpg(p.pid,15)
path=Path.home()/'.local/share/gnome-shell/extensions/putgd@put.gd';print('user copy metadata', (path/'metadata.json').exists(),'managed marker',(path/'.putgd-managed').exists())
