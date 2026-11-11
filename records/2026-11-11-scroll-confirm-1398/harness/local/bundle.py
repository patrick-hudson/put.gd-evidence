from pathlib import Path
import shutil,json,hashlib
B=Path(__file__).parent;R=B/'2026-11-11-scroll-confirm-1398';R.mkdir(exist_ok=True)
def copy(src,dst):
 dst=R/dst;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
for h in ['m74','f44','d69']:
 for f in (B/'native'/h/'raw').rglob('*'):
  if f.is_file():copy(f,Path('native')/h/f.relative_to(B/'native'/h/'raw'))
for label in ['f44-harness-overview','m74-warning']:
 for f in (B/'native'/label/'raw').rglob('*'):
  if f.is_file():copy(f,Path('harness-failures' if label.startswith('f44') else 'supplemental')/label/f.relative_to(B/'native'/label/'raw'))
for run in ['ocn','bcn','ncn','kcr2','kcn-bootfail']:
 p=B/'guests'/run
 if not p.exists():continue
 for f in p.rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(p)
  if f.suffix=='.tgz' or any(x.startswith(('initial-','retry2-')) for x in rel.parts):continue
  if rel.parts[0]=='final':rel=Path(*rel.parts[1:])
  copy(f,Path('guests')/run/rel)
for f in (B/'pictures').glob('*'):copy(f,Path('pictures')/f.name)
for n in ['SOURCE.json','merge-identity.txt','artifact-sha256.json','checks.json','socket-preflight.json','previous-passes.json','combined-analysis.json','m74-release.json','f44-release.json','d69-release.json','m74-warning-release.json','m74-warning-during-upload.png','neon-browser-ready.png','neon-browser-copy-ready.png','f44-running.png','f44-restored.png']:
 if (B/n).exists():copy(B/n,n)
for f in B.glob('*.py'):copy(f,Path('harness/local')/f.name)
for h in ['m74','f44','d69']:
 for n in ['pass2.py','record_run.py','scroll_run.py','verify_text.py','qt_fixture.py','text_fixture.py','rfb.py','upload_setup.py','receiver.py','extras3.py','mcp_verify.py','cleanup.py']:
  f=B/'native-tools'/n
  if f.exists():copy(f,Path('harness/native-base')/n)
for f in (B/'remote-tools').glob('*.py'):copy(f,Path('harness/remote')/f.name)
copy(B/'editor.jsonl','pictures/editor.jsonl')
copy(B/'final-cleanup.json','final-cleanup.json')
copy(B/'report-draft.md','README.md')
assert not any(f.is_symlink() for f in R.rglob('*'));big=[str(f.relative_to(R)) for f in R.rglob('*') if f.is_file() and f.stat().st_size>50*1024**2];assert not big,big
m={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in R.rglob('*') if f.is_file() and f.name!='SHA256SUMS.json'};(R/'SHA256SUMS.json').write_text(json.dumps(m,indent=2));print('Bundled',len(m),'files',sum(f.stat().st_size for f in R.rglob('*') if f.is_file()))
