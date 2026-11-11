from pathlib import Path
import hashlib,json,struct,sys
for k in sys.argv[1]:
 p=Path('/home/patrick/work/svm1398/v3evidence')/k/'final';archive={hashlib.sha256(f.read_bytes()).hexdigest() for f in (p/'archive').rglob('*.png')};out=[]
 for f in (p/'received').glob('*.bin'):
  b=f.read_bytes();start=b.find(b'\x89PNG\r\n\x1a\n');pos=start+8
  try:
   assert start>=0
   while pos+12<=len(b):
    n=struct.unpack('>I',b[pos:pos+4])[0];typ=b[pos+4:pos+8];pos+=12+n
    if typ==b'IEND':break
   sha=hashlib.sha256(b[start:pos]).hexdigest();out.append({'receipt':f.name,'bodySha256':hashlib.sha256(b).hexdigest(),'pngSha256':sha,'matchesArchive':sha in archive})
  except Exception:out.append({'receipt':f.name,'error':'malformed multipart PNG'})
 (p.parent/'upload-verification.json').write_text(json.dumps({'received':len(out),'matched':sum(x.get('matchesArchive',False) for x in out),'receipts':out},indent=2));print(k,len(out),sum(x.get('matchesArchive',False) for x in out))
