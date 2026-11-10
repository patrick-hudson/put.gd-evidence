# Editor tools #1362 — five-desktop CI-package acceptance

Code PR: https://github.com/patrick-hudson/put.gd-desktop/pull/1369. Docs PR: https://github.com/patrick-hudson/put.gd-desktop/pull/1370. Tested 2026-11-10 UTC.

**Result: pass on all five desktops for this feature scope.** Every final driver run passed `--submit` with 34 checks. Saved QMP/uinput results and independent application paste witnesses accompany the table. This is feature acceptance, not a new complete release/package-lifecycle or recording acceptance campaign.

## Exact build and package reuse

Application: **26.1109.4410-dev+g697b74345e89**, source `697b74345e89c3d9019e4e3db596502248da2a15`, clean git tree `a3a746d0542f21817a809afc6f52ed5ee3766c73`. The original five AppImage rows used `putgd-26.1109.4410-dev+g697b74345e89-x86_64.AppImage` from full CI run https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42724867547 (including its successful contracts rerun).

AppImage SHA-256: `4ba77b27e6530f1f853f5eb598ad5a4ebcdc2a8188f18f363c679ab6dd6f100a`. Extracted resident executable SHA-256: `dbd2b622ff494499a1be7d2d251ef0d6827a7c2fe604646bce29ee395b014bc5`.

Accepted PR head: `260abf34500346d0e659880e970d7c0e3cc1d0d9`. Its diff from the packaged commit changes **only** `tools/lab/editor_tools_check.py` and `tools/lab/surface_driver/recipes/editor.py`. The coordinator explicitly authorized continuing with the identical application binaries after those lab-only corrections. Picture captions name the application build actually shown. No builder or workstation compilation was used. The native-package extension below subsequently completed the requested distribution-Qt feature gates.

## Original AppImage desktop results

| Desktop | Actual target and session | What passed | Evidence |
| --- | --- | --- | --- |
| Cinnamon/X11 | d69 fresh overlay `c62b`, Linux Mint 22.3, Cinnamon 6.6.4 / Muffin 6.6.1, native X11 | Driver 34/34 with fixture upload; real drawing/editing/restyling/undo/redo; numbering and constraints; shortcut/button copy and Firefox paste | [Driver](cinnamon/driver-visible/log.json), [real input](cinnamon/real-input.json), [extra input](cinnamon/extra-input.json), [button copy](cinnamon/button-copy.json), [paste](cinnamon/paste-after-button-head0.png), [retirement](cinnamon/overlay-cleanup.json) |
| GNOME/Wayland | f44 fresh overlay `g62`, Fedora 44 Workstation, GNOME Shell 50.0; exact AppImage companion version 19 loaded after guest reset | Driver 34/34; native extension copy with independent XWayland `xclip` read; real drawing/editing/restyling/undo/redo, constraints, both copies and Firefox paste | [Driver](gnome/driver-visible/log.json), [real input](gnome/real-input.json), [extra input](gnome/extra-input.json), [button copy](gnome/button-copy.json), [paste](gnome/paste-after-button-head0.png), [retirement](gnome/overlay-cleanup.json) |
| KDE Plasma/Wayland | physical k72, Kubuntu 26.04.1, Plasma/KWin 6.6.6; lease `e1362-697b` | Driver 34/34; real uinput four-tool drawing, movement/resize, colour/width, undo/redo; real Pixelate; 1/2/3/10 then delete 2; both copies and LibreOffice Draw paste; live S3 + History/browser; layout 100%/150% | [Driver](kde/final-driver/log.json), [real final state](kde/real-final.json), [constraints](kde/real-constraints.json), [button copy](kde/copy-button-check.json), [paste](pictures/pasted.png), [live browser](pictures/live-browser.png), [cleanup](kde/cleanup.json) |
| Budgie/labwc | d69 fresh overlay `b62b`, Fedora 44 Budgie 10.10.2 / labwc 0.9.6, native Wayland | Driver 34/34; real drawing/editing/restyling/undo/redo, numbering and constraints; both copies and Firefox paste | [Driver](budgie/driver3/log.json), [real input](budgie/real-input.json), [extra input](budgie/extra-input.json), [button copy](budgie/button-copy.json), [paste](budgie/paste-after-button-head0.png), [retirement](budgie/overlay-cleanup.json) |
| Hyprland/Omarchy | d69 fresh overlays `h62` and clipboard repeat `h62p`, Omarchy 4.5.0-3 / Hyprland 0.56.2-4, native Wayland | Driver 34/34; real drawing/editing/restyling/undo/redo, numbering and constraints; both copies and Chromium paste | [Repeat driver](hyprland-paste/driver/log.json), [real input](hyprland-paste/real-input.json), [extra input](hyprland/extra-input.json), [verified clipboard actions](hyprland-paste/clipboard-paste-verified.json), [paste](hyprland-paste/button-paste-head0.png), [repeat retirement](hyprland-paste/overlay-cleanup.json) |

