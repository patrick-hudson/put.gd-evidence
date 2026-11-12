from pathlib import Path
import json,hashlib,tarfile,stat,os,sys,struct
P=Path('/home/patrick/work/sa2');H=Path('/home/patrick/work/scroll-review-1398-evidence');H.mkdir(mode=0o700,exist_ok=True);host=sys.argv[1]
received=[]
for f in (P/'received').glob('*.bin'):
 b=f.read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n');j=i+8
 if i<0:continue
 while j+12<=len(b):
  n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=n+12
  if kind==b'IEND':received.append(hashlib.sha256(b[i:j]).hexdigest());break
checks={}
for n in ['cap','postcap','busy-first','busy-second','history-failure']:
 f=P/n/'capture.png'
 if f.exists():
  sha=hashlib.sha256(f.read_bytes()).hexdigest();checks[n]={'sha256':sha,'payloadEqualsPng':sha in received}
(P/'payload-verification.json').write_text(json.dumps({'receivedPngCount':len(received),'cases':checks},indent=2))
files=[]
for f in P.iterdir():
 if f.is_file() and f.name!='env.json' and f.suffix in ['.py','.html','.log','.console','.json','.jsonl','.txt','.png','.sxcu']:files.append(f)
 if f.is_dir() and ((f/'result.json').exists() or f.name in ['user','harness-failures','received']):files.extend(q for q in f.rglob('*') if q.is_file())
manifest={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files};(P/'export-manifest.json').write_text(json.dumps(manifest,indent=2));files.append(P/'export-manifest.json')
out=H/(host+'.tgz')
with tarfile.open(out,'w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(P)))
print(json.dumps({'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files),'bytes':out.stat().st_size}))
