import sys,shlex
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs/og')
if sys.argv[1]=='cmd':print(lab.guest_session(r,sys.argv[2],timeout=300))
if sys.argv[1]=='put':print(lab.put(r,Path(sys.argv[2]),sys.argv[3]))
if sys.argv[1]=='install':print(lab.install(r,appimage=next(Path('/home/patrick/work/svm1398/v2artifacts/release-appimage').glob('*.AppImage'))))
