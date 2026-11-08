import json,re,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path('work/np1275/evidence/2026-11-08-budgie-omarchy-nightly-4234')
flows=['region_upload','window_desktop','recording_upload','edit_upload','link_browser','history_delete','auto_copy','upload_clipboard','copy_image','survives_exit','file_manager_upload','s3_region_upload','proton_region_upload']
rows=[('fedora45-budgie','AppImage',['r2']),('fedora44-budgie','RPM',['r4']),('ubuntu-budgie-2604','DEB',['r5','r5b']),('ubuntu-budgie-2404','DEB',['r1','r1b','r1c']),('omarchy-hyprland-20261108','Arch',['r3','r3b','r3c']),('omarchy-hyprland-20261108','AppImage',['r6'])]
summary=[]
for name,package,batches in rows:
 cells={};attempts=0;identities=[]
 for batch in batches:
  p=root/'batches'/batch/'result.json';v=json.loads(p.read_text());assert v.get('finishedAt')
  assert v['release']=='v26.1108.4234-nightly' and v['build']=='2b5e1b2d3c11757f805331e4104eb06b2c79ad5c'
  if identities:assert all(v[k]==identities[0][k] for k in ('release','build','packageSha256','goldenSha256'))
  identities.append({k:v[k] for k in ('release','build','packageSha256','goldenSha256','driver','run','host')})
  for flow,c in v['cells'].items():
   attempts+=len(c.get('attempts',[]))
   if not c.get('attempts'):continue
   receipt=root/'batches'/batch/Path(c['receipt']).parent.name/'receipt.json';assert receipt.is_file() and hashlib.sha256(receipt.read_bytes()).hexdigest()==c['receiptSha256']
   cells[flow]=dict(status={'green':'pass','red':'fail','not_run':'not-run'}[c['status']],assertion=c['assertion'],batch=batch,receipt=str(receipt.relative_to(root)),receiptSha256=c['receiptSha256'])
 assert set(cells)==set(flows)
 summary.append(dict(row=name,package=package,cells=cells,passCount=sum(c['status']=='pass' for c in cells.values()),failCount=sum(c['status']=='fail' for c in cells.values()),notRunCount=sum(c['status']=='not-run' for c in cells.values()),totalCells=13,attemptCount=attempts,identities=identities,batches=batches))
retained=[];folders=[]
for p in root.glob('batches/*/proton_region_upload-*/receipt.json'):
 v=json.loads(p.read_text());notes=' '.join(r.get('note','') for r in v['interactions']);found=set(re.findall(r'proton_isolated_folder=(putgd-tier1-[0-9a-f]{32})',notes));assert len(found)==1
 folder=next(iter(found));count=1 if 'upload_count=1' in notes else 0
 item=dict(batch=p.parts[-3],attempt=p.parts[-2],folder=folder,retainedSyntheticFiles=count,shareRevoked='revocation_count=1' in notes)
 if count:
  names=set(re.findall(r'Screen-Capture-[0-9-]+\.png',notes));assert len(names)==1;item['filename']=next(iter(names))
  if not item['shareRevoked']:
   proofpath=(root/'cleanup/u24-recovery'/p.parent.name).with_suffix('.json');proof=json.loads(proofpath.read_text());assert proof['folder']==folder and proof['shareStatus']=='revoked';item.update(shareRevoked=True,recoveryReceipt=str(proofpath.relative_to(root)))
  retained.append(item)
 folders.append(item)
assert sum(r['retainedSyntheticFiles'] for r in retained)==3
retention=dict(retainedSyntheticFiles=3,retained=retained,allAttemptFolders=folders,policy='Suite revoke-only cleanup; synthetic private files retained in dedicated test account. No deletion path added.')
(root/'proton-retention.json').write_text(json.dumps(retention,indent=2))
retirements=[]
for batch in ('r1c','r2','r3c','r4','r5-unused','r5b','r6'):
 p=root/'batches'/batch/'retirement.json';assert p.is_file();retirements.append(dict(batch=batch,receipt=str(p.relative_to(root))))
