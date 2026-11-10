import pathlib,json,statistics,sys,xml.etree.ElementTree as X
E=pathlib.Path(sys.argv[1]);old=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-followup');before=json.load(open(old/'analysis.json'));new=json.load(open(E/'motion.json'));diag=json.load(open(E/'diagnostics.json'));med=lambda v:round(statistics.median(v),2)
rows=[]
for r in new['order']:
 r=dict(r);r['stopDiagnostics']=diag[r['tag']];r['afterStop']=json.load(open(E/'runs'/r['tag']/'after-stop.json'));v=r['offsetsMs'];r.update(first4MedianMs=med(v[:4]),last4MedianMs=med(v[-4:]),last4MinusFirst4Ms=round(med(v[-4:])-med(v[:4]),2));rows.append(r)
oldrows=[r for r in before['runs']if r.get('pointer')in('still','sweep')and r['highlights']=='on'];cells=[];groups={}
for build,rs in [('4538',oldrows),('4548',rows)]:
 for mode in ('still','sweep'):
  cell=[r for r in rs if r.get('pointer')==mode];vals=[r['medianMs']for r in cell];groups[(build,mode)]=cell;cells.append({'build':build,'mode':mode,'medians':vals,'ageMeans':[r['stopDiagnostics']['frameAge']['meanMs']for r in cell],'medianOfMedians':med(vals),'spread':round(max(vals)-min(vals),2)})
contrasts=[]
for build in ('4538','4548'):
 still=groups[(build,'still')];sweep=groups[(build,'sweep')];diff=[round(b['medianMs']-a['medianMs'],2)for a,b in zip(still,sweep)];sv=[r['medianMs']for r in still];mv=[r['medianMs']for r in sweep];contrasts.append({'build':build,'pairedSweepMinusStill':diff,'medianPairedDifference':med(diff),'differenceOfCellMedians':round(med(mv)-med(sv),2),'rangesOverlap':not(max(mv)<min(sv)or max(sv)<min(mv)),'maxWithinCellRange':max(max(sv)-min(sv),max(mv)-min(mv))})
def key(s):
 def canon(e):return(e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[canon(c)for c in e])
 return[canon(e)for e in X.fromstring(s).iter('keybind')if not e.attrib.get('bridge','').startswith('customputgd')]
b=(E/'g-new-before.xml').read_text();keys=key(b);cleanup=[]
for tag in ('f-monitor','f-region'):
 t=(E/'runs'/tag/'rc-after-stop.xml').read_text();cleanup.append({'tag':tag,'userBindingsUnchanged':key(t)==keys,'userBindingCount':len(keys),'clickMarkers':t.count('putgd="click-highlights"')})
x={'cells':cells,'contrasts':contrasts,'newRows':rows,'oldRows':oldrows,'cleanup':cleanup,'gRcIdentical':new['gRcIdentical']};(E/'comparison.json').write_text(json.dumps(x,indent=2)+'\n')
md=['| Run | Median ms | Frame age min/mean/max ms | Ordered pair offsets ms | First4 → last4 median ms |','|---|---:|---|---|---|']
for r in rows:
 a=r['stopDiagnostics']['frameAge'];md.append(f"| {r['tag']} | {r['medianMs']} | {a['minMs']}/{a['meanMs']}/{a['maxMs']} | "+', '.join(str(v)for v in r['offsetsMs'])+f" | {r['first4MedianMs']} → {r['last4MedianMs']} |")
(E/'ordered-pairs.md').write_text('\n'.join(md)+'\n');print(json.dumps({'contrasts':contrasts,'cleanup':cleanup},indent=2))
