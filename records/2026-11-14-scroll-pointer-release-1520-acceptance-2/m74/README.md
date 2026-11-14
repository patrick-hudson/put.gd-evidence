# Cinnamon X11 — final-head PR #1520 acceptance addendum

Coordinator-requested extension of the accepted GNOME, Hyprland, Budgie and Plasma round. Tested 2026-11-14 UTC on the physical **m74 (192.168.68.74), Linux Mint 22.3, Cinnamon 6.6.9, native X11 :0, 1920×1080**. The wall's physical :0 stream stayed enabled. No product source edits, builds, subagents, PR comments or merge.

The lock was already free when checked at 16:56:40 UTC (previous holder released at 16:29:31); successful acquire was **16:56:48 UTC**, owner `scroll-1520-acc`, session `scroll1520-r2-m74`. It was extended/heartbeated while driving. Release time: **17:29:47 UTC** ([receipt](release.json)). Shared SSH watchdog processes 313646/313651 were preserved.

Candidate: **2cc507826e564516cd64cfbd6b67513d929fdde8**, tree **ad79b29c5a8248d15e03c71fe11443288b5fbd3f**, dirty=false ([running build](a/build.json)). The full tree was checked against `gh api repos/patrick-hudson/put.gd-desktop/git/commits/2cc507826e564516cd64cfbd6b67513d929fdde8 --jq .tree.sha`. The Ubuntu 24.04 DEB was downloaded from the completed successful [CI run 43608251978](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43608251978), artifact `release-native-ubuntu24.04`.

Before: published [v26.1113.4757-nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1113.4757-nightly), commit `466449a4c69a07a1997668d1b70d637abac76a16`, tree `4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3` ([running build](b/build.json)). The published DEB's GitHub SHA-256 was verified as `f77a9f0ccb69d6a197e7680b091a9d5f7caa556a1a413519b9c9cb49053ee8b8`. [Both package hashes](packages.json).

## Verdict

| Row | Candidate result | Published nightly comparison |
| --- | --- | --- |
| S1 untouched captures | Pass; median 23.454 s, all end_of_content | Median 24.322 s, all end_of_content |
| S2 fixed / random / steer | Pass; 10/10/10 of 10 each | 0/0/0 of 10 each |
| S3 pause/Resume + other window | Pass; 6792 px, zero differing bands; real click + abc while paused | Pause/Resume absent from this published before build; no substitution claimed |
| S3 X11 Esc | Pass; stopped, 3342 px saved | stopped, 2238 px saved |
| S3 pointer restoration | Pass; exact (300,100) after each of three untouched captures | Pass; exact (300,100) after all three |
| S4 cleanup | Pass; package removed, original input list and APT source preserved, final normal-input witness | Initially no installed put.gd package (rc metadata only) |

No candidate acceptance row failed. Nightly mouse-control misses are expected before behavior, and are reported as failed first clicks in the raw tables below. The one premature Esc file assertion was a driver completion check, resolved against the same operation's completed local save; it is documented below without discarding the attempt.

## Method and isolation

Read-only checkout `/home/patrick/work/put.gd-scroll` was not edited or switched. Reused the author's `umouse.py`, try loop and `rfbshot.py`, with the X11 adaptations retained under [setup](setup/). The user-service environment pointed at stale :2/wlroots state; the actual running Cinnamon process supplied :0/X-Cinnamon/x11 instead. That user-service environment was not changed. [Preflight](setup/preflight.json).

Private resident config/data/cache/state and runtime directories under `~/work/s5202/{a,b}`, all task-owned; [resolved socket lengths](setup/socket-paths.json): both session paths 49 UTF-8 bytes, native bus 18, X11 socket 17, all below 107. Configuration has no destination profiles, the scroll action uses **Local only** (`destination: local`) with retained local images. Inspected operation receipts show `uploadStatus: local_only`, `remoteStatus: not_requested`, empty link/publication URL; no upload or link copy. Local-only processing may copy the PNG itself to the clipboard.

Firefox kiosk with our private `ff` profile on `https://en.wikipedia.org/wiki/Linux`, region `[470,200,980,720]`. Three nightly S1 runs, then three candidate S1 runs, on the same desktop. Candidate S2/S3 followed, then the DEB was switched back to nightly for all 30 matching mouse controls and Esc. Each apt transaction was previewed before confirmation and changed **only put.gd**; no desktop/compositor/dependency package was upgraded, installed or removed. Host load sampled with S1 is retained in `a/load.txt` and `b/load.txt`.

