from pathlib import Path
import json,re,shutil,hashlib
b=Path('/tmp/p4a'); e=b/'2026-11-12-proton-chosen-connection-acceptance-round4';e.mkdir(exist_ok=True)
hosts=['d69','k72','m74','f44']; data={};pairs={}; allobs={}
def clean(v):
 if isinstance(v,dict):return {k:clean(w) for k,w in v.items() if not any(t in k.lower() for t in ['url','token','secret','password','credential'])}
 if isinstance(v,list):return [clean(w) for w in v]
 if isinstance(v,str):return re.sub(r'https?://[^\s"<>]+','[address omitted]',v)
 return v
for h in hosts:
 q=b/'new'/h/'pr';dest=e/h;dest.mkdir(exist_ok=True)
 events=[]
 for f in sorted((q/'profile/state/putgd/logs').glob('*.jsonl')):events += [clean(json.loads(l)) for l in f.read_text().splitlines()]
 (dest/'events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in events))
 (dest/'resident.log').write_text(clean((q/'resident.log').read_text()))
 for name in ['results.json','summary.txt','capture-checks.json','display-state.json','observed-operations.jsonl','revocation-verification.json','nonshared-inspections.jsonl']:
  if (q/name).exists():shutil.copy2(q/name,dest/name)
 for name in ['environment.txt','exit.json','run.log']:shutil.copy2(b/'new'/h/name,dest/name)
 shutil.copy2(b/(h+'-driver.log'),dest/'driver.log')
 shutil.copy2(b/'new'/h/'sharing-journal.json',dest/'sharing-journal.json')
 data[h]=json.loads((q/'results.json').read_text())
 obs=[json.loads(x) for x in (q/'observed-operations.jsonl').read_text().splitlines()];allobs[h]=obs
 raw=json.loads((q/'pairs.json').read_text());pb=[]
 # Observed operation sequence: first 5 cases produce 5 operations, then original pair.
 for i,row in enumerate(raw):
  ids2=[next(o['operationId'] for o in obs if any(it.get('historyId')==item.get('historyId') for it in o.get('items',[]))) for item in row['items']]; es=[[x for x in events if x.get('operationId')==oid] for oid in ids2]
  at=[next(x['time'] for x in xs if x['message']=='Operation accepted') for xs in es]
  ft=[next(x['time'] for x in xs if x['message']=='Operation finished') for xs in es]
  row.update(operationIds=ids2,acceptTimes=at,completionTimes=ft,finishedFirst=1 if ft[0]<ft[1] else 2,operationEvents=es)
  pb.append(row)
 pairs[h]=pb;(dest/'pairs.json').write_text(json.dumps(pb,indent=2)+'\n')
for name in ['proton_accept.py','round3.py','round4.py','drive4.py','desktop_lock.py','report4.py','ci.json','package-sha256.txt','merge-provenance.json']:
 if (b/name).exists():shutil.copy2(b/name,e/name)
lines=['# Proton chosen-connection desktop acceptance round 4 (#1414)','', 'Tested PR head `0a6014c8c42c1929d148cb6d13826d0a15c1509f` using successful CI run 43170857019 packages. Extracted packages; no compilation or product edits. No merge, close or approval.','', '| Host | Build | Original cases passed | Extra pairs passed (including one-helper gate) | Shared / attempts | Helpers left |','| --- | --- | --- | --- | --- | --- |']
for h,d in data.items():
 obs=allobs[h];items=[i for o in obs for i in o.get('items',[])];n=sum(i['shareStatus']=='shared' for i in items)
 orig=[x for x in d['results'] if not re.match(r'back-to-back-\d',x['name'])]
 lines.append(f"| {h} | {d['build']['version']} | {sum(x['passed'] for x in orig)}/15 | {sum(x['passed'] and x['helperProcessCount']==1 for x in pairs[h][1:])}/8 | {n}/{len(items)} | {d['helpersLeft']} |")
lines += ['', 'Seconds: round 1 / round 2 / round 3 / round 4. Each is a single network observation. Delayed captures exclude countdown; paired CLI timings follow first operation then second, so use app-log completion times below for finish order. Debian round 2 8 MiB (†) is an app-log interval.','', '| Case | d69 | k72 | m74 | f44 |','| --- | --- | --- | --- | --- |']
old=next((b/'records').glob('*/README.md')).read_text()
for line in old.splitlines():
 if not line.startswith('| '):continue
 cs=[x.strip() for x in line.split('|')[1:-1]]
 if len(cs)!=5 or cs[0] not in [x['name'] for x in data['d69']['results']]:continue
 name=cs[0];cells=[]
 for h,prior in zip(hosts,cs[1:]):
  row=next(x for x in data[h]['results'] if x['name']==name)
  if row.get('state') in ('failed','refused'):v=row.get('error',row['state'])
  elif name=='back-to-back':v=f"{row['firstSeconds']}, {row['secondSeconds']}"
  elif name=='revoke-all':v=f"{row['state']}; {min(row['eachSeconds']):.2f}–{max(row['eachSeconds']):.2f}/link"
  elif name=='cancel-countdown':v=f"{row['state']}; helper gone {row.get('helperGoneAfter')}"
  elif name=='link-answers':v='HTTP '+row['state']
  else:v=str(row.get('secondsAfterCountdown',row.get('seconds')))
  if row.get('error')=='clipboard_unavailable':v+=' *'
  cells.append(' / '.join(prior.split(' / ')[1:]+[v]))
 lines.append('| '+name+' | '+' | '.join(cells)+' |')
lines += ['', 'All nine pairs per host. Times are UTC from app logs, listed in invocation order; first=512 KiB for pairs 1–5 and 64 KiB for pairs 6–9. Pair 1 is the original case. Completion means `Operation finished`, not the later CLI observation. Helpers are distinct PID/kernel-startTicks sampled every 10 ms through helper exit, not an exec audit.','', '| Host/pair | KiB order | Accepted 1 / 2 UTC | Completed 1 / 2 UTC | Finished first | Helpers |','| --- | --- | --- | --- | --- | --- |']
for h in hosts:
 for row in pairs[h]:lines.append(f"| {h}/{row['pair']} | {' / '.join(map(str,row['orderKiB']))} | {' / '.join(t[11:-1] for t in row['acceptTimes'])} | {' / '.join(t[11:-1] for t in row['completionTimes'])} | {row['finishedFirst']} | {row['helperProcessCount']} |")
lines += ['', '| Host | PNGs checked | Black | Single colour | Revocations | Verified no links left |','| --- | --- | --- | --- | --- | --- |']
for h in hosts:
 ck=json.loads((e/h/'capture-checks.json').read_text());rr=next(x for x in data[h]['results'] if x['name']=='revoke-all');rv=json.loads((e/h/'revocation-verification.json').read_text())
 lines.append(f"| {h} | {len(ck)} | {sum(x['black'] for x in ck)} | {sum(x['singleColour'] for x in ck)} | {rr['state']} | {rv['allRevoked']} |")
lines+=['','Failures and oddities (no retries):','']
for h,d in data.items():
 for row in d['results']:
  if not row['passed']:lines.append(f"- {h}: {row['name']}: {row.get('state')}, {row.get('error')}, {row.get('seconds')} s.")
 for row in pairs[h]:
  if row['helperProcessCount']!=1:lines.append(f"- {h} pair {row['pair']}: {row['helperProcessCount']} helpers; all operation log lines are in pairs.json.")
lines+=['','Fedora’s six screenshot cases are not testable (`gnome_extension_missing`), expected; no workaround. All warning/error log lines follow in warnings.md. Full sanitized app events are in each host’s events.jsonl, and every paired operation log line in pairs.json. No link outcome is relabelled by an inspection. Any nonshared outcome has a read-only history.inspectLink diagnostic in nonshared-inspections.jsonl.','', 'The unchanged proton_accept.py SHA-256 is '+hashlib.sha256((b/'proton_accept.py').read_bytes()).hexdigest()+'. Round 3 adapters are retained unchanged. round4.py disables the nightly-control hook, selects the original 15 cases explicitly (skipping sequential screenshots), and runs eight more original back-to-back cases before final revoke-all. Only synthetic payload generation sizes are swapped for pairs 6–9. Every pair waits for both completions and helper exit. All pairs share one resident start and a fresh resident log per host.','', 'Capture PNGs remain private on builders; only pixel statistics exported. Read-only display probes are retained; no logout, unlock, power/display change, keyring extraction or unrelated scratch changes. Socket preflight is in run.log. Both leases were acquired with checked success, heartbeated every minute, and released verified-clean after cleanup. All work is before the nightly window.','', 'Not covered: the intentionally omitted three sequential screenshots and nightly large-file control; memory gates, Aurora, pointer-based region/window selection, expired-token injection or sustained speed. No acceptance case rerun. Kubuntu required separately recorded targeted cleanup for two test links; the original revoke-all result remains failed. Evidence source is /tmp/p4a on the workstation and ~/work/p4a on each builder. Earlier rounds remain untouched.']
(e/'README.md').write_text('\n'.join(lines)+'\n')
w=['# Warning and error log lines','']
for h in hosts:
 rows=[json.loads(x) for x in (e/h/'events.jsonl').read_text().splitlines()];rows=[x for x in rows if x['level'] in ('warning','error')]
 w += [h+': '+str(len(rows))+' lines.','','```jsonl']+[json.dumps(x) for x in rows]+['```','']
(e/'warnings.md').write_text('\n'.join(w))
print(e)
