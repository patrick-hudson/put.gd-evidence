import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import nightly_desktop_guest as g
# Extend the existing protected RPM transaction to this opt-in desktop.
g.FEDORA_DESKTOP=(*g.FEDORA_DESKTOP,'labwc*','budgie*')
out=Path('work/np/install-f44');out.mkdir(mode=0o700)
g.install_rpm(Path('work/lab-runs/np4').resolve(),Path('work/np/assets/v26.1108.4234-nightly/packages/putgd-26.1108.4234-nightly-fedora44-x86_64.rpm').resolve(),out.resolve())
