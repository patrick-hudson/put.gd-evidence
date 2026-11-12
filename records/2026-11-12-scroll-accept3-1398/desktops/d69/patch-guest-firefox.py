from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
for name in ['s3n','s3h']:
 r=Path('/home/patrick/work/put.gd/work/lab-runs')/name
 lab.put(r,Path('/home/patrick/work/s3a/patch-firefox-profile.py'),'/home/lab/work/s3a/patch-firefox-profile.py');print(name,lab.ssh(r,'python3 /home/lab/work/s3a/patch-firefox-profile.py',timeout=30),flush=True)
