import sys
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/b3';s=lab.ssh(r,'sudo -n dnf install -y python3-gobject gtk4 python3-qt6 python3-pillow python3-numpy 2>&1 || true',timeout=300);(B/'v3evidence/b/dependencies-retry.log').write_text(s);print(s[-3500:])
