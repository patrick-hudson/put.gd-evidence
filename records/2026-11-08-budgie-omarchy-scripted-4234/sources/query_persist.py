import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
r=Path(sys.argv[1]).resolve();kind=sys.argv[2]
cmd='pacman -Si wl-clip-persist' if kind=='arch' else 'dnf --color=never info wl-clip-persist'
print(lab.ssh(r,cmd,timeout=120))
