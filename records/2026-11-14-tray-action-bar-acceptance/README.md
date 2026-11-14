# PR 1532 tray and action bar acceptance — revised campaign

The revised campaign is finished. **W7 fails on KDE: resizing the candidate to 1,060 pixels can erase the output summary while “Settings save automatically” remains visible.** The candidate DEB and AppImage show this; the published nightly AppImage retains the summary at the same width. A native UI restart restores it, so this is a resize-path regression, not a claim that the summary is always absent at that width.

The requested tray state sequences pass on all five desktops. T9's recording/upload/failure combination passes on each; its **update portion is NOT RUN** because the exact candidate is a development build whose production update API refuses checks. T5's four missing-shortcut-hint failures are retained as established pre-existing nightly behavior, without repeating them. This is not an all-checklist-pass result.

The [accepted frame index](frames.md) provides each row's full, unmasked and uncropped real desktop frames. [Machine-readable results](results.json), [frame mappings](evidence-index.json), per-host `r2/*/trace.jsonl`, and restoration receipts are included. The [initial report](initial-report.md) and [initial results](initial-results.json) are preserved for audit; this report supersedes their unfinished verdicts and the earlier inconclusive GNOME/Cinnamon click facts.

## Build and scope

The checkout was fetched and detached at **f63d24dbcef39f8744330bec7a80f2bc340092d5**. All candidates came from CI run **43643204150**, native release artifacts and release-appimage; no compilation was performed. CI compiled merge commit b91a65c2ee63aac84093343a384ff085ad0c0f42. Its tree equals the requested head's tree:

**7290d67885b6782efd871ac7b1c2d1787e03e525**

Each resident's production `diagnostics.build.gitTree` was checked before acceptance. Fresh continuation proofs: [KDE](r2/k72/candidate-build.json), [GNOME](r2/f44/candidate-build.json), [Cinnamon](r2/m74/candidate-build.json), [Budgie](r2/budgie/candidate-build.json), [Hyprland](r2/hyprland/candidate-build.json). [Artifact checksums](candidate-package-sha256.json) retain relative artifact paths to distinguish the identically named Ubuntu packages.

The user's revised scope takes precedence over the original checklist: W3–W9 on KDE, W4/W5 again on Cinnamon; T2 on KDE/Cinnamon; T10 on KDE/Hyprland; T11 changes delay and output in the window; T13 opens History and runs region, repeat and one other capture (desktop). KDE W1/W2/W10 remain passes retained from the initial exact-tree run. Other desktops' window rows are omitted. T12 records facts, not pass/fail. The user's serial desktop instruction takes precedence over AGENTS.md's general parallel release-check instruction; no subagents were used.

## Updated verdicts

| Row | KDE | GNOME | Cinnamon | Budgie | Hyprland |
|---|---|---|---|---|---|
| T1 | PASS | PASS | PASS | PASS | PASS |
| T2 | PASS | NOT RUN | PASS | NOT RUN | NOT RUN |
| T3 | PASS | PASS | PASS | PASS | PASS |
| T4 | PASS | PASS | PASS | PASS | PASS |
| T5 | PASS | FAIL | FAIL | FAIL | FAIL |
| T6 | PASS | PASS | PASS | PASS | PASS |
| T7 | PASS | PASS | PASS | PASS | PASS |
| T8 | PASS | PASS | PASS | PASS | PASS |
| T9 | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| T10 | PASS | NOT RUN | NOT RUN | NOT RUN | PASS |
| T11 | PASS | PASS | PASS | PASS | PASS |
| T12 | FACT | FACT | FACT | FACT | FACT |
| T13 | PASS | PASS | PASS | PASS | PASS |

T2/T10 NOT RUN cells are outside the revised requested host scope. T9 is conservatively NOT RUN as a whole: recording + upload + failure ordering passed, but Update available could not be produced. T5 failures predate the PR.

| Window row | KDE |
|---|---|
| W1 | PASS |
| W2 | PASS |
| W3 | PASS |
| W4 | PASS |
| W5 | PASS |
| W6 | PASS |
| W7 | FAIL |
| W8 | PASS |
| W9 | PASS |
| W10 | PASS |

