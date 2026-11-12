from pathlib import Path
import json,shutil,collections
b=Path('/tmp/p4a');e=b/'2026-11-12-proton-chosen-connection-acceptance-round4'
s=(e/'README.md').read_text()
s=s.replace('\n\nTested PR head', '\n\nAll 36/36 pairs used one helper. All 119/119 upload items ended shared. No capture was black. **Not clean acceptance:** Kubuntu revoke-all failed for two items; separate cleanup later revoked both.\n\nTested PR head')
s=s.replace('using successful CI run 43170857019 packages.', 'using [successful CI run 43170857019](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43170857019) packages. Build merge commit `fe1e300569344866158e968f4f9bd513457ca2a5`, tree `742b4c8b92cbcaf16808cc6b0eda9affe4190c71`; merge second parent is the exact requested head (merge-provenance.json).')
s=s.replace('Verified no links left','No available links in initial history read')
for h in ['d69','k72','m74','f44']:
 receipts=[]
 for f in sorted((b/'new'/h/'receipts').glob('*.json')):
  d=json.loads(f.read_text());check=d['check']
  receipts.append({k:d[k] for k in ['lock','releasedBy','event','host','at'] } | {'receiptFile':f.name,'cleanupCounts':{k:len(v) for k,v in check.items()}})
 (e/h/'cleanup-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
for n in ['inspect4.py','inspect4b.py','cleanup4.py','diagdrive.py','diagdrive2.py','cleanupdrive.py','drive4-initial.py','export_sharing.py','collect_journal.py','remote.py','augment4.py','receipts4.py']:
 shutil.copy2(b/n,e/n)
for h in ['d69','m74','f44']:shutil.copy2(b/(h+'-lock-refused.log'),e/h/'lock-refused.log')
for n in ['k72-diagnostic.log','k72-inspection.log','k72-cleanup.log']:shutil.copy2(b/n,e/'k72'/n)
for dn in ['diag','diag2','diag3']:
 target=e/'k72'/dn;target.mkdir(exist_ok=True)
 for n in ['history-status.json','inspections.json']:
  f=b/'new/k72'/dn/n
  if f.exists():
   v=json.loads(f.read_text())
   if n=='inspections.json':
    for x in v:
     if isinstance(x.get('result'),dict):x['result'].pop('receipt',None)
   (target/n).write_text(json.dumps(v,indent=2)+'\n')
s+='''
Kubuntu revoke-all failed and remains failed: `29 revoked`, failures `['unknown', 'unknown']`. The original final history read had zero available links, which did **not** prove revocation: unknown clears local link availability. A separate diagnostic start found 29 `revoked`, two `unknown`. One read-only inspection per uncertain item then found both still `shared`. One targeted cleanup action per exact test item returned `revoked`; these cleanup actions do not turn the original acceptance gate into a pass. Every run-created link now has a confirmed revoke result in the durable sharing journal: d69 31, k72 31, m74 31, f44 26 (119 total). Kubuntu's two original unknown records remain in sharing-journal.json.

Kubuntu durable failure records (the app emitted no corresponding revoke failure log line):
'''
rows=json.loads((e/'k72/sharing-journal.json').read_text())
s+='\n```jsonl\n'+'\n'.join(json.dumps(x) for x in rows if x['status']=='unknown')+'\n```\n'
s+='''
Mint pairs 2 and 7 and Fedora pairs 3 and 9 finished the second-invoked operation first while still using one helper each. Pair operation IDs are matched using the harness result history IDs, preserving invocation order even when log events arrive out of order.

Read-only reconciliation and separate cleanup are in k72/diag2/inspections.json and k72/diag3/inspections.json. Each diagnostic launch used a fresh log under a new directory, checked both locks, stopped its resident and helper, and released verified-clean; no sign-in, sign-out or session copy occurred. These were diagnostic/cleanup launches after the single acceptance run, not repeat acceptance cases.

The initial acquire attempts on d69, m74 and f44 were refused while `scroll-fix7-1398` held their desktop leases; no app started on those attempts. Their logs are preserved as lock-refused.log. The corrected driver allows an existing *empty* output directory left by a refused acquire, but refuses to rerun any host with run.log. The old driver is drive4-initial.py. Coordination occurred with the scrolling screenshot campaign; no lease was broken or foreign process stopped.

Fedora failed screenshot operations, straight from the app log:
'''
ev=[json.loads(l) for l in (e/'f44/events.jsonl').read_text().splitlines()]
failids={r['operationId'] for r in json.loads((e/'f44/results.json').read_text())['results'] if not r['passed'] and r.get('operationId')}
s+='\n```jsonl\n'+'\n'.join(json.dumps(x) for x in ev if x.get('operationId') in failids and (x['message']=='Operation finished' or x['level'] in ['warning','error']))+'\n```\n'
(e/'README.md').write_text(s)
# Self-contained timing chart: four separate host groups, no averaging of pairs.
old=next((b/'records').glob('*/README.md')).read_text()
row=next(l for l in old.splitlines() if l.startswith('| file-64k |'))
prior=[x.strip().split(' / ')[1:] for x in row.split('|')[2:-1]]
parts=['<!doctype html><meta charset="utf-8"><style>:root{font-family:var(--font-sans,system-ui)} .row{display:grid;grid-template-columns:65px 1fr;gap:10px;margin:10px 0}.bars{display:grid;gap:3px}.bar{height:22px;color:var(--foreground);font-size:12px;padding-left:6px;white-space:nowrap}small{color:var(--muted-foreground)}</style><p>64 KiB upload completion time · rounds 1–4</p><small>Single observations in seconds; network variation applies.</small>']
for h,pr in zip(['d69','k72','m74','f44'],prior):
 d=json.loads((e/h/'results.json').read_text());v=next(x['seconds'] for x in d['results'] if x['name']=='file-64k');vals=list(map(float,pr))+[v]
 parts.append('<div class="row"><b>'+h+'</b><div class="bars">')
 for i,v in enumerate(vals):parts.append(f'<div class="bar" style="width:{v/8*90:.2f}%;background:var(--chart-{i+1},#678)">R{i+1} · {v:g}s</div>')
 parts.append('</div></div>')
(e/'timing-comparison.html').write_text(''.join(parts))

with (e/'README.md').open('a') as out:
 out.write("\n* Fedora returned `clipboard_unavailable` on 11 completed upload operations (batch-3, text-small, after-cancel and eight individual paired operations). Every uploaded item still ended shared. The unchanged harness pass criterion checks upload/share completion, not clipboard ownership. All 11 warning lines are retained below and in warnings.md.\n\n```text\n")
 for x in ev:
  if x.get('fields',{}).get('error',{}).get('code')=='clipboard_unavailable':out.write(x['time']+' '+x['operationId']+' '+x['message']+' copyStatus=failed error=clipboard_unavailable message=GNOME helper cannot own CLIPBOARD\n')
 out.write('```\n\nKubuntu’s runtime binary matched round 3 byte for byte: SHA-256 `42e1decb6d718e2640f0a419b3d135a3755f65a27e66682126ed16a2f6581065`.\n')
