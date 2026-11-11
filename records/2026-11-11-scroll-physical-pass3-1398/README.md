# Scroll capture: third physical acceptance pass, PR #1398

**No wrong admitted stitch in the counted matrix. One honest `lost_track`: GNOME at 125%.** Its complete 1200×3000 PNG is exact on every physical scanline, but the helper could not prove the bottom. Do not describe this pass as every capture reaching `end_of_content`.

An earlier **invalid Mint 150% harness attempt** (`m74/scale150`) returned `end_of_content`, 960×4200, with an incorrectly placed/undersized framebuffer rectangle. The verifier raised `image index out of range`; its PNG, helper log and source screenshot remain. This is a framing failure, not accepted feature evidence. Two subsequent notification-obstructed attempts returned `lost_track`; the final correctly framed, unobstructed `scale150-clean` is exact, 1920×4800. These attempts are excluded from the counted matrix, not silently treated as passes.

PR head `acf681fb0e52494a302e3641c04dd233f7585053`; green CI run `42935796173`, checked with `gh pr checks 1398`, packages obtained with `gh run download`. Package version `26.1111.4656~dev+gebb5bd87b7da` identifies GitHub merge `ebb5bd87b7da95fa78ff640733e5737c5d699f52`, with that PR head as its second parent. `SOURCE.json`, per-host package build-info files and `ci-checks.txt` retain the identities. No product code was changed, compiled, committed or pushed. No VM was touched.

| Installed package | Host | SHA-256 |
| --- | --- | --- |
| Ubuntu 24.04 DEB | m74 | `30608ce6c45947b4be1ccc66f91d4c079897045495a9b5e739b875f1f3e48759` |
| Fedora 44 RPM | f44 | `3ef569ecb3a6d3c3d61a5ea76ae8cd3d216740c2c82759cc7939442f0e7e4a0d` |
| Debian 13 DEB | d69 | `135cc78c0abbef96ecc8504b65f9e631f4dfca306227f273ce2aba100b954b90` |

## Counted results

Physical targets: m74 Mint 22.3 / Cinnamon 6.6.9 X11 (tty7); f44 Fedora 44 / GNOME 50.6 native Wayland (tty2); d69 Debian 13 / Plasma 6.3.6 native Wayland (tty1). Host/session/build metadata and per-run visuals are retained under each host directory. “Exact” below means the image verification passed; intentional Stops additionally require `stopped`.

| Case | m74 Cinnamon X11 | f44 GNOME Wayland | d69 Plasma Wayland |
| --- | --- | --- | --- |
| Qt ruler, 2,400 px | 5/5 exact | 5/5 exact | 10/10 exact |
| Firefox ruler, 14 s draw wait | 5/5 exact | 5/5 exact | 5/5 exact |
| GTK 4 text, wide, 1,500 lines | 3/3 complete | 3/3 complete | 3/3 complete |
| GTK 4 text, narrow | 3/3 complete | 3/3 complete | 3/3 complete |
| Qt text, wide, 1,500 lines | 3/3 complete | 3/3 complete | 3/3 complete |
| Qt text, narrow | 3/3 complete | 3/3 complete | 3/3 complete |
| Sticky header and footer | 1/1 exact | — | — |
| Halfway start, from-top on / off | 1/1 each, exact | — | — |
| Default 30,000 px cap + loopback upload | 1/1 exact capped prefix | 1/1 extra visual/control | 1/1 extra visual/control |
| Stop halfway through capture | 1/1 exact prefix, stopped | — | — |
| Stop during scroll-to-top | 1/1 current viewport | 1/1 current viewport | 3/3 current viewport |
| Cancel | 1/1; cancelled, no new history | — | — |
| Fractional output scale | 150%: 1/1 exact | 125%: 1 honest lost_track, exact full image | 125%: 1/1 exact |
| Immediate start after ready | — | 5/5 exact | — |
| 24,000 px ruler | — | — | 1/1 exact |
| Official-SDK MCP → production CLI, PNG fetched | 1/1 exact | 1/1 exact | 1/1 exact |
| Safe Ctrl+Shift+F7 + real drag | 1/1 exact, uploaded | 1/1 exact, uploaded | — |

The requested functional matrix has **96 checks: 88 exact completed PNGs, 7 honest Stop/lost-track PNGs, and 1 Cancel with no PNG; 0 wrong images in counted runs**. The seven are six intentional Stops and the GNOME fractional-scale result. Extra cap-photo captures and six clean Mint wide-text repeats are not inflated into those totals. The counted Mint wide rows use the clean repeats; earlier runs with a stale notification present remain separately named.

Rulers are checked on every scanline, including barcode interiors. Fractional images independently check row centres and every physical scanline within one physical pixel of toolkit rounding. All text cases require 1,500 distinct ink bands, including bands touching an image edge, one constant pitch and no duplicate/gap. Complete text heights/pitches differ by native font: Mint Qt 22,519/15 and GTK 24,000/16; GNOME Qt 28,520/19 and GTK 27,000/18; Plasma Qt 27,022/18 and GTK 27,000/18. Supplemental glyph-template experiments (`order-*.log`, `order-verification.json`, and private `verify_chars.py`) assume font properties that fail for proportional/context-shaped glyphs; they are harness diagnostics, not the acceptance oracle or product failures. Their failure output is preserved. No OCR feature was added.

