from pathlib import Path
import tarfile,hashlib,json
P=Path('/home/patrick/work/p21398');files=[]
for f in P.iterdir():
 if f.is_file() and f.name!='env.json' and f.suffix in ['.py','.json','.jsonl','.png','.log','.txt']:files.append(f)
 if f.is_dir() and (f/'result.json').is_file():files.extend(x for x in f.iterdir() if x.is_file())
files.append(P/'received/receipts.jsonl') if (P/'received/receipts.jsonl').exists() else None
files=sorted(set(files));manifest={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
(P/'export-manifest.json').write_text(json.dumps(manifest,indent=2));files.append(P/'export-manifest.json')
with tarfile.open(P/'export.tar.gz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(P)),recursive=False)
print(len(files),hashlib.sha256((P/'export.tar.gz').read_bytes()).hexdigest())
