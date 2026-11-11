# Scroll-capture confirmation — PR #1398

**Capture matrix: 140 exact images, 7 correct intentional Stop viewports, 0 wrong admitted images, 0 requested cases unrun. Overall desktop acceptance remains blocked by a GNOME Shell crash during additional teardown.**

At 07:39:35 UTC, after the requested GNOME matrix and supplementary warning photo had completed, GNOME Shell PID 3594190 received SIGSEGV. An extra cleanup operation prepared a region, cancelled it immediately, then quit the resident. Operation `b92e251a-c789-406c-a9e3-79101ecc66f2` returned ready, cancelled and quitting; it never received `scroll.start`, produced no PNG and emitted no `scroll: source fresh` summary. The backtrace starts in Mutter `meta_window_update_monitor`, through `meta_window_wayland_update_main_monitor`, `meta_window_move_resize_internal` and GJS. **Crashing component: GNOME Shell/Mutter window placement; the responsible caller and whether this predates the build are unproven.** No product fix or baseline-crash comparison was attempted. [RPC/trigger](native/f44/cleanup-crash.json), [backtrace](native/f44/gnome-shell-core-info.txt), [journal](native/f44/gnome-shell-cleanup-journal.txt). Core memory was not exported. GNOME was restored visibly and its lock cleanup passed.

PR head `eaa1ba198fa537d3cac58879b676ad34e268b96a` matched at start and finish. [CI run 42975726725](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42975726725) has its required CI summary SUCCESS: 16 success, four conditional/non-required skips (collect, pipewire, prune caches, CodeRabbit). Inputs came from `gh run download`, without compiling. Artifacts identify merge `47f90af4ed8bda4630c5865fe82023460f4b4697`, tree `57229edd462c2f784b3df03b06d1870abceb6e4c`, version `26.1111.4667-dev+g47f90af4ed8b`; its second parent is the tested PR head. [Source identity](SOURCE.json), [merge parents](merge-identity.txt), [SHA-256 of every downloaded file](artifact-sha256.json). Native Ubuntu 24.04 DEB on m74, Fedora 44 RPM on f44, Debian 13 DEB on d69; the same CI AppImage on every guest. No product edits, product commits, PR-branch pushes, reviews or merge.

All three physical sessions and all four fresh KVM guests used the table below. Guests ran on d69, at most two at a time, with live wall entries. Qt and GTK text documents contained numbered lines 0–1499 and opened at their end; the long ruler opened at pixel 23,400. Browser bottom fixtures scrolled after canvas painting, and each ready frame was retained. Firefox warmed for 18 seconds; Omarchy used Chromium. From-top was explicitly enabled except for the halfway-off case. Native plain ruler and browser ruler were 2,400 px. The long ruler cap was 40,000, text 60,000; the applied-cap case used 2,000. Each following capture completed exactly. All seven MCP runs started at the 24,000 px ruler's end, used the official SDK stdio helper forwarding only to production CLI, fetched the PNG and verified the returned hash. No driver key or button input was used; no Ctrl+Alt+F shortcut was bound, and no CPU/GPU load experiment ran.

Every ruler PNG was checked on every scanline, in full barcode cells and the right margin. Text checks include edge bands, 1,500 bands, 1,500 distinct bitmaps, constant pitch and clear right background. A one-column RGB (211,212,212) Qt fixture edge on KDE was identified explicitly, matching the previous pass's fixture-edge adjudication; raw background flags are retained, not silently discarded. Exact includes the deliberately capped exact prefix. Honest stop is the requested current viewport, matching the fixture's last position, with zero pointer contamination and `topReached: false`. Every full from-end run proved the top and ended `end_of_content`; none admitted a missing start. Per-case PNGs, helper logs, operation IDs and raw verifier results accompany each desktop.

| Desktop | Exact | Honest intentional Stop | Wrong |
|---|---:|---:|---:|
| Cinnamon X11 — Mint 22.3 | 20 | 1 | 0 |
| GNOME 50.6 Wayland — Fedora 44 | 20 | 1 | 0 |
| Plasma 6.3.6 Wayland — Debian 13 | 20 | 1 | 0 |
| Hyprland 0.56.2 — Omarchy | 20 | 1 | 0 |
| Budgie / labwc 0.20.2 — Fedora 45 | 20 | 1 | 0 |
| KWin 6.8.1 Wayland — KDE neon | 20 | 1 | 0 |
| KWin 6.6.6 Wayland — Kubuntu 26.04 | 20 | 1 | 0 |