## S1 — untouched capture data

Times are helper `elapsedMs/1000`; raw JSONL also records wall seconds and operation IDs. Every capture ended `end_of_content`. Wikipedia's live fundraising banners/layout varied between loads; all heights and samples remain visible. No sample was discarded. The first ready frame was blank while Firefox loaded; the later live frame showed the Linux article and fundraising banner during the first capture. Whole saved outputs were inspected at the selected area's top/middle/footer.

| Build | Try | End reason | Height px | Seconds | Steps | Pointer before → after |
| --- | --- | --- | --- | --- | --- | --- |
| nightly | 1 | end_of_content | 24396 | 24.322 | 59 | [300, 100] → [300, 100] |
| nightly | 2 | end_of_content | 23757 | 24.540 | 59 | [300, 100] → [300, 100] |
| nightly | 3 | end_of_content | 23757 | 24.028 | 59 | [300, 100] → [300, 100] |
| candidate | 1 | end_of_content | 23757 | 23.329 | 59 | [300, 100] → [300, 100] |
| candidate | 2 | end_of_content | 24144 | 23.534 | 60 | [300, 100] → [300, 100] |
| candidate | 3 | end_of_content | 23757 | 23.454 | 59 | [300, 100] → [300, 100] |

Candidate median 23.454 s versus nightly 24.322 s (-3.57%). Every candidate sample was faster than every nightly sample.

## S2 — real relative mouse, all tries

Purely relative `/dev/uinput` mouse, created through `sudo -n`. Before each try, the exact requested `xinput set-prop 'putgd-lab relative mouse' 'libinput Accel Profile Enabled' 0 1 0` and speed 0 were applied and the resulting properties recorded ([properties](setup/flat-properties.jsonl)). [Calibration](setup/calibration.json): 100 relative units changed native cursor [960,540] to [1060,540]. Only the disposable device was changed; it was destroyed after every try.

A first relative centering jump is computed from the native cursor position; the remaining open-loop path sends ~6 px every 10 ms (~600 px/s) from screen center to Stop. Fixed start is nominal 2 s; random start is 1–6 s. Each try's launch phase is independently randomized by 0–1 s. Steer reads **`xdotool getmouselocation --shell` before every relative event**, rounds/clamps each displacement to a Euclidean norm ≤6 px, and uses the author's bounded arrival loop. Stop centers measured from the real bar: candidate `(960,978)`, nightly `(780,978)`. No VNC absolute-pointer input is used in S2, including centering.

Columns retain the author's log metrics: `pausedMs` from first motion to first paused timestamp; `movesAfter` counts put.gd pointer commands after first motion; `corrections` separately counts displacement undo commands. Tiny negative pause values, if present, reflect integer log timestamps and are retained. `first click` stays false when a later API Stop cleans up a miss. End/height reflect that final cleanup, not successful first-click Stop. Deliberate-motion `lost_track` outcomes below are not untouched S1 outcomes.

### Candidate

**fixed: 10/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a-fixed-1 | 2034 | 4.468 | 0 | 0 | yes | stopped | 720 |
| a-fixed-2 | 2020 | 14.585 | 0 | 0 | yes | stopped | 720 |
| a-fixed-3 | 2018 | 13.699 | 0 | 0 | yes | stopped | 720 |
| a-fixed-4 | 2027 | 4.346 | 0 | 0 | yes | stopped | 720 |
| a-fixed-5 | 2017 | 15.502 | 0 | 0 | yes | stopped | 720 |
| a-fixed-6 | 2014 | 0.905 | 0 | 0 | yes | stopped | 720 |
| a-fixed-7 | 2018 | 4.632 | 0 | 0 | yes | stopped | 720 |
| a-fixed-8 | 2020 | 16.152 | 0 | 0 | yes | stopped | 720 |
| a-fixed-9 | 2038 | 4.633 | 0 | 0 | yes | stopped | 720 |
| a-fixed-10 | 2010 | 3.419 | 0 | 0 | yes | stopped | 720 |

