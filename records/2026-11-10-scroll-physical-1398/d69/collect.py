from pathlib import Path
import shutil,json,hashlib,tarfile
p=Path('/tmp/sp1398');out=p/'export';out.mkdir(exist_ok=False)
# Only known synthetic test artifacts and diagnostics. Exclude package binaries,
# browser profiles, XDG config, credential stores, environment and SDK envs.
for f in p.iterdir():
 if f.is_file() and f.suffix in ('.log','.png','.py','.html','.js') or f.is_file() and f.name in ('desktop.json','identities.json','memory.json','memory-ui-open.json','user-history.json','restore-sha256.txt'):
  shutil.copyfile(f,out/f.name)
 if f.is_dir() and (f/'result.json').exists():
  d=out/f.name;d.mkdir()
  for n in ('result.json','rpc.jsonl','capture.png','browser.log'):
   if (f/n).exists():shutil.copyfile(f/n,d/n)
 for n in []:pass
for name in ['received','state']:
 d=p/name
 if name=='received' and (d/'receipts.jsonl').exists():shutil.copyfile(d/'receipts.jsonl',out/'upload-receipts.jsonl')
 if name=='state' and d.exists():
  for f in d.rglob('*.log'):
   dest=out/('resident-state-'+f.name);shutil.copyfile(f,dest)
for f in p.glob('*-staging.json'):shutil.copyfile(f,out/f.name)
manifest={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
(out/'SHA256.json').write_text(json.dumps(manifest,indent=2))
with tarfile.open(p/'evidence.tar','w') as t:t.add(out,arcname='evidence')
print(len(manifest),'files',sum(f.stat().st_size for f in out.rglob('*') if f.is_file()))
