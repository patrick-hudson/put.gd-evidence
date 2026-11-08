import sys,json
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
from PIL import Image
r=S/'work/lab-runs/k1';o=Path.home()/'work/kq/evidence/k1/x11-final'
op=json.loads((o/'save-images-operations.json').read_text())['operations'][0];source=op['items'][0]['local']['path'];lab.get(r,source,o/'original.png');lab.guest_session(r,'export QT_QPA_PLATFORM=xcb\ntimeout 8 xclip -selection clipboard -target image/png -o > ~/x11-after.png');lab.get(r,'/home/lab/x11-after.png',o/'after.png');a=Image.open(o/'original.png').convert('RGBA');b=Image.open(o/'after.png').convert('RGBA');(o/'pixel-result.json').write_text(json.dumps(dict(originalSize=a.size,afterSize=b.size,pixelsEqual=a.size==b.size and a.tobytes()==b.tobytes()),indent=2));print((o/'pixel-result.json').read_text())
