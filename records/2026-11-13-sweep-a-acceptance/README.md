# Sweep A desktop acceptance — 2026-11-13

Candidate: `036a9225e1887e0ae6bc500b4cd5506746800367`, tree `1148ea1108a4f28a749607cf4a8ee8cbbdd90fc7`. All application packages came from manual CI [43513921710](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43513921710), which completed successfully. Every resident start asserted the exact candidate tree; [identities](receipts/build-identities.json) retain physical and guest proofs. No product code, issue, pull request, tag or merge was changed.

One requested behavior failed twice on the candidate and twice on published nightly: immediate Hyprland hotkey then drag returned `capture_geometry`. The remaining checklist rows passed. All requested functional steps were driven; no functional row is claimed from a mock or headless substitute. Early-input tests dispatch input immediately after the hotkey without an intentional wait; they do not measure the exact compositor surface-map timestamp.

| Section | Row | Desktop | Result | Evidence |
|---|---|---|---|---|
| A | 1. Session Prepare / Record / Pause / Resume / Stop | m74 X11; k72 Wayland | Pass | [m74](m74/sam3), [k72](k72/sakm2) |
| A | 2. Bar buttons, inspected after each step | m74 X11; k72 Wayland | Pass | [m74](m74/sarbar1), [k72](k72/sakbar1) |
| A | 3. Cancel: selecting, ready, recording, paused, stopping, reviewing, exporting | m74 X11; k72 Wayland | Pass | [m74](m74/sax1/extra.json), [k72](k72/sakx1/extra.json) |
| A | 4. Double Stop: one review | m74 X11; k72 Wayland | Pass | [m74](m74/sarbar1/bars.json), [k72](k72/sakbar1/bars.json) |
| A | 5. Bar Record plus simultaneous recording.start | m74 X11; k72 Wayland | Pass | [m74](m74/sarbar1/bars.json), [k72](k72/sakrace1) |
| A | 6. Helper pause timeout, late paused state, Stop and motion | m74 X11; k72 Wayland | Pass | [m74](m74/sax1/extra.json), [k72](k72/sakx1/extra.json) |
| A | 7. Own scroll window to end_of_content | m74 X11; k72 Wayland | Pass | [m74](m74/sas1/scroll.json), [k72](k72/saks1/scroll.json) |
| A | 8. Review Upload: all five states and History | m74 X11; k72 Wayland | Pass | [m74](m74/sau2/upload.json), [k72](k72/saku1/upload.json) |
| B | 1. Live B2 Test destination, including cleanup and large-file cancellation | k72 Wayland | Pass | [receipt](k72/sakb5/b2.json) |
| B | 2. Live B2 upload, bounded progress, SHA-256 readback | k72 Wayland | Pass | [receipt](k72/sakb5/b2.json) |
| B | 3. History exact-version delete; unrelated control unchanged | k72 Wayland | Pass | [receipt](k72/sakb5/b2.json) |
| B | 4. Offline custom HTTP upload and delete | k72 Wayland | Pass | [receipt](k72/sakoff1/offline.json), [History frame](k72/sakoff1/frames/B7-confirmed.png) |
| B | 5. Inactive cancel refused; active cancelled; failed item retried | k72 Wayland | Pass | [receipt](k72/sakoff1/offline.json), [History frame](k72/sakoff1/frames/B7-confirmed.png) |
| B | 6. Tray: initial, advancing progress, green completion, idle, attention | k72 Wayland; m74 X11 | Pass | [k72](k72/sakt2), [m74](m74/sat3) |
| B | 7. History Cancel all race: only two still-active uploads counted | k72 Wayland | Pass | [receipt](k72/sakoff1/offline.json), [History frame](k72/sakoff1/frames/B7-confirmed.png) |
| C | 1. Region: mark, independent image paste, save, upload, History; second capture cancelled | m74 X11; k72 Wayland | Pass | [m74](m74/sac3/flow.json), [k72](k72/sakc2/flow.json) |
| C | 2. File: Copy text tool, recognize, Copy all text, independent paste, upload | m74 X11; k72 Wayland | Pass | [m74](m74/sac3/flow.json), [k72](k72/sakc2/flow.json) |
| D | Hotkey drag | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/drag-1-terminal.png) |
| D | Drag begun during crosshair hold | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/early-drag-1-terminal.png) |
| D | Arrow-moved keyboard region, Enter | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/keyboard-enter-1-terminal.png) |
| D | Esc | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/escape-1-terminal.png) |
| D | Right-click | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/right-click-1-terminal.png) |
| D | Zero-size click | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/zero-size-1-terminal.png) |
| D | Esc during hold | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/early-escape-1-terminal.png) |
| D | Tray Capture region drag | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/tray-drag-1-terminal.png) |
| D | Screenshot-first with open menu, then menu closed | m74 X11 | Pass | [receipt](m74/sad3/picker.json), [input frame](m74/sad3/frames/screenshot-first-menu-1-terminal.png) |
| D | Twenty rapid hotkey / Esc cycles | m74 X11 | Pass | [receipt](m74/sad1/picker.json), [input frame](m74/sad1/frames/twenty-cycles-terminal.png) |
| E | Region inside one monitor | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Region across both monitors | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Desktop | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Monitor under pointer | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Repeat last region | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Live region with 3 s delay | Two-head Kubuntu Wayland guest p1 | Pass | [pixels](kde-p1/acceptance/rows.jsonl) |
| E | Window capture | Two-head Kubuntu Wayland guest p2 | Pass | [pixel comparison](kde-p2/acceptance/rows.jsonl), [reference](kde-p2/acceptance/window-full-reference.png), [result](kde-p2/acceptance/window-result.png) |
| F | Desktop | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Live region | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Screenshot-first region | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Window | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Monitor | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Repeat | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Delay 3 s | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Esc during selection | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Layout change: display_changed | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Copy result image and paste into GTK | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Copy put.gd text and paste into GTK | Two-head Budgie labwc; two-head Hyprland | Pass | [Budgie](budgie-b2/acceptance/rows.jsonl), [Hyprland](hyprland-h1/acceptance/rows.jsonl) |
| F | Immediate hotkey then drag | Two-head Hyprland | Fail | [candidate twice](hyprland-h1/acceptance/rows.jsonl), [nightly twice](hyprland-nightly-hn1/acceptance/rows.jsonl) |
| F | Immediate hotkey then Esc | Two-head Hyprland | Pass | [candidate](hyprland-h1/acceptance/rows.jsonl) |

