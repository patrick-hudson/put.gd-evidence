import sys,json,time,subprocess,hashlib
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
n=sys.argv[1];r=S/'work/lab-runs'/n;out=Path.home()/'work/kq/evidence'/n;out.mkdir(parents=True,exist_ok=True)
def g(s): return lab.guest_session(r,s,timeout=200)
def shot(t):
 p=lab.screenshot(r,t)['path'];from PIL import Image;Image.open(p).save(out/(t+'.png'))
print(g('sudo -n apt-get install -y -q wl-clipboard kolourpaint kate >/tmp/kq-install.log 2>&1; cat /etc/os-release; cat /usr/share/config.kcfg/klipper.kcfg 2>/dev/null || true; cat ~/.config/klipperrc 2>/dev/null || true'))
shot('stock-desktop')
# Generate synthetic raster using PNG standard library, on builder, push it.
import zlib,struct
w,h=180,100
raw=b''.join(b'\0'+bytes([220,30,80])*w for _ in range(h))
def chunk(t,b):return struct.pack('!I',len(b))+t+b+struct.pack('!I',zlib.crc32(t+b))
p=out/'source.png';p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
a,d=lab.scp_connection(r);subprocess.run(a+[str(p),d+'source.png'],check=True)
results=[]
for mode in ['stock','save-images']:
 if mode=='save-images': print(g('kwriteconfig6 --file ~/.config/klipperrc --group General --key SaveImages true; qdbus6 org.kde.klipper /klipper reloadConfig'))
 for kind in ['image','text']:
  cmd='wl-copy --foreground --type image/png < ~/source.png' if kind=='image' else 'wl-copy --foreground --type text/plain https://example.invalid/kq-control'
  print(g('( '+cmd+' > ~/owner.log 2>&1 & echo $! > ~/owner.pid ); true'));time.sleep(2)
  read='wl-paste -t image/png' if kind=='image' else 'wl-paste --no-newline -t text/plain'
  before=g('('+read+' 2>/dev/null || true) | sha256sum').split()[0]
  print(g('p=$(cat ~/owner.pid); ps -p "$p" -o pid,comm || true; kill "$p" 2>/dev/null || true'));time.sleep(2)
  after=g('('+read+' 2>/dev/null || true) | sha256sum').split()[0]
  results.append(dict(mode=mode,kind=kind,before=before,after=after,kept=before==after))
  print(results[-1],flush=True)
  if kind=='image':
   print(g('(setsid -f kolourpaint > ~/paint.log 2>&1 </dev/null); true'));time.sleep(3);lab.key(r,['ctrl','v']);time.sleep(2);shot(mode+'-image-owner-exit-paste')
   print(g('for p in $(pgrep -x kolourpaint); do kill "$p"; done; true'))
(out/'controls.json').write_text(json.dumps(results,indent=2))
print(g('kwriteconfig6 --file ~/.config/klipperrc --group General --key SaveImages false; qdbus6 org.kde.klipper /klipper reloadConfig; cat ~/.config/klipperrc'))
