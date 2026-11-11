# Scroll-capture VM acceptance, third pass — PR #1398

**Acceptance blocked. Omarchy produced inexact terminal PNGs: `postcap` returned `end_of_content` with notification pixels; the supplementary `cap-local` returned `height_cap` with notification pixels. Keep these as wrong images, even though no missing, repeated or out-of-order stitch has been demonstrated.** Omarchy also paints the cursor into Stop's viewport. Budgie's wide Qt text stops early in 3/3 runs. No product code was changed, built, committed or pushed, and no physical desktop lock was acquired.

Tested PR head `acf681fb0e52494a302e3641c04dd233f7585053`; green [CI run 42935796173](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42935796173). CI package merge commit `ebb5bd87b7da95fa78ff640733e5737c5d699f52`, tree `61e58ccfd3ca177352244a369212efdb018505c4`, version `26.1111.4656-dev+gebb5bd87b7da`. The merge identity in package names is expected. PR head remained unchanged and the PR remains a draft. Every guest ran this CI AppImage, SHA-256 `b71ddea5e7686d358206ba482b1d400c2dd58ff5f938df8b00c626095b8b9771`. Other downloaded packages were hashed but not run.

All four fresh KVM overlays ran on **d69, 192.168.68.69**, from the same goldens as pass 2, two guests at a time. Initial load was 0.24, available memory 29,862 MiB, KVM readable/writable. No new GPU HANG/GL_CONTEXT_LOST occurred after the repaired incident. Final host load was 0.28 and every owned VM PID and disk was absent. Run IDs, golden hashes, actual desktop/toolkit versions, socket lengths, package identities, saved visuals and retirement receipts accompany each desktop. App tests used private `/tmp/v3` directories and synthetic guest-loopback HTTP upload only. No real objects, bucket policy, versioning, credentials or protected login values were touched.

“Exact” rulers require every coded scanline and barcode interiors, expected height and no unexpected pixels. Text requires 1,500 edge-inclusive bands, 1,500 distinct band bitmaps and constant pitch; no OCR. Wide/narrow fixture widths were 1280/600, with 1260/580 px selections excluding the scrollbar strip. Fractional tests used a native Qt ruler at a verified 125%, allowing ±1 physical pixel at painted boundaries. These are scoped feature tests, not full release or memory acceptance.

| Desktop | Browser: exact / honest early / wrong / contaminated early | Agent-only MCP: exact / honest early / wrong | 24,000 px native ruler |
|---|---|---|---|
| neon / KWin 6.8.1 | Firefox **20 / 0 / 0 / 0** | **5 / 0 / 0** | 1/1 exact |
| Kubuntu / KWin 6.6.6 | Firefox **20 / 0 / 0 / 0** | **5 / 0 / 0** | 1/1 exact |
| Budgie / labwc 0.20.2 | Firefox **5 / 0 / 0 / 0** | not requested | **5/5 exact**, no lost_track |
| Omarchy / Hyprland 0.56.2 | Chromium **1 / 0 / 0 / 4** | not requested | 1/1 exact |

The 40 KDE Firefox and 10 agent-only MCP results are all exact, including PNGs located by the returned SHA. MCP used the official SDK stdio helper forwarding only to the production CLI, with no pointer or keyboard actions from that driver. Omarchy's four rapid repetitions are retained failures: `lost_track`, 800 px, containing the preceding Upload complete toast. They do **not** qualify as honest exact-prefix stops. No unsuccessful run was discarded from these counts.

| Desktop | GTK wide | GTK narrow | Qt wide | Qt narrow |
|---|---|---|---|---|
| Omarchy / Hyprland 0.56.2 | 3/3 | 3/3 | 3/3 | 3/3 |
| Fedora 45 Budgie / labwc 0.20.2 | 3/3 | 3/3 | 0/3 | 3/3 |
| neon / KWin 6.8.1 | 3/3 | 3/3 | 3/3 | 3/3 |
| Kubuntu 26.04 / KWin 6.6.6 | 3/3 | 3/3 | 3/3 | 3/3 |

