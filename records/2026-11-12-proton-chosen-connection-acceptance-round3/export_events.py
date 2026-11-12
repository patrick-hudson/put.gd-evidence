# Run locally only over text evidence already copied; never reads a keyring or captures.
from pathlib import Path
import json,re
b=Path('/tmp/p3a')
def scrub(v):
 if isinstance(v,dict):return {k:scrub(w) for k,w in v.items() if not any(s in k.lower() for s in ('url','token','secret','password','credential'))}
 if isinstance(v,list):return [scrub(w) for w in v]
 if isinstance(v,str):return re.sub(r'https?://[^\s"<>]+','[address omitted]',v)
 return v
for h in ['d69','k72','m74','f44']:
 for kind in ['pr','nc']:
  p=b/'new'/h/kind
  if not p.exists():continue
  events=[]
  for f in sorted((p/'profile/state/putgd/logs').glob('*.jsonl')):
   events.extend(scrub(json.loads(line)) for line in f.read_text().splitlines())
  (p/'events.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in events))
