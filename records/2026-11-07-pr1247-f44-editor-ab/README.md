# PR #1247 Fedora GNOME editor A/B

**Verdict: unclear for SDK causality.** The candidate editor cell is intermittent; current nightly passed both observed rows. These results establish neither a consistent candidate-only failure nor the same failing cell on current nightly. Do not label this an SDK regression or an independently reproduced nightly editor flake.

Four full local Tier 1 rows ran on f44 (192.168.68.70), alternating candidate, current nightly, candidate, current nightly. Each used a fresh overlay of the exact configured Fedora GNOME golden and frozen driver `191f2f41f5ba649e4f471ec100dd7a4ffed1c358`, unchanged recipes and retry policy. Live S3 and Proton were skipped by request: whole-row counts below are the **11 local cells**, not 13 provider-inclusive cells.

| Run | Package | Local cells passed | Terminal Edit cell | Individual Edit attempts |
| --- | --- | --- | --- | --- |
| c1 | candidate | 10/11 | FAIL | 0 pass / 2 fail |
| n1b | nightly | 11/11 | PASS | 1 pass / 0 fail |
| c2b | candidate | 11/11 | PASS | 1 pass / 1 fail |
| n2 | nightly | 11/11 | PASS | 1 pass / 0 fail |

Candidate: **21/22 terminal local cells passed**, Edit 1 pass / 1 fail by row, **1 pass / 3 failures** by attempt. Nightly: **22/22**, Edit **2 passes / 0 failures** by row and attempt. Candidate c2b Auto-copy's first attempt was infrastructure-not-run (synthetic QtKeychain collection unavailable); its automatic retry passed. This is separate from the three functional Edit failures.

## Exact identities and method

- Candidate staged RPM: `putgd-26.1107.4038~dev+g6c1d28296001-1.fc44.x86_64.rpm`, SHA-256 `843707167f28708c65c63ec82e3e54d5caacdd0c65e21b85c865205476733851`, CI 42393591166; tested merge `6c1d282960010c87388ae2d2ea11b6ee45f98893`, PR head `e84d5b08b5107b238002bfb8316d6116a3c3003c`.
- Current-nightly staged RPM: `putgd-26.1107.4036~dev+g369f001b66a9-1.fc44.x86_64.rpm`, SHA-256 `c401e30e4ddd066100fcf6e51c3b4e2e9ca8b97943ea3e67da9d70edf9920423`, CI 42392437798; source `369f001b66a939077ea683f91b735c5730d53de9`.
- Both digests were verified before installation. No packages or catalogs were downloaded from GitHub by this worker, no GitHub token was read or handled, and no host package operation was performed. Nightly's exact-build 447-file UI catalog was staged by the coordinator. Candidate used the original staged catalog. Editor reference PNG and control sidecar are byte-identical between the catalogs.
- Order: Region, Window/desktop, Recording, Edit, Link/browser, History delete, Auto-copy, Upload clipboard, Copy image, Survives exit, Right-click upload. Every row used this complete order; Edit did not run alone.
- Separate short private session paths were checked with the socket-path diagnostic before every app launch. All VMs ran on f44 with KVM and remained on its loopback VNC 5946, forwarded to workstation wall port 6110. Each row has saved synthetic visual results, exact package/build/guest identities and terminal audited receipts.
- `n1` and `c2` were preflight-only failures while the previous VM's reserved port was not yet reusable. No VM/app started in those attempts. Logs are retained; fresh retries were named `n1b` and `c2b`. The wrapper was corrected to wait for both SSH and VNC ports without changing the frozen harness.
- A passive observer sampled compositor windows every three seconds during c1’s second attempt and the n1b, c2b and n2 Edit attempts. It sent no input or activation. Its sampling can perturb timing slightly; c1’s first attempt had no observer. The unchanged driver did all functional gestures and assertions.

## What put Settings in front

All three candidate failures report **arrow tool selected by real input** and their frames show Settings covering the editor. The immediately preceding cell is Recording, and Recording passed in all four rows. Its cleanup is followed by a separate private driver resident for Edit. The c2b observer begins with **no mapped windows**, then records the editor and a newly created Settings helper; this is not evidence of a Recording Settings window being left open.

The **passing candidate retry also maps Settings**: at epoch 1794077206.865754 the editor PID 36538 is focused; at 1794077210.2396557 a new Settings helper PID 36908 is focused while the editor remains mapped; by 1794077213.659757 the editor has regained focus and the four marks/upload succeed. In the first nightly pass the new Settings helper PID 30737 maps after editor PID 30441 while the editor retains focus. See the observer JSONL files and before/result/failure frames.

The unchanged resident source has a concrete matching path: `src/main.cpp` starts `startupRecovery` for a background resident without a tray and calls `showInitialView()` after **10000 ms** if the tray is still absent; that opens Settings. `editor.open` is not the UI activation handler which stops that timer. The fixture restarts a private resident during its own setup (`fixtures/profile.py` / `Scope.restart`); the resulting timer can overlap the first editor input. The late Settings mapping and changing focus are consistent with this path. This is a source-and-timeline inference, not an instrumented timer trace.

The coordinator identified prior [#1115](https://github.com/patrick-hudson/put.gd-desktop/issues/1115) evidence of Settings covering a Fedora GNOME recording test independently of this bump. It matches the visible symptom and supports an older focus/timing problem; it does **not** prove that current nightly fails this exact editor cell.

The source comparison from current nightly to the candidate PR head changes only `cmake/Dependencies.cmake` and `cmake/dependency-lock.json` (SDK 1.11.921 to 1.11.924). No editor, helper, startup timer or input-driver code changes. The arrow assertion occurs before editor submit/upload, outside the SDK upload worker's path. There is no identified direct SDK-to-focus path; an indirect timing/layout-of-process effect has not been ruled out. The observed 1/2 versus 2/2 row outcomes are too few to attribute a rate change to the SDK.

## Frames and cleanup

- c1/edit_upload-1: failed — [decisive frame](c1/edit_upload-1/frames/outcomes.edit_upload/02-failure-before-cleanup.png), [receipt](c1/edit_upload-1/receipt.json).
- c1/edit_upload-2: failed — [decisive frame](c1/edit_upload-2/frames/outcomes.edit_upload/02-failure-before-cleanup.png), [receipt](c1/edit_upload-2/receipt.json).
- n1b/edit_upload-1: passed — [decisive frame](n1b/edit_upload-1/frames/outcomes.edit_upload/02-four-marks-before-upload.png), [receipt](n1b/edit_upload-1/receipt.json).
- c2b/edit_upload-1: failed — [decisive frame](c2b/edit_upload-1/frames/outcomes.edit_upload/02-failure-before-cleanup.png), [receipt](c2b/edit_upload-1/receipt.json).
- c2b/edit_upload-2: passed — [decisive frame](c2b/edit_upload-2/frames/outcomes.edit_upload/02-four-marks-before-upload.png), [receipt](c2b/edit_upload-2/receipt.json).
- n2/edit_upload-1: passed — [decisive frame](n2/edit_upload-1/frames/outcomes.edit_upload/02-four-marks-before-upload.png), [receipt](n2/edit_upload-1/receipt.json).

All four overlays were exported and verified on f44, then retired through guarded cleanup. Each run's `retirement.json`, completion and evidence manifest is retained. Goldens were not modified or deleted. Only the owned SSH tunnel and wall tile were removed. Desktop lock release and cleanup receipts are included. The shared workstation checkout branch and commits were left untouched, and pre-existing untracked work was preserved. No merge was performed.