**147 requested observations: 140 exact and seven correct intentional Stops.** Supplemental probes and invalid harness attempts do not inflate these counts. This confirmation is narrower than the prior full acceptance matrix; it does not re-establish release or memory acceptance.

### Cinnamon X11 — Mint 22.3

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 3.228 / 3.231 / 3.762 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 4.585 / 4.448 / 4.595 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 4.698 / 4.699 |
| Browser ruler, from end | 3 | 0 | 0 | 2.657 / 2.668 / 2.653 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 3.406 |
| **Total** | **20** | **1** | **0** | |

### GNOME 50.6 Wayland — Fedora 44

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 4.871 / 5.597 / 4.996 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 5.105 / 5.041 / 5.062 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 5.439 / 4.741 |
| Browser ruler, from end | 3 | 0 | 0 | 2.671 / 2.690 / 2.724 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 5.043 |
| **Total** | **20** | **1** | **0** | |

### Plasma 6.3.6 Wayland — Debian 13

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 5.060 / 3.631 / 3.520 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 17.505 / 17.602 / 15.853 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 6.603 / 20.316 |
| Browser ruler, from end | 3 | 0 | 0 | 3.306 / 3.460 / 3.462 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 5.054 |
| **Total** | **20** | **1** | **0** | |

### Hyprland 0.56.2 — Omarchy

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 15.612 / 13.316 / 14.214 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 8.739 / 9.238 / 9.347 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 9.212 / 9.073 |
| Browser ruler, from end | 3 | 0 | 0 | 2.505 / 2.458 / 2.064 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 20.172 |
| **Total** | **20** | **1** | **0** | |

### Budgie / labwc 0.20.2 — Fedora 45

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 6.915 / 8.462 / 8.698 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 7.395 / 7.597 / 7.402 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 6.273 / 5.325 |
| Browser ruler, from end | 3 | 0 | 0 | 3.033 / 2.996 / 2.996 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 8.269 |
| **Total** | **20** | **1** | **0** | |

### KWin 6.8.1 Wayland — KDE neon

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 9.437 / 8.520 / 6.811 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 5.772 / 6.088 / 6.033 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 6.774 / 5.805 |
| Browser ruler, from end | 3 | 0 | 0 | 3.549 / 3.529 / 3.515 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 7.040 |
| **Total** | **20** | **1** | **0** | |

### KWin 6.6.6 Wayland — Kubuntu 26.04

| Case | Exact | Honest stop | Wrong | Way up, seconds (each run) |
|---|---:|---:|---:|---|
| 24,000 px ruler, from end | 3 | 0 | 0 | 4.197 / 3.350 / 3.354 |
| Qt text, 1,500 lines, from end | 3 | 0 | 0 | 3.950 / 4.039 / 4.026 |
| GTK 4 text, 1,500 lines, from end | 2 | 0 | 0 | 4.823 / 4.582 |
| Browser ruler, from end | 3 | 0 | 0 | 3.720 / 3.693 / 3.826 |
| Halfway, fromTop off | 1 | 0 | 0 | — |
| Plain native ruler, from top | 3 | 0 | 0 | — |
| Browser ruler, from top | 2 | 0 | 0 | — |
| Stop on way up | 0 | 1 | 0 | — |
| Height cap 2,000; warning + loopback | 1 | 0 | 0 | — |
| Immediate next capture | 1 | 0 | 0 | — |
| Agent-only MCP, from end; fetched PNG | 1 | 0 | 0 | 3.389 |
| **Total** | **20** | **1** | **0** | |

## Intentional Stop details

| Desktop | Current viewport's first pixel | Result | Helper summary |
|---|---:|---|---|
| Cinnamon X11 — Mint 22.3 | 16200 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 28 ms, retries 0, scroll-backs 0 |
| GNOME 50.6 Wayland — Fedora 44 | 18480 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 17 ms, retries 0, scroll-backs 0 |
| Plasma 6.3.6 Wayland — Debian 13 | 21600 | `stopped`, `topReached: false` | scroll: source fresh 2, quiet 1, unproven 0, slowest response 0 ms, retries 0, scroll-backs 0 |
| Hyprland 0.56.2 — Omarchy | 22080 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 0 ms, retries 0, scroll-backs 0 |
| Budgie / labwc 0.20.2 — Fedora 45 | 19680 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 24 ms, retries 0, scroll-backs 0 |
| KWin 6.8.1 Wayland — KDE neon | 16530 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 35 ms, retries 0, scroll-backs 0 |
| KWin 6.6.6 Wayland — Kubuntu 26.04 | 1800 | `stopped`, `topReached: false` | scroll: source fresh 1, quiet 0, unproven 0, slowest response 54 ms, retries 0, scroll-backs 0 |

