import json,pathlib,shutil
B=pathlib.Path('/tmp/pr1414r2'); E=B/'2026-11-12-proton-chosen-connection-acceptance-round2';E.mkdir(exist_ok=True)
R=B/'records/2026-11-12-proton-chosen-connection-acceptance'; O=B/'records/2026-11-10-proton-upload-speed-acceptance'
hosts=['d69','k72','m74','f44']; current={}; old={}; base={};controls={}
for h in hosts:
 for dest,src in [(old,R),(base,O)]:
  f=src/h/'results.json'
  if f.exists():dest[h]=json.loads(f.read_text())
 f=B/h/('pr/combined-results.json' if h=='d69' else 'pr/results.json')
 if f.exists():current[h]=json.loads(f.read_text())
 f=B/h/'nc/results.json'
 if f.exists():controls[h]=json.loads(f.read_text())
def cases(d,h):return {i['name']:i for i in d.get(h,{}).get('results',[])}
def value(i):
 if not i:return 'not run'
 if i.get('timingSource'):return str(i['seconds'])+'†'
 if i.get('error') and i.get('state') in ('failed','refused'):return i['error']
 if i.get('state')=='not_run':return 'not run'
 if i['name']=='back-to-back':return f"{i.get('firstSeconds')}, {i.get('secondSeconds')}"
 if i['name'].startswith('revoke'):
  t=i.get('eachSeconds',[]);return f"{i['state']}; {min(t):.2f}–{max(t):.2f}/link" if t else i['state']
 if i['name']=='cancel-countdown':return f"{i['state']}; helper gone {i.get('helperGoneAfter')}"
 if i['name']=='link-answers':return 'HTTP '+i['state']
 return str(i.get('secondsAfterCountdown',i.get('seconds')))
def stage(i):
 p=i.get('phasesFirstSeenAt',{});return round(p['sharing']-p['uploading'],2) if 'sharing'in p and 'uploading'in p else 'unobserved'
lines=['# Proton chosen-connection desktop acceptance round 2 (#1414)','', 'Exact requested head: `ec6e6a136807cb24ba70e1fa93d2bf0954e0f330`. CI run [43156480415](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43156480415). Latest published nightly control: `26.1111.4633-nightly` (published 2026-11-11 10:45 UTC). No compilation, product edits, merge or approval.','', '| Host | Build | Original cases passed | Helpers left |','| --- | --- | --- | --- |']
for h in hosts:
 d=current.get(h,{});r=d.get('results',[])[:15];lines.append(f"| {h} | {d.get('build',{}).get('version','not run')} | {sum(i['passed'] for i in r)}/{len(r)} | {d.get('helpersLeft','not run')} |")
lines+=['','Times in seconds, **2026-11-10 baseline / round 1 / round 2**. Delayed captures exclude the countdown. Back-to-back shares an invocation origin.','', '| Case | '+' | '.join(hosts)+' |','| --- | '+' | '.join(['---']*4)+' |']
for name in cases(old,'d69'):
 if name.startswith('sequential') or name=='revoke-additions':continue
 lines.append('| '+name+' | '+' | '.join(' / '.join(value(cases(d,h).get(name)) for d in (base,old,current)) for h in hosts)+' |')
lines+=['','Distinct helpers during back-to-back are sampled every 10 ms using user-owned `/proc` comm beginning `putgd-proton-ru`, distinct `(PID, kernel startTicks)` pairs, through helper exit. This is a sampled inventory, not an exec audit. Expected count: one.','','| Host | Helper count | PID/startTicks |','| --- | --- | --- |']
for h in hosts:
 i=cases(current,h).get('back-to-back',{});lines.append(f"| {h} | {i.get('helperProcessCount','not run')} | {i.get('helperProcessesObserved',[])} |")
lines+=['','Sequential screenshots: upload stage is first observed sharing minus first observed uploading; total is invocation to terminal state.','','| Host | Capture 1 stage / total | Capture 2 stage / total | Capture 3 stage / total |','| --- | --- | --- | --- |']
for h in hosts:
 vals=[]
 for n in range(1,4):
  i=cases(current,h).get(f'sequential-desktop-{n}',{});vals.append(f"{stage(i)} / {i.get('seconds','not run')}"+(' (partial)' if i.get('state')=='partial' else ''))
 lines.append('| '+h+' | '+' | '.join(vals)+' |')
