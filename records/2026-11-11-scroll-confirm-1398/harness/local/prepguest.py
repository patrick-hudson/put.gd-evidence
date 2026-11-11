from control import *
ssh('d69', '''python3 - <<'CODE'
from pathlib import Path
p=Path('/home/patrick/work/scn');p.mkdir(mode=0o700)
for d in ['/home/patrick/work/sfinal','/home/patrick/work/sf4']:
 for f in Path(d).glob('*.py'):
  if (p/f.name).exists():continue
  (p/f.name).write_text(f.read_text().replace('/home/patrick/work/sfinal','/home/patrick/work/scn').replace('/home/patrick/work/sf4','/home/patrick/work/scn'))
f=p/'acc4.py';f.write_text(f.read_text().replace('k="o"','k=sys.argv[5] if len(sys.argv)>5 else "o"'))
# Use the bottom-capable text fixture on every guest.
f=p/'prep.py';f.write_text(f.read_text().replace('(B/"v3text.py","v3text.py")','(Path("/home/patrick/work/scn/f4text.py"),"v3text.py")'))
CODE''',check=True)
