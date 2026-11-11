import sys,json,concurrent.futures
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab')
import lab
root=Path('/home/patrick/work/svm1398/repo/work/lab-runs')
if sys.argv[1]=='deps':
 def go(k):
  r=root/(k+'f')
  cmd={'o':'sudo -n pacman -Sy --noconfirm python-gobject gtk4 python-pyqt6 python-pillow python-numpy','b':'sudo -n dnf install -y python3-gobject gtk4 python3-qt6 python3-pillow python3-numpy','n':'sudo -n apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy','k':'sudo -n apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy'}[k]
  try: print(k,lab.ssh(r,cmd,timeout=300),flush=True)
  except Exception as e:print(k,str(e),flush=True)
 with concurrent.futures.ThreadPoolExecutor(4) as p:list(p.map(go,'obnk'))
elif sys.argv[1]=='cmd':print(lab.guest_session(root/(sys.argv[2]+'f'),sys.argv[3],timeout=300))
elif sys.argv[1]=='put':print(lab.put(root/(sys.argv[2]+'f'),Path(sys.argv[3]),sys.argv[4]))
elif sys.argv[1]=='install':print(lab.install(root/(sys.argv[2]+'f'),appimage=Path(sys.argv[3])))
