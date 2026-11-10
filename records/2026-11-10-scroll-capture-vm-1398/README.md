# Scroll capture VM acceptance — PR #1398

**Acceptance blocked; this is an incomplete acceptance round.** Exact CI run 42897860301, head `fe8cd713a22f2c68207de76e43da5f0e56d95243`; CI merge/build commit `e3c1bd6b840a0aae351918bd4c6ef481bfa82d88`, version `26.1110.4635-dev+ge3c1bd6b840a`. Tools archive detached at the PR head; no product code changed, compiled or pushed. All four fresh KVM overlays ran on d69 (192.168.68.69), initially 28 GB available and negligible load. No physical desktop lock was acquired.

The three most important answers:

- **Hyprland: YES, the real helper captures and stitches.** `o/narrowtop` has a 608×2400 PNG, every scanline exact, `end_of_content`, with image-copy frames and wlr virtual-pointer injection. The standalone no-first-frame failure does not reproduce with the real helper. Native Arch package acceptance is blocked separately below.
- **Plasma ≤6.7 AppImage: YES.** KWin 6.6.6 advertises fake input; `k/finecap` is an exact 1280×2000 prefix with `height_cap`; `k/plainclean` is an exact 1280×2400 full page. AppRun writes `Exec="/tmp/.mount_putgd-kekGJH/usr/bin/putgd-record"` and `X-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1,org_kde_kwin_fake_input`. The resident runs from the same mount. No injection_unavailable or executable mismatch was observed. `k-permission.log` preserves the entry.
- **Budgie: YES with the supplemental AppImage.** Hidden-cursor image-copy plus virtual pointer captures the 2400 px ruler and 2480 px sticky ruler exactly. The requested native RPM acceptance was not established.

Artifacts downloaded directly from the specified CI run (not rebuilt):

| Artifact | SHA-256 |
|---|---|
| putgd-26.1110.4635-dev+ge3c1bd6b840a-x86_64.AppImage | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| putgd-26.1110.4635dev.ge3c1bd6b840a-1-x86_64.pkg.tar.zst | `04ec144a666e973582c1a94268469f49687d875aba50f33636b2a8c485e03281` |
| putgd-26.1110.4635~dev+ge3c1bd6b840a-1.fc44.x86_64.rpm | `4ca190067df69d39ab02dbe05b65756367b952fa63a1b8a945cfebaa7a92e855` |

**Package limitations.** The Arch package installs after syncing the disposable guest databases and resolving runtime dependencies, but its binaries cannot load `libcrypto.so.4`. Both Omarchy's installed package and pinned repository provide OpenSSL 3.6.5 / libcrypto.so.3. `omarchy-runtime.txt` records the dependency failure. This is a packaging/ABI compatibility blocker, not an injection or frame-source result. The Fedora 44 RPM does not resolve its FFmpeg 8 sonames on the Fedora 45 probe golden (`budgie-install-retry.log`). That cross-version install failure is not a claim about the RPM on Fedora 44. A Fedora 44 Budgie native-RPM run remains required. The AppImage on Budgie and Omarchy is supplemental evidence, not a substitute native-package pass.

**Common result limitations.** All successful images were saved through the production still-image/history route, but **no upload destination was configured** (`uploadStatus: local_only`). No upload acceptance is claimed. The complete screenshot/notification/agent/fractional-scale/memory matrix is unfinished. No desktop receives overall acceptance.

Each case row below records the exact AppImage SHA-256. `pass` is limited to the stated sub-check; a case with unmet required upload/visual/evidence conditions is `fail` or `not run`. Native fixture cases use Python GTK4 or installed Kate/PyQt, never a compiled substitute.

