import pathlib,json,statistics,sys
root=pathlib.Path(sys.argv[1]);matrix=json.load(open(root/'matrix.json'));motion=json.load(open(root/'motion.json'));rows=matrix['order']+motion['order'];diag=json.load(open(root/'diagnostics.json'));out={'cells':[],'contrasts':[],'runs':rows,'defectCriteria':{'n':4,'allPairedEarlier':True,'disjointRanges':True,'differenceOfCellMediansGreaterThanMaxWithinCellRange':True}}
def med(a):return round(statistics.median(a),2)
def cell(name,rs):
 vals=[r['medianMs']for r in rs if r.get('medianMs')is not None];o={'name':name,'n':len(vals),'values':vals,'median':med(vals),'min':min(vals),'max':max(vals),'spread':round(max(vals)-min(vals),2),'tags':[r['tag']for r in rs]};out['cells'].append(o);return rs,o
cells={}
for target in ('region','monitor'):
 for lead in (3,6):
  for on in ('on','off'):
   name=f'{target} {lead}s {on}';cells[name]=cell(name,[r for r in matrix['order']if r['target']==target and r['lead']==lead and r['highlights']==on and r['repeat']>0])
for mode,on in [('still','on'),('sweep','on'),('sweep','off')]:
 name=f'pointer {mode} {on}';cells[name]=cell(name,[r for r in motion['order']if r.get('pointer')==mode and r['highlights']==on])
def contrast(name,a,b):
 ra,ca=cells[a];rb,cb=cells[b];da={r['repeat']:r['medianMs']for r in ra};db={r['repeat']:r['medianMs']for r in rb};diff=[round(da[k]-db[k],2)for k in sorted(da.keys()&db.keys())];spread=max(ca['spread'],cb['spread']);d=med(diff)
 o={'name':name,'a':a,'b':b,'pairedDifferences':diff,'medianPairedDifference':d,'differenceOfCellMedians':round(ca['median']-cb['median'],2),'maxWithinCellSpread':spread,'rangesOverlap':not(ca['max']<cb['min']or cb['max']<ca['min']),'allEarlier':all(v<0 for v in diff),'consistentEarlyBeyondSpread':len(diff)==4 and all(v<0 for v in diff) and ca['max']<cb['min'] and abs(ca['median']-cb['median'])>spread};out['contrasts'].append(o)
for t in ('region','monitor'):
 for lead in (3,6):contrast(f'{t} on-off lead{lead}',f'{t} {lead}s on',f'{t} {lead}s off')
 contrast(f'{t} off short-long',f'{t} 3s off',f'{t} 6s off')
contrast('moving on-still on','pointer sweep on','pointer still on');contrast('moving on-off','pointer sweep on','pointer sweep off')
for r in rows:
 r['stopDiagnostics']=diag.get(r['tag'],{})
 v=r.get('offsetsMs')or[]
 if len(v)>=8:r['first4MedianMs']=med(v[:4]);r['last4MedianMs']=med(v[-4:]);r['last4MinusFirst4Ms']=round(r['last4MedianMs']-r['first4MedianMs'],2)
(root/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
md=['| Target / condition | Lead | Rep | Median ms | Frame age min/mean/max ms | Ordered pair offsets ms | First4 → last4 median ms |','|---|---:|---:|---:|---|---|---|']
for r in rows:
 condition=('g / '+r['tag'] if r['repeat']==0 else (r.get('target')or('pointer '+str(r.get('pointer')))))+' '+r['highlights']
 age=r['stopDiagnostics'].get('frameAge',{});ageText='/'.join(str(age.get(k,'?'))for k in ('minMs','meanMs','maxMs'))
 md.append(f"| {condition} | {r['lead']} | {r['repeat']} | {r.get('medianMs')} | {ageText} | "+', '.join(str(v)for v in r.get('offsetsMs')or[])+f" | {r.get('first4MedianMs')} → {r.get('last4MedianMs')} |")
(root/'ordered-pairs.md').write_text('\n'.join(md)+'\n')
print(json.dumps({k:out[k]for k in('cells','contrasts')},indent=2))
