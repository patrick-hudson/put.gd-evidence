import pathlib,tarfile,hashlib,json
base=pathlib.Path.home()/'work/f44-editor-ab-1247';files=[]
for label in ['c1','n1b','c2b','n2']:
 out=base/label
 assert (out/'retirement.json').is_file()
 for name in ['result.json','identity.json','retirement.json','completion.json','completion-manifest.json','preflight.json','gnome-desktop.json','reboot.json','rpm-install.json','rpm-transaction.json','sockets.json']:
  files.append(out/name)
 files.extend(out.glob('*observer.jsonl'))
 for receipt in out.glob('*/receipt.json'):
  folder=receipt.parent
  for name in ['receipt.json','terminal.json','coverage-export.json','frame-masks.json']:
   if (folder/name).is_file():files.append(folder/name)
  files.extend(folder.glob('frames/**/*.png'))
for label in ['n1','c2']:files.append(base/(label+'.log'))
for name in ['run.py','remaining.py','observe.py','export.py']:files.append(base/name)
manifest={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(base/'export-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(base/'export-manifest.json')
with tarfile.open(base/'sanitized-export.tar.gz','w:gz') as archive:
 for p in files:archive.add(p,arcname=str(p.relative_to(base)),recursive=False)
print('exported',len(files),'files',flush=True)
