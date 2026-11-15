# GNOME 50 acceptance

Fedora 44, GNOME Shell/Mutter 50.6, native Wayland, Firefox 158.0.1. CI43654654765 AppImage, required tree `bd64ffc5ac593690430bdbabb7e1f9ce6964de7e`, proved by diagnostics. Every destination was local. No system package was installed or compiled. The coordinator decides acceptance.

The main corrected matrix used the native measured viewport `[0,117,1920,963]`. Firefox reported workarea-relative Y85, omitting the32px Shell panel. The earlier wrongly selected rectangle, its images and analysis are preserved under `page-geometry-attempt1`; those scores are not product failures. Some supplemental viewport metadata retained the harness's default Plasma label; native session identity is established by package proofs, GNOME extension state and the actual native pictures.

Full metrics and protocol checks are in [scores](analysis/scores-f44-final.json) and [protocol checks](analysis/scoring-f44/protocol-checks.json). Seconds in score output are harness wall time; use `capture.elapsedMs / height *10` for seconds per10,000px.

| Page | You scroll: tolerant bands, placed/skipped | Auto: tolerant bands, placed/skipped |
|---|---|---|
| Wikipedia |377/377,286/0|374/377,616/0|
| Stack Overflow |780/812,609/9|789/812,2902/304|
| GitHub |719/722,476/35|714/722,1878/0|
| Python |814/814,605/0|814/814,2941/0|
| News |32/110,90/31|77/112,127/0|

Source rates were31.6–34.9fps. Stack Overflow and Python stopped at the52,083px budget: row2 permits this; row1's literal whole-page/untruncated requirement is not met. The news image has pinned ad/video fragments and changing video/ad content. Row matching found the known late220px playlist insertion: image3000→reference3220,5000→5220,6000→6220. The paired pictures are in `analysis/`. Published nightly with its own extension22 also lost this article early:1095px of6316,6.3s. This does not establish that every candidate news artifact is identical to nightly.

Extension24, loaded after login: **10/10 fixed and10/10 random first-click stops, no post-hand injections**, stable Shell PID throughout, independent read-only cursor observer. See `gnome-ext24/`. Extension23 still loaded after installing24 files without login: **2/10 fixed and9/10 random**,70+2 post-hand injection lines, including one put-back. See `gnome-ext23/`. The published nightly with its own loaded22 reproduced pointer fighting:1/3 fixed,1/3 random first-click stops; all six had post-hand injections. Its native Stop calibration and pre-click states are retained under `b/nightly-pointer-comparison/`. These failures predate the candidate; the stale-extension path still fails the stated gate.

The native End/Ctrl+End/Home keys did not reach Firefox during either capture driver. The same trusted key events worked before and after capture, and wheel input worked during it. Published nightly with its own22 reproduced this suppression. Global Ctrl+Shift+F7 still named itself on the bar and saved the image. Consequently native End recovery is a pre-existing failed path. Separately, actual live-page script jumps produced Lost/Found and Auto-lost/Found; real relative Auto-scroll resumed. Their exact-image comparisons were19/19 user,372/374 auto recovery,86/86 mixed-input. Script jumps do not replace the native-key result. A25-notch animated burst was followed,373/377 bands, as the supplied round4 recipe predicts.

Full-screen captures: user377/377 and auto373/377 bands after the explicitly recorded117px browser-UI crop; hiddenCells5760 and hiddenRows72 in both. Real inside Done and Cancel worked for both drivers. The native GNOME bar is white: the dark-bar scan was supplemented by its dark Done-button control, which was positively detected in native bar photos and absent at every image row. Both tails were visually inspected; see [scan](analysis/f44-gnome-white-bar-scan.json).

Done's final screen was checked against real native framebuffer pictures taken during Saving, before the stop reply: Wikipedia15/15, GitHub14/14, news10/10, outside actual fixed/sticky DOM boxes and the control bar. See [native comparison](analysis/f44-native-last-screen.json). Earlier browser screenshots had a one-pixel rendering phase difference; later post-Done screenshots could acquire hover previews. Their raw comparisons remain available and are not used as final-frame failure evidence. The news browser also inserted45px of UI while loading; that UI is explicitly excluded from the native page comparison.

CLI and official-SDK MCP control/stop/cancel passed, including exact canceled-operation absence from History/staging and a hash-verified kept MCP stop image. The toggle during finishing returned `scroll_busy`, whereas the checklist requests `scroll_state`; the image was kept. The old published protocol lacks the new toggle, so its invalid-request reply is not a direct regression comparison. Auto blank and its notice/History/inspect note were observed. The [completed default-driver supplement](supplement/README.md) proves an actual real-wheel crossing and correct Lost state; the initial manual attempt alone did not establish crossing.

The supplemental settings-obscured attempt and asynchronous History-admission harness attempts are preserved. No image was lost by Done in those attempts: later exact operation lookups found and hash-verified the admitted files. The corrected harness waits for admission. The pointer runner's mutable `sys.argv` caused its pointer-only flag to be lost after the20 trials; the additional race/inside trials are retained separately and do not replace the main extension24 evidence.

Cleanup: no product/helper/browser process or lab input device; scope inactive; both extracted AppImage runtimes removed (1388files), original inputs retained non-executable; original mouse settings and extension files/lists restored exactly after a final GDM login. The read-only cursor observer's exact two files were removed. Native clean desktop was visually verified. Lease released05:23:07UTC with a successful cleanup check. See [cleanup](cleanup-receipt.json) and [release](lock-release.json). Original large passed images remain private with hashes in `restore-index.json`; difficult-page images, results, native state pictures, helper logs and all test adapters are included here.

The [completed blank supplement](supplement/README.md) includes final10:55:10 cleanup, original extension/mouse restoration and preserved pre-capture RFB/focus calibration failures.
