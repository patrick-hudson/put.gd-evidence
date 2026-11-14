# PR #1520 desktop acceptance — round 2

Observed on 2026-11-14 UTC. This is the requested S1–S4 rerun, using official packages, real native desktops and real input. No product source was changed or built; no PR comment or merge was made. Results apply to this build and these rows, not the unrequested round-1 matrix (including the large GNOME region issue #1519).

Candidate: head `2cc507826e564516cd64cfbd6b67513d929fdde8`, full tree `ad79b29c5a8248d15e03c71fe11443288b5fbd3f`, dirty=false on all four desktops. The full tree was obtained with `gh api repos/patrick-hudson/put.gd-desktop/git/commits/2cc507826e564516cd64cfbd6b67513d929fdde8 --jq .tree.sha` and matched each desktop's `diagnostics.build.gitTree` (`*/a/build.json`). Packages came from the **completed, successful** [manual CI run 43608251978](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43608251978); see [CI data](ci-run.json), [package digests](packages.json), and [expected identity](expected-build.json).

Before/control: published [v26.1113.4757-nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1113.4757-nightly), commit `466449a4c69a07a1997668d1b70d637abac76a16`, tree `4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3`. Its downloaded assets were checked against GitHub's published SHA-256 values ([digests](nightly-digests.jsonl)); `*/b/diagnostics.json` records the running identity.

Read PR #1520's Round 2 section and issue #1514 with comments, the read-only checkout's lab/design/CLI/acceptance documentation, and the [author's round-2 record](https://github.com/patrick-hudson/put.gd-evidence/tree/ee405a20859dda20019e852e0baf61f8db33cbdd/records/2026-11-14-scroll-pointer-release-1514-round2). Reused its uinput mouse, try loop and RFB screenshot driver. The actual executed host-specific drivers are retained in each `setup/` directory. The inherited trial.py docstring describes its older VNC mode: **all measured S2 trials here selected `--rel --local-center`, so motion after the single initial centering was exclusively relative uinput, not VNC absolute motion**.

## Verdict

| Row | GNOME / f44 | Hyprland / h2 | Budgie / b2 | Plasma 6.8.2 |
| --- | --- | --- | --- | --- |
| S1 untouched timing/end | Pass; median within observed spread, first-run outlier disclosed | Pass; 0/3 lost_track on each build | Pass; slower median within observed spread | Pass; faster, identical PNGs |
| S2 relative mouse | Pass; fixed 8/10, random 10/10; steer not run (no cursor readback) | Not run: only S1 requested | Pass; fixed 9/10, random 10/10; steer not run (no cursor readback) | Pass; fixed 10/10, random 9/10, steer 10/10 |
| S3 pause/Resume and other windows | Pass; 6792 px, zero differing bands; terminal abc | Not run: only S1 requested | Pass; 6792 px, zero differing bands; terminal abc | Pass; 6888 px, zero differing bands; terminal abc |
| S4 cleanup | Pass; package removed, settings restored, real re-login/input witness | Pass; input witness, exported and guarded-retired | Pass; original labwc settings restored, input witness, exported and guarded-retired | Pass; cursor script/service and own apps removed, input witness, lock released |

No requested acceptance gate failed. Open-loop misses are reported below without treating them as the steer gate. On GNOME and Budgie, no usable cursor query was available, and the explicitly requested fallback gate was met by random open-loop 10/10.

## Desktops, sessions and isolation

| Desktop | Environment / host use | Session and lease / retirement |
| --- | --- | --- |
| GNOME | Physical f44 (192.168.68.70), Fedora 44, GNOME/Mutter 50.6 Wayland, 1920×1080. Official RPM; packaged Shell extension v22 nightly / v23 candidate ACTIVE. | scroll1520-r2-gnome, 15:32:15–15:46:34 UTC; control lease scroll1520-r2-gnome-control, 16:47:01–16:52:46 UTC (lab/ receipts) |
| Hyprland | Omarchy 4.5 / Hyprland 0.56.2 Wayland guest h2 on f44, 2 vCPU / 6 GiB, software rendering, one 1920×1080 output. Host not compiling put.gd; guest was the test workload. | run f0fad077-eb5d-403a-917c-9dc44e15929b; guarded-retired 16:01:45 UTC |
| Budgie | Fedora 45, Budgie 10.10.3 / labwc 0.20.2 Wayland guest b2 on f44, 2 vCPU / 6 GiB, one 1920×1080 output. | run 66ecd3b8-c9b4-425c-b7ce-03b8dc06999b; guarded-retired 16:28:12 UTC |
| Plasma | Physical aurora-amd (192.168.68.71), Fedora 45, native KWin 6.8.2-2.fc45 / plasma-workspace 6.8.2-1.fc45 Wayland. Official extracted AppImages; private Flatpak Firefox profile. | scroll1520-r2-plasma, 16:25:34–16:45:58 UTC, after coordinator handoff and successful acquire |

Only one physical desktop lease was held at once. Guests stayed on the live wall, then their own tiles/forwards were removed after retirement; physical wall displays were preserved. Goldens were not booted or modified. [Lab metadata](lab/) includes launch preflight, run IDs, completion manifests, guarded cleanup receipts and desktop release receipts. S1 used our browser on `https://en.wikipedia.org/wiki/Linux` (Firefox except the Omarchy Chromium wrapper), region `[470,200,980,720]`, local save only, no destination profiles and no upload/link copy. Residents used private task config/data/cache/state; native runtime where required. Every resolved session/Wayland/bus/PipeWire/guest/QMP/VNC socket was checked before use; the longest checked path was 96 UTF-8 bytes, below 107.

## S1 — untouched captures

Three nightly controls followed by three candidate captures on each desktop, without a build or environment change between them. Seconds below are helper `elapsedMs / 1000`; raw JSONL also retains wall time and operation IDs. All 24 runs ended `end_of_content`, with complete article top/middle/footer inspected. Candidate Budgie and Plasma PNGs matched corresponding nightly hashes; Hyprland candidate runs 2/3 also matched nightly runs 1/3. Live page height varied slightly on GNOME/Budgie, so S3 uses the static fixture.

Timing decision: compare the three-run medians against the observed nightly max–min spread; also disclose every sample and the candidate spread. This is a small-sample observed-spread check, not a claim of statistical equivalence. GNOME's first candidate run took 27.118 s / 65 steps (the other two took 24.607/24.364 s / 60 steps), so it is explicitly retained as an outlier. Budgie's median was 3.630 s (11.4%) slower, within its nightly 7.032 s spread. Neither is described as a measured speedup.

| Desktop | Nightly median (range), s | Candidate median (range), s | Delta, s | Nightly spread, s |
| --- | --- | --- | --- | --- |
| GNOME / f44 | 24.399 (24.339–24.984) | 24.607 (24.364–27.118) | +0.208 | 0.645 |
| Hyprland / h2 | 65.871 (63.530–66.749) | 56.825 (56.559–60.582) | -9.046 | 3.219 |
| Budgie labwc / b2 | 31.788 (30.332–37.364) | 35.418 (34.770–38.021) | +3.630 | 7.032 |
| Plasma 6.8.2 / aurora-amd | 31.500 (31.350–31.750) | 19.240 (19.207–19.307) | -12.260 | 0.400 |

| Desktop | Build | Try | End reason | Height px | Seconds | Steps |
| --- | --- | --- | --- | --- | --- | --- |
| GNOME / f44 | nightly | 1 | end_of_content | 23734 | 24.984 | 60 |
| GNOME / f44 | nightly | 2 | end_of_content | 24121 | 24.339 | 61 |
| GNOME / f44 | nightly | 3 | end_of_content | 23734 | 24.399 | 60 |
| GNOME / f44 | candidate | 1 | end_of_content | 23734 | 27.118 | 65 |
| GNOME / f44 | candidate | 2 | end_of_content | 23734 | 24.607 | 60 |
| GNOME / f44 | candidate | 3 | end_of_content | 23734 | 24.364 | 60 |
| Hyprland / h2 | nightly | 1 | end_of_content | 22940 | 63.530 | 64 |
| Hyprland / h2 | nightly | 2 | end_of_content | 22940 | 66.749 | 68 |
| Hyprland / h2 | nightly | 3 | end_of_content | 22940 | 65.871 | 68 |
| Hyprland / h2 | candidate | 1 | end_of_content | 22940 | 60.582 | 52 |
| Hyprland / h2 | candidate | 2 | end_of_content | 22940 | 56.559 | 52 |
| Hyprland / h2 | candidate | 3 | end_of_content | 22940 | 56.825 | 52 |
| Budgie labwc / b2 | nightly | 1 | end_of_content | 24373 | 31.788 | 62 |
| Budgie labwc / b2 | nightly | 2 | end_of_content | 23734 | 30.332 | 60 |
| Budgie labwc / b2 | nightly | 3 | end_of_content | 24121 | 37.364 | 70 |
| Budgie labwc / b2 | candidate | 1 | end_of_content | 23734 | 35.418 | 60 |
| Budgie labwc / b2 | candidate | 2 | end_of_content | 23734 | 34.770 | 60 |
| Budgie labwc / b2 | candidate | 3 | end_of_content | 24121 | 38.021 | 61 |
| Plasma 6.8.2 / aurora-amd | nightly | 1 | end_of_content | 25298 | 31.750 | 75 |
| Plasma 6.8.2 / aurora-amd | nightly | 2 | end_of_content | 25298 | 31.500 | 75 |
| Plasma 6.8.2 / aurora-amd | nightly | 3 | end_of_content | 25298 | 31.350 | 75 |
| Plasma 6.8.2 / aurora-amd | candidate | 1 | end_of_content | 25298 | 19.240 | 51 |
| Plasma 6.8.2 / aurora-amd | candidate | 2 | end_of_content | 25298 | 19.207 | 51 |
| Plasma 6.8.2 / aurora-amd | candidate | 3 | end_of_content | 25298 | 19.307 | 51 |

Hyprland: **0/3 full-height `lost_track` on the candidate and 0/3 on the nightly**. The author's intermittent case did not reproduce in these untouched runs. A `lost_track` from a deliberate mouse/control trial below is not counted as an untouched S1 result.

## S2 — relative mouse

Root-owned `/dev/uinput` device via `sudo -n`; acceleration flat, 6 pixels per 10 ms (~600 px/s) for open-loop. Each capture's launch phase was independently randomized by 0–1 s. Fixed motion starts ~2 s after `scroll.start`; random starts 1–6 s. One uinput tablet event establishes the initial middle-of-screen position, followed only by relative mouse motion and the first click. No repeated absolute pointer event masks a pull-back. Failed first clicks are marked false even if the driver's later API Stop saved the image.

Plasma steering reads `workspace.cursorPos` through a temporary, uniquely named KWin script (`scroll1520r2-cursor`) and private user D-Bus reader before **every event**. Rounded displacement is capped to a 6-pixel Euclidean norm; an additional bounded arrival loop is the author's steering behavior. Calibration observed [960,540] → [1060,540] for 100 relative units with flat acceleration ([calibration](plasma/setup/cursor-calibration.json)). The script only reads cursor state; it was loaded after S1, then unloaded and its service stopped during cleanup. See [KWin API](https://develop.kde.org/docs/plasma/kwin/api/), and the actual script/reader in `plasma/setup/`.

GNOME steering not run: Shell `Eval` returned `(false, '')`, and RFB PointerPos yielded no samples. Budgie steering not run: no wlrctl; labwc CLI exposes no cursor position; no Shell Eval object; RFB CursorShape/PointerPos active probe yielded no coordinates despite relative movement. No alternate compositor or unsafe Shell mode was introduced. Their random open-loop 10/10 meets the user's fallback threshold ≥9/10.

`pausedMs` is the log's first paused timestamp minus the driver's first-motion timestamp, in milliseconds. Tiny negative values are retained (integer log timestamps vs sub-ms driver timestamps), not changed to zero. `movesAfter` counts put.gd pointer commands sent after the first motion; `corrections` counts logged displacement undo commands, separately. No correction commands were observed in these candidate trials. A late warp can still occur: GNOME fixed tries 1/10 had two each; Budgie fixed try 8 had one; Plasma random try 10 and steer try 8 had one each. Plasma steer try 8 still stopped on the first click.

### GNOME / f44

**fixed: 8/10 first-click Stop.** [Raw tries](gnome/a/tries-fixed.jsonl), [helper log](gnome/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-fixed-1 | 2002 | 80.875 | 2 | 0 | **NO** |
| a-fixed-2 | 2002 | 2.037 | 0 | 0 | yes |
| a-fixed-3 | 2003 | 0.228 | 0 | 0 | yes |
| a-fixed-4 | 2002 | 10.962 | 0 | 0 | yes |
| a-fixed-5 | 2002 | -0.241 | 0 | 0 | yes |
| a-fixed-6 | 2002 | 2.327 | 0 | 0 | yes |
| a-fixed-7 | 2002 | -0.020 | 0 | 0 | yes |
| a-fixed-8 | 2002 | 1.952 | 0 | 0 | yes |
| a-fixed-9 | 2002 | 0.548 | 0 | 0 | yes |
| a-fixed-10 | 2002 | 57.172 | 2 | 0 | **NO** |

**random: 10/10 first-click Stop.** [Raw tries](gnome/a/tries-random.jsonl), [helper log](gnome/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-random-1 | 5555 | 1.487 | 0 | 0 | yes |
| a-random-2 | 1738 | 10.884 | 0 | 0 | yes |
| a-random-3 | 1312 | 1.022 | 0 | 0 | yes |
| a-random-4 | 1089 | 4.872 | 0 | 0 | yes |
| a-random-5 | 5750 | 12.088 | 0 | 0 | yes |
| a-random-6 | 5552 | 0.059 | 0 | 0 | yes |
| a-random-7 | 4447 | 11.399 | 0 | 0 | yes |
| a-random-8 | 5592 | 10.907 | 0 | 0 | yes |
| a-random-9 | 1868 | 1.144 | 0 | 0 | yes |
| a-random-10 | 4730 | 0.440 | 0 | 0 | yes |

### Budgie labwc / b2

**fixed: 9/10 first-click Stop.** [Raw tries](budgie/a/tries-fixed.jsonl), [helper log](budgie/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-fixed-1 | 2002 | 0.648 | 0 | 0 | yes |
| a-fixed-2 | 2002 | 0.530 | 0 | 0 | yes |
| a-fixed-3 | 2003 | 0.030 | 0 | 0 | yes |
| a-fixed-4 | 2002 | 0.921 | 0 | 0 | yes |
| a-fixed-5 | 2002 | 0.258 | 0 | 0 | yes |
| a-fixed-6 | 2002 | 0.048 | 0 | 0 | yes |
| a-fixed-7 | 2004 | 0.456 | 0 | 0 | yes |
| a-fixed-8 | 2002 | 28.386 | 1 | 0 | **NO** |
| a-fixed-9 | 2002 | -0.086 | 0 | 0 | yes |
| a-fixed-10 | 2002 | -0.055 | 0 | 0 | yes |

**random: 10/10 first-click Stop.** [Raw tries](budgie/a/tries-random.jsonl), [helper log](budgie/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-random-1 | 3831 | 28.455 | 0 | 0 | yes |
| a-random-2 | 4305 | 1.331 | 0 | 0 | yes |
| a-random-3 | 4903 | 6.965 | 0 | 0 | yes |
| a-random-4 | 4035 | 6.941 | 0 | 0 | yes |
| a-random-5 | 5489 | 25.191 | 0 | 0 | yes |
| a-random-6 | 4851 | 10.291 | 0 | 0 | yes |
| a-random-7 | 2455 | 68.908 | 0 | 0 | yes |
| a-random-8 | 2566 | -0.305 | 0 | 0 | yes |
| a-random-9 | 1238 | 1.049 | 0 | 0 | yes |
| a-random-10 | 4985 | 34.396 | 0 | 0 | yes |

### Plasma 6.8.2 / aurora-amd

**fixed: 10/10 first-click Stop.** [Raw tries](plasma/a/tries-fixed.jsonl), [helper log](plasma/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-fixed-1 | 2001 | 0.389 | 0 | 0 | yes |
| a-fixed-2 | 2001 | 5.063 | 0 | 0 | yes |
| a-fixed-3 | 2001 | 0.159 | 0 | 0 | yes |
| a-fixed-4 | 2001 | -0.378 | 0 | 0 | yes |
| a-fixed-5 | 2001 | -0.194 | 0 | 0 | yes |
| a-fixed-6 | 2001 | 0.269 | 0 | 0 | yes |
| a-fixed-7 | 2001 | 0.030 | 0 | 0 | yes |
| a-fixed-8 | 2001 | -0.075 | 0 | 0 | yes |
| a-fixed-9 | 2001 | 0.341 | 0 | 0 | yes |
| a-fixed-10 | 2001 | -0.350 | 0 | 0 | yes |

**random: 9/10 first-click Stop.** [Raw tries](plasma/a/tries-random.jsonl), [helper log](plasma/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-random-1 | 3134 | 0.327 | 0 | 0 | yes |
| a-random-2 | 1580 | 1.685 | 0 | 0 | yes |
| a-random-3 | 3421 | 0.400 | 0 | 0 | yes |
| a-random-4 | 2747 | 2.698 | 0 | 0 | yes |
| a-random-5 | 4584 | 0.430 | 0 | 0 | yes |
| a-random-6 | 1037 | -0.063 | 0 | 0 | yes |
| a-random-7 | 5579 | -0.339 | 0 | 0 | yes |
| a-random-8 | 4407 | 0.037 | 0 | 0 | yes |
| a-random-9 | 3582 | 0.118 | 0 | 0 | yes |
| a-random-10 | 3545 | 3.150 | 1 | 0 | **NO** |

**steer: 10/10 first-click Stop.** [Raw tries](plasma/a/tries-steer.jsonl), [helper log](plasma/a/helper.log).

| Try | Actual start ms | Pause ms | put.gd moves after motion | Corrections | First click Stop |
| --- | --- | --- | --- | --- | --- |
| a-steer-1 | 5988 | 6.822 | 0 | 0 | yes |
| a-steer-2 | 1416 | -0.382 | 0 | 0 | yes |
| a-steer-3 | 4136 | 2.934 | 0 | 0 | yes |
| a-steer-4 | 4707 | 0.043 | 0 | 0 | yes |
| a-steer-5 | 3722 | 0.166 | 0 | 0 | yes |
| a-steer-6 | 2368 | 0.431 | 0 | 0 | yes |
| a-steer-7 | 1372 | 2.641 | 0 | 0 | yes |
| a-steer-8 | 3507 | 5.448 | 1 | 0 | yes |
| a-steer-9 | 5761 | -0.162 | 0 | 0 | yes |
| a-steer-10 | 4785 | 0.287 | 0 | 0 | yes |

### Misses and published-nightly comparisons

GNOME fixed tries 1 and 10 missed: pause after 80.875/57.172 ms, two put.gd pointer moves after first motion on each, no logged correction. Both were finally stopped by the driver's API cleanup at height 720; their first clicks are failures. The published nightly also failed this motion path (0/10 fixed trials, no pause, 15–72 further moves). The separate current-nightly fixed-series control is in `gnome/nightly-control/` and summarized below. These informational fixed misses do not alter the random fallback gate.

Budgie fixed try 8 missed: 28.386 ms to pause, one later put.gd pointer move, no correction; API cleanup saved 720 px. A published-nightly control at the same nominal 2.002 s also missed: no pause, 15 later moves, no correction, then `lost_track` at 852 px after the missed click navigated the opened Wikipedia page to Fedora Linux. [Raw control](budgie/b/failure-rechecks.jsonl), [nightly identity](budgie/b/recheck-diagnostics.json).

Plasma random try 10 missed: 3.150 ms to pause, one later put.gd pointer move, no correction; API cleanup saved 1404 px. Published-nightly control at the same nominal 3.545 s also missed: no pause, 18 later moves, no correction, `lost_track` at 2259 px. [Raw control](plasma/b/failure-rechecks.jsonl), [nightly identity](plasma/b/recheck-diagnostics.json). The candidate's actual start was 3545 ms; nightly's was 3546 ms. Open-loop phase trials are not deterministic replay.

GNOME current-nightly fixed control: **0/10**, using the same relative driver, region, page and 2 s start with the published bar's Stop coordinate. All ten first-click outcomes and motion counts are retained; this control followed the candidate series under a new lease.

| Try | Actual start ms | Pause ms | Moves after motion | First click Stop | End reason | Height |
| --- | --- | --- | --- | --- | --- | --- |
| nightly-fixed-1 | 2003 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-2 | 2002 | none | 72 | **NO** | stopped | 8772 |
| nightly-fixed-3 | 2002 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-4 | 2002 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-5 | 2002 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-6 | 2002 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-7 | 2002 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-8 | 2003 | none | 18 | **NO** | lost_track | 1248 |
| nightly-fixed-9 | 2002 | none | 15 | **NO** | lost_track | 852 |
| nightly-fixed-10 | 2003 | none | 18 | **NO** | lost_track | 1248 |

## S3 — pause, Resume and unrelated input

A static local page was opened in the same browser to remove Wikipedia live-layout differences. One untouched capture and one capture paused by real mouse motion, held quiet and resumed by clicking the **actual Resume button** were saved separately per desktop. `scroll.inspect` reported `paused: true, pausedBy: pointer`. Both captures ended `end_of_content`. Their separate PNG files have identical hashes and RGB pixels: every 64-row band compares equal. Band-comparison JSON names the distinct source files.

| Desktop | Plain height | Resumed height | Different 64-row bands | Evidence |
| --- | --- | --- | --- | --- |
| GNOME / f44 | 6792 | 6792 | 0 | [gnome comparison](gnome/a/band-comparison.json) |
| Budgie labwc / b2 | 6792 | 6792 | 0 | [budgie comparison](budgie/a/band-comparison.json) |
| Plasma 6.8.2 / aurora-amd | 6888 | 6888 | 0 | [plasma comparison](plasma/a/band-comparison.json) |

While each capture was paused, an actual native terminal received a real click and `abc` + Enter; the terminal's independently written witness file and screen show it. `terminal-quiet.log` has zero `scroll inject:` lines during those inputs; the two-second still pause has `injectionLines: []`. The capture was then stopped through its owned session ID. Hyprland S3 was not requested.

## Screenshots and image inspection

All linked screenshots are from this candidate. The surrounding region, running text and paused controls can be inspected directly; full saved image PNGs are in each `a/out/images/`. Running-state screenshots were captured on Plasma in this rerun; GNOME/Budgie's retained S3 screenshots show their paused state. A full R4 state-size/large-region rerun was outside the requested S rows.

| Desktop | Capture / paused controls | Unrelated input while paused | Final clean desktop |
| --- | --- | --- | --- |
| GNOME | [Paused](gnome/a/pointer-paused.png) | [Typed abc](gnome/a/terminal-typed.png) | [Clean](gnome/a/r12-clean.png) |
| Hyprland | S1 only; no S2/S3 states requested | [Cleanup input witness](hyprland/host/h-r12-typed.png) | [Clean](hyprland/host/h-r12-clean.png) |
| Budgie | [Paused](budgie/a/pointer-paused.png) | [Typed abc](budgie/host/b-terminal-typed.png) | [Clean](budgie/host/b-r12-clean.png) |
| Plasma | [Running](plasma/a/pointer-running.png), [Paused](plasma/a/pointer-paused.png) | [Typed abc](plasma/a/terminal-typed.png) | [Clean](plasma/a/r12-clean.png) |

Helper logs show `rest on the bar at 486,944 (local 16,14)` on all desktops. Hyprland/labwc log `watch over Virtual-1 with holes at …`; Plasma logs the region's `DP-2` output. GNOME has no watch surface. In GNOME's 20 candidate mouse trials, **2/20 had pull-back commands (two each, four total), both fixed-start misses; random 0/10 pull-backs and 10/10 first-click Stop**. No correction was logged. These are log command counts; no unavailable cursor trajectory is invented.

## S4 — state left behind

f44: no put.gd RPM or extension files remain, both saved Shell lists restored exactly and a final real GDM re-login performed. The state actually found for this round was enabled `['background-logo@fedorahosted.org', 'putgd@put.gd']`, disabled `['hkwitness@lab']`; this differed from round 1 and was preserved. Mouse acceleration restored to `'default'`. No test uinput devices, resident, helper, test window or surface; normal terminal click/key witness `abc` succeeded. The later nightly control repeats this cleanup, with its own receipt. **Offline-update observation:** DNF previews warned of an offline queue; installs used tested direct RPM transactions. At first cleanup `dnf offline status` reported the saved queue invalid because the system changed. Its validity before testing was not measured, so we cannot attribute the invalidity or claim preservation. No desktop/compositor package was installed, upgraded or downgraded; the queue was not applied or rescheduled.

Hyprland h2 and Budgie b2: input restored and normal terminal input witnessed; no product surfaces/devices before shutdown. Budgie's original `rc.xml` restored exactly (SHA-256 `a044c469f5070438b28690dc95972ccfe294dd06064f0b223b0042ced6034e08`). Evidence was exported and checksum-verified before guarded `lab.py cleanup`; overlays retired, immutable source goldens preserved. Only these guests' wall tiles and tunnel services were removed. Run identities and retirement receipts remain on f44, with public metadata in this record.

Aurora: no package installed; extracted AppImages and private evidence remain under `~/work/s5202`, inactive. Own Firefox Flatpak instance closed; its before and after running-instance lists are empty. Temporary KWin cursor script unloaded (`isScriptLoaded=false`) and exact owned reader PID stopped. Test uinput devices gone; `~/.config/kcminputrc` was absent before and remains absent. Normal Konsole click/key witness `abc` succeeded, then the terminal was closed and the clean desktop observed. Lock released 16:45:58 UTC; pre-existing shared Toolbx/conmon PID 4102 left alone. No other host was changed. No guest or physical lease remains owned by this campaign.

## Setup deviations and retention

Invalid GNOME initial nightly attempts captured the owned Settings window at 1098 px; they were excluded and retained as `s1-initial-settings-invalid.jsonl`. The Settings window was visibly closed before the three valid article controls. A malformed candidate launcher replaced parts of `bin`/`bus` text; the failed attempt and log were retained, command corrected, and sockets rechecked before retry. The first post-login VNC frame was black; a later independent live frame established the desktop before valid measurements. Plasma's Firefox first-run Terms page was closed before any measurements. No invalid setup attempt was counted as an acceptance capture.

Raw helper logs contain only our public/synthetic capture content and technical state. No profile database, credential input, private key or browser data is published. Cold export archives remain privately retained outside this record, with [verified SHA-256 and byte sizes](export-checksums.json). Exported test source, full result images, operation IDs and errors remain here; source evidence is not deleted as a substitute for archiving.


## Cinnamon X11 final-head addendum

The coordinator requested m74 after accepting the four-desktop round above. [Cinnamon X11 acceptance](m74/README.md) tests the same final head and full tree, with three captures per build, all relative-mouse modes, Resume equality, paused-window input, Esc, pointer restoration and cleanup. All candidate rows passed; the addendum retains the full nightly comparison. m74 was released 2026-11-14T17:29:47Z.
