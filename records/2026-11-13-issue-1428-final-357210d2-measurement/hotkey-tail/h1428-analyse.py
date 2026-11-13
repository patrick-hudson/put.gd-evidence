from pathlib import Path
import json,math,random,statistics,sys
r=Path(sys.argv[1]);blocks=[]
q=lambda a,p:statistics.median(a) if p==.5 else sorted(a)[max(0,math.ceil(p*len(a))-1)]
def stats(a):return {**{f'p{int(p*100)}':q(a,p) for p in [.5,.9,.95,.99]},'max':max(a),'n':len(a)}
for p in sorted((r/'data').glob('*/witness/receipt.json')):
 v=json.loads(p.read_text());identity=json.loads((p.parent.parent/'identity.json').read_text());assert v['complete'];assert identity['version']['gitCommit']=={'A':'466449a4c69a07a1997668d1b70d637abac76a16','B':'357210d2f1cb7b65f77166e34eb535d42e497fd0'}[identity['build']]
 blocks.append({'name':p.parent.parent.name,'build':identity['build'],'condition':identity['condition'],'block':identity['block'],'rows':v['rows'],'files':identity['files']})
assert len(blocks)==66 and sum(len(b['rows']) for b in blocks)==420
summary={'sign':'candidate minus baseline; p50 median; p90/p95/p99 nearest-rank quantiles; no samples removed','warmBlocks':[],'pooled':{},'bootstrap':{},'faults':{},'files':{}}
for b in blocks:
 if b['condition']=='warm':summary['warmBlocks'].append({'block':b['name'],**stats([x['onScreenMs'] for x in b['rows']])})
rng=random.Random(1428)
for condition in ['warm','quiet']:
 by={build:sorted([b for b in blocks if b['condition']==condition and b['build']==build],key=lambda b:b['block']) for build in ['A','B']};data={build:[x for b in by[build] for x in b['rows']] for build in by}
 assert all(len(data[b])==(180 if condition=='warm' else 30) for b in by)
 for build in by:
  summary['pooled'][condition+'-'+build]={metric:stats([row[metric] for row in data[build]]) for metric in ['onScreenMs','mapMs','drawableMs']}
  summary['faults'][condition+'-'+build]={metric:stats([row['faultDelta'][metric] for row in data[build]]) for metric in ['minflt','majflt']}
  if condition=='quiet':summary['faults'][condition+'-'+build]['memory']={'beforeQuietRssMedian':statistics.median(x['beforeQuiet']['Rss'] for x in data[build]),'beforePressRssMedian':statistics.median(x['beforePress']['Rss'] for x in data[build]),'quietElapsedMin':min(x['quietElapsedSeconds'] for x in data[build]),'rssDrops':[x['beforeQuiet']['Rss']-x['beforePress']['Rss'] for x in data[build]]}
 vals={build:[x['onScreenMs'] for x in data[build]] for build in by};dist={metric:[] for metric in ['p50','p95']};iid={metric:[] for metric in dist}
 for rep in range(10000):
  chosen=rng.choices(range(len(by['A'])),k=len(by['A']));resampled={}
  for build in by:
   resampled[build]=[x['onScreenMs'] for i in chosen for x in rng.choices(by[build][i]['rows'],k=len(by[build][i]['rows']))]
  for metric,pct in [('p50',.5),('p95',.95)]:
   dist[metric].append(q(resampled['B'],pct)-q(resampled['A'],pct))
  ir={build:rng.choices(vals[build],k=len(vals[build])) for build in by}
  for metric,pct in [('p50',.5),('p95',.95)]:iid[metric].append(q(ir['B'],pct)-q(ir['A'],pct))
 summary['bootstrap'][condition]={'replicates':10000,'seed':1428,'primaryMethod':'paired adjacent A/B blocks, resample block pairs then samples within blocks; quiet pairs each contain one observation','differences':{m:{'estimate':q(vals['B'],p)-q(vals['A'],p),'ci95':[q(dist[m],.025),q(dist[m],.975)],'includesZero':q(dist[m],.025)<=0<=q(dist[m],.975),'iidSensitivityCi95':[q(iid[m],.025),q(iid[m],.975)]} for m,p in [('p50',.5),('p95',.95)]}}
for build in ['A','B']:
 b=next(x for x in blocks if x['build']==build);summary['files'][build]={name:v for name,v in b['files'].items() if Path(name).name=='putgd' or 'libputgd' in Path(name).name.lower()}
(r/'analysis.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary['bootstrap'],indent=2))