| Desktop | Case | Status | Observation / missing gate | Artifact SHA-256 |
|---|---|---|---|---|
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Chromium plain ruler | pass | narrowtop: exact 608×2400, every scanline, end_of_content; local save only. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Sticky header/footer | not run | Attempt overlapped GTK fixture launch; preserved as invalid harness evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Native GTK4 | fail | nativegtk: returned end_of_content at 700 px on a 1500-line text document. Page movement/readability gate not established. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Native Qt | not run | PyQt6 missing; qt.log preserved. No native Qt application capture established. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Height cap + notification + upload | fail | MCP reached height_cap at 2000; warning screen saved, upload absent. Earlier 1280-wide verifier attempt was invalid because canvas was 608 wide. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Stop halfway | fail | Stop happened during from-top rewind and cancelled before any rows; retained-prefix/upload gate not met. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Cancel | pass | cancel: no new history row; final staging-file inventory empty. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Shortcut + real drag + ring/bar | fail | Shortcut opened selector; first drag missed, retry made selection. Required during-capture bar/ring frame not established. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Agent-only MCP | fail | Official SDK prepare/start/inspect reached height_cap through production CLI, no driver input. Separate MCP PNG export/verification and upload remain incomplete. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Native compiled fixture window | not run | CI artifacts do not contain the native ruler fixture; no compilation was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Second browser | not run | Only Chromium on Omarchy and Firefox on the other three guests were exercised. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Halfway, from-top on | not run | From-top was exercised from prior scroll positions, but a controlled halfway start was not recorded. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Halfway, from-top off | not run | Off was exercised for Stop; a controlled halfway-start full capture remains required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Fractional scale | not run | No fractional-scale campaign was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Tray entry screenshot | not run | No tray-menu screenshot was saved. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Omarchy 4.5.0-3 / Hyprland 0.56.2 | Memory after 180 s idle | not run | Final RSS/PSS snapshots only; no 180 s quiet idle gate. Open putgd-ui processes on o/b/n make these unsuitable idle evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Firefox plain ruler | pass | plainfull: exact 1280×2400, end_of_content; local save only. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Sticky header/footer | pass | sticky: exact 1280×2480; header/footer once, body exact. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Native GTK4 | fail | nativegtk: lost_track after 700 px despite GTK adjustment movement. Matcher/loop continuity gate failed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Native Qt | fail | nativeqt did not complete a usable capture; see raw result and qt.log. Native application readability gate incomplete. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Height cap + notification + upload | fail | finecap: exact 1280×2000, height_cap and history note; separate visible warning screenshot not established; no upload. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Stop halfway | fail | stop: stopped, exact 800-px prefix from row 0 on re-verification; stopoff starts at pixel 1600 and is also exact. No upload. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Cancel | pass | cancel/canceloff: history unchanged; final staging-file inventory empty. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Shortcut + real drag + ring/bar | fail | Shortcut opened real selector; drag started automatically; user-bar.png shows ring and bar outside selection (rewind phase). Capturing-phase frame still required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Agent-only MCP | fail | Official SDK prepare/start/inspect reached height_cap. No upload; separate MCP raster verification incomplete. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Native compiled fixture window | not run | CI artifacts do not contain the native ruler fixture; no compilation was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Second browser | not run | Only Chromium on Omarchy and Firefox on the other three guests were exercised. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Halfway, from-top on | not run | From-top was exercised from prior scroll positions, but a controlled halfway start was not recorded. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Halfway, from-top off | not run | Off was exercised for Stop; a controlled halfway-start full capture remains required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Fractional scale | not run | No fractional-scale campaign was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Tray entry screenshot | not run | No tray-menu screenshot was saved. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | Memory after 180 s idle | not run | Final RSS/PSS snapshots only; no 180 s quiet idle gate. Open putgd-ui processes on o/b/n make these unsuitable idle evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Firefox plain ruler | fail | plainclean: lost_track at 1205 px even after warnings dismissed. Raw PNG and fresh-frame/recovery helper timeline retained. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Sticky header/footer | pass | sticky: exact 1280×2480, end_of_content. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Native GTK4 | not run | GTK4 namespace absent; attempted nativegtk actually captured browser, invalid as GTK evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Native Qt | not run | Fixture setup failed after missing GTK process; attempted nativeqt is not accepted as native Qt evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Height cap + notification + upload | fail | finecap: exact 1280×2000, height_cap and note; no upload, separate warning screenshot not established. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Stop halfway | fail | stopoff: stopped and exact 1007-px prefix from pixel 0 on re-verification. No upload. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Cancel | pass | cancel/canceloff: history unchanged; final staging-file inventory empty. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Shortcut + real drag + ring/bar | fail | Real shortcut/drag automatically started; user-bar.png shows ring/bar during rewind. Capturing-phase frame still required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Agent-only MCP | fail | Official SDK path completed with lost_track; not a complete capture. Separate returned-raster export incomplete. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Native compiled fixture window | not run | CI artifacts do not contain the native ruler fixture; no compilation was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Second browser | not run | Only Chromium on Omarchy and Firefox on the other three guests were exercised. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Halfway, from-top on | not run | From-top was exercised from prior scroll positions, but a controlled halfway start was not recorded. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Halfway, from-top off | not run | Off was exercised for Stop; a controlled halfway-start full capture remains required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Fractional scale | not run | No fractional-scale campaign was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Tray entry screenshot | not run | No tray-menu screenshot was saved. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| neon / KWin 6.8.1 | Memory after 180 s idle | not run | Final RSS/PSS snapshots only; no 180 s quiet idle gate. Open putgd-ui processes on o/b/n make these unsuitable idle evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Firefox plain ruler | pass | plainclean: exact 1280×2400, end_of_content. Earlier repeats contaminated by old warnings are preserved. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Sticky header/footer | pass | sticky: exact 1280×2480, end_of_content. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Native GTK4 | fail | nativegtk: end_of_content at 700 px on a 1500-line document. Injection replies alone do not prove delivery; application continuity gate failed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Native Qt | fail | nativeqt: lost_track at 600 px; readability/continuity gate failed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Height cap + notification + upload | fail | finecap: exact 1280×2000 with height_cap and history note; no upload, separate visible warning screenshot not established. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Stop halfway | fail | stop: exact 800-px prefix from pixel 0; stopoff exact 1007-px prefix from pixel 1393. No upload. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Cancel | pass | cancel/canceloff: unchanged history and final staging-file inventory empty. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Shortcut + real drag + ring/bar | fail | Real shortcut/drag; user-bar.png shows ring and bar outside selection during rewind. Capturing-phase frame still required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Agent-only MCP | fail | Official SDK path completed with lost_track. Returned-raster export/verification incomplete. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Native compiled fixture window | not run | CI artifacts do not contain the native ruler fixture; no compilation was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Second browser | not run | Only Chromium on Omarchy and Firefox on the other three guests were exercised. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Halfway, from-top on | not run | From-top was exercised from prior scroll positions, but a controlled halfway start was not recorded. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Halfway, from-top off | not run | Off was exercised for Stop; a controlled halfway-start full capture remains required. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Fractional scale | not run | No fractional-scale campaign was performed. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Tray entry screenshot | not run | No tray-menu screenshot was saved. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |
| Kubuntu 26.04 / KWin 6.6.6 | Memory after 180 s idle | not run | Final RSS/PSS snapshots only; no 180 s quiet idle gate. Open putgd-ui processes on o/b/n make these unsuitable idle evidence. | `bf2f6655bea59f0ecb5fe03d24f27141e3873367664d63262fdcae6ba29911a7` |

