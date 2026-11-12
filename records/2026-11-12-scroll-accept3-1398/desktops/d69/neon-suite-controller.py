from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3n');P=Path('/home/patrick/work/s3a');lab.put(r,P/'guest-native-suite.py','/home/lab/work/s3a/guest-native-suite.py')
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 guest-native-suite.py',timeout=7200),flush=True)
