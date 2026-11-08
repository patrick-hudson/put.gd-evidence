import glob, os, time, tarfile
from PIL import Image, ImageChops
W=sorted(glob.glob('/tmp/watch/1*.png'), key=lambda p: float(os.path.basename(p)[:-4]))
R=[p for p in sorted(glob.glob('/tmp/refs/*.png'), key=lambda p: float(os.path.basename(p)[:-4])) if Image.open(p).size==(1024,768)]
C=[p for p in sorted(glob.glob(os.path.expanduser('~/Documents/put.gd/images/*.png')), key=os.path.getmtime) if Image.open(p).size==(600,400)]
print('watch',len(W),'refs',len(R),'captures',len(C))
clean=Image.open(R[0]).convert('RGB').crop((200,200,800,246))
def rows(img):
    d=ImageChops.difference(img,clean).convert('L').point(lambda v:255 if v>8 else 0)
    # pointer lives in the first 27 columns; ignore it
    d=d.crop((30,0,600,46)); b=d.getbbox(); return (b[3] if b else 0)
fmt=lambda t: time.strftime('%H:%M:%S',time.localtime(t))+'.%03d'%(int(t*1000)%1000)
print('refs:', [(fmt(float(os.path.basename(p)[:-4])), rows(Image.open(p).convert('RGB').crop((200,200,800,246)))) for p in R])
caps=[(os.path.getmtime(p), rows(Image.open(p).convert('RGB').crop((0,0,600,46)))) for p in C]
print('captures:', [(fmt(t),r) for t,r in caps])
print('watch:', [(fmt(float(os.path.basename(p)[:-4])), rows(Image.open(p).convert('RGB').crop((200,200,800,246)))) for p in W])
# trial with a card band: capture, then the nearest watch frame on either side
pick=max(range(len(caps)), key=lambda i: caps[i][1])
t=caps[pick][0]
near=min(W, key=lambda p: abs(float(os.path.basename(p)[:-4])-t))
print('pick', pick, fmt(t), caps[pick][1], os.path.basename(near))
with tarfile.open('/tmp/bar.tgz','w:gz') as a:
    a.add(C[pick],arcname='capture.png'); a.add(near,arcname='watch.png'); a.add(R[0],arcname='ref-clean.png')
