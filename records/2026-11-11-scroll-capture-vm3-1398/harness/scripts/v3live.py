import sys
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs'/(sys.argv[1]+'3');print(lab.guest_session(r,'cat /tmp/v3/cases/'+sys.argv[2]+'/live.json; tail -3 /tmp/v3/helper.log'))
