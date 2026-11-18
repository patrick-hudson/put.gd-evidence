#!/usr/bin/env python3
"""verify.py ORIG.png RED.png REPORT.json -> per mark: pixels, black %, original-pixel-surviving count"""
import sys,json
from PIL import Image
o=Image.open(sys.argv[1]).convert('RGB');r=Image.open(sys.argv[2]).convert('RGB');rep=json.load(open(sys.argv[3]))
assert o.size==r.size,(o.size,r.size)
ok=True;out=[]
po=o.load();pr=r.load()
# union mask of mark rects
rects=[s['rect'] for s in rep['shapes'] if s.get('rect')]
for i,(x,y,w,h) in enumerate(rects):
    n=black=same=samenb=0
    for yy in range(max(0,y),min(o.size[1],y+h)):
        for xx in range(max(0,x),min(o.size[0],x+w)):
            n+=1;a=po[xx,yy];b=pr[xx,yy]
            if b==(0,0,0): black+=1
            elif a==b: same+=1
    out.append({'rect':[x,y,w,h],'px':n,'black':black,'nonblack_equal_to_original':same})
    if same: ok=False
changed_outside=0
mask=Image.new('1',o.size,0)
for (x,y,w,h) in rects: mask.paste(1,(x,y,x+w,y+h))
pm=mask.load()
for yy in range(o.size[1]):
    for xx in range(o.size[0]):
        if not pm[xx,yy] and po[xx,yy]!=pr[xx,yy]: changed_outside+=1
print(json.dumps({'marks':out,'changed_outside_marks_px':changed_outside,'pass':ok and all(m['black']==m['px'] for m in out),'allMarksFullyBlack':all(m['black']==m['px'] for m in out),'marksCount':len(out)},indent=1))