## Reproduced failure and nightly comparison

F, Hyprland immediate hotkey then drag (PR 1471 / issue 1446 area): on the fresh two-head Omarchy guest, bind Region to Ctrl+Shift+F9, move to (300,300), send that chord, then immediately drive a real virtual-pointer drag to (600,500), 12 steps of 10 ms. The operation fails with `capture_geometry`, message “The region helper could not complete selection”, with no image. Expected: one completed region capture. Both candidate attempts failed: `8da9b197-3303-4530-ae91-bb03b4986575` and `131e67a5-e5bc-4ad5-b7db-c7f53379a68e`. [Candidate log](hyprland-h1/vm-h1-checks.log), [first frame](hyprland-h1/acceptance/early-hotkey-drag-1-head0.png), [second frame](hyprland-h1/acceptance/early-hotkey-drag-2-head0.png).

The same sequence on a fresh guest from the same immutable golden, published nightly `26.1113.4757-nightly` (tree `4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3`), also failed twice with the same code/message. [Nightly log](hyprland-nightly-hn1/vm-hn1-checks.log), [nightly frame](hyprland-nightly-hn1/acceptance/early-hotkey-drag-1-head0.png). This establishes a pre-existing failure for this fast-input sequence; it does not attribute its introduction to PR 1471. Ordinary live/screenshot-first selection and immediate Esc passed on the candidate. The driver timing limitation above means this is a command-dispatch race result, not a submillisecond timing characterization.

## Recording and visual evidence

The cover combines horizontally moving SMPTE bars and a moving ball. Frozen exported controls score **0.000** on [m74](m74/sam2/results.json) and [k72](k72/sakm1/results.json). Corresponding A1 exports score **4.985** and **5.188**. A2/A4/A5 exports score **4.426 / 2.322 / 2.596** on m74 and **4.612 / 2.789 / 3.001** on k72. The A6 late-helper exports score **0.125** and **1.636**; both callers received `recording_helper_timeout`, then inspection caught up to paused and Stop opened review. Only the owned exact recorder PID was stopped, for a scripted 20 seconds, and continued in `finally`. A8 uploaded clips score **3.697** and **3.928**; the read-only session observer recorded recording → acquiring → stored → running → completed on each desktop. Exported clips and frozen controls are retained beside their receipts.

All seven A3 cancellation frames on each physical desktop were visually inspected: no bar, capture ring, dimming or review remained, and the journal operation was cancelled. [X11 contact sheet](derived/m74-cancel-atlas.png), [Wayland contact sheet](derived/k72-cancel-atlas.png); originals remain in the runs. Review frames show one review after double Stop. Bar state frames were checked against `recording.inspect`.

Tray proof uses actual StatusNotifierItem properties, native pixmaps and real desktop frames during a slow 15.75 MiB HTTP upload. The native visual is an advancing amber fill in the seasonal tray glyph, followed by green “Upload complete”, then idle; failure displays the attention badge and “Needs attention”. It is a fill, rather than a literal circular outline. [X11 sequence](derived/m74-tray-atlas.png), [Wayland sequence](derived/k72-tray-atlas.png), with full original frames in the linked runs. The initial frame matches idle and later fill advances (m74 31→43%, k72 17→34%).

B7's confirmation was opened while three separate file uploads were active; the small file finished before confirmation. The final line is **“Cancellation requested for 2 uploads.”**, no cancellation-failure line appears, the other two operations are cancelled, and the finished link served identical bytes. The B5 first failed HTTP upload has operation state `partial` because its local archive succeeded; its item is failed, and explicit retry completes it. Active cancellations are also covered by B7.