**random: 10/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a-random-1 | 2177 | 50.119 | 0 | 0 | yes | stopped | 720 |
| a-random-2 | 2274 | 4.300 | 0 | 0 | yes | stopped | 720 |
| a-random-3 | 1738 | 4.317 | 0 | 0 | yes | stopped | 720 |
| a-random-4 | 5199 | 5.074 | 0 | 0 | yes | stopped | 3756 |
| a-random-5 | 5186 | 29.450 | 0 | 0 | yes | stopped | 3756 |
| a-random-6 | 1754 | 4.583 | 0 | 0 | yes | stopped | 720 |
| a-random-7 | 4574 | 1.933 | 0 | 0 | yes | stopped | 2928 |
| a-random-8 | 4154 | 1.654 | 0 | 0 | yes | stopped | 2514 |
| a-random-9 | 2182 | 42.853 | 0 | 0 | yes | stopped | 720 |
| a-random-10 | 3229 | 1.932 | 0 | 0 | yes | stopped | 1272 |

**steer: 10/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a-steer-1 | 1407 | 13.096 | 0 | 0 | yes | stopped | 720 |
| a-steer-2 | 2337 | 3.862 | 0 | 0 | yes | stopped | 720 |
| a-steer-3 | 5615 | 2.565 | 0 | 0 | yes | stopped | 4170 |
| a-steer-4 | 2040 | 13.863 | 0 | 0 | yes | stopped | 720 |
| a-steer-5 | 2266 | 5.534 | 0 | 0 | yes | stopped | 720 |
| a-steer-6 | 5845 | 3.643 | 0 | 0 | yes | stopped | 4584 |
| a-steer-7 | 3412 | 2.343 | 0 | 0 | yes | stopped | 1686 |
| a-steer-8 | 3600 | 11.094 | 0 | 0 | yes | stopped | 2100 |
| a-steer-9 | 1414 | 3.350 | 0 | 0 | yes | stopped | 720 |
| a-steer-10 | 4606 | 10.897 | 0 | 0 | yes | stopped | 3342 |

### Published nightly

**fixed: 0/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| b-fixed-1 | 2022 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-2 | 2032 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-3 | 2029 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-4 | 2013 | none | 78 | 0 | **FAIL** | stopped | 10794 |
| b-fixed-5 | 2015 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-6 | 2027 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-7 | 2018 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-8 | 2007 | none | 78 | 0 | **FAIL** | stopped | 10843 |
| b-fixed-9 | 2016 | none | 18 | 0 | **FAIL** | lost_track | 1272 |
| b-fixed-10 | 2007 | none | 18 | 0 | **FAIL** | lost_track | 1272 |

**random: 0/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| b-random-1 | 3850 | none | 18 | 0 | **FAIL** | lost_track | 3342 |
| b-random-2 | 5496 | none | 18 | 0 | **FAIL** | lost_track | 5412 |
| b-random-3 | 3775 | none | 81 | 0 | **FAIL** | stopped | 13278 |
| b-random-4 | 3433 | none | 81 | 0 | **FAIL** | stopped | 12864 |
| b-random-5 | 2898 | none | 82 | 0 | **FAIL** | stopped | 12312 |
| b-random-6 | 5008 | none | 19 | 0 | **FAIL** | lost_track | 4998 |
| b-random-7 | 2879 | none | 81 | 0 | **FAIL** | stopped | 11642 |
| b-random-8 | 4798 | none | 81 | 0 | **FAIL** | stopped | 14934 |
| b-random-9 | 5491 | none | 81 | 0 | **FAIL** | stopped | 15347 |
| b-random-10 | 2410 | none | 78 | 0 | **FAIL** | stopped | 11208 |

**steer: 0/10.**

| Try | Actual start ms | Pause ms | Moves after motion | Corrections | First click Stop | End | Height |
| --- | --- | --- | --- | --- | --- | --- | --- |
| b-steer-1 | 2713 | none | 95 | 0 | **FAIL** | stopped | 12864 |
| b-steer-2 | 3317 | none | 101 | 0 | **FAIL** | stopped | 15348 |
| b-steer-3 | 2681 | none | 100 | 0 | **FAIL** | stopped | 14207 |
| b-steer-4 | 1136 | none | 91 | 0 | **FAIL** | stopped | 11208 |
| b-steer-5 | 1092 | none | 97 | 0 | **FAIL** | stopped | 13278 |
| b-steer-6 | 2220 | none | 97 | 0 | **FAIL** | stopped | 13295 |
| b-steer-7 | 3892 | none | 103 | 0 | **FAIL** | stopped | 16590 |
| b-steer-8 | 4515 | none | 99 | 0 | **FAIL** | stopped | 16590 |
| b-steer-9 | 3931 | none | 97 | 0 | **FAIL** | stopped | 14520 |
| b-steer-10 | 5402 | none | 98 | 0 | **FAIL** | stopped | 17446 |

