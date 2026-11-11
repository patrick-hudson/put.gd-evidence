# Final scroll-capture acceptance — PR #1398

**Acceptance blocked: one wrong admitted image on Omarchy.** Wide Qt text run 2 returned `end_of_content`, 1,260 × 19,920, with only 1,422 of the 1,500 numbered lines. Lines **0–77 are missing**. The retained bands match lines 78–1,499 of the complete same-font run, consecutively, with no unmatched band. This is a wrong image under the requested rule, not an honest early stop.

[Wrong PNG](guests/ofin/cases/qt1280-2/capture.png) · [helper log](guests/ofin/cases/qt1280-2/helper.log) · [result and operation ID](guests/ofin/cases/qt1280-2/result.json) · [complete band mapping](guests/ofin/qt-wide-missing-prefix.json).

PNG SHA-256: `07e5806c27ebfbe2d0a38cadcc05ada30848dd51fe2295efa3b35a3e5d2f3efb`.

Helper: `scroll: source fresh 2, quiet 0, unproven 0, slowest response 156 ms, retries 0, scroll-backs 0`. The capture had `fromTop 1`. Its 46 upward batches consumed the 15-second scroll-to-top budget; downward capture then began at line 78. Source inspection identifies **ScrollRun::wayToTop completion handling**: exhaustion of `toTopLimitMs` falls through to normal capture without proving the top. The retained suffix stitches correctly; the missing prefix is silently admitted as `end_of_content`. This is not attributed to quiet acquisition frames or the text matcher.

Tested PR head **`0a5010c073d23baf7b3565b644ef97c0f608a070`**, unchanged at start and finish. [CI run 42957942901](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42957942901) was checked with `gh pr checks 1398`: CI summary passed, 16 checks passed and four conditional/non-required checks skipped. Artifacts were obtained with `gh run download`. They identify GitHub merge **`0b36fa3b9e741dcceb9e4fed440f7f6babf334bc`**, tree `41c3b9a7cf47ad258d9d590081a71baf3ccc81e2`, version `26.1111.4665-dev+g0b36fa3b9e74`; that merge's second parent is the tested PR head. [Source identity](SOURCE.json), [merge parents](merge-identity.json), [all 679 downloaded-file hashes](package-sha256.json), and [the separately downloaded selected-artifact hashes](selected-artifact-sha256.json) are retained. No product was compiled, edited, committed or pushed. The worktree is clean and detached at the requested head; the PR remains a draft.

Installed inputs:

- m74 Ubuntu 24.04 DEB: `c8bad62842eaabfeb965f67e7ca2f580106dc2b2f4f84c166daad64ce7a16c43`.
- f44 Fedora 44 RPM: `48ceb6429bd2462c2f60de3f1e4f16ab38d31b9a1156c8360441806b5a84e5fa`.
- d69 Debian 13 DEB: `5da248aca8a225909e9c21d27f29062ed5ef8ea98675dcee2dcbd86ea8d9aa59`.
- Every guest's CI AppImage: `8702da9d21f6d9c1f5a0f8b7155e5921b3163d6a44ef6e90795ee0b0fb1b8304`.

**E** = exact completed content, or an exact intentionally capped prefix; **H** = honest intentional Stop with an exact prefix/current viewport and `stopped`; **W** = wrong admitted PNG; **C** = clean Cancel with no PNG, history row or staging file; **N** = not run. Text cells require 1,500 distinct, edge-inclusive bands at a constant pitch. Every listed run used this same build.

