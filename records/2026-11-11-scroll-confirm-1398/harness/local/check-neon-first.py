from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
D=Path('/home/patrick/work/scn');r=Path('/home/patrick/work/svm1398/repo/work/lab-runs/ncn');f=D/'neon-first-browser.png';lab.get(r,'/tmp/v3/cases/browser-bottom-0/capture.png',f);ns={};exec(Path('/home/patrick/work/svm1398/v2analyze.py').read_text().split('out=json.loads')[0],ns);print(ns['ruler'](f,2400,codewidth=1280))
