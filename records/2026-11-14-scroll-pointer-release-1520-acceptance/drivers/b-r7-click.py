import time
from pathlib import Path
from geometry import output
from localinput import Pointer
l=Path.home()/'work/s1520';p=l/'a/helper.log';(l/'a/terminal-log-offset').write_text(str(p.stat().st_size));m=Pointer(output());m.pointer(850,450,1);time.sleep(.1);m.pointer(850,450);m.close()
