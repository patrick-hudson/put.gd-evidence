# Proton chosen-connection desktop acceptance round 2 (#1414)

Back-to-back used one helper on every completed host. No black or single-colour capture was found. This is not clean acceptance: Kubuntu sequential screenshot 2 ended with unknown sharing status, its nightly 1 MiB control failed, and Debian has instrumentation-related coverage gaps.

Exact requested head: `ec6e6a136807cb24ba70e1fa93d2bf0954e0f330`. CI run [43156480415](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43156480415). Latest published nightly control: `26.1111.4633-nightly` (published 2026-11-11 10:45 UTC). No compilation, product edits, merge or approval.

| Host | Build | Original cases passed | Helpers left |
| --- | --- | --- | --- |
| d69 | 26.1112.4655-dev+g201f0693f175 | 13/15 | [] |
| k72 | 26.1112.4655-dev+g201f0693f175 | 15/15 | [] |
| m74 | 26.1112.4655-dev+g201f0693f175 | 15/15 | [] |
| f44 | 26.1112.4655-dev+g201f0693f175 | 9/15 | [] |

Times in seconds, **2026-11-10 baseline / round 1 / round 2**. Delayed captures exclude the countdown. Back-to-back shares an invocation origin.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| file-64k | 5.39 / 3.74 / 3.9 | 5.56 / 4.01 / 6.22 | 5.3 / 5.95 / 6.66 | 4.97 / 4.92 / 4.83 |
| file-1m | 6.59 / 10.09 / 5.53 | 7.84 / 5.27 / 5.87 | 11.74 / 5.4 / 5.46 | 13.9 / 5.5 / 6.06 |
| file-8m | 9.26 / 13.0 / 8.152† | 7.95 / 15.95 / 8.88 | 10.7 / 14.57 / 8.53 | 8.42 / 12.03 / 8.37 |
| batch-3 | 12.45 / 7.99 / 8.1 | 16.89 / 8.25 / 7.7 | 11.29 / 8.02 / 8.07 | 10.33 / 8.41 / 8.27 |
| text-small | 4.03 / 2.83 / 2.71 | 3.78 / 2.84 / 3.06 | 5.67 / 3.06 / 3.06 | 4.63 / 3.18 / 3.16 |
| back-to-back | 5.9, 11.41 / 5.19, 8.25 / 4.96, 6.97 | 9.02, 12.7 / 4.77, 7.99 / 5.28, 7.28 | 5.52, 9.16 / 7.64, 7.66 / 5.38, 7.79 | 8.82, 12.21 / 4.91, 8.96 / 8.28, 10.49 |
| desktop-now | 7.22 / 3.59 / 4.44 | 6.76 / 4.42 / 4.49 | 8.88 / 4.5 / 4.71 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3 | 4.91 / 3.76 / 3.95 | 4.5 / 3.77 / 3.69 | 5.27 / 4.25 / 4.89 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3-again | 7.27 / 3.76 / 3.92 | 6.08 / 5.6 / 5.21 | 8.27 / 4.33 / 4.91 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| monitor-delay3 | 6.59 / 3.62 / 3.96 | 4.69 / 3.72 / 5.43 | 7.79 / 4.51 / 4.98 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| cancel-countdown | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| after-cancel | 3.95 / 3.01 / 3.1 | 3.81 / 3.18 / 3.26 | 5.06 / 3.1 / 3.31 | 3.68 / 3.27 / 3.82 |
| history-picture | 5.69 / 4.46 / 4.51 | 8.78 / 4.48 / 4.39 | 5.79 / 4.94 / 5.3 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| link-answers | HTTP 200 / HTTP 200 / not run | HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 |
| revoke-all | 15 revoked; 2.54–4.85/link / 15 revoked; 2.21–2.86/link / 15 revoked; 2.20–2.79/link | 15 revoked; 2.49–4.82/link / 15 revoked; 2.26–2.92/link / 15 revoked; 2.27–2.63/link | 15 revoked; 2.67–4.33/link / 15 revoked; 2.24–2.46/link / 15 revoked; 2.24–2.46/link | 10 revoked; 2.50–3.82/link / 10 revoked; 2.34–2.93/link / 10 revoked; 2.36–3.04/link |

Distinct helpers during back-to-back are sampled every 10 ms using user-owned `/proc` comm beginning `putgd-proton-ru`, distinct `(PID, kernel startTicks)` pairs, through helper exit. This is a sampled inventory, not an exec audit. Expected count: one.

