from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3n');lab.put(r,Path('/home/patrick/work/s3a/firefox-tou-inspect.py'),'/home/lab/work/s3a/firefox-tou-inspect.py');print(lab.ssh(r,'python3 /home/lab/work/s3a/firefox-tou-inspect.py 2>&1; true',timeout=30))