Stop-during-top adjudication compares the PNG's uniquely decoded first pixel with the fixture's final painted position: Mint **20,400**, GNOME **21,000**, Plasma **21,600 in all three**. All match, with current-viewport adjudications saved. MCP operation IDs, transcripts, fetched files and matching reported/fetched SHA-256 values are retained in `mcp-fetch-receipts.json`.

## Failure and prerequisite attribution

- **GNOME 125%, `f44/scaled-00`:** `lost_track`, 3,000 rows, zero bad scanlines. Helper: **source fresh 0, quiet 0, unproven 3**, slowest response 45 ms, retries 0, scroll-backs 0. Terminal note: no fresh frame after the last scroll steps, so the end is not proven. Component: **Mutter frame-tap freshness / end confirmation**. PNG and helper log retained. This is an honest stop, including an exact whole-page image, not a proven end-of-content pass.
- **Mint invalid scale framing, `m74/scale150`:** `end_of_content` 4,200 rows; **fresh 3, quiet 0**, slowest response 94 ms, retries 0. Component: **acceptance harness rectangle/DPR assumption**. The first retry (`scale150-notification-obstructed`) and second (`scale150-correct`) both have **fresh 1, quiet 0**, four retries and four scroll-backs; their source shows a stale notification obscuring the ruler, and the matcher stops with `lost_track` at 1,320 rows. Neither is claimed to be an exact prefix. The corrected clean run (`scale150-clean`) has **fresh 3, quiet 0**, zero retries, 4,800 exact rows. At 150%, Cinnamon captures the 2× framebuffer before downsampling to the output; this does not prove post-downsample exactness.
- **GNOME provisioning:** 28 preserved attempts refused before capture with `gnome_login_required`, installed extension 22 / loaded 0. No helper PNG/source summary exists for these refusals. After checking no Patrick apps were open, GDM was restarted, the desktop exited Activities visibly, and extension 22 loaded before the counted retry campaign.
- **GNOME user-style harness:** its first VNC connection exposed a remembered 960×600 region instead of the whole desktop, so the real-drag attempt produced no new capture. `user-invalid-vnc` retains it. Restarting `putgd-gnome-vnc.service` restored 1920×1080; the repeated user-style run uploaded one verified exact PNG, and its saved frame shows **Capturing**, ring and bar.

Mint's pre-existing stale “Local save failed” notification did not dismiss via its close button or notification API. Cinnamon was replaced in the same X11 session after checking for user apps; the stale layer cleared. The isolated resident was restarted afterward to restore its notification connection; a real new cap warning was saved. The final clean tray photo required restarting `putgd-native-vnc.service`: input hit the wrong place after the framebuffer scale changes until its dimensions were refreshed. A second Cinnamon replacement during this photo diagnosis left the same native X11 desktop active. Plasma's tray was restored with its `plasma-plasmashell.service` restart. No display server was restarted on d69 or m74, no VT shortcut was bound, and no CPU-starvation experiment was used.

## PR visuals, transfer and restoration

`pr-screenshots/` contains actual desktop frames for the new tray entry, both Settings fields, capturing ring/bar and cap notification on each desktop. All frames contain synthetic fixtures, private test paths or the idle desktop; no credential or protected login value is shown. Functional run screenshots, including failures, are also retained. The output used only isolated profiles under `/home/patrick/work/p31398` and synthetic uploads to each host's `127.0.0.1:19399`. Every session socket was checked before resident launch: **46 UTF-8 bytes**. Firefox was allowed 14 seconds to draw.

Export manifests were verified after transfer: d69 592 files, f44 629 files, Mint 713 files in the initial export; the later Mint photo cleanup has its own receipt. Raw evidence remains on the builders. The workstation holds downloaded CI artifacts, exported evidence and this report; it did no product build or desktop test execution.

All output scales and Cinnamon fractional settings were restored. Private shortcuts were restored. The GNOME AppIndicator extension was disabled again, RPM removed and GNOME re-logged in to unload the removed package extension. Test residents, UI helpers, fixtures and loopback receivers were stopped; all installed test packages were removed without purging pre-existing configuration. Console/session identity checks were recorded before and after. Locks released: d69 **01:59:48 UTC**, f44 **02:02:53 UTC**, Mint initial campaign **02:04:31 UTC**, and Mint photo lease **02:09:56 UTC**. All releases precede 07:15 UTC.

Left on each host: private raw evidence, isolated profiles, scripts and downloaded package under **`/home/patrick/work/p31398`**. Mint's normal Cinnamon session continues with its replacement process; Plasma's normal shell and GNOME's normal desktop/VNC service continue. Existing projects, user configuration, signing agent, wall services/tunnels, VMs and golden images were preserved. No test app or receiver is intentionally left running. This feature pass is not release or memory acceptance.