C was run fully on m74 X11 and k72 Wayland. Region edits, Copy image into an independent GTK client, saved-copy SHA-256 comparison, explicit upload and History records all passed; a second region editor was cancelled. File editing, the Copy text tool, recognition, Copy all text and exact GTK text paste passed, then the second upload completed. No `image_job_io`, `editor_io`, staging or input-changed error occurred.

D retains each panel-before/panel-after/terminal frame, exact synthetic terminal input, operation state and empty putgd overlay-window list. The screenshot-first run uses a genuine GTK menu held open at invocation and then closed. Both relevant runs also completed twenty rapid hotkey/Esc cycles with immediate input recovery.

E region, Repeat, desktop, monitor and delayed-region comparisons have mean absolute pixel difference **0.000** against their full-desktop references. The window comparison has mean difference **0.005892**, a 640×448 image at independently located reference box [1472,160,2112,608]. All used default image limits; no one-monitor `input_excessive` error occurred.

F image clipboard pastes match captured pixels exactly on both desktops; text pastes equal the synthetic recognized text. Layout changes fail with `display_changed`, rather than producing an image. Hyprland's software cursor may appear in region pixels, as documented for the VM.

## Harness attempts retained, not candidate failures

The earliest m74 motion attempts did not yet contain both moving elements; only the corrected moving runs and frozen controls support acceptance. Early offline retry polling omitted terminal `partial` and was corrected. An xterm-menu attempt did not hold a menu open; `sad3` replaces it with a genuine GTK menu. The first Wayland clipboard driver clicked the front editor instead of the covered GTK client; `sakc2` uses KWin's native window activation API. The first Wayland simultaneous-start driver clicked Discard after the API had already started; it is not used as A5 proof. `sakrace1` releases the actual Record button immediately before spawning the API caller, then records a normal recording bar and a motion export. Earlier tray drivers missed the short green hold or hovered the neighboring remote-control icon; final runs use the correct tray icon and an immediate framebuffer read. These retained attempts never turn into product failures or passes by themselves.

Guest `b1` stopped at the lab layout command before candidate installation. Its launch preflight already verified Budgie's reversed native two-head layout; fresh `b2` uses that verified layout. Both overlays were retired. Initial B2 provisioning tried a CLI method that deliberately refuses credentials; no live object was created in those attempts. Final B2 runs use the documented standalone QtKeychain lab bridge and explicit unlock. The bridge alone was built from its documented small standalone source using already-installed system dependencies; no application was compiled and no dependency package was added. Live secrets were read only into memory on k72, never copied off the builder or recorded. Both test profiles and their unique keychain entries were removed; the owned prefix and unfinished-large-file listing were empty after testing. Deletion compared an unrelated synthetic control object in the isolated prefix before/after exact-version deletion.

## State left behind

m74 and k72 both started as **deinstall ok config-files 26.1113.4757~nightly**; neither initially had an installed native package. m74 was tested from the candidate CI AppImage and its package state never changed. k72 was tested with the candidate native DEB, then only putgd was downgraded to published nightly and removed, leaving the exact original config-files state. The final race retest followed the same scoped install/restore procedure. No extension was changed on any host. f44's physical package remains absent; its GNOME extension state was untouched.

All owned residents, helpers, receivers and test windows stopped. All physical leases were released after empty cleanup checks. All six disposable overlays (p1, b1, b2, h1, hn1, p2) were stopped, exported, checksum-verified and retired through guarded `lab.py cleanup`. Immutable goldens were not modified. Final separate `pgrep -c qemu-system` calls returned zero on m74, k72 and f44. This run's wall entries, tunnel units and preview tab are gone. One old owned, non-listening Unix socket was found during the final inventory; after verifying `ECONNREFUSED`, its exact socket node was removed.

Scratch is retained deliberately for audit: `/home/patrick/work/sa1113` is about 1.09 GB on m74, 0.91 GB on k72 and 0.81 GB on f44. Private `/tmp` run/runtime directories total about 7.92 GB on m74 and 0.33 GB on k72, predominantly AppImage extracts on m74. Exact paths and sizes, package state and process inventories are in [m74](receipts/m74-final.json), [k72](receipts/k72-final.json), [f44](receipts/f44-final.json). Cleanup and package transaction receipts are under [receipts](receipts/). No test source was removed from a builder. Package metadata accidentally copied into the local publication staging directory was omitted; original CI packages and extracts remain on the builders.

The record contains acceptance outputs, original frames and clips, scripts, build identities, CI receipts and retirement manifests. Public JSON copies omit redundant nonsecret `concurrencyToken` version/digest markers that matched the generic API-key scanner; exact B2 `objectReference.fileId`, artifact SHA-256 and all outcomes remain. [Redaction receipts](receipts/publication-redactions.json) retain before/after file hashes and counts. Raw JSON stays on the builders; no authentication value was found in the publication copies. Derived contact sheets are labelled as such and retain their originals. Published frames were checked to show lab windows and synthetic data only. No credentials or revealed login fields are included. Nothing was added under docs/evidence.
