# PR 1520 scrolling-pointer desktop acceptance — 2026-11-14

This is an independent desktop acceptance round for [PR #1520](https://github.com/patrick-hudson/put.gd-desktop/pull/1520), part of [#1514](https://github.com/patrick-hudson/put.gd-desktop/issues/1514). No product changes, builds, subagents, PR comments or merge were performed. **Acceptance fails.** Hyprland R3 is a demonstrated regression against the published nightly. Other target failures and baseline comparisons are listed separately below.

## Builds and method

Candidate commit `4630ddcb0bdf14a2603c985fe1498449b748a712`, tree `9513f33d6ffdb474b4e8937a7da83bd840886574`. Only completed, successful manual CI run [43581469746](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43581469746) artifacts were used. `ci-run.json`, `ci-watch.log` and `packages.json` retain status, identity and package hashes. GNOME used the Fedora 44 RPM and its packaged, loaded extension 23. Other desktops used the official AppImage, extracted in private test directories. On each desktop `a/build.json` is the actual running `diagnostics` result's `build` object, with the expected tree and `dirty: false`.

Before/control: published GitHub release `v26.1113.4757-nightly`, commit `466449a4c69a07a1997668d1b70d637abac76a16`, tree `4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3` (full values in `b/build.json`/diagnostics). GNOME baseline used its RPM and packaged, loaded extension 22; other baselines used the published AppImage. All test actions saved locally only, with no upload or copied link. Public Wikipedia Linux was opened by this test. `drivers/page.html` was used for the deterministic pause/resume and top-return comparisons.

Author's drivers were fetched from evidence record `2026-11-14-scroll-pointer-release-1514` and adapted here. Stuck-mouse motion came from a real relative `/dev/uinput` mouse at roughly 600 px/s, 6 px per 10 ms, with flat acceleration. VNC was used for screenshots and occasional setup clicks, never the qualifying repeated relative gesture. Each try had randomized pre-start jitter; random-series motion began 1–6 seconds after capture start. `startMs` records actual timing. Hyprland used one local relative initial-centering displacement based on `hyprctl cursorpos`; Budgie used one local absolute-tablet centering event, then the same relative-only path and first click. The tablet is not reasserted during the gesture. Logs count put.gd pointer-move injections after first motion, and pause latency is taken from the helper's clock relative to the injector timestamp (sub-millisecond timestamp ordering noise can produce a small negative value; retained raw).

Physical tests used actual Wayland sessions. GNOME: f44, Fedora 44, GNOME/Mutter 50.6; leases `scroll1520-gnome` 09:39:36–09:46:48 UTC and `scroll1520-gnome-pr` 10:14:47–10:33:40. Plasma: aurora-amd, Fedora 45, Plasma/KWin 6.8.2; lease `scroll1520-plasma` 09:51:58–10:14:37. Every acquire was checked; only one physical lease was held at once. Omarchy/Hyprland 0.56.2 and Fedora 45 Budgie 10.10.3/labwc 0.20.2 used fresh f44 KVM overlays, one output at 1920×1080, with their displays exposed on the live wall. No d69 build work was disturbed. See retirement receipts for exact guest identities.

Private config/data/cache/state directories contained no credentials or profiles for upload. Resolved socket lengths were checked; GNOME's initially intended private runtime was not adopted by its native session, a recorded setup deviation (actual session socket 33 bytes); other test sockets were below 107 bytes, Budgie's session socket 43 bytes. The original unsuccessful commands, screenshot transport failures, invalid trials and corrected attempts remain in logs and `SETUP-NOTES.txt`; excluded trials are not counted below.

## Candidate table

PASS is evidence for that row on this exact build, FAIL is a missed requested target, NOT RUN has its explicit reason. A failed target is not automatically a PR regression: the nightly comparison determines that.

| Row | Test | GNOME | Hyprland | Budgie/labwc | Plasma 6.8.2 |
|---|---|---|---|---|---|
| R1 | Build identity | PASS | PASS | PASS | PASS |
| R2 | Pointer rest/watch helper log | PASS | PASS | PASS | PASS |
| R3 | Two whole untouched captures | PASS | FAIL (C) | PASS | PASS |
| R4 | Bar position, text and fixed size | PASS | PASS | PASS | PASS |
| R5 | Relative-mouse fixed/random tries | FAIL (A) | FAIL (D) | FAIL (F) | FAIL (E) |
| R6 | Pointer/API pause and resume; 64-row comparison | PASS | PASS | PASS | PASS |
| R7 | Other-window clicks/keys while paused; no injections | PASS | PASS | PASS | PASS |
| R8 | Stop keeps; Cancel leaves no file/history | PASS | PASS | PASS | PASS |
| R9 | Stop while returning to top | PASS | PASS | PASS | PASS |
| R10 | Near-full-screen region | FAIL (B) | PASS | PASS | PASS |
| R11 | Hyprland two monitors | NOT RUN: Hyprland-only | NOT RUN: one-output profile | NOT RUN: Hyprland-only | NOT RUN: Hyprland-only |
| R12 | Cleanup and normal input | PASS | PASS | PASS | PASS |

## Published-nightly before column

| Row | GNOME before | Hyprland before | Budgie before | Plasma before |
|---|---|---|---|---|
| R1 | PASS | PASS | PASS | PASS |
| R2 | NOT RUN: new logging contract | same | same | same |
| R3 | PASS, two complete | PASS, four matched controls | PASS, two complete | PASS, two complete |
| R4 | NOT RUN independently | same | same | same |
| R5 | FAIL, 0/10 | FAIL, 0/10 | FAIL, 0/10 | FAIL, 0/10 |
| R6 | NOT RUN: pause/resume absent | same | same | same |
| R7 | NOT RUN: pause absent | same | same | same |
| R8 | NOT RUN: pause absent | same | same | same |
| R9 | NOT RUN independently | same | same | same |
| R10 | FAIL, same hidden bar/no pause | NOT RUN independently | same | same |
| R11 | NOT RUN: Hyprland only | NOT RUN: single head | NOT RUN: Hyprland only | NOT RUN: Hyprland only |
| R12 | Cleanup verified after baseline; final row follows all testing | same | same | same |

The before tests are explicitly bounded. No before result is inferred from the candidate or from an older evidence record.

## Failures and nightly comparison

- **A — GNOME R5:** fixed 10/10 first clicks, 0 further pointer moves. Random 5/10 first clicks. Five of ten random motions were pulled back: three once, two twice. Every pull-back case missed the first click; the five with no pull-back all stopped. This exceeds the expected single pull-back during one wheel step and does not satisfy reliable first-click Stop. Nightly fixed controls: 0/10. All five exact failing random delays were repeated with the nightly RPM/extension 22 and also missed. **Same failing row on nightly; not a demonstrated new regression.**
- **B — GNOME R10:** near-full-screen `[700,30,1200,1030]` region left the bar hidden, with no usable pad/rest surface; mouse movement did not pause (`paused: false`). The user saw the capture ring without controls. Nightly repeated the same hidden-bar/no-pause behavior. **Same on nightly.**
- **C — Hyprland R3:** four untouched candidate captures stopped at `time_limit` rather than `end_of_content`: 180.023 s / 16,560 px, 180.061 s / 15,360 px under mixed host load, then 180.016 s / 21,000 px and 180.048 s / 21,240 px after physical GNOME testing ended. Nightly completed two original controls at 22,940 px in 61.124/64.994 s, and two controls under the same mixed host load in 81.085/110.826 s. Full nightly images have identical SHA-256. Candidate images stop within references, short of the footer. **Nightly passes the same row; this failure counts against the PR.** No mouse arrow was observed in inspected candidate image portions, but incomplete images do not pass R3.
- **D — Hyprland R5:** fixed 8/10 first clicks, further moves `[0,0,0,1,0,0,0,0,15,1]`; fixed try 4 missed after one pull-back and try 9 never paused, injected 15 more moves and missed. Try 10 stopped despite one further move. Random 10/10 clicks, but tries 5 and 8 each had one additional move, violating the zero-move target. Nightly with the same corrected local-centering driver: 0/10 fixed clicks. **Same failing row on nightly; not a demonstrated new regression.**
- **E — Plasma R5:** fixed 10/10 first clicks, 0 further moves. Random 9/10; try 9 at actual 5,397 ms start delay paused after 6.54 ms but injected one further move and missed the first click. Nightly fixed controls: 0/10; the exact failing 5.397 s delay also missed on nightly with 67 further moves. **Same on nightly.**

- **F — Budgie R5:** fixed 10/10 first clicks and zero further moves; random 9/10. Random try 6 at actual 5,401 ms paused after 50.56 ms but injected one further pointer move and missed the first click. Nightly fixed controls: 0/10. The same failing random delay was also repeated on nightly: actual 5,405 ms, no pause, 48 further pointer moves and a missed first click (`b/failure-rechecks.jsonl`). **Same failing row on nightly; not a demonstrated new regression.**

## Functional evidence

The native helper logs show `rest on bar` for GNOME; on Hyprland, labwc and KWin they also show the region output's watch surface and holes. Normal-region bar states have the same 628×52 geometry, beside the region. Screenshots named `live-0-running.png`, `pointer-paused.png`, `api-paused.png`, `top-running.png` (Hyprland also `top-running-qmp.png`) and `top-paused.png` show running/top-return hint and paused reason/Resume/Stop/Cancel. A screenshot of the bar is evidence of UI state, not evidence of a completed capture.

For R6 both actual GUI Resume after pointer pause and `scroll.pause`/`scroll.resume` completed. `pointer-paused.json` reports `paused: true, pausedBy: pointer`; `api-paused.json` reports `pausedBy: request`. `band-comparison.json` compares distinct saved plain/resumed PNGs as RGB in 64-row bands. GNOME 6,792 px, Plasma 6,888 px and Hyprland 6,672 px pairs have equal heights and zero different bands. Quiet paused intervals contain zero `scroll inject:` lines. Normal terminal witness files/screenshots prove clicks and keys reach another window while paused; helper logs were checked for no injections. Stop results keep their image; `cancel.json` has identical before/after History and file inventories. `stoptop.json` has `endReason: stopped`, 720 px, `topReached: false` after actual UI Stop on the way up.

GNOME's two complete captures are 23,735 and 23,734 px; Plasma's are both 25,298 px. Browser-owned, whitelisted scroll metadata in `browser-scroll.json` independently records final CSS offsets: GNOME 23,015/23,014 and Plasma 24,578; adding the selected viewport's 720 px matches the stitched image heights. Top/middle/footer were inspected. Live Wikipedia variation explains GNOME height differences. Both virtual profiles are single-head, so R11 is explicitly not run; there is no claim of two-monitor coverage.

## Per-try data

Times are milliseconds. `pause —` means no automatic pause was observed. `moves` counts put.gd pointer injections after first relative motion. `click` is the first click only; a later API cleanup stop does not count. Raw JSONL, helper logs and driver stderr are retained beside each table.

### gnome

Nightly fixed: 0/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2002 | — | 72 | NO | stopped |
| 2 | 2002 | — | 18 | NO | lost_track |
| 3 | 2002 | — | 18 | NO | lost_track |
| 4 | 2002 | — | 18 | NO | lost_track |
| 5 | 2003 | — | 72 | NO | stopped |
| 6 | 2004 | — | 18 | NO | lost_track |
| 7 | 2004 | — | 18 | NO | lost_track |
| 8 | 2002 | — | 18 | NO | lost_track |
| 9 | 2002 | — | 18 | NO | lost_track |
| 10 | 2003 | — | 18 | NO | lost_track |

Candidate fixed: 10/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2004 | 2.08 | 0 | yes | stopped |
| 2 | 2002 | 1.99 | 0 | yes | stopped |
| 3 | 2003 | 3.02 | 0 | yes | stopped |
| 4 | 2004 | 2.78 | 0 | yes | stopped |
| 5 | 2002 | 15.24 | 0 | yes | stopped |
| 6 | 2002 | 20.21 | 0 | yes | stopped |
| 7 | 2004 | 3.36 | 0 | yes | stopped |
| 8 | 2003 | 2.99 | 0 | yes | stopped |
| 9 | 2004 | 3.86 | 0 | yes | stopped |
| 10 | 2002 | 18.20 | 0 | yes | stopped |

Observed pause range 1.99–20.21 ms; median 3.19 ms.

Candidate random: 5/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 1800 | 7.15 | 0 | yes | stopped |
| 2 | 3183 | 36.29 | 1 | NO | stopped |
| 3 | 1503 | 17.15 | 0 | yes | stopped |
| 4 | 4904 | 1.68 | 0 | yes | stopped |
| 5 | 4559 | 44.89 | 1 | NO | stopped |
| 6 | 3493 | 9.41 | 0 | yes | stopped |
| 7 | 2143 | 130.65 | 2 | NO | stopped |
| 8 | 3660 | 65.38 | 2 | NO | stopped |
| 9 | 2547 | 7.22 | 0 | yes | stopped |
| 10 | 4720 | 45.85 | 1 | NO | stopped |

Observed pause range 1.68–130.65 ms; median 26.72 ms.

### hyprland

Nightly fixed: 0/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2087 | — | 28 | NO | stopped |
| 2 | 2079 | — | 27 | NO | stopped |
| 3 | 2048 | — | 27 | NO | stopped |
| 4 | 2029 | — | 13 | NO | lost_track |
| 5 | 2051 | — | 13 | NO | lost_track |
| 6 | 2044 | — | 28 | NO | stopped |
| 7 | 2124 | — | 27 | NO | stopped |
| 8 | 2114 | — | 27 | NO | stopped |
| 9 | 2050 | — | 31 | NO | stopped |
| 10 | 2073 | — | 30 | NO | stopped |

Candidate fixed: 8/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2021 | 47.14 | 0 | yes | stopped |
| 2 | 2052 | 0.35 | 0 | yes | stopped |
| 3 | 2038 | 90.55 | 0 | yes | stopped |
| 4 | 2093 | 161.55 | 1 | NO | stopped |
| 5 | 2031 | 111.51 | 0 | yes | stopped |
| 6 | 2096 | 38.62 | 0 | yes | stopped |
| 7 | 2047 | 38.14 | 0 | yes | stopped |
| 8 | 2183 | 1.55 | 0 | yes | stopped |
| 9 | 2264 | — | 15 | NO | stopped |
| 10 | 2058 | 131.52 | 1 | yes | stopped |

Observed pause range 0.35–161.55 ms; median 47.14 ms.

Candidate random: 10/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 5889 | 103.04 | 0 | yes | stopped |
| 2 | 3514 | 0.76 | 0 | yes | stopped |
| 3 | 5049 | 86.82 | 0 | yes | stopped |
| 4 | 2171 | 125.63 | 0 | yes | stopped |
| 5 | 3743 | 106.27 | 1 | yes | stopped |
| 6 | 1839 | 45.88 | 0 | yes | stopped |
| 7 | 2940 | 109.32 | 0 | yes | stopped |
| 8 | 5517 | 68.55 | 1 | yes | stopped |
| 9 | 2823 | 1.16 | 0 | yes | stopped |
| 10 | 1944 | 153.74 | 0 | yes | stopped |

Observed pause range 0.76–153.74 ms; median 94.93 ms.

### budgie

Nightly fixed: 0/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2004 | — | 13 | NO | lost_track |
| 2 | 2002 | — | 18 | NO | lost_track |
| 3 | 2003 | — | 18 | NO | lost_track |
| 4 | 2006 | — | 15 | NO | lost_track |
| 5 | 2002 | — | 15 | NO | lost_track |
| 6 | 2002 | — | 51 | NO | stopped |
| 7 | 2001 | — | 18 | NO | lost_track |
| 8 | 2004 | — | 15 | NO | lost_track |
| 9 | 2003 | — | 48 | NO | stopped |
| 10 | 2002 | — | 15 | NO | lost_track |

Candidate fixed: 10/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2005 | 39.98 | 0 | yes | stopped |
| 2 | 2002 | 15.24 | 0 | yes | stopped |
| 3 | 2005 | 5.20 | 0 | yes | stopped |
| 4 | 2004 | 8.82 | 0 | yes | stopped |
| 5 | 2002 | 14.65 | 0 | yes | stopped |
| 6 | 2004 | 13.41 | 0 | yes | stopped |
| 7 | 2002 | 21.78 | 0 | yes | stopped |
| 8 | 2002 | 6.24 | 0 | yes | stopped |
| 9 | 2002 | 28.28 | 0 | yes | stopped |
| 10 | 2009 | 82.98 | 0 | yes | stopped |

Observed pause range 5.20–82.98 ms; median 14.95 ms.

Candidate random: 9/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 1510 | -0.15 | 0 | yes | stopped |
| 2 | 1009 | -0.31 | 0 | yes | stopped |
| 3 | 2364 | 49.81 | 0 | yes | stopped |
| 4 | 1830 | 19.89 | 0 | yes | stopped |
| 5 | 2751 | 3.76 | 0 | yes | stopped |
| 6 | 5401 | 50.56 | 1 | NO | stopped |
| 7 | 5019 | 44.95 | 0 | yes | stopped |
| 8 | 2624 | 26.88 | 0 | yes | stopped |
| 9 | 4206 | 40.90 | 0 | yes | stopped |
| 10 | 5088 | 14.34 | 0 | yes | stopped |

Observed pause range -0.31–50.56 ms; median 23.39 ms.

### plasma-6.8.2

Nightly fixed: 0/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2001 | — | 12 | NO | lost_track |
| 2 | 2001 | — | 12 | NO | lost_track |
| 3 | 2001 | — | 12 | NO | lost_track |
| 4 | 2001 | — | 12 | NO | lost_track |
| 5 | 2001 | — | 12 | NO | lost_track |
| 6 | 2001 | — | 12 | NO | lost_track |
| 7 | 2001 | — | 12 | NO | lost_track |
| 8 | 2001 | — | 12 | NO | lost_track |
| 9 | 2001 | — | 12 | NO | lost_track |
| 10 | 2001 | — | 12 | NO | lost_track |

Candidate fixed: 10/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 2001 | 5.40 | 0 | yes | stopped |
| 2 | 2001 | 0.76 | 0 | yes | stopped |
| 3 | 2001 | 0.58 | 0 | yes | stopped |
| 4 | 2002 | 1.81 | 0 | yes | stopped |
| 5 | 2001 | 0.50 | 0 | yes | stopped |
| 6 | 2001 | 0.46 | 0 | yes | stopped |
| 7 | 2001 | 0.50 | 0 | yes | stopped |
| 8 | 2001 | 0.42 | 0 | yes | stopped |
| 9 | 2001 | 1.02 | 0 | yes | stopped |
| 10 | 2001 | 1.12 | 0 | yes | stopped |

Observed pause range 0.42–5.40 ms; median 0.67 ms.

Candidate random: 9/10 first clicks.

| Try | start | pause | moves | click | end |
|---|---:|---:|---:|---|---|
| 1 | 1395 | 3.10 | 0 | yes | stopped |
| 2 | 1449 | 0.66 | 0 | yes | stopped |
| 3 | 5016 | 0.76 | 0 | yes | stopped |
| 4 | 1599 | 0.75 | 0 | yes | stopped |
| 5 | 5103 | 0.16 | 0 | yes | stopped |
| 6 | 3385 | 6.76 | 0 | yes | stopped |
| 7 | 4642 | 5.86 | 0 | yes | stopped |
| 8 | 5316 | 0.35 | 0 | yes | stopped |
| 9 | 5397 | 6.54 | 1 | NO | stopped |
| 10 | 4156 | 5.22 | 0 | yes | stopped |

Observed pause range 0.16–6.76 ms; median 1.93 ms.

## Cleanup, retention and limitations

Both physical leases were released only after verified-clean checks and normal-window click/key tests. f44 has no put.gd RPM, the saved enabled/disabled extension lists restored, packaged putgd extension disabled/removed with its RPM, original pointer acceleration restored, and a final real re-login completed. Its saved lists, rather than assumptions about baseline, were restored: enabled background-logo and appindicator; disabled hkwitness and putgd. **Installing the nightly RPM invalidated a pre-existing pending dnf5daemon-server offline transaction.** No desktop/compositor package was installed or upgraded, and that transaction was not recreated or applied. This is a material package-manager state difference. Other pre-existing dependencies were preserved during uninstall.

Aurora has no test package installed, the test Flatpak Firefox instance and owned terminals stopped, all owned uinput devices gone and the newly created test-device `kcminputrc` setting/file removed, restoring its original absence. No other session's projects or desktop work were changed. GNOME and Aurora real final cleanup screenshots and typed witnesses are retained. Hyprland's input settings were restored, owned devices removed, application stopped, a normal terminal received QMP keys exactly, and its test-generated persistent failure notification was dismissed; final screenshot has no put.gd surface or notification. Its immutable golden was preserved and disposable overlay retired with a checksummed manifest and guarded receipt.

All host-side source evidence, private export archives and retirement receipts are retained outside release source. Public record excludes browser profiles, keys, login inputs, credentials and payloads other than synthetic fixture/public Wikipedia captures. No source checkout was edited. Budgie final cleanup details and exported checks follow below.


## Budgie completion and final lab state

Budgie's two untouched captures completed in 147.700 and 152.529 seconds, at 23,735 and 23,734 px. The published nightly completed in 39.092 and 37.700 seconds (24,122 and 23,734 px; live-page variation). Whitelisted Firefox scroll metadata records final offsets 23,015/23,014; plus 720 matches both candidate images. Both top/middle/footer sets were inspected and no cursor arrow was observed. Both deterministic Resume pairs are distinct saved files, exactly equal in all 64-row RGB bands at 6,792 px. Candidate R7 and R12 terminal witnesses both received exactly `abc` through local clicks and QMP keyboard events. The paused R7 log has zero sent injections. Cancel's before/after History and file sets are identical. Top-return UI Stop retained 720 px with `topReached: false`.

For R10 on Hyprland, Budgie and Plasma the bar was at x=62, y=1008, 628×52, to the left of the large region; no pad was needed. Pointer motion paused and the person saw the paused reason and Resume/Stop/Cancel. On all normal-region bar state screenshots the measured rectangle is x=470, y=930, 628×52; geometry JSON and original screenshots are retained.

Budgie `r12-cleanup.json` proves the original labwc XML bytes restored (SHA-256 `a044c469f5070438b28690dc95972ccfe294dd06064f0b223b0042ced6034e08`), no lab uinput devices and no putgd/putgd-ui/putgd-record processes. Final normal-window click/key and clean screenshots have no product surface or notification. Temporary guest tools, AppImages and sudo rules existed only in disposable overlays. Private export SHA-256 `015bf06eb6c0a2fe063832e96fe405eed561a081c014fbe68acbf495eb643b6b` was verified guest → f44 → workstation before guarded retirement.

Omarchy overlay retirement completed at 11:01:49 UTC; Budgie completed at 11:37:34 UTC. Both immutable source goldens remain, all historical host-side evidence remains, and both disposable overlays are gone. Guest wall tiles and owned forwarding/watch processes were removed/stopped; the five original physical wall entries remain. No physical lease is held, and no guest from this campaign is running during the 11:45–13:30 UTC reservation. d69, k72 and m74 were not used by this round. The protected temporary local login input was removed after use and was never included in evidence.

## Untouched capture timings

These are observed timings, not a separate performance threshold. Every timed-out candidate image remains a failed completion check. Excluded first-run-modal attempts are retained separately and omitted from this table. Hyprland’s recovered nightly session is an additional completed session after a screenshot-transport failure; it is supporting evidence outside the two-run primary series.

| Desktop | Build | Result file | Height | Seconds | End |
|---|---|---|---:|---:|---|
| gnome | nightly | `gnome/b/live-0.json` | 23734 | 24.798 | end_of_content |
| gnome | nightly | `gnome/b/live-1.json` | 24373 | 25.166 | end_of_content |
| gnome | candidate | `gnome/a/live-0.json` | 23735 | 91.488 | end_of_content |
| gnome | candidate | `gnome/a/live-1.json` | 23734 | 88.000 | end_of_content |
| hyprland | nightly | `hyprland/b/live-0-original.json` | 22940 | 61.124 | end_of_content |
| hyprland | nightly | `hyprland/b/live-0-recovered.json` | 23327 | 69.018 | end_of_content |
| hyprland | nightly | `hyprland/b/live-0.json` | 22940 | 81.085 | end_of_content |
| hyprland | nightly | `hyprland/b/live-1-original.json` | 22940 | 64.994 | end_of_content |
| hyprland | nightly | `hyprland/b/live-1.json` | 22940 | 110.826 | end_of_content |
| hyprland | candidate | `hyprland/a/live-0-mixedload.json` | 16560 | 180.023 | time_limit |
| hyprland | candidate | `hyprland/a/live-0.json` | 21000 | 180.016 | time_limit |
| hyprland | candidate | `hyprland/a/live-1-mixedload.json` | 15360 | 180.061 | time_limit |
| hyprland | candidate | `hyprland/a/live-1.json` | 21240 | 180.048 | time_limit |
| budgie | nightly | `budgie/b/live-0.json` | 24122 | 39.092 | end_of_content |
| budgie | nightly | `budgie/b/live-1.json` | 23734 | 37.700 | end_of_content |
| budgie | candidate | `budgie/a/live-0.json` | 23735 | 147.700 | end_of_content |
| budgie | candidate | `budgie/a/live-1.json` | 23734 | 152.529 | end_of_content |
| plasma-6.8.2 | nightly | `plasma-6.8.2/b/live-0.json` | 25298 | 31.566 | end_of_content |
| plasma-6.8.2 | nightly | `plasma-6.8.2/b/live-1.json` | 25298 | 31.432 | end_of_content |
| plasma-6.8.2 | candidate | `plasma-6.8.2/a/live-0.json` | 25298 | 67.611 | end_of_content |
| plasma-6.8.2 | candidate | `plasma-6.8.2/a/live-1.json` | 25298 | 66.809 | end_of_content |
