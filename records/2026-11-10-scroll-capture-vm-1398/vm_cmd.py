import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'))
import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/sys.argv[1]
print(lab.guest_session(r,sys.argv[2],timeout=180))