| Host | Helper count | PID/startTicks |
| --- | --- | --- |
| d69 | 1 | [{'pid': 3914211, 'startTicks': '224549185'}] |
| k72 | 1 | [{'pid': 3308617, 'startTicks': '114055178'}] |
| m74 | 1 | [{'pid': 505742, 'startTicks': '185794600'}] |
| f44 | 1 | [{'pid': 3919290, 'startTicks': '91271516'}] |

Sequential screenshots: upload stage is first observed sharing minus first observed uploading; total is invocation to terminal state.

| Host | Capture 1 stage / total | Capture 2 stage / total | Capture 3 stage / total |
| --- | --- | --- | --- |
| d69 | 2.11 / 4.34 | 1.94 / 4.4 | 2.04 / 4.33 |
| k72 | 3.71 / 6.1 | 2.01 / 3.87 (partial) | 2.2 / 4.57 |
| m74 | 2.19 / 4.54 | 2.18 / 4.51 | 2.22 / 4.78 |
| f44 | unobserved / not run | unobserved / not run | unobserved / not run |

Same-hour control, one sample per build/case. PR 1 MiB and 8 MiB ran first; nightly then ran immediately with its own new private profile, under the same locks. PR resident stopped during the control and restarted afterwards. Network variance and order effects remain.

| Host | Case | PR stage / total | Nightly stage / total | PR minus nightly total |
| --- | --- | --- | --- | --- |
| d69 | file-1m | unobserved / 5.53 | 3.64 / 8.55 | -3.02 |
| d69 | file-8m | unobserved / 8.152† | 11.62 / 15.3 | not comparable |
| k72 | file-1m | 2.83 / 5.87 | unobserved / 0.85 (failed) | not comparable |
| k72 | file-8m | 5.52 / 8.88 | 5.3 / 9.21 | -0.33 |
| m74 | file-1m | 2.72 / 5.46 | 3.52 / 8.26 | -2.8 |
| m74 | file-8m | 5.47 / 8.53 | 4.36 / 7.64 | 0.89 |
| f44 | file-1m | 2.83 / 6.06 | 2.66 / 6.91 | -0.85 |
| f44 | file-8m | 5.27 / 8.37 | 4.84 / 8.33 | 0.04 |

Capture checks: every locally saved PNG has byte size, dimensions, RGB extrema and black/single-colour flags in capture-checks.json. All-black or single-colour captures fail visual acceptance even if the unchanged harness reports successful upload/share. Display-state observations are read-only and preserve errors/unavailable interfaces.

| Host | PNGs checked | Black | Single-colour |
| --- | --- | --- | --- |
| d69 | 8 | 0 | 0 |
| k72 | 8 | 0 | 0 |
| m74 | 8 | 0 | 0 |
| f44 | 0 | 0 | 0 |

Failures and oddities (all attempts retained; no pass-seeking retry):

- d69 PR: `file-8m` state `completed`, error ``, 8.152 s.
- d69 PR: `link-answers` state `not_run`, error ``, None s.
- k72 PR: `sequential-desktop-2` state `partial`, error ``, 3.87 s.
- k72 nightly: `file-1m` state `partial`, error ``, 0.85 s.
- f44 PR: `desktop-now` state `failed`, error `gnome_extension_missing`, 0.15 s.
- f44 PR: `desktop-delay3` state `failed`, error `gnome_extension_missing`, 0.13 s.
- f44 PR: `desktop-delay3-again` state `failed`, error `gnome_extension_missing`, 0.12 s.
- f44 PR: `monitor-delay3` state `failed`, error `gnome_extension_missing`, 0.13 s.
- f44 PR: `cancel-countdown` state `failed`, error `gnome_extension_missing`, 0.15 s.
- f44 PR: `history-picture` state `failed`, error `gnome_extension_missing`, 0.13 s.

Added instrumentation: `round2.py` imports the byte-identical published `proton_accept.py` from c0a3ff1c and wraps calls to add capture pixel checks, display-state snapshots, an immediate extra desktop capture if black, and the nightly control after the PR large-file cases. `drive.py` supplies new scratch paths, downloads/copies/extracts exact packages, holds and heartbeats both locks, collects outputs and releases after cleanup. The published `run_accept.sh` is retained byte-identical; its hard-coded round-1 paths prevent executing it directly without touching round-1 scratch, so drive.py performs its orchestration. No original case bodies or process-counting logic changed.

