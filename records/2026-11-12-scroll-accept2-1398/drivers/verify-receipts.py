from pathlib import Path
import json,hashlib,struct,sys
p=Path(sys.argv[1]);got=[]
for f in (p/'received').glob('*.bin'):
 b=f.read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n')
 if i<0:continue
 j=i+8
 while j+12<=len(b):
  n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=12+n
  if kind==b'IEND':got.append(hashlib.sha256(b[i:j]).hexdigest());break
out={}
root=p/'cases' if (p/'cases').exists() else p
for d in root.iterdir():
 f=d/'capture.png'
 if not d.is_dir() or not f.is_file():continue
 sha=hashlib.sha256(f.read_bytes()).hexdigest();out[d.name]={'sha256':sha,'loopbackPayloadEqualsPng':sha in got}
(p/'upload-verification.json').write_text(json.dumps({'receivedPngCount':len(got),'cases':out},indent=2));print({n:v for n,v in out.items() if n in ['cap','cap-visual','postcap','busy-first','busy-second','history-failure']})
