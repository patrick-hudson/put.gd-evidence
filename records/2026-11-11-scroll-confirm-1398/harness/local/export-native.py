from pathlib import Path
import json,hashlib,tarfile,struct,sys
P=Path(sys.argv[1]);got=[]
for f in (P/'received').glob('*.bin'):
 b=f.read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n')
 if i<0:continue
 j=i+8
 while j+12<=len(b):
  n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=12+n
  if kind==b'IEND':got.append(hashlib.sha256(b[i:j]).hexdigest());break
v={}
for n in ['cap','postcap','mcp']:
 f=P/n/'capture.png'
 if f.exists():sha=hashlib.sha256(f.read_bytes()).hexdigest();v[n]={'sha256':sha,'loopbackReceived':sha in got}
(P/'upload-verification.json').write_text(json.dumps({'receivedPngCount':len(got),'cases':v},indent=2))
files={}
for f in P.iterdir():
 if f.is_file() and f.suffix in ['.json','.log','.jsonl','.console','.txt','.png'] and f.name not in ['env.json','hashes-confirm.json']:files[f.name]=f
 if f.is_dir() and (f/'result.json').exists():
  for g in f.rglob('*'):
   if g.is_file() and g.suffix in ['.png','.json','.log']:files[str(g.relative_to(P))]=g
for f in (P/'supplemental').rglob('*'):
 if f.is_file():files[str(f.relative_to(P))]=f
for f in (P/'s/putgd/logs').glob('*.jsonl'):files['events/'+f.name]=f
m={n:hashlib.sha256(f.read_bytes()).hexdigest() for n,f in files.items()};(P/'hashes-confirm.json').write_text(json.dumps(m,indent=2))
with tarfile.open(P/'export-confirm.tgz','w:gz') as t:
 for n,f in files.items():t.add(f,arcname=n)
 t.add(P/'hashes-confirm.json',arcname='hashes-confirm.json')
print('Exported',len(files),'files; loopback',v)
