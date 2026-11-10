import pathlib,re,json,sys
root=pathlib.Path(sys.argv[1]);out={}
for p in sorted((root/('r' if (root/'r').is_dir() else 'runs')).glob('*.debug')):
 lines=p.read_text(errors='replace').splitlines();ts=[s for s in lines if ' timestamps:'in s];fs=[s for s in lines if ' frames:'in s]
 v={'timestampsLines':ts,'framesLines':fs}
 if ts:
  s=ts[-1]
  for label,key in [('frame age','frameAge'),('video lateness','videoLateness'),('audio lateness','audioLateness')]:
   m=re.search(re.escape(label)+r' (-?[0-9.]+)/(-?[0-9.]+)/(-?[0-9.]+) ms \(n=(\d+)\)',s)
   if m:v[key]={'minMs':float(m[1]),'meanMs':float(m[2]),'maxMs':float(m[3]),'n':int(m[4])}
 if fs:
  m=re.search(r'cadence lock (\d+) early dropped / (\d+) resyncs / (\d+) changes slotted after a repeat',fs[-1])
  if m:v['cadenceLock']={'earlyDropped':int(m[1]),'resyncs':int(m[2]),'changesAfterRepeat':int(m[3])}
 out[p.stem]=v
(root/'diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
print('runs',len(out),'timestamps',sum(bool(x['timestampsLines'])for x in out.values()))