| Window row | Cinnamon |
|---|---|
| W4 | PASS |
| W5 | PASS |

## New failure: W7, KDE resize path

Exact reproduction used a private profile on k72, normal desktop font, and the actual destination **Tray acceptance HTTP destination with a long label** (50 characters):

1. Set every capture output to inherit the default destination, choose that custom uploader, keep a local copy, and set capture delay to 5 seconds.
2. Open Settings → General in a 1,440 × 880 window. The output summary, delay control and automatic-save explanation are visible: [wide candidate](r2/k72/W7-wide-long-output.png).
3. Resize the live window to 1,200 pixels, then 1,060 × 880. At 1,200 the output remains visible and the automatic-save explanation hides ([frame](r2/k72/W7-width1200.png)). At 1,060 the output summary is absent and the explanation returns, while delay remains intact: [candidate DEB failure](r2/k72/W7-width1060.png).
4. Restore the width: [summary returns](r2/k72/W7-width-restored.png). Quit/restart the native UI and revisit the narrow case: [later frame](r2/k72/W7-width1060-settled.png) has the summary visible. This limits the finding to the live resize path and contradicts any claim of permanent loss.
5. Run the exact CI candidate AppImage with the same output configuration and resize from wide to 1,060: [candidate AppImage failure](r2/k72/W7-candidate-appimage-width1060.png), [wide](r2/k72/W7-candidate-appimage-wide.png), [candidate identity](r2/k72/W7-candidate-appimage-identity.json).
6. Run the published nightly AppImage with the same accepted output configuration on the same KDE desktop and resize to 1,060 × 880: [nightly retains full summary](r2/k72/W7-nightly-width1060.png), [nightly identity](r2/k72/W7-nightly-identity.json). KWin's actual frame/content geometry is logged in the trace.

**Classification: regression.** Published nightly v26.1114.5000-nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885, tree 72e44106c147d2c855ff55044f59c85ce0b1b113 does not lose the summary in the matched resize comparison. The nightly lacks the new delay control, so it is a comparison of output-summary retention, not a claim of identical status-band contents. The exact candidate AppImage comparison removes the native-package versus AppImage format difference.

Other W7 portions passed: delay appears on History, Destinations, General, Capture, Hotkeys and Advanced; the output summary hides on Capture; choosing 5 highlights the delay control and updates the native tray. Those frames remain indexed.

## Retained failures: T5 missing bound shortcut hints

These four results were already checked against published nightly and were explicitly settled by the user. They were not repeated in this continuation.

Exact steps: start the candidate with the private profile; verify a bound Ctrl+Shift+1 region shortcut in diagnostics; right-click the tray icon to open the desktop's native menu; inspect region/window/desktop rows. The menus omit the bound-key hints. KDE displays them, including the host's shifted-digit formatting.

| Desktop | Candidate frame | Published nightly frame | Classification |
|---|---|---|---|
| GNOME | [candidate](f44-tray.png) | [nightly](f44-nightly-menu.png) | Same on nightly; predates PR |
| Cinnamon | [candidate](m74-tray.png) | [nightly](m74-nightly-tray.png) | Same on nightly; predates PR |
| Budgie | [candidate](budgie-tray3.png) | [nightly](budgie-nightly-menu.png) | Same on nightly; predates PR |
| Hyprland | [candidate](omarchy-menu-no-tooltip.png) | [nightly](omarchy-nightly-menu.png) | Same on nightly; predates PR |

The comparator is the published v26.1114.5000-nightly identified above. GNOME used its AppImage; Cinnamon used its Ubuntu 24.04 DEB in a private prefix; both fresh guest nightly comparators have retained identity and retirement receipts. GNOME's put.gd Shell extension 23 and AppIndicator were active during its checks.

## Tray sequence coverage

All P1 tray rows were completed across the five desktops before the P3 window run. Earlier corrected input attempts are preserved; only the frames explicitly listed in [frames.md](frames.md) establish passes.

