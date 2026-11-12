from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3k')
print(lab.guest_session(r,sys.argv[1],timeout=180),end='')