| Case | m74 Cinnamon X11 | f44 GNOME Wayland | d69 Plasma 6.3.6 | Omarchy Hyprland | Budgie labwc | neon KWin 6.8 | Kubuntu KWin 6.6 |
|---|---|---|---|---|---|---|---|
| Qt ruler, 2,400 px | 5 E | 5 E | 5 E | 5 E | 5 E | 5 E | 5 E |
| Browser ruler | 5 E | 5 E | 5 E | 5 E | 5 E | 5 E | 5 E |
| Qt text, wide | 2 E | 2 E | 2 E | 1 E / 1 W | 2 E | 2 E | 2 E |
| Qt text, narrow | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E |
| GTK 4 text, wide | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E |
| GTK 4 text, narrow | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E | 2 E |
| Qt ruler, 24,000 px; cap 40,000 | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Applied cap 2,000; warning + loopback upload | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Immediate capture after cap | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Three rapid captures | 3 E | 3 E | 3 E | 3 E | 3 E | 3 E | 3 E |
| Stop halfway | 1 H | 1 H | 1 H | 1 H | 1 H | 1 H | 1 H |
| Stop during scroll-to-top | 1 H | 1 H | 1 H | 1 H | 1 H | 1 H | 1 H |
| Cancel; no row or staging files | 1 C | 1 C | 1 C | 1 C | 1 C | 1 C | 1 C |
| Halfway start, from-top on | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Halfway start, from-top off | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Fractional scale | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Agent-only MCP; PNG fetched | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| Safe shortcut + real drag | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E | 1 E |
| **Totals** | 29 E / 2 H / 1 C | 29 E / 2 H / 1 C | 29 E / 2 H / 1 C | 28 E / 2 H / 1 W / 1 C | 29 E / 2 H / 1 C | 29 E / 2 H / 1 C | 29 E / 2 H / 1 C |

**Totals: 202 exact completed PNGs, 14 honest intentional Stop PNGs, 1 wrong PNG, 0 not run, and 7 clean Cancels: 224 requested observations.** There were no unplanned `lost_track` results in the requested matrix. The fourteen H results are the two requested Stop cases on each desktop. Supplementary captures and invalid harness attempts are retained separately and do not inflate these totals.

Physical sessions were Mint 22.3/Cinnamon X11 on m74, Fedora 44/GNOME 50.6 native Wayland on f44, and Debian 13/Plasma 6.3.6 native Wayland on d69. Guests used Omarchy/Hyprland 0.56.2, Fedora 45 Budgie/labwc 0.20.2, KDE neon/KWin 6.8.1, and Kubuntu 26.04/KWin 6.6.6. All guests ran fresh KVM overlays on d69, at most two at a time, visibly exposed on the display wall. Main run IDs and golden identities accompany their install and cleanup receipts. Two additional fresh overlays verified Budgie and Kubuntu cap-banner presentation on the same AppImage.

The prior harnesses under `acceptance/`, the builders' `/home/patrick/work/p31398`, and d69's `/home/patrick/work/svm1398` were reused through new scripts/profiles under `/home/patrick/work/pfin` and `/home/patrick/work/sfinal`. Native session sockets were 44 UTF-8 bytes; guest session sockets were 34, QMP paths 59/60, and the Hyprland runtime IPC paths were checked by the guest initializer. No overlong path was used. Firefox was allowed at least 14 seconds to draw; Omarchy used Chromium. Only synthetic fixtures and guest/host-loopback HTTP receivers were used.

Rulers were checked on every scanline, including full barcode cells and their right margin, for row order and unexpected pixels. Fractional cases check every physical scanline with the existing one-physical-pixel boundary allowance. Text verification counts bands touching image edges and checks distinct bitmaps and constant pitch; no OCR was added. The failed Omarchy output additionally has a complete bitmap-to-line mapping against its successful first run. All supplemental ruler PNGs also passed their applicable verifiers.

Fractional results are exact: GNOME 125% reaches `end_of_content`, 1,200 × 3,000, with `fresh 3, quiet 0, unproven 0`; its shipped extension was installed and reloaded by re-login before testing. Plasma and all four guests passed at 125%. Mint passed at 150% output scale using the corrected 2× framebuffer rectangle, 1,920 × 4,800; this verifies Cinnamon's framebuffer before output downsampling, not post-downsample pixels.