Failure analysis and harness corrections:

- The original probe HTML's 40-pixel uniform barcode rows cause `Ambiguous`/`lost_track`. The finer canvas ruler uses the shipped ScrollRuler.h pattern, including ten unique scanlines per row. Do not count the periodic-page failures as absence of first frames.
- Plasma warnings from earlier cap captures appeared in subsequent PNGs (notably n/plain/capture.png), creating false matching/recovery conditions. This is UI/notification interference, not injection unavailability. Clean warnings before a fresh acceptance case. Neon also failed a clean full-page trial; helper logs identify `LostTrack` after stream/recovery movement. This round does not establish whether that clean failure predates this build.
- Selecting only 700 of an 800-pixel viewport omits the bottom 100 pixels. The b/plain 2300-pixel result was a harness geometry error, corrected to full viewport for plainfull.
- Omarchy created its canvas while Chromium was tiled, so it was 608 pixels wide even after fullscreen. Corrected capture/verifier width to 608; narrowtop passed.
- The shared driver initially requested history limit 1000, rejected by the production maximum 200. scroll_run_vm.py changes that request to 200 and otherwise preserves the driver. cap1 and failed staging attempts remain. Missing Pillow on Omarchy was installed from its normal package repository before corrected verification.
- The MCP SSH transport initially failed to forward --params-stdin and exit status. Corrected vm_mcp_cli.py translates the input to an argument to the same production CLI. The first attempt is saved as *-mcp-harness-failed.json; those are not product MCP failures.
- The general driver treats a stopped-before-first-frame cancellation as a passing Cancel. This report explicitly rejects it as Stop evidence. Re-verification of retained Stop PNGs searches a unique starting scanline and checks the entire prefix; see analysis.json.
- MCP terminal envelopes and helper/resident logs were exported, but the separate raster for each MCP operation was not collected before overlay retirement. This evidence gap prevents an MCP image-exactness claim. No missing evidence is represented as a pass.

