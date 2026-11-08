import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import nightly_desktop_guest as g
# Extend the existing protected RPM transaction to this opt-in desktop.
g.FEDORA_DESKTOP=(*g.FEDORA_DESKTOP,'labwc*','budgie*')
out=Path(sys.argv[3]);out.mkdir(mode=0o700)
g.install_rpm(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),out.resolve())