record=dict(createdAt=datetime.now(timezone.utc).isoformat(),tag='v26.1108.4234-nightly',build='2b5e1b2d3c11757f805331e4104eb06b2c79ad5c',rows=summary,totalCells=78,passed=sum(v['passCount'] for v in summary),failed=sum(v['failCount'] for v in summary),notRun=sum(v['notRunCount'] for v in summary),retirements=retirements)
assert record['passed']+record['failed']+record['notRun']==78
(root/'results.json').write_text(json.dumps(record,indent=2))
labels=['Region','Window/desktop','Recording','Edit','Browser','Delete','Auto-copy','Clipboard upload','Copy image','Exit','Right-click','S3','Proton']
table='| Row/package | '+' | '.join(labels)+' | Total |\n|'+' --- |'*15+'\n'
for r in summary:table+='| '+r['row']+' '+r['package']+' | '+' | '.join(r['cells'][f]['status'] for f in flows)+' | '+str(r['passCount'])+'/13 pass; '+str(r['failCount'])+' fail; '+str(r['notRunCount'])+' not-run |\n'
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
text='# Private Budgie and Omarchy Tier 1 nightly check, build 4234\n\n'+table+'\n'
text+='All '+str(record['totalCells'])+' unique cells had actual suite invocations, with '+str(record['passed'])+' passing, '+str(record['failed'])+' failing after corrections, and '+str(record['notRun'])+' not-run. A not-run is not a pass. Individual attempts, including original failures, remain unchanged in batches/. results.json derives the latest corrected result for each unique cell and points to its audited receipt.\n\n'
text+='Exact published tag v26.1108.4234-nightly; clean source 2b5e1b2d3c11757f805331e4104eb06b2c79ad5c, tree 33b8f29b0a44ec5c0dc37d154cc0938d3612d328. Release asset SHA256SUMS, build identities, catalog provenance and package/overlay receipts are retained. The Fedora 45 row used the published AppImage, matching packaging/install.sh; Fedora 44 used the RPM. Arch and AppImage used separate fresh Omarchy overlays. Hosts f44/d69, real Budgie X11/Wayland and Hyprland sessions, QMP input and independent VNC frames. No EC2 or physical desktop lease.\n\n'
text+='Ubuntu Budgie 24.04 passed all 13 cells across its original run and corrective reruns. Its original 1280x800 output fitted the app beneath a Budgie panel shadow, blocking the keyboard guard; the real VM output was changed to 1920x1080 and the affected cells reran on the same DEB. A right-click upload visibly displayed its banner, but the observer accepted only NativeTray’s put.gd name and missed QApplication’s putgd name. The harness now admits both exact names only from verified private-family senders, preserving reply/ID correlation. The private Nemo profile also uses the existing scoped banner enable/restore because general nag suppression matched Budgie’s GNOME desktop token. The corrected right-click cell verified the drawn banner, uploaded file hash, clipboard and History row.\n\n'
text+='The five Wayland rows remain blocked by the current surface driver’s native witness support. The ext/wlr toplevel observation supplies identity and activation, without the PID/geometry the guard needs. Hyprland IPC and Lua expose client/layer bounds but no native point hit-test or layer input regions; the Omarchy bar surface spans the whole output while drawing a thin bar, so bounding-box inference cannot establish a safe input target. Native snapshots and API evidence are in environment/ and diagnostics/. No geometry, ownership, input or secret guard was weakened. Product window-capture availability and unavailable reasons on those rows remain unverified because the suite stopped at these prerequisites.\n\n'
text+='Omarchy recording preparation also left an external share-picker layer after its private helper had cleaned up. That layer kept later GTK pattern windows tiled (1256x750, fullscreen0) instead of full-screen. The exact owned VM picker PID/start time was verified and terminated; the source then returned to 1280x800/fullscreen2, and the four affected cells reran to the normal native-witness blocker. The harness now verifies the native recording source geometry before preparing a portal request; a corrective Ubuntu26 recording run and the later Omarchy AppImage row use that preflight. Original red attempts, the orphan cleanup receipt and before/after native traces remain preserved. The [portal session contract](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Session.html) requires related dialogs to end when the session closes and treats client exit as closing its sessions; the surviving picker after verified private-client cleanup supports a portal/backend cleanup classification.\n\n'
text+='Harness-only draft PR https://github.com/patrick-hudson/put.gd-desktop/pull/1314 at '+head+' targets nightly, based on 2b5e1b2d3. It adds opt-in owned-VM admission, Arch package labeling, Budgie discovery, isolated oo7 handling, Proton retention notes, the widget notification observer correction and recording-source preflight. There is no product change or alternate build. On f44, the current surface contract suite ran 1159 tests: 1158 passed and one existing skip. Unit/mocked checks are separate from graphical proof.\n\n'
text+='Proton uses the approved suite revoke-only cleanup. Exactly three synthetic files remain private in the dedicated test account, one in each folder below; all three shares were revoked. Empty folders from blocked attempts are enumerated in proton-retention.json.\n\n'
for r in retained:text+='- `'+r['folder']+'/'+r['filename']+'` — 1 retained synthetic file; share revoked.\n'
text+='\nS3 cleanup removed the three uploaded live origin objects, with origin absence verified (including independent authenticated HEAD404 for the two recovered original attempts). The suite permits cached CloudFront200 after origin deletion; no bucket policy/versioning or existing user object was changed. All owned history entries, profiles, cache roots and borrowed credential/keychain items were cleaned; the original X11 recovery receipts are in cleanup/.\n\n'
text+='Seven disposable overlays, including the prepared-only relocated Ubuntu26 overlay, were exported, SHA-verified on the workstation, then guarded-retired. Retirement receipts are indexed in results.json. Every launched VM had its own putgd-vm-np1275 systemd SSH tunnel and wall entry; all owned entries/units were removed at retirement. Other workers and Patrick’s processes were preserved. No change or post to #1003, no nightly chart rows, no builder nightly config/timer edits, and no use of ~/nd or ~/ne/results. The controller source blob is unchanged (build/repo-scope.json); the campaign used its own private configs/results and a publisher-free thin driver over the same FLOWS/recipes/verdicts.\n\n'
text+='Audited receipt/terminal/coverage data and selected decisive frames are readable here. Full original terminal archives remain private at the verified paths/hashes in archive-index.json; visual-retention.json maps every original image, including those kept only in those archives. Exact effective profile sources and checksums are in profiles/. Original evidence and test source were preserved.\n'
(root/'README.md').write_text(text)
print(json.dumps({k:record[k] for k in ('totalCells','passed','failed','notRun')}))
