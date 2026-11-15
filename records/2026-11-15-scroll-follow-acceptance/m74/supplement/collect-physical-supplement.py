"""Export every owned capture/result/source; configuration, keys and profiles excluded."""
import json,hashlib,tarfile,gzip,shutil,subprocess
from pathlib import Path
P=Path.cwd();files={};raw={}
def sha(f):
 h=hashlib.sha256()
 with f.open('rb')as r:
  for b in iter(lambda:r.read(4<<20),b''):h.update(b)
 return h.hexdigest()
for f in P.rglob('*'):
 parts=f.relative_to(P).parts
 if f.is_symlink()or not f.is_file():continue
 if any(x.startswith('profile-')or x in ['squashfs-root','tools','c','d','s','cache','r','__pycache__']for x in parts):continue
 if f.name in ['session-env.json','export-receipt.json','supplement-restore-index.json']or f.name.endswith('.tar.gz'):continue
 if f in [P/'helper.log',P/'b/helper.log']:continue
 if f.suffix in ['.py','.json','.jsonl','.png','.log','.err','.md','.html','.txt','.xml','.gz']or f.name in ['cli','kcminputrc-before']:files[str(f.relative_to(P))]=f
for root in [P,P/'b']:
 f=root/'helper.log'
 if not f.exists():continue
 g=root/'helper-complete.log.gz'
 with f.open('rb')as a,gzip.open(g,'wb')as b:shutil.copyfileobj(a,b)
 with gzip.open(g,'rb')as r:assert hashlib.sha256(r.read()).hexdigest()==sha(f)
 files[str(g.relative_to(P))]=g;raw[str(f.relative_to(P))]={'sha256':sha(f),'bytes':f.stat().st_size,'compressed':str(g.relative_to(P)),'restore':'gzip -dc MEMBER > helper.log'}
notice=[]
for f in(P/'s').rglob('*.jsonl'):
 for line in f.read_text(errors='replace').splitlines():
  if 'scroll_blank_stretch'in line:notice.append(json.loads(line))
n=P/'blank-notice-log.json';n.write_text(json.dumps(notice,indent=1));files[n.name]=n
n=P/'package-input-proof.json';n.write_text(json.dumps({'osRelease':Path('/etc/os-release').read_text(),'appImages':{x.name:sha(x)for x in[P/'candidate.AppImage',P/'nightly.AppImage']if x.exists()},'installedBinaries':{str(f.relative_to(P)):sha(f)for root in[P,P/'b']for f in(root/'squashfs-root/usr/bin').glob('putgd*')if f.is_file()and not f.is_symlink()}},indent=1));files[n.name]=n
index={name:{'sha256':sha(f),'bytes':f.stat().st_size}for name,f in files.items()}
assert all(v['bytes']<50*1024*1024 for v in index.values()),[(n,v['bytes'])for n,v in index.items()if v['bytes']>=50*1024*1024]
n=P/'supplement-restore-index.json';n.write_text(json.dumps({'files':index,'compressedSources':raw,'excluded':'Credential/session environment, browser profiles, keys, private configuration, caches, vendor and installed runtime binaries. All originals retained privately on this builder.'},indent=1));files[n.name]=n
out=P/'desktop-evidence.tar.gz'
with tarfile.open(out,'w:gz')as t:
 for n,f in sorted(files.items()):t.add(f,arcname=n,recursive=False)
print(json.dumps({'files':len(files),'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out)}),flush=True)