- **T3:** used the real delay submenu; None → 5 moves the sole radio mark, relabels the parent and adds the disabled hotkey note. Changing the production hotkey-delay setting removes the note; returning to None removes it and moves the radio mark back. No resident/tray-host restart or catalog rebuild was used. Budgie dismisses an open submenu during its model update; reopening the native submenu shows the new state.
- **T4:** every host displayed a Default row, timing and an action exception from an actual configured profile. Change output opened Settings → Capture. KDE/Hyprland also used the 50-character destination label for T10.
- **T6:** real `upload.files` operations went through a documented lab Zipline receiver with a small slow-response proxy. Two simultaneous uploads produced Uploading 2 files and Cancel all uploads; release of the held responses removed the upload rows live. No catalog fixture was used.
- **T7:** the real refusing HTTP endpoint returned 503, creating an unknown-outcome upload failure and the attention row. Clicking the actual attention row opened History's Failed uploads view and cleared the badge. Cinnamon was repeated with corrected coordinates after the host moved the menu as live rows disappeared.
- **T8:** start Record screen through the product and select a real region, leaving the session Ready to record. Show recording and the unchanged Record screen row each raised that same recording ID; production recording inspection verified no second session and no stop. Cancel ended the session and removed the block.
- **T9:** the Ready recording phase + Show recording, Uploading + Cancel upload, and Failed uploads row appeared in that order above one separator on each host: [KDE](r2/k72/T9-combined-clear-frame.png), [GNOME](r2/f44/T9-combined.png), [Cinnamon](r2/m74/T9-combined.png), [Budgie](r2/budgie/T9-combined-clean.png), [Hyprland](r2/hyprland/T9-combined.png). Update was not faked. Each host's real `update.check` returned `update_check_unavailable`, reason `development_build`, “This build does not check for updates”: [KDE](r2/k72/update-check.json), [GNOME](r2/f44/update-check.json), [Cinnamon](r2/m74/update-check.json), [Budgie](r2/budgie/update-check.json), [Hyprland](r2/hyprland/update-check.json). No supported available-update path was found for this development build, so appearance/placement after Settings is NOT RUN.
- **T11:** used actual window controls to change output to Local only and delay to 3 seconds. The first subsequent native menu already showed both on each host, including Cinnamon. Hyprland required scrolling its same first-open menu to see both ends.
- **T13:** native Open put.gd opened History. Native region started the selector and completed a real synthetic capture; native Repeat completed another region capture; native Capture desktop completed a full-desktop capture. Production operation IDs/states are retained in traces. The other capture kinds are outside the revised T13 request.
- **T2:** KDE and Cinnamon opened both the clipboard editor and the real native file chooser from the tray Edit image submenu. Cinnamon's asynchronous portal chooser was allowed to settle before the accepted frame.

## Window coverage and boundaries

- **W3:** enlarged the real desktop General font to 18 points and mirrored that desktop font setting into the private XDG configuration used by Qt. The labels remained full and wrapped in the same order: [frame](r2/k72/W3-enlarged-private-desktop-font.png). Both real/private font keys were restored to their prior absent state. No product text-scale override was used.
- **W4/W5:** on KDE and Cinnamon, tested both split buttons through arrow and right-click; other seven right-clicks opened no menu. Tested Tab focus, Alt+Down, F4, Menu, Shift+F10, first-row highlight, Enter routing and Esc closure. Corrected KDE attempts account for UI-helper PID changes and an already-open editor. Accepted frames show actual new region/editor operations, not only a popup.
- **W6:** dragged an actual 96 × 64 PNG from Dolphin onto Capture region & edit and opened the editor ([drop](r2/k72/W6-drop-opens-editor.png)). With genuine no-output configuration, the capture action was unavailable and its dropdown still opened the two edit sources ([frame](r2/k72/W6-unavailable-output-menu.png)). This exercises configuration-caused unavailability; the region capture backend itself remained available and no backend outage was forced.
- **W8:** checked all nine tooltips: the six delayed actions include “Waits 5 seconds first”; scrolling/recording/clipboard do not. A real delayed desktop button click was still acquiring at 3.860 seconds, and completed by 8.300 seconds. The same desktop action's real Ctrl+Shift+3 hotkey completed in 2.624 seconds with delay 5 and hotkey-delay off. [Timing receipt](r2/k72/W8-timing.json), [countdown frame](r2/k72/W8-click-countdown.png), [hotkey frame](r2/k72/W8-hotkey-immediate.png).
- **W9:** a real Ready recording left Record screen's label intact and added “Ready to record” to both tooltip ([frame](r2/k72/W9-active-window-tooltip.png)) and its native AT-SPI screen-reader description ([observation](r2/k72/W9-accessibility.json)). The recording was cancelled afterward.

