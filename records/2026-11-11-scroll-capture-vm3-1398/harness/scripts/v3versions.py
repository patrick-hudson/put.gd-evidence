import sys
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
for k in sys.argv[1]:
 r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
 c='pacman -Q qt6-base python-pyqt6 gtk4 hyprland quickshell' if k=='o' else 'rpm -q qt6-qtbase python3-pyqt6-base gtk4 labwc budgie-desktop' if k=='b' else 'dpkg-query -W libqt6widgets6 python3-pyqt6 libgtk-4-1 kwin-wayland'
 (o/'native-versions.log').write_text(lab.guest_session(r,c+' || true'))