f44 and m74 physical desktops were held by other lanes when selected, so matching fresh guests were used. Their physical desktops were not acceptance targets here. No physical-hardware gate applies to this feature. VMs used KVM and immutable golden backing disks; guest identities, exact golden hashes and run IDs are in each `state.json`. Physical k72 identity is in `kde/host-identity.json`.

## What the checks prove

The agent driver creates every new mark, changes tools and Step/Blur controls, undoes/redoes, copies, reads back the desktop clipboard, compares Copy image and Save a copy byte-for-byte, and submits to a synthetic loopback S3 receiver through the production uploader. The editor remains editing after copy. Final logs retain operation IDs and replies.

The real-input checks send QMP events to guests and uinput events to k72: keys N/P/E/L, clicks and drags, arrow movement, Shift+arrow resize, palette and width changes, undo/redo; steps 1/2/3, Next number 10 and then 11, deletion of 2 leaving 1/3/10; pen dot; Shift circle; drawing inside an ellipse; Shift line snapping and end-handle snapping. `final-gestures.json` records guest end-handle and image-edge checks. Geometric endpoints may sit at x=1200, the boundary of a 1200-pixel raster; this is not an exported pixel outside the image. The initial strict `<1200` diagnostic assertion was corrected to `<=1200`; correction receipts are retained.

The independent browser paste page receives a real native Ctrl+V event, displays the PNG and computes its digest in the browser. This is an application paste, not an image loaded from a file in place of a paste. k72 additionally uses LibreOffice Draw. Both Copy image button and Ctrl+Shift+C were exercised; button-copy receipts require unchanged History and an open editor. Clipboard-copy capability was explicitly within this task's scope.

## Redaction contract and corrected driver

The original driver put its ellipse across the first mask. The copied PNG consequently contained annotation ink on black, making its all-black assertion fail. The coordinator clarified that the contract removes **source pixels** beneath redactions while permitting later annotation ink. The application compositing was preserved.

The lab correction moves that ellipse away, keeping the original whole-mask black assertion. A second magenta source area is redacted and deliberately crossed by a red rectangle; exported pixels there must be exactly black or annotation red. A separate pair of sources differs only under the masks; identical geometry-only annotations, Blur and Pixelate over those masks must export identical PNG bytes. Every final desktop run passes these tests. No source-pixel survival was found.

The first expanded byte comparison also included Step labels frozen by different helper instances; the observed differences were confined to the glyphs, outside the source masks. The final comparison uses geometric marks to avoid comparing distinct frozen glyph paths. Copy/save/upload identity within one draft remains checked, including Steps.

Other lab fixes: wait for an editor this driver itself cancelled to finish closing; bound `wl-paste` to five seconds and fall back to `xclip`; deselect the current Step before the surface recipe edits Next number. All changes are in lab tools. Synthetic setup attempts with a malformed session envelope, an initially missing Cinnamon `xclip`, and GNOME's initially unloaded companion are retained as harness/setup failures, not passing acceptance.

## Live S3 and browser

k72 read the protected builder credential input in memory and typed it into Settings using uinput. No credential value was written to scripts, commands, logs, screenshots or evidence. The Settings fields were cleared before subsequent captures. Session-only credentials were used.

Live operation `dd5531d6-c463-4b8a-9146-89b787ceb149`, History `796e8dac-6152-4ed8-bbbd-0b073ce9b7fe`, uploaded the sanitized image containing every mark. `history.openLink` returned `opened: true`, `route: portal`, and the temporary default Firefox visibly loaded the real public image. A public GET matched SHA-256 `e1d60cd73e290e472268459ea01d456d76dffc82abaebc4a542d4704dbd4ced8`.

The temporary browser handler was removed and native MIME files restored byte-for-byte. Exact-ID guarded deletion operation `3c00e8ba-624d-4aec-87ca-786fc524fdff` completed for this one synthetic object. Local copies remain in the private evidence archive. No policy, versioning or unrelated object was changed.

## PR pictures

The annotated editor pictures were captured from the tested CI AppImage on physical k72; `clipboard-pair.png` is the same-build Hyprland h62p editor beside its independently verified Chromium paste page. Only `before.png` shows nightly `32a9a763e3502e0bf26db88def6140a7e250bbb4` (CI run 42706400392). The illustrative combined-mark scene is prepared through production editor commands; real-input runs are independently recorded above. Crops and coloured boxes/text were exported by put.gd's own image editor, with [operation receipts](pictures/editor-overlay-receipts.json) and the [corrected default-150% crop receipt](pictures/editor-overlay-scale150-correction.json).

