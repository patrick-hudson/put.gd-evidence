from PIL import Image
from pathlib import Path
import json,hashlib
root=Path.home()/'putgd-lab/h1396-ci/p2-safe-crops'
own=Image.open(root/'owned-before.png').convert('RGB');full=Image.open(root/'private-after.png').convert('RGB');sw,sh=full.size;ww,wh=own.size
anchor=own.crop((12,20,180,21)).tobytes();data=full.tobytes();pos=0;matches=[]
while True:
 i=data.find(anchor,pos)
 if i<0:break
 pos=i+1
 if i%3:continue
 x=(i//3)%sw-12;y=(i//3)//sw-20
 if x>=0 and y>=0 and x+ww<=sw and y+wh<=sh and full.crop((x+12,y+12,x+180,y+48)).tobytes()==own.crop((12,12,180,48)).tobytes():matches.append((x,y))
assert len(matches)==1,matches
x,y=matches[0];full.crop((x,y,x+ww,y+wh)).save(root/'history-multi-select-failure.png')
print(json.dumps({'crop':[x,y,ww,wh],'owned_reference_sha256':hashlib.sha256((root/'owned-before.png').read_bytes()).hexdigest(),'original_sha256':hashlib.sha256((root/'private-after.png').read_bytes()).hexdigest(),'reason':'Unique exact header match to the driver owned History window; recipe only sent list keyboard input, with no window movement. Crop generated on k72; original retained privately.'},indent=2))
