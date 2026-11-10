import sys,json,hashlib,shlex
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'))
import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs/o')
p=next(Path('/home/patrick/work/svm1398').glob('*.zst'))
lab.put(r,p,'/home/lab/putgd.pkg.tar.zst')
print(lab.ssh(r,'sudo -n pacman -U --noconfirm /home/lab/putgd.pkg.tar.zst',timeout=180))
print(lab.guest_session(r,"mkdir -p ~/putgd-lab; export PUTGD_RECORD_DEBUG_LOG=$HOME/putgd-lab/helper.log; export XDG_STATE_HOME=$HOME/putgd-lab/state; nohup putgd-launcher --background > ~/putgd-lab/app.log 2>&1 < /dev/null &"))
