import pathlib,json,hashlib,shutil,tarfile,sys
H=pathlib.Path.home();dst=H/'export';dst.mkdir(mode=0o700,exist_ok=True);files=[]
for name in ('monitor-on','monitor-off','h'):
 run=H/'f'/name;report=json.loads((run/'results.json').read_text())
 assert not report.get('error')
 for row in report['rounds']:
  assert row.get('barHidden') is True
  assert not row.get('error') and row['frame']['ok']
  assert name=='h' or not row.get('problems') and row.get('evidencePublishable') is not False
 files += [(p,pathlib.Path('runs')/name/p.relative_to(run)) for folder in ('out','working','frames','logs') for p in (run/folder).rglob('*') if p.is_file() and not(name=='h' and '-countdown-after' in p.name)]
 files += [(run/'results.json',pathlib.Path('runs')/name/'results.json')]
 files += [(H/'f'/(name+s),pathlib.Path('runs')/(name+s)) for s in ('.log','.command.json')]
 # Only validated capture artifacts by exact filename; never copy profile/data trees.
 for row in report['rounds']:
  for capture in row.get('delayedCaptures',[]):
   if not capture['cover']['ok']:continue
   matches=list((run/'archive').rglob(capture['local']['file']));assert len(matches)==1
   files.append((matches[0],pathlib.Path('runs')/name/'captures'/capture['local']['file']))
 # Keep one explicit startup identity, excluding generated profile/caches/data.
 for p in (run/'state').rglob('*.jsonl'):
  for line in p.read_text().splitlines():
   x=json.loads(line)
   if x.get('message')=='Resident started' or (x.get('fields') or {}).get('qtRuntime'):
    ident=dst/'identities'/name/'startup.json';ident.parent.mkdir(parents=True,exist_ok=True);ident.write_text(json.dumps(x,indent=1));break
  else:continue
  break
files.append((H/'inspect-monitor.json',pathlib.Path('inspect-monitor.json')))
for name in ('record_run.py','record_run-hide-bar.py','cover_player.py','virtual_mic.py','rfb.py','summarize_run.py'):
 files.append((H/'lab'/name,pathlib.Path('scripts')/name))
for name in ('followup.py','measure.py','export.py','inspect-live.py','followup.log'):
 files.append((H/name,pathlib.Path('scripts')/name))
files.append((H/'f/ring-effects.json',pathlib.Path('ring-effects.json')))
manifest={}
for source,rel in files:
 assert not source.is_symlink() and source.is_file()
 assert not any(c in ('config','cache','data','__pycache__') for c in rel.parts)
 target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert digest(source)==digest(target)
 manifest[str(rel)]=dict(sha256=digest(target),source=str(source),bytes=source.stat().st_size)
(dst/'export-manifest.json').write_text(json.dumps(manifest,indent=1))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as archive:
 archive.add(dst,arcname='.',recursive=True)
