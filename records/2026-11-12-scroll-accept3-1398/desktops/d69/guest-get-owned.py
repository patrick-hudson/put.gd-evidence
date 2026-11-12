from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2')
lab.get(r,'/home/lab/work/s3a/'+sys.argv[1],Path('/home/patrick/work/s3a')/sys.argv[2])
