import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'lab'))
import lab,overlay_cleanup
overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd')
lab.main()
