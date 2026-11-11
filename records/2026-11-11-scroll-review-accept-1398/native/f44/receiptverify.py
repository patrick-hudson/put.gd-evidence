from pathlib import Path
import json,hashlib,struct
P=Path('/home/patrick/work/sr8');got=[]
for f in (P/'received').glob('*.bin'):
 b=f.read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n')
 if i<0:continue
 j=i+8
 while j+12<=len(b):
  n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=12+n
  if kind==b'IEND':got.append(hashlib.sha256(b[i:j]).hexdigest());break
out={}
for name in ['cap-final','cap-warning','stop-middle-final','mcp','user']:
 f=P/name/'capture.png'
 if f.exists():
  sha=hashlib.sha256(f.read_bytes()).hexdigest();out[name]={'sha256':sha,'loopbackReceived':sha in got}
(P/'loopback-verification.json').write_text(json.dumps({'receivedPngCount':len(got),'cases':out},indent=2));print(out)
