import sys,time,json,subprocess,hashlib
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
r=S/'work/lab-runs/k1';o=Path.home()/'work/kq/evidence/k1/x11-control';o.mkdir(exist_ok=True);out=[]
from PIL import Image
Image.new('RGB',(210,110),(20,80,220)).save(o/'source-x11.png');lab.put(r,str(o/'source-x11.png'),'source-x11.png')
def g(s):return lab.guest_session(r,'export QT_QPA_PLATFORM=xcb\n'+s)
for mode in ['stock','save-images']:
 print(g('kwriteconfig6 --file ~/.config/klipperrc --group General --key IgnoreImages '+('true' if mode=='stock' else 'false')+'; qdbus6 org.kde.klipper /klipper reloadConfig'))
 g('(xclip -quiet -selection clipboard -target image/png -i < ~/source-x11.png > ~/owner.log 2>&1 & echo $! > ~/owner.pid); true');time.sleep(2)
 g('timeout 8 xclip -selection clipboard -target image/png -o > ~/before.png');g('p=$(cat ~/owner.pid); kill "$p" 2>/dev/null || true');time.sleep(2);g('timeout 8 xclip -selection clipboard -target image/png -o > ~/after.png 2>/dev/null || true')
 for f in ['before','after']:lab.get(r,'/home/lab/'+f+'.png',o/(mode+'-control-'+f+'.png'))
 from PIL import Image
 a=(o/(mode+'-control-before.png')).read_bytes();b=(o/(mode+'-control-after.png')).read_bytes();pixels=False
 if b:
  aa=Image.open(o/(mode+'-control-before.png')).convert('RGBA');bb=Image.open(o/(mode+'-control-after.png')).convert('RGBA');pixels=aa.size==bb.size and aa.tobytes()==bb.tobytes()
 out.append(dict(mode=mode,beforeSha=hashlib.sha256(a).hexdigest(),afterSha=hashlib.sha256(b).hexdigest(),byteEqual=a==b,pixelEqual=pixels,afterBytes=len(b)));print(out[-1],flush=True)
(o/'control-pixels.json').write_text(json.dumps(out,indent=2));g('kwriteconfig6 --file ~/.config/klipperrc --group General --key IgnoreImages true; qdbus6 org.kde.klipper /klipper reloadConfig')