Not covered: Aurora, GNOME captures with missing extension, real pointer region/window selection, memory gates, package installation audits, expired-token or transport fault injection. These are timing samples, not a statistical regression claim. No display change, logout, extension workaround or keyring inspection. Prior scratch, including d69 pf2, untouched. Raw logs/copies remain private under /tmp/pr1414r2 and ~/work/pecr2.

Debian interruption and continuation: `d69/run.log` ends with `FileExistsError: ... pr/resident.log` after the nightly control. The unchanged App.start opens its log with mode `x`; the additive adapter failed to rotate it before restarting. `round2-first-attempt.py` preserves that adapter. `round2.py` fixes only the restart log handling and adds a durable per-operation observation journal before control execution. `resume.py` reopened the same private profile and ran only unrun cases, followed by the three screenshots and revocation. No failed product case was retried. Its existing-work directory allowance is limited to that exact run/profile. First-attempt logs, interrupted results and continuation results are all preserved. The continuation's raw summary says 15/15 because it includes its added captures; it is not the original 15-case count.

Debian's first two PASS totals (3.90 and 5.53 s) survive in the log. The 8 MiB operation completed, but its CLI outcome was lost before the case recorder returned. † The 8.152 s value is the app log interval `04:59:01.252 Operation accepted` to `04:59:09.404 Operation finished`, not invocation-to-terminal CLI time. Its upload-stage observation is unavailable. `combined-results.json` is an explicit report composite, retaining that case as not fully evidenced; raw `results.json` remains the continuation output. `link-answers` was not run on Debian. Original-case count: 13 fully evidenced passes, one app-log-only completion, one unrun. No clean 15/15 acceptance is claimed.

Kubuntu added-case failure: `FAIL sequential-desktop-2: partial in 3.87 s`; item `uploadStatus=uploaded`, `shareStatus=unknown`, `link=false`. `05:05:32.579 Sharing finished` has `status=unknown`; `05:05:32.631 Operation finished` has `state=partial`. No retry. Later revoke-additions revoked two links and final history has zero available links; the unknown item required separate reconciliation; this later cleanup does not relabel the failure. The upload-stage interval 2.01 s and 3.87 s total in the screenshot table are failed-case measurements.

Kubuntu nightly control failure: `FAIL file-1m partial 0.85 s`; item error `keychain_unavailable`, upload failed, share not requested. `05:03:27.448 Name check failed` records `The private keychain is unavailable.`; `05:03:27.482 Operation finished` records `state=partial`, durationMs=813. It was not retried and is not a speed comparison. All other nightly control uploads passed.

Read-only pre-capture state: d69 was active/unlocked, Wayland on VT1, HDMI-A-1 enabled/connected at 1920x1080. Its XWayland server exposed no DPMS extension; that is not proof of compositor power state. k72 was active/unlocked, Wayland on VT3, HDMI-A-1 DRM DPMS On (other disconnected outputs Off), with no XWayland DPMS extension. m74 was active/unlocked, X11 on VT7, HDMI-A-1 DRM DPMS On, X11 DPMS disabled. Window stacking, active window IDs and PID/comm inventories are retained in display-state.json; read-only inventories cannot reliably establish which session owns every window. The first captures show the desktop background and this run's notifications, and History frames show this run's app. No unlock, logout, display-power change or desktop change was performed. Since no black image occurred, no immediate diagnostic repeat was triggered. Round 1 had no contemporaneous display-state record; this round does not establish its black-image cause.

Warnings are preserved in per-host events.jsonl and driver logs. d69 app logs had no warning/error lines. k72 PR logged two portal app-ID registration warnings (one per resident start), plus the sharing/partial warnings above; nightly logged one portal warning plus the keychain/partial warnings. m74 PR logged two portal app-ID warnings and one GStreamer external-plugin-loader warning; nightly logged one of each. Recording was not tested. d69's History screenshot also shows triangular clipping through one desktop notification; its cause was not investigated. These warnings and visual oddities were not hidden or used as reasons to repeat a test.

The retained `run_accept.sh` is byte-identical to c0a3ff1c but was **not executed**: its fixed `/tmp/p1414-final` and `~/work/pf65` paths would reuse prior scratch. `drive.py` performs its orchestration with fresh `~/work/pecr2` instead. Thus the acceptance case bodies and helper-counting code were reused exactly; the shell orchestration was replaced. This is a deviation from the instruction to run both original scripts exactly. The original shell script, original Python script, both adapter revisions and actual continuation script are included for review.

