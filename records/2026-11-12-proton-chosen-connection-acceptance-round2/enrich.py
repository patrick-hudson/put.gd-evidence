from pathlib import Path
import json,shutil,collections
b=Path('/tmp/pr1414r2');e=b/'2026-11-12-proton-chosen-connection-acceptance-round2'
for h in ['d69','k72','m74','f44']:
 root=b/h
 if not (root/'pr/results.json').exists():continue
 out=e/h; out.mkdir(exist_ok=True)
 for n in ['resume.log']:
  if (root/n).exists():shutil.copy2(root/n,out/n)
 # Store bounded event fields; omit payloads, addresses, account configuration.
 events=[]
 for kind in ['pr','nc']:
  for f in (root/kind/'profile/state/putgd/logs').glob('*.jsonl'):
   for line in f.read_text().splitlines():
    x=json.loads(line);fields=x.get('fields',{})
    if x['level'] in ['warning','error'] or x['message'] in ['Operation accepted','Operation finished','Upload attempt','Upload finished']:
     events.append({'build':kind,'time':x['time'],'level':x['level'],'message':x['message'],'fields':{k:v for k,v in fields.items() if k in ['operationId','state','durationMs','byteCount','error','itemErrors','status','provider','uploadStatus','items','action']}})
 (out/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in events))
 (out/'driver.log').write_text((b/(h+'-driver.log')).read_text())
 if (root/'nc/results.json').exists():
  shutil.copy2(root/'nc/results.json',out/'nightly-results.json')
  shutil.copy2(root/'nc/summary.txt',out/'nightly-summary.txt')
 r=json.loads((root/'pr/results.json').read_text());cs=root/'pr/capture-checks.json'
 if cs.exists():
  op=next((x.get('operationId') for x in r['results'] if x['name']=='history-picture'),None)
  for x in json.loads(cs.read_text()):
   if x['operationId']==op:shutil.copy2(root/'pr'/x['file'],out/'history.png')
# Local acquisition and prior scratch metadata, no content from other sessions.
(e/'scratch-notes.txt').write_text('Earlier cancelled attempt: /tmp/pr1414-r2 preserved; no ~/work/p9r2 on the four hosts at preflight, no held locks belonging to it. No locks broken. Existing /tmp/pg1414-accept, /tmp/pa1414 and d69 ~/work/pf2 left untouched.\n')
