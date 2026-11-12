from pathlib import Path
import json
P=Path('/home/lab/work/s3a')
for n in ['newcases.py.console','new-f-0-fixture.log','new-a-0-fixture.log','new-counter-0-fixture.log']:
 f=P/n
 if f.exists():print(n,f.read_text()[-2200:])
for d in P.glob('new-*'):
 if d.is_dir() and (d/'result.json').exists():
  r=json.loads((d/'result.json').read_text());print(d.name,{k:r.get(k) for k in ['error','capture','oracle']})
print('fonts',list(map(str,Path('/usr/share/fonts').rglob('*Mono*.ttf')))[:8])
