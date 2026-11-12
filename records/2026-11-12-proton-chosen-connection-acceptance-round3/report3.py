import json,pathlib,shutil,re
B=pathlib.Path('/tmp/p3a');E=B/'2026-11-12-proton-chosen-connection-acceptance-round3';E.mkdir(exist_ok=True)
hosts=['d69','k72','m74','f44']
def read(f,default=None):return json.loads(f.read_text()) if f.exists() else default
current={h:read(B/'new'/h/'pr/results.json',{}) for h in hosts};controls={h:read(B/'new'/h/'nc/results.json',{}) for h in hosts}
base={h:read(B/'records/2026-11-10-proton-upload-speed-acceptance'/h/'results.json',{}) for h in hosts}
old={h:read(B/'records/2026-11-12-proton-chosen-connection-acceptance'/h/'results.json',{}) for h in hosts}
r2={h:read(B/h/('combined-results.json' if h=='d69' else 'results.json'),{}) for h in hosts}
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
L=['# Proton chosen-connection desktop acceptance round 3 (#1414)','', 'Requested head `8596919291d0fb903bf8d1cf8f1fd4859f68d10e`, CI [43164839474](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43164839474). Published nightly control `26.1111.4633-nightly`. Packages extracted, never compiled. No product edits, merge, close or approval.','', '| Host | PR build | Original passes | Helpers left | Shared / attempts |','| --- | --- | --- | --- | --- |']
for h in hosts:
 d=current[h];rs=d.get('results',[]);items=[i for r in rs for i in r.get('items',[]) if r.get('state')!='cancelled' and i.get('shareStatus') not in (None,'not_requested')]
 L.append(f"| {h} | {d.get('build',{}).get('version','not run')} | {sum(r['passed'] for r in rs[:15])}/{len(rs[:15])} | {d.get('helpersLeft','not run')} | {sum(i['shareStatus']=='shared' for i in items)}/{len(items)} |")
L+=['','Seconds: **2026-11-10 baseline / round 1 / round 2 / round 3**. Delayed captures exclude countdown; back-to-back totals share one invocation origin. † Debian round 2 8 MiB is an app-log interval, not a CLI total.','','| Case | '+' | '.join(hosts)+' |','| --- | '+' | '.join(['---']*4)+' |']
for name in cases(old,'d69'):
 if name.startswith('sequential') or name=='revoke-additions':continue
 L.append('| '+name+' | '+' | '.join(' / '.join(value(cases(d,h).get(name)) for d in (base,old,r2,current)) for h in hosts)+' |')
L+=['','| Host | Back-to-back helpers | PID/startTicks |','| --- | --- | --- |']
for h in hosts:
 i=cases(current,h).get('back-to-back',{});L.append(f"| {h} | {i.get('helperProcessCount','not run')} | {i.get('helperProcessesObserved',[])} |")
L+=['','Helpers sampled every 10 ms as distinct PID/startTicks pairs, unchanged from round 2; this is not an exec audit.','','| Host | Screenshot 1 stage / total | Screenshot 2 stage / total | Screenshot 3 stage / total |','| --- | --- | --- | --- |']
for h in hosts:
 L.append('| '+h+' | '+' | '.join(f"{stage(i)} / {i.get('seconds','not testable')} ({i.get('state','gnome_extension_missing')})" for i in [cases(current,h).get(f'sequential-desktop-{n}',{}) for n in range(1,4)])+' |')
L+=['','Order-balanced large-file control: one network sample per build/case. Upload stage = first observed sharing minus first observed uploading. Total = invocation to terminal observation. These numbers support no conclusion about sustained speed.','','| Host | First build | Case | PR stage / total | Nightly stage / total |','| --- | --- | --- | --- | --- |']
for h in hosts:
 for n in ['file-1m','file-8m']:
  a=cases(current,h).get(n,{});b=cases(controls,h).get(n,{})
  L.append(f"| {h} | {'nightly' if h in ('d69','m74') else 'PR'} | {n} | {stage(a)} / {a.get('seconds','not run')} ({a.get('state','')}) | {stage(b)} / {b.get('seconds','not run')} ({b.get('state','')}) |")
L+=['','| Host | PNGs | Black | Single-colour | PR revoked | Nightly revoked |','| --- | --- | --- | --- | --- | --- |']
for h in hosts:
 c=read(B/'new'/h/'pr/capture-checks.json',[])
 rev=[r['state'] for r in current[h].get('results',[]) if r['name'].startswith('revoke')]
 nc=cases(controls,h).get('revoke-all',{}).get('state','not run')
 L.append(f"| {h} | {len(c)} | {sum(i['black'] for i in c)} | {sum(i['singleColour'] for i in c)} | {', '.join(rev)} | {nc} |")
L+=['','Failures and oddities:','']
for h in hosts:
 for label,d in [('PR',current),('nightly',controls)]:
  for i in d[h].get('results',[]):
   if not i['passed']:L.append(f"- {h} {label}: {i['name']}: {i.get('state')}, error `{i.get('error','')}`, {i.get('seconds')} s; items `{json.dumps(i.get('items',[]))}`.")
  if d[h].get('failure'):L.append(f"- {h} {label}: STOPPED {d[h]['failure']}")
L+=['','Every operation log event is retained in each build’s events.jsonl, with addresses and secret-bearing fields omitted. Non-shared outcomes, if any, have one immediate read-only history.inspectLink and share.inspect completion in nonshared-inspections.jsonl. An inspection does not relabel the original outcome.','', 'Method: proton_accept.py is byte-identical to round 2 (SHA-256 945751b11a52f31004021b8754f4906910c3e85ffab02066532ed4193135d810). round3.py is the additive round-2 adapter adjusted for balanced ordering, a fresh log on every start, no black-capture retry, and immediate non-shared inspections. drive3.py uses new /tmp/p3a and ~/work/p3a paths. On PR-first hosts the resident is stopped after file-8m, nightly runs and revokes its links, then PR resumes with a new resident log. On nightly-first hosts the nightly process finishes before PR starts. No failed product case is retried. Read-only display probes precede the first capture and are inside that first case’s reported timer. Pixel analysis follows terminal timing.','', 'Capture PNGs remain private on their builders; byte sizes, dimensions and RGB extrema are exported. No desktop logout, unlock, power change or GNOME extension workaround. The display wall remains enabled. No memory gate, region/window pointer selection, Aurora, package install audit, or transport/expired-token injection is covered. No statistical speed claim. Protected inputs, keyrings and earlier scratch were not read or modified.','']
(E/'README.md').write_text('\n'.join(L)+'\n')
for name in ['proton_accept.py','round3.py','drive3.py','adapt.py','export_events.py','report3.py','desktop_lock.py','ci.json','nightly-current.json','package-sha256.txt','merge-provenance.json','k72-b2b-events.jsonl']:
 if (B/name).exists():shutil.copy2(B/name,E/name)
for h in hosts:
 out=E/h;out.mkdir(exist_ok=True)
 for kind in ['pr','nc']:
  p=B/'new'/h/kind
  for name in ['results.json','summary.txt','capture-checks.json','display-state.json','observed-operations.jsonl','revocation-verification.json','nonshared-inspections.jsonl','events.jsonl']:
   if (p/name).exists():shutil.copy2(p/name,out/(('nightly-' if kind=='nc' else '')+name))
 for name in ['environment.txt','run.log','exit.json']:
  if (B/'new'/h/name).exists():shutil.copy2(B/'new'/h/name,out/name)
print(E)
