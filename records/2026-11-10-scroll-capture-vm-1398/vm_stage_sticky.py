import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
for r in ['o','b','n','k']:
 run=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/r
 lab.put(run,Path(__file__).parent/'sticky-vm.html','/home/lab/putgd-lab/ruler.html')