- [Before](pictures/before.png) and [after](pictures/after.png) toolbar.
- [Each new mark](pictures/marks.png), [Blur beside Pixelate](pictures/blur-pixelate.png), [Steps and Next number](pictures/steps-next.png).
- [Copy confirmation on the illustrative scene](pictures/copied.png), [real-input draft pasted into LibreOffice](pictures/pasted.png), [matching Hyprland editor/paste pair](pictures/clipboard-pair.png), [live browser](pictures/live-browser.png).
- [Minimum 100%](pictures/min100.png), [minimum 150%](pictures/min150.png), [default 150%](pictures/scale150.png).

The application always uses its own `putgd::Ui` proxy over Fusion (`src/ui/Ui.cpp`), so one toolkit-style layout set covers these AppImage rows. Minimum widths measured on this package were 619 pixels at 100% and 929 at `QT_SCALE_FACTOR=1.5`; history/zoom wrap and Redact/Blur remain labelled. The host desktop's scale was not changed.

## Visibility, failures and cleanup

Publication QA caught that the first Hyprland browser windows were tiled to the right while the scripted paste click landed in the editor. Those earlier pages said Waiting and did not prove paste; the old screenshots and state-only button receipt are retained under `hyprland/` as failure context. Before publication, a fresh `h62p` overlay repeated the driver (34/34), real new-tool input and the clipboard gates on its visible wall tile. The corrected check reads the real Chromium window bounds, focuses its paste surface, and requires the browser title to contain the exact Save a copy SHA-256 after both actions. It seeds the clipboard with benign text before each action, so a stale image cannot pass. Both native actions pasted PNG `2d5fc79af4ec059b5ce2aaf580c6e7e99ef4fbc7526fab413519de9476123682`; History stayed unchanged and the editor stayed open. The repeat's saved pictures and receipt are under `hyprland-paste/`. During the probe, manual real shortcut/button input released the clipboard owner whose inherited pipe held the SSH call; the retained reproduction helper redirects that tool's output.

Budgie and Hyprland were on correct wall tunnels throughout. Initial workstation ports 5996/5997 for Cinnamon/GNOME were already occupied by another lane; the owned tunnel units failed to bind. This was found on audit. Only incorrect screenshots were read from those ports; all input was through the owned guests' QMP sockets. The other lane's tunnels, tiles and guests were untouched. Own entries were corrected to verified-free 6015/6016, the actual guests were visually verified, and the driver and real-input/paste runs were repeated there before acceptance. Earlier results were not used to claim visible acceptance.

All five own overlays (including the focused Hyprland repeat) have completed guarded retirement receipts. Their wall entries and tunnels were removed. k72's private residents/helpers/fixture, input service and browser were stopped; two temporary accessibility packages were removed; native MIME restoration and remote deletion were verified. The desktop lease was released clean at 01:10:15 UTC, well before the nightly deadline. No other desktop lease was taken.

Private full exports (including original PPM witnesses, source helpers and failed attempts) remain on d69/f44 under `/home/patrick/work/e1362vm`, and on k72 under `/home/patrick/work/e1362` and the private `/tmp/e1362*` evidence roots. Public records omit guest SSH keys, credentials, runtime environments, browser profiles and unrelated desktop frames. Retirement manifests enumerate the full private verified export; this record contains the PNG/JSON subset and receipts. No golden was booted directly, modified or deleted.

No acceptance blocker remains for this feature scope. No merge was performed and no PR watch was created.


## Native distribution-Qt extension

At the coordinator’s request, the same full CI run’s native packages were tested without rebuilding. Application source remains `697b74345e89c3d9019e4e3db596502248da2a15`; accepted PR head remains `260abf34500346d0e659880e970d7c0e3cc1d0d9` (lab-only changes). [Exact package names, SHA-256 and sizes](native/packages/identities.json) and per-artifact build manifests identify all four packages.

