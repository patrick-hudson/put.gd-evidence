from pathlib import Path
import json,shlex
root=Path(__file__).resolve().parents[1]
p=root/'README.md';s=p.read_text();s=s.replace('Follow-up test of merged PR #1396.', '**Result: Fedora manual coverage and Mint linked-selection coverage are complete within the scopes below; the History recipe campaign is incomplete and has failures. No overall desktop/driver acceptance is claimed.**\n\nFollow-up test of merged PR #1396.')
s=s.replace('Pending final receipts.', '''**Incomplete; not a suite pass.** Native runs were stopped gracefully after the unchanged runner produced whole-desktop images and chooser listings of the home directory, contrary to this run's app-window-only picture rule. Those originals are retained privately outside this publishable record at `/home/patrick/work/put.gd-history-ui/work/accept/2026-11-10-history-page-acceptance-2-private-driver/driver/` and in the original `/tmp/hp2*out*` output directories. They are not published. The evidence review caught this after the driver's first frames were collected on the workstation; that collection was broader than the screenshot rule. No credential was exposed. Continuing the unchanged runner would repeat it, and changing the runner/profiles was prohibited.

Published `driver/` contents preserve the original receipts, command metadata and terminal manifests, plus only verified app-window crops. Full-frame references in those receipts intentionally resolve only in the private originals; `driver-publication-index.json` identifies the published subset. The selected-state failure crop `history-multi-select-failure.png` was generated **on k72** by uniquely matching the driver's owned-window header to its original after-frame, with exact crop provenance in `k72-failure-crop.json`. No UI content was repainted or modified.

Two native campaigns were resumed after pausing the initial broad requests. Guest-only fixtures were not bypassed. The recipe inventory includes other shell/capture/launcher routines from `history.py`; unchanged shell interactions and acquisition commands are outside this History-control follow-up and were not run. `history.save_diagnostics`, `history.retry_upload`, `history.active_banner`, `history.cancel_all`, `history.delete_remote`, `history.clear_history`, `history.list_gestures`, `links.history_*`, and the three requested `outcomes.*` routines require guest-only fixture paths on this native placement and/or were never reached before the safe stop; none is a pass. Live S3/Proton outcome recipes were out of scope. No guest was booted; native placement was used and the documented guest-only restrictions were reported rather than bypassed.''')
s=s.replace('m74/k72: pending final recipe/package cleanup receipts.', '''m74: only putgd was installed and later removed; its residual dpkg configuration record identifies the tested version, as in run 1. The runner restored the original image clipboard on both of its campaigns, stopped its notification/probe children, quit residents and removed `/tmp/hp2mr` and `/tmp/hp2ms`. Release cleanup had no new leftovers; lease released **2026-11-10T21:10:57Z**.

k72: putgd, python3-pyatspi and libatk-adaptor were added and all three removed (no autoremove, upgrades or desktop package changes). putgd and libatk-adaptor retain dpkg residual configuration records; python3-pyatspi is absent. The own transient `history-p2-input` unit and exact workstation tunnel PID 3628944 were stopped. The two admitted driver campaigns restored the empty original Wayland clipboard, stopped helpers and removed `/tmp/hp2ks` and `/tmp/hp2kt`; refused attempts created no resident profile. Release cleanup had no new leftovers; lease released **2026-11-10T21:10:58Z**.

The complete release checks, successful release receipts, final package states and `final-locks.json` are included. Downloaded packages, helper scripts and safe/private evidence remain under each host's `~/putgd-lab/h1396-ci/`. The checkout is clean; the runner's default generated coverage exports were moved by exact filenames from the source tree into `generated-coverage/`, and resumed runs used explicit scratch coverage paths.''')
s=s.replace('Mint 22.3 · Cinnamon / X11','Mint 22.3 · Cinnamon 6.6.9 / X11')
s+='\nAll safe driver images from k72 are captioned **k72 · Kubuntu 26.04 · Plasma 6.6.6 / Wayland · Qt 6.10.2 · CI DEB 26.1110.4614-dev+g8662a5fd13b3**; safe m74 driver images use the Mint caption above. The static `catalog/` images are CI synthetic UI renders, not desktop evidence.\n'
# Exact command aliases.
commands=[]
for file in ('driver-running-commands.json','driver-commands-rest.json'):
 for x in json.loads((root/file).read_text()):
  commands.append(x['argv'])
