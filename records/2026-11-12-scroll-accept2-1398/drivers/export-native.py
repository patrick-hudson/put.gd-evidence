from pathlib import Path
import os,json,hashlib,tarfile,sys,shutil,stat,time
h=sys.argv[1];roots={'m74':['sa2','sl25','sq3','sq4'],'f44':['sa2','sf2'],'d69':['sa2','sl25','sd2']}[h];A=Path('/home/patrick/work/scroll-accept2-archive');A.mkdir(mode=0o700,exist_ok=True);O=A/(h+'-public');O.mkdir(mode=0o700,exist_ok=True);manifest={};files=[]
for n in roots:
 p=Path('/home/patrick/work')/n;assert p.is_dir() and p.stat().st_uid==os.getuid()
 for f in p.rglob('*'):
  if f.is_symlink() or not f.is_file():continue
  assert f.stat().st_uid==os.getuid(),str(f);rel=n+'/'+str(f.relative_to(p));manifest[rel]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size};files.append((f,rel))
 (O/n).mkdir(exist_ok=True)
 cases=[d for d in p.iterdir() if d.is_dir() and ((d/'result.json').exists() or (d/'capture.png').exists())]
 for fa in p.glob('fa*'):
  if fa.is_dir():cases += [d for d in fa.iterdir() if d.is_dir() and (d/'result.json').exists()]
 for d in cases:
  q=O/n/d.relative_to(p);q.mkdir(parents=True,exist_ok=True)
  for f in d.iterdir():
   if not f.is_file() or f.is_symlink():continue
   if f.name not in ['capture.png','helper.log','result.json','verification.json','timing.json'] and not f.name.endswith('-verification.json'):continue
   if h=='f44' and n=='sa2' and d.name.startswith('long-bottom-') and f.name=='capture.png':continue
   shutil.copyfile(f,q/f.name)
  if any(d.glob('screen-*.png')) and d.name.startswith('cancel'):
   for f in d.glob('screen-*.png'):shutil.copyfile(f,q/f.name)
 for f in p.iterdir():
  if f.is_file() and not f.is_symlink() and (f.name in ['identity.json','capabilities.json','rpc.jsonl','cleanup.json','extension-restoration.json','upload-verification.json','variant-summary.json','blank-margin-summary.json','notify-method-events.jsonl','small-footer-cap-refusal.json','dashboard-preparation.json','socket-preflight.json'] or f.name.endswith(('.error','-ready.json'))):shutil.copyfile(f,O/n/f.name)
 for fa in p.glob('fa*'):
  if fa.is_dir() and (fa/'events.json').exists():
   q=O/n/fa.name;q.mkdir(exist_ok=True)
   for f in fa.iterdir():
    if f.is_file() and f.name in ['events.json','notify.log','helper.log','after-capture.png','first-after-capture.png']:shutil.copyfile(f,q/f.name)
 for name in ['cap-warning-visible.png','history-failure.png','balloon-visible.png','before-first-frame.png','tray-restored.png','done']:
  f=p/name
  if f.is_file():shutil.copyfile(f,O/n/name)
 # User-style capture files have their own verifier and helper logs.
 if (p/'user').is_dir():
  q=O/n/'user';q.mkdir(exist_ok=True)
  for f in (p/'user').iterdir():
   if f.is_file() and f.suffix in ['.png','.json','.log']:shutil.copyfile(f,q/f.name)
M=A/(h+'-cold-manifest.json');M.write_text(json.dumps({'roots':roots,'files':manifest},indent=2));arc=A/(h+'-cold.tgz')
with tarfile.open(arc,'w:gz',compresslevel=1) as t:
 t.add(M,arcname='cold-manifest.json')
 for f,rel in files:t.add(f,arcname=rel,recursive=False)
# Verify every retained file from the archive before scratch deletion is allowed.
with tarfile.open(arc) as t:
 for m in t:
  if m.name=='cold-manifest.json':continue
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==manifest[m.name]['sha256'],m.name
v={'host':h,'roots':roots,'filesVerified':len(files),'archiveSha256':hashlib.sha256(arc.read_bytes()).hexdigest(),'verified':True,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(A/(h+'-cold-verified.json')).write_text(json.dumps(v,indent=2));pub={str(f.relative_to(O)):hashlib.sha256(f.read_bytes()).hexdigest() for f in O.rglob('*') if f.is_file()};(O/'manifest.json').write_text(json.dumps(pub,indent=2))
with tarfile.open(A/(h+'-public.tgz'),'w:gz') as t:
 for f in O.rglob('*'):
  if f.is_file():t.add(f,arcname=str(f.relative_to(O)),recursive=False)
print(json.dumps(v),flush=True)
