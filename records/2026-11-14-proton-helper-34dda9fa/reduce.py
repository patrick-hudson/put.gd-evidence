from pathlib import Path
import tarfile,json,hashlib,sys
base=Path(__file__).resolve().parent/'record';host=sys.argv[1];run=sys.argv[2];active=sys.argv[3] if len(sys.argv)>3 else run
with tarfile.open(base/f'{host}-numeric.tar.gz') as t:
 def load(name):return json.load(t.extractfile(f'{host}/{name}'))
 r=load(run+'/results.json');i=load(run+'/new-idle.json');family=load(active+'/family.json')
 assert r['build']['gitCommit']=='ff636bba2bee89caccf9dddeb1a4992d0a411acd'
 assert r['uiClosedBeforeIdle']['code']==0 and r['uiClosedBeforeIdle']['status']=='normal'
 assert r['helpersLeft']==[] and all(c['passed'] for c in r['results']) and i['passed']
 windows=[]
 for w in i['windows']:
  rows=load(run+f'/new-idle-{w["index"]}-samples.json');p=load(run+f'/quiet-preflight-{w["index"]}.json')
  assert p['qemuCount']==0 and not p['builders']
  assert w['elapsed']>=300 and all(w['gates'].values())
  assert all(not z['busy'] and max(z['load'])<1 and len(z['processes'])==1 and z['processes'][0]['pid']==i['pid'] and str(z['processes'][0]['startTicks'])==str(i['startTicks']) for z in rows)
  windows.append({**w,'hostLoadMaxima':[max(z['load'][j] for z in rows) for j in range(3)],'preflight':p,'privateCleanPeak':max(z['processes'][0]['memory']['Private_Clean'] for z in rows),'privateDirtyPeak':max(z['processes'][0]['memory']['Private_Dirty'] for z in rows),'swapPeak':max(z['processes'][0]['memory']['Swap'] for z in rows)})
 assert len(windows)==2
 cases=[]
 for c in r['results']:
  assert all(z.get('shareStatus')!='changed' for z in c.get('items',[]))
  if 'initialUnknownFinding' in c:assert c['retryHistoryIdsMatch'] and all(z['shareStatus']=='shared' for z in c['items'])
  cases.append({k:c[k] for k in ('name','passed','state','seconds','operationId','helpersObserved','helperGoneAfter','initialUnknownFinding','retryHistoryIdsMatch','explicitRetryAttempts') if k in c})
 life=[c for c in cases if c['name'] in ('region-complete','region-cancel')]
 assert len(life)==2 and all(c.get('helpersObserved') and c['helperGoneAfter'] is not None for c in life)
 peaks={k:max(sum(p['memory'][k] for p in z['processes']) for z in family) for k in ('Rss','Pss','Private_Clean','Private_Dirty','Swap')}
 peakLoads={k:next(z['load'] for z in family if sum(p['memory'][k] for p in z['processes'])==v) for k,v in peaks.items()}
 summary={'host':host,'desktop':r['desktop'],'sessionType':r['sessionType'],'build':r['build'],'functionalRun':run,'functionalPassed':len(cases),'functionalTotal':len(cases),'cases':cases,'unknownFindings':[c for c in cases if 'initialUnknownFinding' in c],'unchangedFilesReportedChanged':0,'uiExit':r['uiClosedBeforeIdle'],'settlingSeconds':i['settlingSecondsAfterUiExit'],'installedBinaries':i['binaries'],'resident':{'pid':i['pid'],'startTicks':i['startTicks']},'sameUsedResidentTwoDisjointWindows':True,'idleWindows':windows,'activeRun':active,'activeFamilyPeakBytes':peaks,'activePeakHostLoads':peakLoads,'activeHostLoadMax':max(z['load'][0] for z in family),'activeNumbersAreDiagnostic':True,'residentLibraries':i['libraries'],'qtPlatformLibraries':sorted({q for z in family for p in z['processes'] for q in p.get('platformLibraries',[])}),'helpersLeft':r['helpersLeft'],'sampleCadenceSeconds':.2,'processScope':'Same-UID putgd-prefixed processes, including CLI and all product helpers; PID/PPID/startTicks/executable, RSS/PSS/private memory, CPU ticks, swap and load retained. Finite sampling is not an exhaustive exec trace.'}
 (base/host/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(host,'PASS',len(cases),'functional, two quiet windows; unknown findings',len(summary['unknownFindings']))
