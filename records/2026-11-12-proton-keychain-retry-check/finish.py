from pathlib import Path
import json,shutil,subprocess
b=Path('/tmp/kr19');out=b/'2026-11-12-proton-keychain-retry-check'
for f in ['drive-k72.py','never-first.py','retry.py','collect-extra.py','finish.py']:
 shutil.copyfile(b/f,out/f)
for f in ['k72-drive.log','d69-drive.log','retry.log']:
 shutil.copyfile(b/f,out/f)
# Full baseline failure instrumentation, from the requested immutable record.
base=[]
for n in [1,4,5]:
 x=json.loads(subprocess.check_output(['git','-C','/home/patrick/work/put.gd-evidence','show',f'dbcfca8d:records/2026-11-12-proton-k72-revoke-reliability/p{n}/results.json']))
 for r in x['revocations']:
  if r['status']!='revoked':base.append({'pass':n,'build':x['build'],**r})
(out/'baseline-failures.json').write_text(json.dumps(base,indent=2)+'\n')
table=(out/'table.md').read_text()
for build,label in [('pr','Earlier PR build, 3 passes'),('nightly','Earlier nightly, 3 passes')]:
 failures='; '.join(f"{r['index']} / {r['startUtc']} / {r['errorCode']} / {r['seconds']} s" for r in base if r['build']==build)
 table=table.replace('2 authentication_required' if build=='pr' else '1 authentication_required',failures)
(out/'table.md').write_text(table)
checks=[];warnings=[]
for host in ['k72','d69']:
 previous=None
 for f in sorted((out/host).glob('p*/results.json')):
  x=json.loads(f.read_text());assert x['shared']==31 and x['revokedFirst']==31 and len(x['revocations'])==31 and not x['processesLeft'] and x['helpersGoneAfter'] is not None
  assert len(x['uploads'])==31 and all(u['state']=='completed' for u in x['uploads'])
  if previous:
   from datetime import datetime
   gap=(datetime.fromisoformat(x['startedUtc'].replace('Z','+00:00'))-datetime.fromisoformat(previous.replace('Z','+00:00'))).total_seconds();assert gap>=20;checks.append(f'{host} {f.parent.name} gap {gap:.3f} s')
  previous=x['endedUtc']
 for f in sorted((out/host).glob('*/app.jsonl')):
  for line in f.read_text().splitlines():
   x=json.loads(line)
   if x.get('level') in ['warning','error']:warnings.append(f'{host}/{f.parent.name}: '+line)
(out/'warnings.txt').write_text('\n'.join(warnings)+'\n');(out/'validation.txt').write_text('\n'.join(checks)+'\nAll 217 uploads completed/shared; all 217 first revocations revoked; all pass process inventories empty.\n')
readme='''# Proton keychain retry reliability check, PR #1419

Measured first-time revocation failures: k72 0/186; d69 0/31. All 217 uploads ended shared, and all 217 links ended revoked on the first attempt. No cleanup inspection or retry was needed. This sample did not reproduce the earlier failure; it does not prove a zero failure rate.

'''+table+'''
Totals: PR build k72 shared 186/186 and revoked first time 186/186; d69 shared 31/31 and revoked first time 31/31. Earlier k72 baseline: shared 186/186, revoked first time 183/186, failures 3/186 across two builds ([baseline record](https://github.com/patrick-hudson/put.gd-evidence/tree/dbcfca8d16ac7ebf61191dc6314e8138f2eaf07f/records/2026-11-12-proton-k72-revoke-reliability)). Baseline row indices are revocation order within the named earlier pass.

Exact PR head de622c1c9c15726b72e59a5776a124a9bf2af8f5; CI run 43183607287 passed. Packages downloaded with gh run download: release-native-ubuntu26.04 and release-native-debian13. Both identify merge f36f0e8f4560b59c4273671fca48996ce0a689a0, whose second parent is the requested PR head, version 26.1112.4662-dev+gf36f0e8f4560. Package hashes, build identities, merge provenance and full CI job state are included. Packages were extracted with dpkg-deb -x; no installation or compilation. No product source changes, merge, close or approval.

Method: proton_accept.py is byte-identical to the earlier record. run.py preserves the earlier upload path and action polling, history.list order, linkAvailable filter, and revoke-all request/poll logic; changes select this package for all six k72 passes and one d69 pass, rename owned scratch/lock identities and add upload index/UTC/duration instrumentation. Each app run uploads 31 synthetic 65536-byte files, one operation after another, to that builder's configured isolated Proton lab folder, then revokes once per link. No retries within a pass. All links were revoked before the next app run. Gap checks are in validation.txt: at least 21 seconds, no putgd process at shutdown or next startup. Every app socket preflight resolved /run/user/1000/putgd/session.sock to 33 UTF-8 bytes. Tests ran in the existing physical Plasma Wayland sessions, with no display redirection or screenshot collection. This is a targeted CLI-driven reliability check, not complete graphical acceptance.

Commands: python3 -u /tmp/kr19/drive.py k72 (original bytes saved as drive-k72.py); python3 -u /tmp/kr19/drive.py d69; python3 -u /tmp/kr19/retry.py k72. Remote reliability command: cd ~/work/kr19 && LAB_HOST=HOST PASSES=6-or-1 python3 -u run.py. Desktop and Proton locks were acquired and checked before each app, heartbeated every minute, and released verified-clean. Release receipts are included. No owned putgd or putgd-proton-runtime remained. Existing scratch and user work were preserved; synthetic source files remain private on each builder. No share links, tokens, keyring contents or payloads are published.

Never-connected check: docs/automation/cli.md documents setup.testDestination and setup.inspect. The runtime capabilities object was read; it is a feature snapshot, not a method-name list. In a private profile, a second Proton destination copied the lab destination's non-secret folder settings but used a fresh credential reference putgd/proton/lab-k72-never-connected-kr19, with no keychain entry created. The lab reference was unchanged. setup.testDestination returned a setupId; setup.inspect ended failed with authentication_required in 1.021 s: "The Proton session is unavailable. Reconnect this account before explicitly inspecting or retrying the saved operation." No session_unread in the response; browser process inventories were empty before and after. No sign-in, connectAccount, keychain writes or browser launch was requested. Result: the expected normal not-connected answer.

Harness/probe failures, preserved: the initial never-connected attempt asserted that capabilities must contain the method name, and stopped before adding a profile or testing a destination. Its app was shut down and locks released. The corrected command above uses a new private directory never2 and retains the actual capabilities object, with no such assertion. never-first.py, never-driver.log and k72/never retain the failed attempt. Separately, an SSH-only plasmashell --version metadata probe failed because it had no display environment (Qt xcb startup error); the app was not yet started. k72-drive.log preserves the error; collect-extra.py records the corrected dpkg-query -W plasma-workspace kwin-wayland command and output. Neither failure was an upload or revocation failure.

App logs: k72/p1 through p6 and d69/p1, plus both never-connected attempts, each contain app.jsonl and resident.log. Every k72 app start logged the same portal app-ID registration warning as the baseline (putgd-ui app info not found); no other warning/error entries were present. d69 had no warning/error entries. warnings.txt contains every such full log line. failure-context.txt records that there were no upload/revocation failures, so there are no failure rows or surrounding app log lines to report. No other odd behavior was measured.
'''
(out/'README.md').write_text(readme)
print((out/'validation.txt').read_text())
