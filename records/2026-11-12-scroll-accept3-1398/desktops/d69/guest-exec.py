import sys
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');source=Path(sys.argv[1]);lab.put(r,source,'/home/lab/work/s3a/'+source.name)
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 '+source.name,timeout=90),flush=True)
