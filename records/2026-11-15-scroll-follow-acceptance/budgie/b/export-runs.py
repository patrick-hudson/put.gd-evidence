import tarfile,sys
from pathlib import Path
P=Path.home()/'work/sfa15'
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as t:
 for d in sorted((P/'runs').iterdir()):
  if not d.name.startswith(sys.argv[1]) or 'incomplete' in d.name or not (d/'result.json').exists():continue
  for n in ['result.json','capture.png','reference.png','pinned.json','helper.log','done-viewport.png','done-viewport-info.json']:
   p=d/n
   if p.is_file():t.add(p,arcname=str(Path('runs')/d.name/n))
