import sys,time
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path(sys.argv[1]).resolve();x,y=map(int,sys.argv[2:4]);button=sys.argv[4] if len(sys.argv)>4 else 'left'
lab.pointer(run,x,y,1280,800,True,button)
time.sleep(.15)
lab.pointer(run,x,y,1280,800,False,button)
time.sleep(.5)
print('real QEMU pointer',x,y,button)