**45/48 text runs complete exactly; 3/48 are honest exact-prefix lost_track stops, all Budgie Qt wide.** Those three retain 35 distinct visible bands at 17 px pitch in a 600 px image. Every text pixel matches the initial viewport; the rest matches its flat background with the reference screenshot's pointer excluded. See `b/qt-wide-prefix-verification.json`. Each helper says `Ambiguous offset 4 ... score 1.00 evidence 455`, twice, then “first step is ambiguous”; source fresh 1 / quiet 0, one retry, zero scroll-backs (slowest response 0, 9, 10 ms). **Component: ScrollStitcher first-step disambiguation on wide, near-periodic text**, not a quiet frame source. Narrow Qt is 3/3 complete. Pitches: Omarchy GTK/Qt 18/14; Budgie 18/17; neon 21/18; Kubuntu 18/18.

| Requested case | neon | Kubuntu | Budgie | Omarchy |
|---|---|---|---|---|
| Height cap: exact 2,000 px, warning, loopback upload | 1/1 | 1/1 | 1/1 | 1/1 |
| Stop halfway: exact retained prefix, upload | 1/1 | 1/1 | 1/1 | 1/1 |
| Stop during scroll-to-top: on-screen viewport | 1/1 | 1/1 | 1/1 | 0/1 raster; correct rows, cursor painted |
| Cancel: no history row or staging path | 1/1 | 1/1 | 1/1 | 1/1 |
| Halfway start, from-top on / off | 1/1 each | 1/1 each | 1/1 each | 1/1 each |
| 125% native Qt ruler | 1/1 | 1/1 | 1/1 | 1/1 |
| Shortcut, real drag, visible bar/ring, exact retained PNG | 1/1 | 1/1 | 1/1 | 1/1 after dismissing retained notifications |
| Next capture after own cap warning | 1/1 exact | 1/1 exact | 1/1 exact | **0/1: notification contamination** |

Stop-on-the-way-up row positions match the fixture's last logged position: neon 9,330; Kubuntu 7,500; Budgie 9,000; Omarchy 10,200 (600 px viewport). Omarchy's Stop PNG has **146 unexpected cursor pixels**, source fresh 1 / quiet 0, slowest response 68 ms. Normal Omarchy full-screen ruler capture has zero mismatches across every barcode pixel, cell edges and the right margin: the corner/48 px guard helps normal capture, but does not make Stop's current viewport cursor-free. **Component: Hyprland hidden-cursor frame acquisition/Stop interaction**, not a row-order stitch.

Omarchy `postcap` has 24,000 rows but 1,807 unexpected pixels in the first rows, source fresh 3 / quiet 0, slowest response 165 ms, no retries or scroll-backs. The separate local-route probe also retains notifications: `cap-local` has 18,368 unexpected pixels (fresh 1 / quiet 0, 3 retries/backtracks); `postcap-local` stops at 1,040 px with 22,490 unexpected pixels (fresh 1 / quiet 0, 4 retries/backtracks). Its initial cap raster already contains an older toast, so that supplementary raster does not isolate the stitcher. The notification-close observation does: the D-Bus trace records CloseNotification for IDs 29 and 28, both acknowledged by QuickShell with NotificationClosed reason 3, while saved mid-operation frames still show the preceding Saved locally card; a cap warning remains visible afterward. **Component: QuickShell notification presentation after acknowledged closes.** PNGs, helper logs, literal source summaries, step logs and complete frame timestamp sequences are retained in `failure-index.json` and the case directories.

The old Hyprland halfway failure did **not** reproduce: from-top on is exactly 24,000 rows from zero; off is exactly 12,000 rows from row 12,000. Helper source fresh 3 / quiet 0 for on (202 ms slowest), 2 / 0 for off (139 ms), no recovery. An instrumented Qt viewport plus Wayland client trace received both -10 batches and moved 12,000 → 11,400 → 10,800; single -1 notches moved to 10,740 and 10,680; +1 moved to 10,740. Neither Hyprland nor the application ignored those batches in this pass. This does not establish the cause of the old non-motion. `o/hypr-wheel.log` retains the protocol, QWheelEvent and position evidence.

