from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
for n in ['s3n','s3h']:
 r=Path('/home/patrick/work/put.gd/work/lab-runs')/n;lab.put(r,Path('/home/patrick/work/s3a/guest-cancel-diagnose.py'),'/home/lab/work/s3a/guest-cancel-diagnose.py');print(n,lab.ssh(r,'python3 /home/lab/work/s3a/guest-cancel-diagnose.py',timeout=30),flush=True)
