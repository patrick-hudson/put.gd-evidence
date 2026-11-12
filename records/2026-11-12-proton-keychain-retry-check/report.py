from pathlib import Path
import json,shutil
b=Path('/tmp/kr19');out=b/'2026-11-12-proton-keychain-retry-check'
lines=['| Host | Pass | Shared of 31 | Revoked first time of 31 | Failures: index / UTC start / error / seconds |','| --- | --- | --- | --- | --- |'];contexts=[];totals={}
for host in ['k72','d69']:
 shared=revoked=count=0
 for path in sorted((out/host).glob('p*/results.json')):
  x=json.loads(path.read_text());fail=[];count+=len(x['revocations']);shared+=x['shared'];revoked+=x['revokedFirst']
  for kind,rows in [('upload',x['uploads']),('revocation',x['revocations'])]:
   for r in rows:
    bad=r.get('status')!='revoked' if kind=='revocation' else r.get('state')!='completed' or any(i.get('shareStatus')!='shared' for i in r.get('items',[]))
    if not bad:continue
    desc=f"{kind} {r['index']} / {r['startUtc']} / {r.get('errorCode') or r.get('error')} / {r['seconds']} s";fail.append(desc)
    logs=(path.parent/'app.jsonl').read_text().splitlines();before=[];after=[]
    for line in logs:
     item=json.loads(line);stamp=item.get('timestamp',item.get('time',''))
     (before if stamp<r['startUtc'] else after).append(line)
    contexts += [f"{host} pass {x['pass']}: {desc}",*before[-3:],*after[:3],'']
  lines.append(f"| {host} | {x['pass']} | {x['shared']}/31 | {x['revokedFirst']}/31 | {'; '.join(fail) or 'None'} |")
 totals[host]={'shared':shared,'revoked':revoked,'count':count}
lines += ['| k72 baseline | Earlier PR build, 3 passes | 93/93 | 91/93 | 2 authentication_required |','| k72 baseline | Earlier nightly, 3 passes | 93/93 | 92/93 | 1 authentication_required |']
(out/'table.md').write_text('\n'.join(lines)+'\n');(out/'failure-context.txt').write_text('\n'.join(contexts) if contexts else 'No upload or first-time revocation failures.\n')
for f in ['run.py','drive.py','never.py','proton_accept.py','report.py']:
 shutil.copyfile(b/f,out/f)
shutil.copyfile('/home/patrick/work/put.gd/tools/lab/desktop_lock.py',out/'desktop_lock.py')
print(json.dumps(totals));print('\n'.join(lines))
