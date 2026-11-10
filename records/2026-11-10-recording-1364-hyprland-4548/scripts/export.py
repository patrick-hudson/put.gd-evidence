import pathlib,json,hashlib,shutil,tarfile,sys
H=pathlib.Path.home();dst=H/'export';dst.mkdir(mode=0o700,exist_ok=True);files=[]
for name in ('m-still','m-sweep','r-still','r-sweep','off','h'):
 run=H/'n'/name;data=json.loads((run/'results.json').read_text())
 for r in data['rounds']:
  assert not r.get('error') and not r.get('problems') and r['frame']['ok'],(name,r.get('problems'))
 files += [(p,pathlib.Path('runs')/name/p.relative_to(run)) for folder in ('out','working','frames','logs') for p in (run/folder).rglob('*') if p.is_file()]
 for file in ('results.json','helper.debug','inspect.jsonl','pointer-events.json','ring-effect.json'):
  if (run/file).is_file():files.append((run/file,pathlib.Path('runs')/name/file))
 for suffix in ('.log','.command.json'):files.append((H/'n'/(name+suffix),pathlib.Path('runs')/(name+suffix)))
 for r in data['rounds']:
  for c in r.get('delayedCaptures',[]):
   assert c['cover']['ok'];hits=list((run/'archive').rglob(c['local']['file']));assert len(hits)==1
   files.append((hits[0],pathlib.Path('runs')/name/'captures'/hits[0].name))
 for p in (run/'state').rglob('*.jsonl'):
  found=False
  for line in p.read_text().splitlines():
   x=json.loads(line)
   if (x.get('fields') or {}).get('qtRuntime'):
    q=dst/'identities'/name/'startup.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(x,indent=1));found=True;break
  if found:break
for file in ('cursor-witness.json','inspect.json','helper.debug'):
 files.append((H/'cursor-probe'/file,pathlib.Path('cursor-probe')/file))
for file in ('ring-effects.json','summary.json','still-helper-crosscheck.json'):
 files.append((H/'n'/file,pathlib.Path(file)))
for file in ('guest-identity.json','matrix.log'):
 files.append((H/file,pathlib.Path(file)))
for file in ('click_driver.py','matrix.py','measure_rings.py','cursor_probe.py','extract_cursor.py','export.py','guest_identity.py'):
 files.append((H/file,pathlib.Path('scripts')/file))
for file in ('record_run-hide-bar.py','cover_player.py','virtual_mic.py','rfb.py','summarize_run.py'):
 files.append((H/'lab'/file,pathlib.Path('scripts/lab')/file))
manifest={}
for source,rel in files:
 assert source.is_file() and not source.is_symlink()
 assert not any(c in ('config','cache','data','__pycache__') for c in rel.parts)
 target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert digest(source)==digest(target)
 manifest[str(rel)]=dict(sha256=digest(target),source=str(source),bytes=source.stat().st_size)
(dst/'export-manifest.json').write_text(json.dumps(manifest,indent=1))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as archive:archive.add(dst,arcname='.')
