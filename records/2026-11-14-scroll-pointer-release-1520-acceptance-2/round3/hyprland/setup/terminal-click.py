from pathlib import Path
from trial import Rfb
from localinput import Pointer
import time,subprocess
l=Path.home()/'work/s5302';p=l/'a/helper.log';(l/'a/terminal-offset.txt').write_text(str(p.stat().st_size));m=Pointer(Rfb(5901));m.pointer(450,300,1);time.sleep(.1);m.pointer(450,300);m.close();subprocess.run(['sudo','-n','python3',str(l/'keyboard.py')],check=True);time.sleep(.3);(l/'a/terminal-quiet.log').write_bytes(p.read_bytes()[int((l/'a/terminal-offset.txt').read_text()):]);print((l/'a/terminal-received.txt').read_text())
