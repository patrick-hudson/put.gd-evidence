#!/usr/bin/env python3
"""vnc.py PORT shot OUT.png | key a b.. | type TEXT | click X Y | dclick X Y | rclick X Y | drag x0 y0 x1 y1 | scroll X Y N | sleep S  (several actions chained with --)"""
import sys,time
sys.path.insert(0,'/home/patrick/.t3/worktrees/put.gd/t3-4467dc54-32c1a4eaa1c59795/tools/lab')
from rfb import RFB
port=int(sys.argv[1]); c=RFB(port)
acts=[];cur=[]
for a in sys.argv[2:]:
    if a=='--': acts.append(cur);cur=[]
    else: cur.append(a)
acts.append(cur)
for a in acts:
    k=a[0]
    if k=='shot': c.screenshot(a[1]); print('shot',a[1])
    elif k=='key': c.key(*a[1:])
    elif k=='type': c.type(a[1])
    elif k=='click': c.click(int(a[1]),int(a[2]))
    elif k=='dclick': c.click(int(a[1]),int(a[2])); time.sleep(.12); c.click(int(a[1]),int(a[2]))
    elif k=='rclick':
        x,y=int(a[1]),int(a[2]); c.pointer(x,y); time.sleep(.05); c.pointer_button(x,y,'right',True); time.sleep(.05); c.pointer_button(x,y,'right',False)
    elif k=='move': c.pointer(int(a[1]),int(a[2]))
    elif k=='drag': c.drag(*map(int,a[1:5]))
    elif k=='scroll': c.scroll(int(a[1]),int(a[2]),int(a[3]))
    elif k=='sleep': time.sleep(float(a[1]))
    time.sleep(.3)
c.close()
