import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/sys.argv[1]
lab.put(r,Path(__file__).parent/'ruler-vm.html','/home/lab/putgd-lab/ruler-vm.html')
print(lab.guest_session(r,'''python3 - <<'INNER'
from pathlib import Path
p=Path.home()/'putgd-lab';p.joinpath('ruler.html').write_text(p.joinpath('ruler-vm.html').read_text())
INNER'''))
