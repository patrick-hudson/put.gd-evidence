from pathlib import Path
import json,hashlib,struct,zlib
P=Path('/home/lab/work/s3a');payloads=[]
for f in (P/'received').glob('*.bin'):
 b=f.read_bytes();start=b.find(b'\x89PNG\r\n\x1a\n')
 if start<0:continue
 pos=start+8;valid=True
 while pos+12<=len(b):
  n=struct.unpack('>I',b[pos:pos+4])[0];kind=b[pos+4:pos+8];chunk=b[pos+4:pos+8+n];crc=struct.unpack('>I',b[pos+8+n:pos+12+n])[0]
  if zlib.crc32(chunk)&0xffffffff!=crc:valid=False;break
  pos+=12+n
  if kind==b'IEND':break
 if valid and kind==b'IEND':payloads.append({'file':f.name,'bodySha256':hashlib.sha256(b).hexdigest(),'pngSha256':hashlib.sha256(b[start:pos]).hexdigest(),'pngBytes':pos-start})
out={}
for name in ['cap','cap-warning','busy-first','postcap']:
 f=P/name/'capture.png'
 if not f.exists():continue
 sha=hashlib.sha256(f.read_bytes()).hexdigest();matches=[x for x in payloads if x['pngSha256']==sha];v={'pngSha256':sha,'pngBytes':f.stat().st_size,'loopbackPngBytesEqual':bool(matches),'matches':matches};(f.parent/'upload-verification.json').write_text(json.dumps(v,indent=2));out[name]=v
(P/'payload-proof.json').write_text(json.dumps(out,indent=2));print({n:v['loopbackPngBytesEqual'] for n,v in out.items()})
