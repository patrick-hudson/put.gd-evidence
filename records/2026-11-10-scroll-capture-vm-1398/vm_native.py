import sys,shlex
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=sys.argv[1];kind=sys.argv[2];run=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/r
lab.put(run,Path(__file__).parent/'toolkit.py','/home/lab/putgd-lab/toolkit.py')
print(lab.guest_session(run,f'nohup python3 ~/putgd-lab/toolkit.py {kind} > ~/putgd-lab/{kind}.log 2>&1 < /dev/null & echo $! > ~/putgd-lab/{kind}.pid'))
