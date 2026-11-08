import sys
from PIL import Image, ImageChops
a=Image.open(sys.argv[1]).convert('RGB'); b=Image.open(sys.argv[2]).convert('RGB')
top=int(sys.argv[3]); bottom=int(sys.argv[4]); w,h=a.size; box=(0,top,w,h-bottom)
d=ImageChops.difference(a.crop(box),b.crop(box)).convert('L').point(lambda v:255 if v>24 else 0)
print(sum(1 for v in d.tobytes() if v))
