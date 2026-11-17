from pathlib import Path
import json,shutil,hashlib,re,sys
P=Path.cwd();O=P/'evidence';O.mkdir(exist_ok=True);summ=[]
def cp(f,to):
 to.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,to)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for d in sorted((P/'runs').iterdir()):
 if not(d/'verdict.json').exists():continue
 r=json.loads((d/'result.json').read_text());v=json.loads((d/'verdict.json').read_text());c=r['capture'];summ.append({'name':d.name,'verdict':v['verdict'],'height':c['height'],'beforeDoc':r['before']['docHeight'],'afterDoc':r['after']['docHeight'],'endReason':c['endReason'],'placed':c.get('framesPlaced'),'skipped':c.get('framesSkipped'),'recovered':c.get('recovered'),'fps':c.get('framesPerSecond'),'captureSeconds':c.get('elapsedMs',0)/1000,'wallSeconds':None if r['site']=='blank'else r['seconds'],'id':c['id']})
 out=O/'runs'/d.name
 for f in d.iterdir():
  if f.is_file()and f.suffix in ['.json']or(f.is_file()and f.suffix=='.log'and('where'in f.name or'excerpt'in f.name or'unwritten'in f.name)):cp(f,out/f.name)
 if v['verdict']!='RIGHT':
  for f in d.glob('*.png'):
   if 'seam'in f.name or f.name in ['lost.png','blank-default-past.png','autoScrolling.png']:cp(f,out/f.name)
  log=d/('blank-default-helper.log'if(d/'blank-default-helper.log').exists()else'helper.log');lines=log.read_text().splitlines();lost=[i for i,l in enumerate(lines)if'state lost'in l];ids={i for i,l in enumerate(lines)if any(t in l for t in ['scroll: prepare','scroll: ended','scroll: source',' recovered','pointer put back','scroll result'])}
  ids.update(lost[:2]+lost[-2:]);(out/'helper-excerpt.log').write_text('\n'.join(lines[i]for i in sorted(ids))+'\n')
(O/'summary.json').write_text(json.dumps(summ,indent=1))
for name in ['cold-start-proof.json','socket-preflight.json','actual-socket-preflight.json','host-proof.json','input-before.json','inside-results.json','inside-verdict.json','control-process-results.json','image-limit-correction.json','stale-notification.txt','start-attempt1.txt','pause-verdict.json','cap-notification-dismissed.txt','loss-notification-dismissed.txt']:
 if(P/name).exists():cp(P/name,O/name)
for f in P.glob('pause-random-*.json'):cp(f,O/'pause'/f.name)
for f in P.glob('trial-random-*.log'):cp(f,O/'pause'/f.name)
for f in P.glob('pause-random-*-excerpt.log'):cp(f,O/'pause'/f.name)
for name in ['accept.py','live7.py','pages-relative.py','sess.py','trial_relative.py','umouse.py','rfb.py','controls.py','batch.py','start.py','where.py','seam.py','default-blank-proof.py','relative-control-native.py','kwin-pointer-witness.py','normalize-blank.py','cleanup.py','analyze.py','retry-so.py','collect.py','unwritten.py','retry-auto.py','control-batch.py']:
 if(P/name).exists():cp(P/name,O/'scripts'/name)
# Passing images are represented by hashes. Produce exact names for the authorized deletion.
deletes={};protected=set()
for d in(P/'runs').iterdir():
 if not(d/'verdict.json').exists():continue
 v=json.loads((d/'verdict.json').read_text());r=json.loads((d/'result.json').read_text());c=r['capture'];cs=c.get('result',{}).get('sha256')
 if v['verdict']!='RIGHT':
  if cs:protected.add(cs)
  continue
 for f in d.glob('*.png'):deletes[str(f)]={'sha256':sha(f),'bytes':f.stat().st_size}
passing=set()
for d in(P/'runs').iterdir():
 if(d/'verdict.json').exists()and json.loads((d/'verdict.json').read_text())['verdict']=='RIGHT':passing.add(json.loads((d/'result.json').read_text())['capture']['result']['sha256'])
for f in P.glob('pause-random-*.json'):
 r=json.loads(f.read_text())
 if r['stoppedByClick']and not r['injectionsAfter']:passing.add(r['capture'].get('result',{}).get('sha256'))
 else:protected.add(r['capture'].get('result',{}).get('sha256'))
if(P/'inside-results.json').exists():
 for r in json.loads((P/'inside-results.json').read_text()):
  if r['firstClickWorked']:passing.add(r['capture'].get('result',{}).get('sha256'))
 for f in P.glob('inside-*-capture.png'):deletes[str(f)]={'sha256':sha(f),'bytes':f.stat().st_size}
for f in(P/'archive').rglob('*.png'):
 h=sha(f)
 if h in passing and h not in protected:deletes[str(f)]={'sha256':h,'bytes':f.stat().st_size}
(P/'passing-image-deletion-manifest.json').write_text(json.dumps(deletes,indent=1));cp(P/'passing-image-deletion-manifest.json',O/'passing-image-deletion-manifest.json')
index={str(f.relative_to(P)):{'sha256':sha(f),'bytes':f.stat().st_size}for f in(P/'runs').rglob('*')if f.is_file()and str(f)not in deletes};index.update({f.name:{'sha256':sha(f),'bytes':f.stat().st_size}for f in P.iterdir()if f.is_file()and f.suffix in ['.py','.log','.json','.txt','.png']and str(f)not in deletes});(O/'restore-index.json').write_text(json.dumps({'host':sys.argv[1],'root':str(P),'keptFiles':index,'passingImageDeletionManifest':'passing-image-deletion-manifest.json'},indent=1))
print(json.dumps(summ,indent=1))
