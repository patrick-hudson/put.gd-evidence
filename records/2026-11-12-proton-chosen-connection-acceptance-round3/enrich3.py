from pathlib import Path
import json,shutil,collections
b=Path('/tmp/p3a');e=b/'2026-11-12-proton-chosen-connection-acceptance-round3'
p=e/'README.md';s=p.read_text();s=s.replace('\nRequested head','\nAll 64/64 PR-build item share attempts ended `shared`. No black or single-colour image among 24 PNGs. **Not clean acceptance:** Kubuntu back-to-back sampled two helpers, failing the expected one-helper gate. Debian, Mint and Fedora sampled one. The unchanged harness reports Kubuntu 15/15 because its verdict does not enforce helperProcessCount == 1.\n\nRequested head',1)
s+='''
CI packages identify merge commit `1be97a25835175db460ec8cccc27756ca8e3db2c`, tree `cce1e5c83de497f454570be3ae340aba41a25669`; its second parent is the exact requested PR head (merge-provenance.json). All four residents reported `26.1112.4656-dev+g1be97a258351`. Control release published 2026-11-11 10:45 UTC; its downloaded files matched the release API SHA-256 digests. CI artifact hashes are in package-sha256.txt.

No non-shared item occurred, so no history.inspectLink failure diagnostic was needed. Original and added PR revocations totalled 64, controls revoked 8; each profile's final history.list had zero available links. No helper remained on either build. Helpers are sampled, not audited; Kubuntu's two identities were PID 3323360/startTicks 114553567 and PID 3323491/startTicks 114553937. k72-b2b-events.jsonl holds every app event for the two operations. The log has `06:27:01.660 Operation accepted` and `06:27:01.691 Operation accepted`, then `06:27:05.306 Sharing finished status=shared` and `06:27:10.187 Sharing finished status=shared`. Both finished completed; the first-invoked operation finished last. No app log line explains the two Proton helper lifetimes, and their cause is not established. No retry.

The initial local driver attempt stopped with `FileExistsError: /tmp/p3a/m74` before taking any lease or starting an app: the round-2 evidence extraction had made that path. The failed command was `python3 /tmp/p3a/drive3.py m74 > /tmp/p3a/m74-driver.log 2>&1`. Corrected command: `python3 /tmp/p3a/drive3.py m74 > /tmp/p3a/m74-driver-corrected.log 2>&1`, with new output under `/tmp/p3a/new/m74`. Both logs are retained. No product case was retried. Raw text/profile-state evidence remains private under /tmp/p3a/new; captures remain on builders under ~/work/p3a. The supplied round-2 shell orchestrator was not run because its fixed paths address earlier scratch; the corrected Python driver was reused with fresh paths. Scripts as run and the adaptation script are included.

Both locks were checked after every acquire and heartbeated once per minute. Each acquire was for 45 minutes. No lease was broken. Verified-clean desktop releases: Mint 06:25:23Z, Kubuntu 06:28:51Z, Fedora 06:31:20Z, Debian 06:34:57Z, all before 12:15Z. Their driver logs retain host-side receipt paths and the no-new-items cleanup results. Debian's baseline item and shared SSH processes were preserved. The prior holder released Debian naturally; no coordination message, logout, unlock or display change was needed.

Timing interpretation: back-to-back follows the first operation to completion before observing the second. If the second finishes first (as on Kubuntu), its reported time is the later CLI observation, not its actual completion latency. Upload-stage measurements are polling observations, not internal transfer-only timers. PR first controls interrupt the resident sequence; nightly first controls use separate private profiles. These are single samples on a varying network; no comparison establishes sustained performance.

Read-only pre-capture display observations:
'''
for h in ['d69','k72','m74','f44']:
 d=json.loads((e/h/'display-state.json').read_text());obs=d[0]['observations'];vals=[]
 for x in obs:
  if x.get('command',[None])[0]=='loginctl' and 'LockedHint=' in x.get('stdout',''):vals.append(x['stdout'].strip().replace('\n',', '))
  if x.get('file','').endswith('/dpms'):vals.append(x['file']+'='+x['value'])
 s+='\n- '+h+': '+'; '.join(vals)+'.\n'
p.write_text(s)
for h in ['d69','k72','m74','f44']:
 for kind in ['pr','nc']:
  q=b/'new'/h/kind;v=json.loads((q/'revocation-verification.json').read_text());assert v['allRevoked'];assert not json.loads((q/'results.json').read_text())['helpersLeft']
 shutil.copy2(b/(h+'-driver-corrected.log' if h=='m74' else h+'-driver.log'),e/h/'driver.log')
shutil.copy2(b/'m74-driver.log',e/'initial-driver-failure.log')
lines=['# All warning and error log lines','', 'Addresses and secret-bearing fields are omitted by export_events.py. All remaining fields are retained.','']
for h in ['d69','k72','m74','f44']:
 for kind in ['pr','nc']:
  rows=[json.loads(l) for l in (b/'new'/h/kind/'events.jsonl').read_text().splitlines()];rows=[x for x in rows if x['level'] in ['warning','error']]
  lines+=['',f'{h} {kind}: {len(rows)} warning/error lines.','','```jsonl']+[json.dumps(x) for x in rows]+['```']
(e/'warnings.md').write_text('\n'.join(lines)+'\n')
with p.open('a') as f:f.write('\nAll warning/error lines, including Fedora clipboard and capture errors, portal registration, tray, Fontconfig, GStreamer, Wayland text-input and Mint nightly NoReply warnings, are retained in [warnings.md](warnings.md). They were not suppressed or used to trigger retries.\n')
