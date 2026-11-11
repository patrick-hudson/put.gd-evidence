from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs/ncn');p=Path('/home/patrick/work/scn/firefox-policy-copy.py');lab.put(r,p,'/home/lab/firefox-policy-copy.py');print(lab.ssh(r,'python3 /home/lab/firefox-policy-copy.py',timeout=120))
