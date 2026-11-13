import sys
from rfb import RFB
r=RFB(int(sys.argv[1]));r.frame();r.screenshot(sys.argv[2])