## T12 facts

| Desktop | Plain left click | Middle click | Double click | Starting state / evidence |
|---|---|---|---|---|
| KDE | Opens History | No visible change | No visible change | Initial run started on Settings for left click; History already visible for middle/double. [Frames](frames.md#t12) |
| GNOME | Opens native menu; main window stays closed | No visible action; main stays closed | Two menu toggles leave menu and main closed | New checks all start with main window closed, outside Overview. [Left](r2/f44/T12-left-closed.png), [middle](r2/f44/T12-middle-closed.png), [double](r2/f44/T12-double-closed.png) |
| Cinnamon | Opens History | No visible action; main stays closed | Opens History | New checks each start with main closed. [Closed proof](r2/m74/T12-window-closed-proof.png), [left](r2/m74/T12-left-clean.png), [middle](r2/m74/T12-middle-clean.png), [double](r2/m74/T12-double-clean.png) |
| Budgie | Opens History | Leaves History visible | Leaves History visible | Retained initial facts; History already visible for middle/double. [Frames](frames.md#t12) |
| Hyprland | Opens native menu | Leaves History visible without menu | Leaves menu open | Retained initial facts; History already visible, so no view-switch conclusion. [Frames](frames.md#t12) |

No visible change is an observation, not proof that no activation signal was delivered.

## Other observations

- Hyprland/quickshell constrains the menu to a scrolling viewport and cleanly elides even ordinary output text and long detail rows. The menu remains usable with the 50-character destination; disabled text is low contrast. The tray-icon tooltip can cover the first row until the pointer moves into the menu. These are host observations, not newly established regressions.
- Budgie dismisses an open submenu during the live hotkey-delay update. Reopening shows the correct mark and note visibility; the resident/tray was not rebuilt.
- The HTTP-503 unknown-outcome attention row opens a Failed uploads filter showing zero items, despite the artifact being present in All items. Badge clearing works. This looks inconsistent, but was not compared with nightly and is not classified as a PR regression or a failure of the requested badge behavior.
- No additional established label clipping or oversized-menu regression was observed. GNOME's disabled detail rows were readable. Early missed input coordinates and cover-window interference were corrected; they are not evidence that product rows require two clicks.

## Hosts, proven tree and restoration

Every desktop proved tree **7290d67885b6782efd871ac7b1c2d1787e03e525** in the build receipts linked above.

| Desktop | Host, OS and desktop | Final put.gd / guest state |
|---|---|---|
| KDE | k72 / 192.168.68.72; Ubuntu 26.04.1; Plasma 6.6.6; native Wayland | Candidate DEB removed, nightly/candidate AppImages quit, no resident. Original installed-runtime absence restored. Font key restored. |
| GNOME | f44 / 192.168.68.70; Fedora 44; GNOME 50.6; native Wayland; put.gd extension 23 ready during test | Candidate RPM removed, no resident. GDM re-login unloads candidate extension, AppIndicator disabled again and original enabled-extension configuration preserved. |
| Cinnamon | m74 / 192.168.68.74; Mint 22.3; Cinnamon 6.6.9; native X11 | Candidate DEB removed, no resident; owned cover/editor/chooser ended. Original installed-runtime absence restored. |
| Budgie | Disposable b3 on f44; Fedora 45; Budgie 10.10.3 / labwc 0.20.2; native Wayland | Guest stopped, evidence exported with matching SHA-256, overlay retired by guarded cleanup. No guest/tile/tunnel remains. |
| Hyprland | Disposable o3 on f44; Omarchy 4.5.0; Hyprland 0.56.2; native Wayland | Guest stopped, evidence exported with matching SHA-256, overlay retired by guarded cleanup. No guest/tile/tunnel remains. |

The physical hosts had no installed put.gd before the campaign; removal is the restoration requested in the revised brief. There is no previous running version to confirm. Final k72/m74 dpkg residual state is `rc 26.1114.5029~dev+gb91a65c2ee63` (configuration residue, no installed binary); f44 reports package absent. Final checks: [k72](r2/restoration/k72-final.txt), [f44](r2/restoration/f44-final.txt), [m74](r2/restoration/m74-final.txt). Thus runtime absence is restored, not a byte-identical package database.

All final desktop leases released verified-clean with empty `check.left`: [receipt summaries and hashes](r2/restoration/desktop-leases.json). The slow proxy PID is gone and receiver ports 18361–18363/18432 are absent: [final receiver check](r2/restoration/k72-receivers-final.txt). Owned receiver containers were stopped/removed through the documented down command; private receiver volumes were retained. [Guest host process/listener check](r2/restoration/f44-guest-host-final.txt) and [wall check](r2/restoration/wall-final.json) show no owned guests/tiles, preserving the other five wall entries.

Guest guarded-cleanup receipts: [b3](r2/budgie/overlay-cleanup.json), [o3](r2/hyprland/overlay-cleanup.json). Private exported evidence archives matched SHA-256 b3 `4a8cfb87124fd2b33d1fe08e387d911325ed1fc9145fc423cb7691267d102922`, o3 `8d577dfb582813c7000595ea16dd005df253be9d82e63be483f7404c22fd3824`. Archives can contain bootstrap SSH identities, so are retained privately rather than published. Goldens were never booted or modified; earlier b1/b2/o1/o2 retirement receipts remain in this record.

Two restoration qualifications from the original run remain: installing only putgd through DNF invalidated f44's pre-existing staged offline transaction; that pending-transaction state was not restored. The initial report and install log retain this fact. The documented k72 lab prerequisite python3-pyatspi (plus its dependency) remains installed as authorized by the revised brief. Neither changes the desktop/compositor under test. No general upgrade was performed.

## Execution and evidence handling

All SSH/SCP used the lab's pinned key, BatchMode, IdentitiesOnly, StrictHostKeyChecking and per-host known-hosts files through the existing PhysicalHost transport. One native desktop lock at a time, with 45-minute-or-shorter leases and heartbeats; no foreign lock was broken. KDE's single documented surface-driver prerequisite fix left the tray selector blocked, so existing real VNC input was used, as on the other blocked hosts. No new harness or catalog fixture was built; the small control helper composes the existing lab transport/RFB/production CLI.

Private profiles kept credential storage session-only and isolated XDG paths from the real desktop keyring. Socket preflight checked all resolved paths before launch (native session sockets 36 bytes, guest session sockets 46 bytes, guest QMP/VNC 55 bytes, maximum allowed 107). Payloads were synthetic; uploads used the documented lab receiver, not user objects. Credentials, private uploader imports and raw lease files remain outside this published source. All frames are full and uncropped; none were masked.

Some owned cover processes survived a polite stop; their exact recorded PIDs were stopped and verified gone before the final clean lease release. No pattern kill, recursive directory deletion, compositor package change, workstation desktop input, or guest left on the wall. The product checkout remains unchanged. No PR comments, issues or merge actions were taken.

The first continuation publication’s secret-scan job flagged 25 non-secret `concurrencyToken` UUIDs in upload receipts. Their count and locations matched exactly. The current published traces replace those 25 values with JSON null; operation IDs, settings revisions, diagnostics and all frames are unchanged. [Omission counts and raw-source hashes](publication-log-omissions.json) document this publication-only change. Full original logs remain private. No real authorization-header value occurred in the published source.