Identity and retirement:

| Guest | Run ID | Immutable golden SHA-256 |
|---|---|---|
| o: Omarchy 4.5.0-3 / Hyprland 0.56.2 | `dff6be62-ec00-4b0b-a59e-cfed784619d0` | `bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256` |
| b: Fedora 45 / Budgie 10.10.3 / labwc 0.20.2 | `15d19f92-ac2d-4792-ba33-f638217ab827` | `a6749512438d507ef2b2c47fe675955627464d9a5a85341002f91cd54fb401ad` |
| n: neon / KWin 6.8.1 | `2b466887-5bd4-4308-9da2-59a10f7c4244` | `191852a5b552492daa9eac1093acd7e15578b0cc5374f4c9a660037af5863238` |
| k: Kubuntu 26.04 / KWin 6.6.6 | `f563f321-9099-4d01-98a3-6f6662b69135` | `49fcacff969b81ac38e36fefdf21407d20c82187e1725c58f128a3b76065a81c` |

All four ran with KVM and live localhost VNC forwards on workstation ports 5940/5942/5944/5946. Saved VM visuals, state, exact resident binary hashes, final memory snapshots, CLI transcripts and helper/resident logs are in the per-guest evidence directories. No credential was configured or captured. Final staging inventories are empty. Guarded cleanup receipts show each overlay retired after checksum-verified export; original QEMU PIDs are absent. Only this worker's four wall entries and putgd-vm-svm1398-{o,b,n,k} units were removed.

Left on d69: `/home/patrick/work/svm1398/` with the source archive, three CI artifacts, locked MCP environment, scripts, guest run metadata, exported evidence, analyses, private per-run lab keys, UEFI variables where applicable and cleanup receipts. No QEMU process or overlay disk remains for these runs. Goldens, physical desktop work and other projects were preserved. On the workstation the acceptance directory contains the report, artifact copies and verified evidence exports; no golden or overlay disk was stored there. Product worktree remains clean and detached at fe8cd713a.

Remaining acceptance work is explicit in the table: matched native packages, the controlled halfway/fractional cases, both browsers, complete native-app gates, tray/capturing-phase/notification visuals, exact MCP PNG export, real upload, and the 180-second idle gate. This report does not close issue #1376 work item 8.
