from pathlib import Path
import tarfile,json,datetime,os
BASE=Path('/tmp/w7-1399/record')
def load(t,name):return json.load(t.extractfile(name))
def family_metrics(rows):
 keys=('Rss','Pss','Private_Clean','Private_Dirty','Swap')
 peaks={k:max(sum(p['memory'][k] for p in r['processes']) for r in rows) for k in keys}
 at={k:next({'atMonotonic':r['monotonic'],'load':r['load']} for r in rows if sum(p['memory'][k] for p in r['processes'])==v) for k,v in peaks.items()}
 identities={}
 for r in rows:
  for p in r['processes']:
   key=f"{p['pid']}:{p['startTicks']}";identities.setdefault(key,{'pid':p['pid'],'ppid':p['ppid'],'startTicks':p['startTicks'],'comm':p['comm'],'exe':p['exe'],'platformLibraries':p.get('platformLibraries',[]),'firstSeen':r['monotonic'],'lastSeen':r['monotonic'],'cpuTicksFirst':p['cpuTicks'],'cpuTicksLast':p['cpuTicks']})
   identities[key]['lastSeen']=r['monotonic'];identities[key]['cpuTicksLast']=p['cpuTicks']
 return {'summedFamilyPeakBytes':peaks,'peakHostLoads':at,'hostLoadOneMinuteRange':[min(r['load'][0] for r in rows),max(r['load'][0] for r in rows)],'identities':list(identities.values()),'sampleCount':len(rows),'sampleCadenceSeconds':.2,'scope':'All same-UID processes whose comm begins putgd, including short-lived CLI and transient workers. Finite cadence is not an exhaustive exec trace.'}
def summarize(host,full,resource,additional):
 with tarfile.open(BASE/(host+'-numeric.tar.gz')) as t:
  functional=[]
  for run in [full,*additional]:
   x=load(t,f'{host}/{run}/results.json');functional.append({'run':run,'passed':sum(r['passed'] for r in x['results']),'total':len(x['results']),'results':x['results'],'helpersLeft':x['helpersLeft']})
  active=os.environ.get('ACTIVE_RUN',resource)
  r=load(t,f'{host}/{resource}/results.json');idle=load(t,f'{host}/{resource}/new-idle.json');rows=load(t,f'{host}/{active}/family.json')
  windows=[]
  for w in idle['windows']:
   samples=load(t,f'{host}/{resource}/new-idle-{w["index"]}-samples.json')
   w.update(hostLoadOneMinuteRange=[min(s['load'][0] for s in samples),max(s['load'][0] for s in samples)],privateCleanPeak=max(s['processes'][0]['memory']['Private_Clean'] for s in samples),privateDirtyPeak=max(s['processes'][0]['memory']['Private_Dirty'] for s in samples),swapPeak=max(s['processes'][0]['memory']['Swap'] for s in samples));windows.append(w)
  lifetimes=[]
  for run in dict.fromkeys([full,resource,active]):
   report=load(t,f'{host}/{run}/results.json');events=load(t,f'{host}/{run}/events.json');trace=load(t,f'{host}/{run}/family.json');offset=events['clockCorrelationSnapshot']['utc']-events['clockCorrelationSnapshot']['monotonic']
   for case in report['results']:
    if case['name'] not in ('region-complete','region-cancel'):continue
    ev=[e for e in events['events'] if e['operationId']==case['operationId']]
    start=datetime.datetime.fromisoformat(ev[0]['time'].replace('Z','+00:00')).timestamp()-offset
    end=datetime.datetime.fromisoformat(ev[-1]['time'].replace('Z','+00:00')).timestamp()-offset
    seen={}
    for row in trace:
     if start<=row['monotonic']<=end:
      for p in row['processes']:
       if p['comm'].startswith('putgd-proton'):seen.setdefault(f"{p['pid']}:{p['startTicks']}",[]).append(row['monotonic']-start)
    lifetimes.append({'run':run,'case':case['name'],'operationId':case['operationId'],'state':case['state'],'helperGoneAfterSeconds':case['helperGoneAfter'],'observedHelperIdentities':[{ 'identity':k,'firstSampleSecondsAfterAccepted':min(v),'lastSampleSecondsAfterAccepted':max(v)} for k,v in seen.items()],'directPollingIdentities':case.get('helpersObserved',[]),'correlation':'Approximate UTC/monotonic offset from export; see raw trace and events. Driver explicitly waits for zero helpers before the next action; no kill before that observation.'})
  value={'host':host,'desktop':r['desktop'],'sessionType':r['sessionType'],'build':r['build'],'functionalRuns':functional,'resourceRun':resource,'resourcePassed':idle['passed'],'settlingSecondsAfterUiExit':idle.get('settlingSecondsAfterUiExit',35),'sameResidentTwoWindows':True,'residentIdentity':{'pid':idle['pid'],'startTicks':idle['startTicks']},'idleWindows':windows,'residentLibraries':idle['libraries'],'activeFamilyRun':active,'activeFamily':family_metrics(rows),'regionHelperLifetimes':lifetimes,'helpersLeft':r['helpersLeft']}
  (BASE/host/'summary.json').write_text(json.dumps(value,indent=2)+'\n')
  print(host,'functional',[(s['run'],s['passed'],s['total']) for s in functional],'idle',idle['passed'],'load',value['activeFamily']['hostLoadOneMinuteRange'],'peak MiB',{k:round(v/1048576,2) for k,v in value['activeFamily']['summedFamilyPeakBytes'].items()})
if __name__=='__main__':
 import sys
 summarize(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4:])