The driver also initially treated the lock tool's non-final release exit 1 as fatal on d69; the manual verified-clean release succeeded at 05:02:38 UTC, after confirming no run helpers/resident remained. Other hosts use the corrected release handling. The first checksum command expected the single-artifact download in a subdirectory and reported no matching AppImage; the corrected checksum inventory covers all six actual downloaded packages. No app was launched from an unchecked alternative build. The package build-info files match merge 201f0693f175, second parent ec6e6a136.

The earlier cancelled round's `/tmp/pr1414-r2` scratch was found and preserved. No `~/work/p9r2` run directory or held lock from it was found on any of the four hosts. No lock was broken. The initial Mint lock and later Fedora lock belonged to scroll-fix7-1398, not the cancelled attempt. The refused Fedora acquisition is retained; no Fedora app ran during it. /tmp/pg1414-accept, /tmp/pa1414 and d69 ~/work/pf2 were left alone.

Kubuntu unknown-share cleanup at 05:13 UTC acquired both locks again, inspected capabilities, and used history.inspectLink on exact history ID 2f12a198-cd73-4ca6-92b4-8bfd1e3e5bb8. Share operation 20e9ecda-1cf0-437b-9006-c02717b6e6b9 completed with status private. No revoke mutation was needed for that row; remainingLinks=0, helpersLeft=[]. Both locks released verified-clean at 05:13:55–56 UTC. The private outcome resolves cleanup uncertainty without relabeling the original partial case.

Timing instrumentation limit: the first capture records display state inside the action.invoke wrapper, after the unchanged case starts its monotonic timer. Its reported total therefore includes those read-only probes. The operation outcome timer is finalized before pixel analysis; pixel scanning is outside its reported total. Subsequent captures do not repeat display-state probes unless black. The nightly controls add a resident restart before the remaining PR cases, so this round is not the same uninterrupted resident sequence as round 1.

Timing sources: [2026-11-10 baseline](https://github.com/patrick-hudson/put.gd-evidence/tree/c0a3ff1cb04bc6dd96a7242dcd1094775fcc58e5/records/2026-11-10-proton-upload-speed-acceptance) and [round 1](https://github.com/patrick-hudson/put.gd-evidence/tree/c0a3ff1cb04bc6dd96a7242dcd1094775fcc58e5/records/2026-11-12-proton-chosen-connection-acceptance). Their per-host results.json supply the comparison table; clipboard-unavailable outcomes on successful cases are not substituted for elapsed times.

Fedora completed on the restored GNOME Wayland desktop: six expected capture failures, all gnome_extension_missing, at 0.15/0.13/0.12/0.13/0.15/0.13 s for desktop-now, desktop-delay3, desktop-delay3-again, monitor-delay3, cancel-countdown, history-picture. No PNGs, so no black-image statement can be made about GNOME captures. The three extra captures were not attempted, following the frozen script. PR revoked all 10 links; nightly revoked both links; final available-link count zero. No helper remained. Verified-clean release was 05:35:50–51 UTC. All locks of this run are released; final d69 desktop status belongs to scroll-fix7-1398 and was left alone.

Fedora warnings: PR resident logs contain two tray ServiceUnknown, four portal app-ID registration, two Fontconfig FcInit, two GStreamer external-plugin-loader, five Wayland text-input warnings and eight Automatic copy finished warnings with clipboard_unavailable. Nightly logs contain one tray, two portal, one Fontconfig, one GStreamer, three text-input and two automatic-copy warnings. Log excerpts include `The name is not activatable`, `Connection already associated with an application ID`, `using without calling FcInit()`, `External plugin loader failed`, and `Trying to disable ... but 0x0 is focused`. These did not make successful upload/share outcomes pass by suppression; all warnings are retained in events.jsonl. Capture failures are expected untestable cases, not accepted screenshots.

Measured conclusion: one helper on every host, versus two in round 1. Zero black/single-colour images among 24 produced PNGs. All three comparable 8 MiB PR upload-stage samples were slower than nightly: k72 +0.22 s, m74 +1.11 s, f44 +0.43 s. Total times were mixed: k72 -0.33 s, m74 +0.89 s, f44 +0.04 s. Debian's 8 MiB CLI comparison is unavailable. Successful 1 MiB totals were lower on PR; Kubuntu's failed nightly sample is not comparable. These are single samples in fixed PR-first order, not proof of a sustained regression or its resolution.

Fedora pre-capture state: active/unlocked Wayland session on VT2; HDMI-A-1 DRM DPMS On. Read-only window/process inventory retained; no screenshot was available to establish visual window coverage there.