| Desktop | Actual target / deployment | Qt actually loaded by putgd-ui | What ran; result | Evidence |
| --- | --- | --- | --- | --- |
| Mint 22.3 Cinnamon/X11 | d69 fresh overlay `c62n`, Ubuntu 24.04 DEB **installed** by apt/dpkg | **6.4.2**, system `libQt6Core.so.6.4.2`, native xcb | **PASS** — driver `--submit` 34/34; 35 real-input assertions: each Step/Pen/Ellipse/Line/Pixelate drawn, moved, resized, restyled, undone and redone; button and Ctrl+Shift+C copied, both pasted into Firefox with exact saved-PNG digest; History unchanged/editor open; minimum width at 100% and 150% | [Driver](native/mint/driver-final/log.json), [real input](native/mint/real-input.json), [paste receipts](native/mint/native-paste.json), [button paste](native/mint/native-paste-button-result-head0.png), [loaded Qt](native/mint/loaded-qt.json), [installed DEB](native/mint/package-install-result.json) |
| Fedora 44 GNOME Wayland | f44 fresh overlay `g62n`, Fedora RPM **installed** by dnf; system package extension v19 ACTIVE after guest restart/fresh login | **6.11.2**, system `libQt6Core.so.6.11.2`, native qwayland | **PASS** — driver `--submit` 34/34, including independent XWayland clipboard read | [Driver](native/gnome/driver-final/log.json), [Qt](native/gnome/loaded-qt-final.json), [loaded package extension](native/gnome/extension.json), [installation](native/gnome/native-install.log) |
| Kubuntu 26.04.1 Plasma Wayland | physical k72, Ubuntu 26.04 DEB **extracted under private roots**, explicitly permitted for this row; installed package unchanged | **6.10.2**, `/usr/lib/x86_64-linux-gnu/libQt6Core.so.6.10.2`, native qwayland | **PASS** — driver `--submit` 34/34 | [Driver](native/kde/log.json), [Qt](native/kde/loaded-qt.json), [host/extraction identity](native/kde/host.json), [cleanup](native/kde/cleanup.json) |
| Omarchy/Hyprland Wayland | d69 fresh overlay `h62n`, Arch package **installed** by pacman | **6.12.0**, system `/usr/lib/libQt6Core.so.6.12.0`, native qwayland | **PASS** — driver `--submit` 34/34 | [Driver](native/arch/driver/log.json), [Qt](native/arch/loaded-qt-final.json), [installation](native/arch/native-install.log) |

Budgie retains its accepted AppImage row; no additional native row was requested. The three non-Mint native rows are the requested driver-only feature checks. They do **not** add real-input/paste/layout, a second live-bucket/browser exercise, full release acceptance, upgrade/uninstall lifecycle or recording coverage.

Mint’s native clipboard actions both produced PNG SHA-256 `07cb874d73011b9a83df1e7626cda7638bea4c573f02e5ca6af8593eabe51c85`, equal to Save a copy. Before each action, the clipboard was seeded with benign text; the real Firefox paste listener’s title and displayed digest had to match. The [shortcut paste](native/mint/native-paste-shortcut-result-head0.png) and button paste were visually verified. All four native drivers pass the strict black token, intentional black-or-red annotation overlap, copy/save/upload equality and paired-source Blur/Pixelate redaction invariance gates. No source pixels were found surviving a redaction.

Four additional PR pictures come from the **installed Ubuntu 24.04 DEB on Mint, Qt 6.4.2**, application `697b74345`: [toolbar after](pictures/native-mint-after.png), [every new mark](pictures/native-mint-marks.png), [minimum 100%](pictures/native-mint-min100.png), [minimum 150%](pictures/native-mint-min150.png). These show the actual real-input draft. Crops, boxes and labels were exported by that installed editor; [overlay receipts](pictures/native-mint-overlay-receipts.json).

The native Mint 100% minimum is 619 physical pixels. At `QT_SCALE_FACTOR=1.5`, Qt 6.4.2 reports minimum 905 pixels plus two-pixel X11 resize increments/base -2; Cinnamon settles at **908 physical pixels** even when asked for width 1. [100%](native/mint/minimum100.json) and [150% hints/actual geometry](native/mint/minimum150.json) preserve the measurement. This differs from the AppImage/KWin 929-pixel result; it is measured per toolkit/window manager, not assumed equal. Both native toolbars wrap undo/redo/zoom, keep every new glyph and Redact/Blur accessible, and their footers fit. Pictures retain the observed dark 100% and light 150% appearances. No clipping or missing glyph was observed.

Setup failures were saved before correction: Mint had no clipboard-reader utility; xclip was added to the disposable guest. GNOME’s wl-paste did not serve the unfocused reader; the installed package extension was verified ACTIVE and xclip provided the same independent bridge used in the accepted AppImage row. A Mint real-input probe left focus in Block size before Ctrl+Z; focusing the canvas before document undo corrected that harness probe. Firefox’s first fresh-profile startup had not reached the paste page when the first input arrived; the retry waited for its actual page title and focused the observed paste pad. Failed visuals/logs remain alongside passing receipts. No application change was made.

Native cleanup: all three guest overlays were stopped and retired with guarded manifests/receipts, their owned SSH tunnels and wall entries removed, and immutable goldens preserved. Physical k72’s isolated resident/helper and loopback fixture were stopped and absence verified before its lease was released clean; its private package extraction was then removed by exact owned file paths. Native system packages/MIME/desktop settings on k72 were unchanged. Private source/evidence exports remain in the builder evidence archives. No lease, guest, tunnel, wall entry or test process remains owned by this extension. No merge/watch was performed.