lines+=['','Same-hour control, one sample per build/case. PR 1 MiB and 8 MiB ran first; nightly then ran immediately with its own new private profile, under the same locks. PR resident stopped during the control and restarted afterwards. Network variance and order effects remain.','','| Host | Case | PR stage / total | Nightly stage / total | PR minus nightly total |','| --- | --- | --- | --- | --- |']
for h in hosts:
 for n in ('file-1m','file-8m'):
  a=cases(current,h).get(n,{});b=cases(controls,h).get(n,{})
  delta=round(a['seconds']-b['seconds'],2) if 'seconds'in a and 'seconds'in b and a.get('state')=='completed' and b.get('state')=='completed' and not a.get('timingSource') else 'not comparable'
  at=str(a.get('seconds','not run'))+('†' if a.get('timingSource') else '')
  bt=str(b.get('seconds','not run'))+(' (failed)' if b.get('state') in ('partial','failed') else '')
  lines.append(f"| {h} | {n} | {stage(a)} / {at} | {stage(b)} / {bt} | {delta} |")
lines+=['','Capture checks: every locally saved PNG has byte size, dimensions, RGB extrema and black/single-colour flags in capture-checks.json. All-black or single-colour captures fail visual acceptance even if the unchanged harness reports successful upload/share. Display-state observations are read-only and preserve errors/unavailable interfaces.','', '| Host | PNGs checked | Black | Single-colour |','| --- | --- | --- | --- |']
for h in hosts:
 f=B/h/'pr/capture-checks.json';c=json.loads(f.read_text()) if f.exists() else []
 lines.append(f"| {h} | {len(c)} | {sum(i['black'] for i in c)} | {sum(i['singleColour'] for i in c)} |")
lines+=['','Failures and oddities (all attempts retained; no pass-seeking retry):','']
for h in hosts:
 for d in (current,controls):
  for i in d.get(h,{}).get('results',[]):
   if not i['passed']:lines.append(f"- {h} {'PR' if d is current else 'nightly'}: `{i['name']}` state `{i['state']}`, error `{i.get('error','')}`, {i.get('seconds')} s.")
 if current.get(h,{}).get('failure'):lines.append(f"- {h}: STOPPED {current[h]['failure']}")
lines+=['','Added instrumentation: `round2.py` imports the byte-identical published `proton_accept.py` from c0a3ff1c and wraps calls to add capture pixel checks, display-state snapshots, an immediate extra desktop capture if black, and the nightly control after the PR large-file cases. `drive.py` supplies new scratch paths, downloads/copies/extracts exact packages, holds and heartbeats both locks, collects outputs and releases after cleanup. The published `run_accept.sh` is retained byte-identical; its hard-coded round-1 paths prevent executing it directly without touching round-1 scratch, so drive.py performs its orchestration. No original case bodies or process-counting logic changed.','', 'Not covered: Aurora, GNOME captures with missing extension, real pointer region/window selection, memory gates, package installation audits, expired-token or transport fault injection. These are timing samples, not a statistical regression claim. No display change, logout, extension workaround or keyring inspection. Prior scratch, including d69 pf2, untouched. Raw logs/copies remain private under /tmp/pr1414r2 and ~/work/pecr2.']
(E/'README.md').write_text('\n'.join(lines)+'\n')
for f in ['proton_accept.py','run_accept.sh']:shutil.copy2(R/f,E/f)
for f in ['round2.py','round2-first-attempt.py','drive.py','drive-first-attempt.py','resume.py','ci.json','nightly.json','merge-provenance.json','package-sha256.txt']:shutil.copy2(B/f,E/f)
for h in current:
 dest=E/h;dest.mkdir(exist_ok=True)
 for f in ['results.json','combined-results.json','interrupted-results.json','summary.txt','capture-checks.json','display-state.json','black-immediate-repeat.json','nightly-control-exit.json','revocation-verification.json','observed-operations.jsonl']:
  src=B/h/'pr'/f
  if src.exists():shutil.copy2(src,dest/f)
 for f in ['results.json','summary.txt']:
  src=B/h/'nc'/f
  if src.exists():shutil.copy2(src,dest/('nightly-'+f))
 shutil.copy2(B/h/'run.log',dest/'run.log')
 shutil.copy2(B/h/'environment.txt',dest/'environment.txt')
 if (B/h/'pr/capture-checks.json').exists():
  for c in json.loads((B/h/'pr/capture-checks.json').read_text()):
   if c['black']:shutil.copy2(B/h/'pr'/c['file'],dest/('black-'+pathlib.Path(c['file']).name))
print(E)
