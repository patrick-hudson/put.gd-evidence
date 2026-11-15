import json,sys
from pathlib import Path
p=Path(sys.argv[1]);s=p.read_text();d=json.JSONDecoder();rows=[];i=0
while i<len(s):
 j=s.find('{',i)
 if j<0:break
 try:v,i=d.raw_decode(s,j)
 except ValueError:i=j+1;continue
 if 'label'in v:rows.append(v)
out={'source':str(p),'note':'raw_decode preserves adjacent JSON records interleaved by a child writer before the parent stdout buffer flushed; original log unchanged.','rows':rows,'groups':{}}
for typ in ['fixed','random']:
 g=[r for r in rows if r['label'].startswith(typ+'-')];out['groups'][typ]={'tries':len(g),'firstClickStops':sum(bool(r.get('stoppedByClick')) for r in g),'injectionsAfterHand':sum(len(r.get('injectionsAfter',[])) for r in g),'pauseMs':[r.get('pausedMs') for r in g],'startMs':[r.get('startMs') for r in g]}
p.with_suffix('.summary.json').write_text(json.dumps(out,indent=1));print(json.dumps(out['groups'],indent=1))