All received loopback PNG payloads match archive hashes: neon **49/49**, Kubuntu **91/91**, Omarchy **26/26**, Budgie **30/30**. Totals include diagnostic captures; the requested cap/Stop PNG hashes are included. Raw multipart bodies and duplicate archive images remain private. Successful Cancel IDs and absence checks are in each `cancel-invariants.json`.

Harness problems are separate from product failures. Neon initially showed Firefox's welcome dialog; it was visibly dismissed before the 20 counted clean repetitions. Kubuntu's first wall forward collided with an existing unrelated Fedora tunnel: the first 20 Firefox, 5 MCP and 12 text results remain diagnostics, and **all 37 were repeated with the corrected live wall connection**. A malformed environment assignment prevented the first native long fixture from starting; a shell-quoted control predicate caused NameError and temporary scroll_active refusals. Those wrappers, active operation IDs and failed attempts were preserved, then the control script was corrected and all affected cases rerun. A live export/read race caused a transient verifier error; final quiescent exports match both descriptor and file-manifest SHA-256 and decode normally. Fedora's package is `python3-pyqt6-base`, not the old script's `python3-qt6`; this was resolved before any Budgie capture. On Hyprland, native Wayland pointer input was used to click the visible notification X and perform the final real selector drag. None of these setup errors is counted as a stitcher failure. `harness-index.json`, retained case directories and the final harness sources preserve the distinction.

All **four** overlays (`n3`, `k3`, `o3`, `b3`) were stopped and retired through lab.py after builder/workstation SHA verification. All owned wall entries and `putgd-vm-sv3-*` tunnel units were removed; the original five physical tiles remain connected. No physical desktop, other project, old evidence or immutable golden was removed. The unrelated pre-existing Fedora tunnel was preserved. Final cleanup is recorded in `host-cleanup.json`, `workstation-cleanup.json` and per-guest cleanup receipts.

Left on **d69**: `/home/patrick/work/svm1398/ci3.AppImage`, `v3*.py`, `v3evidence/`, `v3-harness.tgz`, source/tools and all four retired run directories with metadata/receipts; no owned QEMU process or overlay disk. Left on the **workstation**: this report, the sanitized record, downloaded CI artifacts, harness and private verified exports under `/home/patrick/work/rolling-capture-research/acceptance/`; no VM disk or golden. The worktree is clean and detached at the tested PR head. No full release, memory, native-package or physical-desktop acceptance is claimed.

| Downloaded package (artifact directory disambiguates DEBs) | SHA-256 |
|---|---|
| putgd-26.1111.4656-dev+gebb5bd87b7da-x86_64.AppImage | `b71ddea5e7686d358206ba482b1d400c2dd58ff5f938df8b00c626095b8b9771` |
| release-native-fedora44/putgd-26.1111.4656~dev+gebb5bd87b7da-1.fc44.x86_64.rpm | `3ef569ecb3a6d3c3d61a5ea76ae8cd3d216740c2c82759cc7939442f0e7e4a0d` |
| release-native-ubuntu24.04/putgd_26.1111.4656~dev+gebb5bd87b7da_amd64.deb | `30608ce6c45947b4be1ccc66f91d4c079897045495a9b5e739b875f1f3e48759` |
| release-native-archlinux/putgd-26.1111.4656dev.gebb5bd87b7da-1-x86_64.pkg.tar.zst | `fce33041163d10b8f5974af7ed6cdb88c8ea32e782edfb4bf55ed5e6207e9347` |
| release-native-debian13/putgd_26.1111.4656~dev+gebb5bd87b7da_amd64.deb | `135cc78c0abbef96ecc8504b65f9e631f4dfca306227f273ce2aba100b954b90` |
| release-native-ubuntu26.04/putgd_26.1111.4656~dev+gebb5bd87b7da_amd64.deb | `8c6ccd5d7d3c18491a353a96d1bc332d72b8433f3f130840a7f6cf3036b0b174` |

Every downloaded file, including build metadata, is hashed in `package-sha256.json`. `SHA256SUMS.json` hashes the exported public evidence. The harness bundle includes actual fixture/verifier/CLI bridge sources and the official-SDK lock; it excludes private keys, profiles, credentials and raw multipart bodies.
