from pathlib import Path
import json,shutil,hashlib,sys
P=Path.cwd();O=P/'evidence2';O.mkdir(exist_ok=True)
def cp(f,t):t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t)
rootnames=['package-identity.json','chrome-reference.log','chrome-reference-attempt1.log','chrome-reference-where.log','chrome-dense.log','cleanup-reference-desktop.png','extracted-file-list.json','removed-runtime-files.json','cold-start-proof.json','actual-socket-preflight.json','host-proof.json','input-before.json','pause-summary.json','history-note.json','history-ui.json','history-note.png','notice-events.log','summary.json','cutout-summary.json','pinned-summary.json','cleanup-receipt.json','cleanup.log','baseline-desktop.png','cleanup-desktop.png','batch.log','retry-so.log','pause.log','force-notice.log','force-notice-2.log','history-notice.log','history-notice-attempt1.log','cutouts-attempt1.log','Bso-2-error.txt']
for n in rootnames:
 if(P/n).is_file():cp(P/n,O/n)
for f in P.glob('pause-random-*.json'):cp(f,O/'pause'/f.name)
for f in P.glob('trial-random-*.log'):cp(f,O/'pause'/f.name)
for d in sorted((P/'runs').iterdir()):
 if not(d/'result.json').is_file():continue
 r=json.loads((d/'result.json').read_text());c=r['capture'];out=O/'runs'/d.name
 for f in d.iterdir():
  if f.is_file()and(f.suffix=='.json'or f.suffix=='.log'and any(x in f.name for x in ['where','excerpt','unwritten'])):cp(f,out/f.name)
 for f in d.glob('*.png'):
  if 'seam'in f.name or f.name=='cutout-comparison.png'or f.name=='desktop-notice.png'and c.get('foundAgain',0)>0 or f.name=='capture.png'and(d/'damaged.json').exists():cp(f,out/f.name)
 if not(d/'image-hashes.json').exists():
  data={str(f.name):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}for f in d.glob('*.png')};(out/'image-hashes.json').write_text(json.dumps(data,indent=1))
for n in ['accept.py','start.py','batch.py','pages-relative.py','live7.py','sess.py','umouse.py','rfb.py','controls.py','trial_relative.py','kwin-pointer-witness.py','relative-control-native.py','where.py','seam.py','unwritten.py','score.py','scroll_tracker_score.py','score-round.py','band-details.py','cutouts.py','curate.py','finalize-m74.py','force-notice.py','force-notice-2.py','find_history.py','history-notice.py','baseline.py','cleanup.py','collect-round.py','retry-so-round.py','finalize-aurora.py','chrome-reference.py','chrome-dense.py']:
 if(P/n).is_file():cp(P/n,O/'scripts'/n)
if(P/'prior-cutouts/identity.json').exists():cp(P/'prior-cutouts/identity.json',O/'prior-comparison/identity.json')
index={str(f.relative_to(P)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}for f in(P/'runs').rglob('*')if f.is_file()};(O/'restore-index.json').write_text(json.dumps({'host':sys.argv[1],'root':str(P.resolve()),'keptFiles':index,'deletions':[]},indent=1));print('exported',len(list(O.rglob('*'))),'entries',flush=True)
