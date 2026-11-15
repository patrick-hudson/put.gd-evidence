"""Curate public evidence; retain original native exports and full pass images privately."""
from pathlib import Path
import sys,json,hashlib,gzip,shutil,tarfile
P=Path('/home/patrick/work/sfa15');kind=sys.argv[1];assert kind in ['h','b','h2'];root=P/('guest-'+kind);base=P/('guest-'+kind+'-baseline');files={};omitted={};compressed={}
def sha(f):
 h=hashlib.sha256()
 with f.open('rb')as r:
  for chunk in iter(lambda:r.read(4<<20),b''):h.update(chunk)
 return h.hexdigest()
keep_ids={'034ee88f-3b20-4146-8a95-e169587cba1b'}if kind=='h'else set()
for directory in [root,base]:
 f=directory/'mcp-results.json'
 if f.exists():
  for r in json.loads(f.read_text()):
   a=r.get('arguments',{})
   if r.get('tool')=='control_scroll_capture'and a.get('command')=='stop':keep_ids.add(a['id'])
for label,directory in [('',root),('b/',base)]:
 if not directory.exists():continue
 for f in directory.rglob('*'):
  if f.is_symlink()or not f.is_file():continue
  rel=f.relative_to(directory);parts=rel.parts
  if any(x.startswith('profile')or x in ['tools','c','d','s','cache','r','squashfs-root','__pycache__']for x in parts):continue
  if f.name=='session-env.json'or f.name.endswith('.tar.gz'):continue
  arc=label+str(rel)
  if 'archive'in parts:
   if any(s in f.name for s in keep_ids):files[arc]=f
   elif f.suffix=='.png':omitted[arc]={'privatePath':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'reason':'Original admitted image retained privately; public packet has case captures, result hashes, state photos and selected control images.'}
   continue
  if f.suffix not in ['.py','.json','.jsonl','.png','.log','.err','.md','.html','.txt','.xml','.c','.h','.gz']and f.name!='cli':continue
  if f.name=='helper.log'and len(parts)==1:
   g=directory/'helper-complete-public.log.gz'
   with f.open('rb')as a,gzip.open(g,'wb')as b:shutil.copyfileobj(a,b)
   with gzip.open(g,'rb')as a:assert hashlib.sha256(a.read()).hexdigest()==sha(f)
   files[label+g.name]=g;compressed[arc]={'compressedMember':label+g.name,'sourceSha256':sha(f),'sourceBytes':f.stat().st_size,'restore':'gzip -dc MEMBER > helper.log'}
   continue
  if f.name in ['capture.png','reference.png']and parts[0]=='runs':
   case=parts[1];omit=('-wiki-'in case and not('-auto-inside'in case and f.name=='capture.png'))or(f.name=='reference.png'and('-python-auto'in case or'-github-auto'in case))
   if omit:
    omitted[arc]={'privatePath':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'reason':'Large passed image/reference retained privately with original case scores; native bar/Saving pictures and all failure cases remain public.'};continue
  files[arc]=f
 # Copy all retirement receipts and cleanup visual verification.
R=P/('retirement-'+kind)
for f in R.rglob('*')if R.exists()else[]:
 if f.is_file()and not f.is_symlink():files['retirement/'+str(f.relative_to(R))]=f
run=P/'repo/work/lab-runs'/('sfa15'+kind)
for name in ['overlay-cleanup.json','overlay-cleanup-status.json']:
 if(run/name).exists():files['retirement/'+name]=run/name
if kind=='h2':
 for f in P.glob('h2-*'):
  if f.is_file()and f.suffix in ['.py','.json','.log']:files['host-setup/'+f.name]=f
 for name in ['wall-h2-controlled','wall-h2-firefox']:
  for f in(P/name).glob('*'):
   if f.is_file()and f.suffix in ['.png','.json','.log']:files['wall/'+name+'/'+f.name]=f
for name in ['curate-guest-evidence.py','offline-hypr-controls.py','analyze-budgie.py','wide-row-check.py','arrow-pair-scan.py','arrow-scan.py']:
 if(P/name).exists():files['analysis-sources/'+name]=P/name
index={n:{'sha256':sha(f),'bytes':f.stat().st_size}for n,f in files.items()};large=[(n,v['bytes'])for n,v in index.items()if v['bytes']>=50*1024*1024];assert not large,large
manifest=root/'public-restore-index.json';manifest.write_text(json.dumps({'files':index,'compressedSources':compressed,'omittedLargeImages':omitted,'note':'Original complete native exports and every host test source/result remain private on d69. Omitted public copies are large pass images/references or redundant admitted images, never deleted. Credential/session environment, keys, private configuration, caches, profiles and vendor binaries are excluded, not copied into this record.'},indent=1));files[manifest.name]=manifest
out=P/(kind+'-curated-evidence.tar.gz')
with tarfile.open(out,'w:gz')as t:
 for n,f in sorted(files.items()):t.add(f,arcname=n,recursive=False)
print(json.dumps({'source':str(root),'path':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':sha(out),'omittedLargeImages':len(omitted)}),flush=True)
