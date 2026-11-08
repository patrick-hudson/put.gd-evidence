import json,hashlib,tarfile,shutil,re
from pathlib import Path,PurePosixPath
root=Path('work/np1275/evidence/2026-11-08-budgie-omarchy-nightly-4234');root.mkdir(mode=0o700,parents=True,exist_ok=True)
index=[]
visuals=[]
selected_global=set()
for batch in ('r1','r1b','r1c','r2','r3','r3b','r3c','r4','r5','r5b','r6','r5-unused'):
 src=Path('work/np1275/export')/batch
 if not src.exists():continue
 for p in src.glob('*.json'):
  target=root/'batches'/batch/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 archive=src/'attachments.tgz'
 if not archive.exists():continue
 with tarfile.open(archive) as t:
  selected=set()
  for m in t.getmembers():
   if not m.isfile() or not m.name.endswith('/receipt.json'):continue
   receipt=json.load(t.extractfile(m));rows=receipt['interactions'];frames={f['path']:f for row in rows for f in row.get('frames',[])};parent=str(PurePosixPath(m.name).parent)
   wanted=('outcome-failed-before-cleanup',) if any(r.get('functional')!='passed' for r in rows) else ('four-marks-before-upload','recording-private-review','browser-content','copy-image-exact-pixels','clipboard-after-restart','upload-banner','exact-deletion-confirmation','delete-exact-owned-object','revoke-exact-owned-link','browser-link-unavailable','browser-cloudfront-status-200')
   chosen=[name for name,f in frames.items() if f['label'] in wanted]
   if not chosen:
    chosen=[name for name,f in frames.items() if f['label']=='publication-result'][:1] or list(frames)[:1]
   selected.update(parent+'/'+name for name in chosen)
  for m in t.getmembers():
   if not m.isfile():continue
   path=PurePosixPath(m.name)
   assert not path.is_absolute() and '..' not in path.parts
   if path.name not in ('receipt.json','terminal.json','coverage.json','commands.jsonl','frame-masks.json','pattern-occlusion.json') and path.suffix!='.png':continue
   data=t.extractfile(m).read()
   if path.suffix=='.png':
    selected_here=m.name in selected;relative='batches/'+batch+'/'+str(path);target=root/relative
    visuals.append(dict(path=relative,sha256=hashlib.sha256(data).hexdigest(),archiveMember=m.name,published=selected_here,batch=batch))
    if not selected_here:
     if target.exists():
      assert hashlib.sha256(target.read_bytes()).hexdigest()==hashlib.sha256(data).hexdigest();target.unlink()
     continue
    selected_global.add(relative)
   target=root/'batches'/batch/str(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 index.append(dict(batch=batch,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size,workstation=str(archive.resolve()),restore='python3 -m tarfile -e <archive> <private-empty-dir>; require_terminal verifies receipt/coverage digests before reuse'))
(root/'visual-retention.json').write_text(json.dumps(visuals,indent=2))
(root/'archive-index.json').write_text(json.dumps(index,indent=2))
for p in Path('work/np1275/export/u24-recovery').glob('*.json'):
 target=root/'cleanup/u24-recovery'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for p in Path('work/np1275/profiles').glob('*.json'):
 target=root/'sources/private-profiles'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for name in ('run_row.py','run_row-13cell-original.py','retire_row.py','export_verified.py','configure_rows.py','prepare_arch.py','prepare_fedora.py','install_arch.py','install_f44.py'):
 p=Path('work/np1275')/name;target=root/'sources'/name;shutil.copyfile(p,target)
print(root,len(list(root.rglob('*.png'))),'audited PNG frames')
