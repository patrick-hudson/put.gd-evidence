from pathlib import Path
from PIL import Image,ImageChops
import json,sys
r=Path(sys.argv[1]);a=Image.open(r/'quick-source.png').convert('RGB');b=Image.open(r/'quick-email.png').convert('RGB');assert a.size==b.size
box=ImageChops.difference(a,b).getbbox();assert box
upperSame=ImageChops.difference(a.crop((0,0,a.width,140)),b.crop((0,0,b.width,140))).getbbox() is None
lowerSame=ImageChops.difference(a.crop((0,210,a.width,a.height)),b.crop((0,210,b.width,b.height))).getbbox() is None
# A fully opaque black rectangle must cover every original email ink pixel.
ink=[]
for y in range(140,200):
 for x in range(a.width):
  if min(a.getpixel((x,y)))<100:ink.append((x,y))
covered=bool(ink) and all(b.getpixel(p)==(0,0,0) for p in ink)
v={'sourceSize':a.size,'changedBounds':box,'firstTwoLinesUnchanged':upperSame,'belowEmailUnchanged':lowerSame,'originalEmailInkPixels':len(ink),'allEmailInkBlack':covered,'pixelCheckPassed':upperSame and lowerSame and covered and box[1]>=140 and box[3]<=210}
(r/'pixel-verification.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