These seven are expected control outcomes; the component is the requested Stop, not a capture fault. Full barcode and margin checks found no pointer pixels.

## Harness failures and supplementary checks

- GNOME initially remained in Activities overview after re-login: three captures returned `lost_track` against the thumbnail view, with `source fresh 4, quiet 0, unproven 0` (slowest 21/0/0 ms, retries 1, scroll-backs 3). No `end_of_content` or `height_cap` image was admitted. Component: fixture/desktop readiness. Those PNGs/logs remain under `harness-failures/gnome-overview`. The campaign was stopped by its exact PIDs, retained, and repeated in a new private profile after the Shell's `OverviewActive` property was set false and read back false. No key injection was used.
- Neon's first five browser attempts and five subsequent preference-only retries hit Firefox's Terms startup modal and refused `scroll_no_movement`, without PNGs. Each helper summary is `source fresh 9, quiet 0, unproven 0`, retries 0, scroll-backs 0. Component: browser fixture startup. A private byte-identical copy of the installed distro Firefox used the documented `SkipTermsOfUse` policy; the system installation was untouched. Ready images show the unobstructed ruler, and five repeated cases passed. Initial/refused cases and exports remain retained. The attempted root policy setup was refused by the guest's sudo rules; no password was requested or bypassed.
- Kubuntu's first overlay failed the lab desktop preflight before product install: `plasmashell --version` had no display during startup. It was exported and retired as a failed harness run. A fresh overlay delayed the same unchanged preflight by 25 seconds and passed. Its capture matrix used that fresh run. Premature dependency probes, an old-suffix export command, and an early analysis command were retained separately; corrected commands did not change product code or case counts.
- The strict text-background oracle initially flagged KDE Qt's known constant gray last column. Counts, pixel bounds, color and adjudication are retained; there was no missing, repeated, out-of-order or foreign content in those PNGs.
- Cap history notes name 2,000 and loopback payload hashes match the PNGs on every desktop. Warning presentation was checked separately where a fullscreen fixture suppressed banners or the immediate next capture dismissed the prior warning. Budgie, neon and Kubuntu warning-only probes closed the fixture before the photo. Cinnamon's upload-complete toast replaced the cap banner too quickly for its first photo; a separate synthetic loopback probe delayed the HTTP response by eight seconds and photographed the cap banner before completion. These probes use the same CI build, and do not count as matrix repetitions. Annotation pictures reuse the permitted physical pass-3 clean inputs and were marked/cropped by the current build's own `editor.open`, `editor.apply`, `editor.saveCopy` and `editor.cancel` methods; editor RPC records and input hashes are retained.

## Cleanup and retained material

Every native test package was removed without purging user configuration. Fedora's three gained runtime packages (jasper-libs, libmng, qt6-qtimageformats) were removed. Its extension enabled/disabled lists match their saved originals; GNOME was re-logged in to unload the removed extension, VNC restored and the unlocked desktop checked visibly. Native residents, fixtures and loopback receivers stopped. No user app was closed. The existing d69 signing agent was preserved. No output scale or shortcut was changed. dnf reported invalidating a pending offline transaction; no OS upgrade was run.

All physical locks passed cleanup and were released: m74 07:37:52 and the supplementary photo lease 07:48:52, f44/d69 07:41:32 UTC. Patrick corrected the brief's stale 07:30 schedule: the installed timer is authoritative, with reservation from 12:15 UTC through release after 12:30. No lease approaches that window. All five disposable overlays, including the failed Kubuntu boot, were retired with guarded `lab.py cleanup` after verified export. Goldens stayed immutable. Owned wall entries/tunnels were removed, preserving the five physical tiles. Final receipts accompany the record.

Left on m74: private scripts, downloaded DEB and raw evidence in `~/work/pcn` and `~/work/pwc`. Left on f44: private scripts/RPM/evidence in `~/work/pcn` (invalid overview attempts and settings baseline) and `~/work/pc2` (valid campaign and teardown diagnostics); the system-managed GNOME core stays private on f44. Left on d69: `~/work/pcn` native evidence and `~/work/scn` guest AppImage, scripts, exports and receipts; retired run metadata under `~/work/svm1398/repo/work/lab-runs`, plus stopped private editor profiles `/tmp/acn` and `/tmp/acn2`. Workstation: CI artifacts, verified exports, annotated PNGs and this report under `acceptance/confirm`; no VM disk or golden. Local bulk archives and installers stay private; the public record contains the readable source identities, all case PNGs/logs/results, harness sources, visual evidence and cleanup receipts. The build under test remains detached and clean.
