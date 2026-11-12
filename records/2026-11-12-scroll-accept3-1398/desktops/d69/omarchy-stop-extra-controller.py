from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3h');lab.put(r,Path('/home/patrick/work/s3a/omarchy-stop-extra-browser.py'),'/home/lab/work/s3a/omarchy-stop-extra-browser.py');print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 omarchy-stop-extra-browser.py',timeout=180),flush=True)