## S3 — images, window input, Esc, restoration

One untouched static local fixture and one real mouse pause + real Resume-button capture saved distinct PNGs. `scroll.inspect` reported `paused: true, pausedBy: pointer`; both ended `end_of_content`, at 6792 px, with identical SHA-256 and every 64-row RGB band equal. [Comparison](a/band-comparison.json), [paused state](a/pointer-paused.json), [quiet interval](a/pointer-quiet.json), [Resume click](a/resume-click.json). The actual paused bar shows Resume/Stop/Cancel beside the region ([running](a/pointer-running.png), [paused](a/pointer-paused.png)).

In a separate capture paused by actual uinput motion, an actual XTerm received a relative-mouse click and uinput `abc` + Enter. Its independently written witness and the screen agree; there were zero `scroll inject:` lines over that period. [Input result](a/terminal-input.json), [typed screenshot](a/terminal-typed.png), [raw quiet log](a/terminal-quiet.log). The owned capture was then stopped and the terminal closed.

Esc was a real uinput `KEY_ESC` press/release while capture was running. The candidate stopped and retained its partial PNG. The first driver's assertion checked the output folder immediately after helper `done`, before pipeline completion, and found no new file. **That failed check is retained** as [immediate snapshot](a/escape-initial-immediate-check.json) and [driver log](a/escape-driver.log). Follow-up against the **same operation ID**, without repeating the key, confirmed `operation.inspect.state: completed`, `local.status: saved`, its exact new path and matching checksum. [Final candidate Esc evidence](a/escape.json). The corrected nightly driver waits for pipeline completion; [nightly Esc evidence](b/escape.json). No product failure was hidden by retrying the capture.

For untouched pointer restoration, each S1 driver put the pointer at `(300,100)` before capture, queried it with the native X11 cursor API, sent no motion during capture, then queried it again after completion. All three runs on **each build** returned exactly `(300,100)`; raw S1 rows above retain both positions.

## S4 — host left behind

Package was **not installed before** (only `rc` metadata for `26.1114.4983~dev+g62a5f8c65233` remained), and is uninstalled again after testing. Removed-package `rc` version metadata now reflects the tested nightly; the original status is retained in [before state](setup/before-state.json). The pre-existing `/etc/apt/sources.list.d/putgd.sources` was preserved byte-for-byte; SHA-256 before/after `83d1c8e34b4724ba11307fbd161d674d0a3b0d4b0664a78fefc1629a30e5fb81`. No autoremove or pending update applied.

Own resident/helpers, Firefox and terminals closed; no test uinput devices or session sockets remain. The initial strict XInput check found that the master devices cached classes from the last removed test device, although all test devices and sockets were already gone ([initial check](a/cleanup-initial-check.json)). Ordinary XTEST motion and a Shift press/release restored the original master-device classes ([restore driver](setup/restore-input.py)); the final XInput list exactly matches the saved original. Three retained Saved locally notifications, all from this run, were inspected and cleared ([before](a/notifications-open.png), [after](a/notifications-cleared.png)). A fresh normal terminal received a real click and `abc` + Enter after app removal, then was closed; pointer returned to its acquisition position. [Cleanup result](a/cleanup.json), [normal-input screenshot](a/r12-typed.png), [clean desktop](a/r12-clean.png), [release receipt](release.json). Task evidence/private browser/config directories remain inactive under `~/work/s5202`; no other project, host, guest or shared SSH watchdog was changed.

## Retention

Actual executed drivers, per-try JSONL, helper logs, state screenshots, six full untouched PNGs and other result PNGs are retained in this directory. Private profile/config databases, APT-source backup bytes and SSH key material are excluded. [Private export checksum](export-checksum.json) records the verified cold archive; source evidence remains on m74. This addendum extends the existing record; the four-desktop accepted report remains above it.