Stop-on-the-way-up PNGs match each fixture's final visible position: m74 20,400; f44 20,400; d69 21,600; Omarchy 11,340; Budgie 10,140; neon 9,930; Kubuntu 7,500. Full barcode/margin checks find zero pointer pixels. Cancellation operation IDs and empty history/staging matches are retained per desktop. All seven agent-only MCP operations used the official SDK stdio helper forwarding to the production CLI, with no driver pointer/keyboard actions during the operation; their fetched PNGs match the returned SHA-256 and pass verification. User-style cases used Ctrl+Shift+F7/F9 and a real selector drag. No Ctrl+Alt+F-key was bound.

Each applied-cap PNG is exactly 2,000 pixels, its warning names 2,000, and its loopback payload SHA matches. Every immediately following capture is exact. Budgie's banner is absent while the fixture is fullscreen and visible after it closes; [supplemental visual](guests/bfin2/cap-after-fixture-close.png). Kubuntu explicitly reports notifications received during fullscreen Do Not Disturb, then shows the cap banner after the fixture closes; [supplemental visual](guests/kfin2/cap-after-fixture-close.png). These presentation checks used the same CI AppImage, with no product/settings workaround. Omarchy's full-screen browser repetitions and post-cap capture have no retained notification pixels; its Stop viewport has no painted cursor.

Harness failures remain separate from the product finding. Eight initial neon browser/rapid attempts hit Firefox's welcome dialog and refused `scroll_no_movement` without a PNG (`fresh 9, quiet 0, unproven 0`; component: browser fixture prerequisite). The dialog and helper logs remain under `harness-firefox-consent-*`; after a visible Continue click, all eight were repeated against the unobstructed ruler and are exact. GNOME's first Cancel photo used the wrong VNC port after its RPC had cancelled successfully (component: photo wrapper); it was repeated with port 5901. Two supplementary GNOME warning preparations overlapped MCP and refused `scroll_active` (component: campaign scheduling); the warning probes were repeated serially. Those refusals have no PNG or helper source summary. Budgie's first dependency setup stalled downloading zchunk metadata; an owned, synced disposable-guest reset and a zchunk-disabled retry resolved it before product tests. Early boot/setup probes, a supplemental log-collector quoting failure, and earlier export snapshots are preserved privately; final exports were made quiescent and checksum verified. No unsuccessful product PNG was discarded or relabelled as a pass.

All native test packages were uninstalled without purging existing user configuration. The three extra Fedora runtime packages brought by the RPM were removed. Output scales and shortcuts were restored; GNOME's removed extension was disabled and unloaded by re-login, and its wall VNC was restored. No user application was closed. Test residents, fixtures and HTTP receivers were stopped. Lease cleanup checks passed: m74 released **05:02:08 UTC**, f44 and d69 **05:03:18 UTC**. All six overlays (`ofin`, `bfin`, `nfin`, `kfin`, `bfin2`, `kfin2`) were retired through guarded `lab.py cleanup` after verified export; their exact PIDs/disks are absent and goldens remain. Owned wall entries/tunnels were removed and the original five physical tiles preserved. Final host cleanup is recorded in [host-cleanup.json](host-cleanup.json) and [workstation-cleanup.json](workstation-cleanup.json), before the **07:15 UTC** deadline. No CPU/GPU load experiment ran on d69.

Left on m74 and f44: private raw evidence, isolated profiles, scripts and downloaded installers under `/home/patrick/work/pfin`. Left on d69: the same native evidence plus `/home/patrick/work/sfinal` (CI AppImage, drivers, verified exports and receipts) and retired run metadata under the existing lab checkout; no owned VM or overlay disk remains. Existing projects, desktop services, signing agent and goldens were preserved. Fedora's dnf install/remove logs report invalidation of a pending offline transaction; no broad OS update was run. The workstation retains CI artifacts, private exports, this report and the sanitized record under `acceptance/final`; it holds no VM disk or golden. No test app, receiver or owned tunnel remains running. This is feature acceptance, not release or memory acceptance.
