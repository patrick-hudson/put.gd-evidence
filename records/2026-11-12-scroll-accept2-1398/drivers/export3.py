from pathlib import Path
import tarfile,hashlib,json
P=Path('/home/patrick/work/sa2');files=[]
for f in P.iterdir():
 if f.is_file() and f.name not in ['env.json','export-manifest.json'] and f.suffix in ['.py','.json','.jsonl','.png','.log','.txt']:files.append(f)
 if f.is_dir() and ((f/'result.json').is_file() or f.name in ['prerequisite-refusals','user-invalid-vnc']):
  files.extend(x for x in f.rglob('*') if x.is_file() and not any(t in ['c','d','s','r','archive','cache','__pycache__'] for t in x.relative_to(f).parts) and x.name!='env.json')
files.extend((P/'s/putgd/logs').glob('*.jsonl'))
if (P/'received/receipts.jsonl').exists():files.append(P/'received/receipts.jsonl')
files=sorted(set(files));manifest={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
(P/'export-manifest.json').write_text(json.dumps(manifest,indent=2));files.append(P/'export-manifest.json')
with tarfile.open(P/'export.tar.gz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(P)),recursive=False)
print(len(files),hashlib.sha256((P/'export.tar.gz').read_bytes()).hexdigest())
