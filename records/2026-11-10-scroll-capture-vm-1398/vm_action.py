import sys,json,shlex,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'))
import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/sys.argv[1]
a=sys.argv[2]
if a=='appimage':
 p=next(Path('/home/patrick/work/svm1398').glob('*.AppImage')); print(lab.install(r,appimage=p))
elif a=='rpm':
 p=next(Path('/home/patrick/work/svm1398').glob('*.rpm'));lab.put(r,p,'/home/lab/putgd.rpm');print(lab.ssh(r,'sudo -n dnf install -y /home/lab/putgd.rpm 2>&1 || true',timeout=240))
elif a=='start':
 print(lab.guest_session(r,'mkdir -p ~/putgd-lab; export XDG_STATE_HOME=$HOME/putgd-lab/state; export PUTGD_RECORD_DEBUG_LOG=$HOME/putgd-lab/helper.log; nohup putgd-launcher --background > ~/putgd-lab/app.log 2>&1 < /dev/null &'))
elif a=='stage':
 lab.put(r,next(Path('/home/patrick/work/svm1398').glob('*.AppImage')),'/home/lab/ci.AppImage')
 for f in ['scroll_run_vm.py','ruler.html']:lab.put(r,Path(__file__).parent/f,'/home/lab/putgd-lab/'+f)
