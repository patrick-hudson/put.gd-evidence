from pathlib import Path
import tarfile,hashlib,json
B=Path('/home/patrick/work/svm1398');repo=B/'repo';files={}
for p in B.glob('v3*.py'):files['scripts/'+p.name]=p
for n in ['v2analyze.py','v2ruler.html']:files['scripts/'+n]=B/n
for n in ['qt_fixture.py','verify_text.py']:files['fixtures/'+n]=Path('/home/patrick/work/sf1398')/n
for n in ['lab.py','wayland_pointer.py','wayland_toplevels.py']:files['lab/'+n]=repo/'tools/lab'/n
for p in (repo/'tools/mcp/share_mcp').glob('*.py'):files['mcp/share_mcp/'+p.name]=p
for n in ['uv.lock','pyproject.toml']:files['mcp/'+n]=repo/'tools/mcp'/n
with tarfile.open(B/'v3-harness.tgz','w:gz') as t:
 for n,p in files.items():t.add(p,arcname=n)
(B/'v3-harness-hashes.json').write_text(json.dumps({n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()},indent=2))