s+='\n## Exact driver commands and recipe outcomes\n\nAll commands below ran from `/home/patrick/work/put.gd-history-ui`. C1/C2 requested broad History-control coverage; C3/C4 resumed native-supported recipes after clipboard restoration and private-profile cleanup. C1/C2 were gracefully stopped to schedule check 7 and avoid repeating guest-only fixtures; C3/C4 were stopped for the observed screenshot-policy conflict. Interrupted or unreached work is **not run**, not a product failure.\n'
for i,a in enumerate(commands,1):s+='\n**C%d**\n\n```sh\n%s\n```\n'%(i,shlex.join(a))
rows={};runmap={'hp2mout':'C1','hp2kout4':'C2','hp2mout2':'C3','hp2kout5':'C4'}
for run,command in runmap.items():
 r=json.loads((root/'driver'/run/'receipt.json').read_text())
 for x in r['interactions']:
  key=(x['recipe'],x['host'])
  if key in rows:continue
  status={'passed':'pass','failed':'fail','blocked':'not run'}[x['functional']]
  note=x.get('note','')
  if 'runner interrupted' in note:status='not run'
  rows[key]=(status,command,note)
selected=[]
for a in commands:
 for n in a[a.index('--recipes')+1].split(','):
  from tools.lab.surface_driver.run import discover
  for r in discover(n):
   if r.name not in selected:selected.append(r.name)
s+='\n| Recipe | m74 | k72 | Command / exact failure or block |\n| --- | --- | --- | --- |\n'
for name in selected:
 vals=[];notes=[]
 for host in ('m74','k72'):
  value=rows.get((name,host))
  if value:
   status,command,note=value;vals.append(status+' ('+command+')')
   if status!='pass':notes.append(host+': '+note)
  else:vals.append('not run');notes.append(host+': unreached before campaign stopped; no result claimed')
 s+='| `'+name+'` | '+' | '.join(vals)+' | '+'; '.join(notes).replace('|','\\|').replace('\n',' ')+' |\n'
s+='\n## Findings and practical limits\n\n| Finding | Host / reproduce | Expected / actual | Screenshot / evidence |\n| --- | --- | --- | --- |\n'
s+='| Driver multi-select expects the old visible summary | k72, C4 `history.multi_select`: two real local operations, close details, focus list, Home + Shift+Down | Exact two IDs and aggregate bytes passed; `_size(ctx, bytes, "Total size")` then timed out. The refined header visibly shows `2 selected`, `2.7 KB · 2 local only`, with details closed. This is an incompatible recipe expectation; the manual 3-link header test passed. | `history-multi-select-failure.png`; `driver/hp2kout5/receipt.json` |\n'
s+='| Driver search / preview / receipt deadlines | m74 C1 search and preview; k72 C2 search; both C3/C4 receipt-details | Expected recipe completion within its unchanged 120 s deadline; actual `recipe deadline exceeded: history.search`, `.preview`, or `.receipt_details`. No pre-build comparison or specific missing control was established; these are failed recipes, not proven product regressions. | Safe search before-crops under `driver/hp2mout/frames/history.search/01-before.png` and `driver/hp2kout4/frames/history.search/01-before.png`; full failure originals private |\n'
s+='| Save-copy chooser recipe failures | m74 C1 portal/fallback; k72 C2 portal | Mint portal changed to fallback with `org.freedesktop.DBus.Error.NoReply` (not run). Mint fallback failed assertion `resident received the exact typed path`. Kubuntu portal timed out waiting for `desktop chooser top-level is accessible and drawn`; its fallback recipe passed. Attribution to #1396 is not established. | Driver receipt JSONs; original chooser pictures withheld from publication because they show the home listing |\n'
s+='| Native probe transport lost its reply | m74 C3 multi-select and paging admission | Expected a native probe reply within 15 s; actual reply outstanding and further input withheld, with instruction to start a new run. Both recipes are not run. Cleanup and clipboard restoration subsequently passed. | `driver/hp2mout2/receipt.json`, terminal manifest |\n'
s+='| Driver picture scope exceeds this task rule | both native campaigns | Expected put.gd-only pictures; actual unchanged runner also saved whole-desktop before/after frames and home-directory chooser contents. Runs were stopped, originals retained privately, and only safe crops are published. This blocks completing remaining recipes unchanged under the stated picture restriction. | `driver-publication-index.json`; private original paths above; no broad frame published |\n'
s+='\nNo new product defect was established by the successful manual walkthroughs. Run 1\'s Mint toolbar-spacing observation was not reproduced in the fresh linked-selection screenshot; no fix, issue or regression attribution is asserted. The exact-build nightly History recipes still require a corrected/safe campaign and guest-only coverage before acceptance.\n'
p.write_text(s)
(root/'recipe-results.json').write_text(json.dumps([{'recipe':k[0],'host':k[1],'result':v[0],'command':v[1],'note':v[2]} for k,v in rows.items()],indent=2))
