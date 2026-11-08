# Hyprland adapter acceptance on Omarchy 4.5 (#1275, PR #1293)

Graphical acceptance of put.gd's `hyprland-wayland` adapter on a real Omarchy 4.5 session (Hyprland 0.56.2,
Lua config, quickshell), with real keyboard and tablet input through QEMU, never `wtype`.

## Identities

- Host: d69 (Debian 13 builder), VM run `d1` (fresh `lab.py` overlay, never the golden), golden
  `omarchy-hyprland-20261108` (SHA-256 `bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256`),
  profile `omarchy-hyprland`, UEFI, `virtio-vga`, software rendering, 2 vCPU / 6 GiB. Shown on the display wall.
- Code: PR #1293 head `b65a69173` (stacked on `feat/budgie-wayland-1275` 2b9402b2f). Both packages are the PR's own CI
  artifacts (run 42445129538), built from GitHub's test merge `3af1e6b2b0a58e857eccbf52a823713aeac02905`,
  version `26.1108.4146-dev+g3af1e6b2b0a5`, dirty=false:
  - Arch: `putgd-26.1108.4146dev.g3af1e6b2b0a5-1-x86_64.pkg.tar.zst`, SHA-256
    `921cfef15bf2b352dd3c6a01e4d077b706343595aee15cf0ee4be03f21ca410f`, installed with `pacman -Sy` then `pacman -U`.
  - AppImage: `putgd-26.1108.4146-dev+g3af1e6b2b0a5-x86_64.AppImage`, SHA-256
    `10b17d0189650b2451d62f460eb58d84cf2cb68a6b450f9f371e62418b19af6c`.
- `step1/` frames were taken earlier with a pre-PR build of the same branch while probing Omarchy and during
  development (window capture cases, reload, conflicts, tray, Nautilus, file dialog, themes).

## Results (both packages unless noted)

| Check | Result |
| --- | --- |
| Routing | `adapter: hyprland-wayland`, Core route, `QT_QPA_PLATFORM=wayland;xcb` |
| Desktop hotkey Ctrl+Shift+3 | 1280x800, equal to the QMP screendump except the notification stack that changed between the two |
| Region hotkey Ctrl+Shift+1 + tablet drag | 400x300, 0 differing pixels (AppImage: 20 px = the pointer at the drag corner, which screenshots exclude) |
| Window hotkey Ctrl+Shift+2 | equal to `grim -T <stableId>` (0 px) |
| Own windows | Settings and the image editor refused: `target_unavailable` |
| Window cases (step 1) | covered window: own pixels only; other workspace and special (hidden) workspace: full content; Omarchy floating workspace: client area, hyprbars titlebar excluded |
| Shortcuts | Ctrl+Shift+1/2/3 bound and read back from `j/binds`; Print and Super+Shift+S `shortcut_conflict` (Omarchy's "Screenshot" and "Google Maps"); both Omarchy binds still fire |
| Rebind, unbind, recorder pause, quit, Omarchy theme change | Omarchy's 251 binds identical to the pre-put.gd list every time; quit leaves exactly them; put.gd binds come back after every reload |
| Hotkey with no resident | harmless after quit and after `kill -9` (stale binds); same Hyprland PID, no crash report; restart adopts stale binds without doubling |
| Permissions | deny rule: `capture_permission` with `hl.permission({ binary = [[/usr/bin/putgd]] ... })` (AppImage: `[[/tmp/\.mount_[^/]+/usr/bin/putgd]]`), desktop and window; documented allow rules for putgd and putgd-record: capture and recording work |
| Clipboard | GTK4 client text and PNG imported unfocused; put.gd capture pasted into GTK4 byte-identical; PRIMARY unchanged; Omarchy clipboard history keeps capturing |
| Recording (no picker process at any point) | monitor motion 21.1, window (stableId via `recording.windows`) 70.6, region 62.1, static control 0.72; cursor painted |
| Outputs | scale 1.25 at 1920x1080: desktop and 600x450 region exact; 90-degree rotation: upright, equal to the scanout turned back; mixed-density second output composed at density 2; layout change during selection: `display_changed` |
| Screenshot-first region | result equals the frame at selector open, not the later frame |
| 1080p60 cadence (fluidity fixture) | fixture itself ~7.8 fps in this software-rendered VM; clip 7.58 distinct/s, i.e. the recorder kept the source's pace (one single-frame skip, longest skip 33 ms) |
| A/V sync (marker clip, system audio) | 15 pairs, median -19.3 ms, range -30.7..+36 ms |
| Memory (resident, 20 s idle / after captures and a recording) | native PSS 16.8 / 17.8 MB (RSS 38.1 / 39.3); AppImage PSS 27.5 / 29.0 MB |
| Tray, Nautilus, file dialog, themes | quickshell tray menu opened and "Capture desktop" ran (pre-PR build; on the CI build the tray item is registered but the menu was not re-captured); Nautilus "Upload with put.gd" reaches put.gd (no destination: Destinations opens); portal folder chooser; Light/Dark/System |

## Found and not fixed here (follow-up issues)

- quickshell keeps put.gd's critical (urgency 2) failure notices across reboots (`pictures/critical-notice-survives-reboot.png`).
- After an output is rotated and set back, the running resident keeps the rotated transform (Hyprland does not resend
  `wl_output.geometry`); desktop capture reports `display_changed` until put.gd restarts.
- No upload destination was configured in the VM, so a real upload and opening its link in Chromium were not run.
- Animations are off in this VM, so the selector's `no_anim` layer rule could not be observed.

## Files

`pictures/` annotated PR pictures; `arch-ci/`, `appimage-ci/` row logs and captures with their references;
`outputs/` scale, rotation, two-output, screenshot-first; `step1/` probe and UI frames.

## Round 2 (2026-11-08, final head): #1299 fixed, #1300 accepted, tray on the CI build, #1304 checks

Build: CI artifacts of PR #1293 head 571c9f53a (test merge bfd9c820e = `26.1108.4156-dev+gbfd9c820e038`), Arch package
`putgd-26.1108.4156dev.gbfd9c820e038-1` and AppImage (sha256 b72feb38627d11e3...). The PR head was then rebased onto B's
18852a0fb (4b24f3b33); B's delta is SettingsWindow text height only. Host: fresh overlay `d3` of golden
`omarchy-hyprland-20261108` on d69 (Omarchy 4.5.0, Hyprland 0.56.2, quickshell), on the wall (port 5994), real QEMU
keyboard/tablet input. Files in `round2/`.

| Check | Result |
| --- | --- |
| #1299 rotate → back → capture, same resident (`rotate-d3/`) | PID 2790 throughout. Transform 1: 800x1280 completed. Back to 0: 1280x800 completed and matches the screendump except the toast stack (1.6 %). 1→0 again: completed. |
| #1300 hotkey upload (Arch, `final-arch/`) | Real S3 destination (key set 2 lent to the guest's disposable keychain through `provision_live_credentials.py`; bucket put.gd, isolated prefix `acceptance/d1275-hyprland/<uuid>/`). Origin 200, public 200 `image/png` 1410145 bytes. |
| #1300 link opened from History in the default browser | `history.openLink` → portal → Chromium, title "Screen-Capture-2026-11-08-00-16-13.png (1280×800) - Chromium" (`pictures/omarchy-chromium-opens-hotkey-upload.png`). |
| #1300 Nautilus "Upload with put.gd" (Arch) | Upload completed, origin 200, link opened in Chromium (`pictures/omarchy-nautilus-upload-menu.png`, `pictures/omarchy-chromium-opens-nautilus-upload.png`). |
| #1300 cleanup | Both objects deleted through History (`delete.prepare`/`confirm`, `remote: removed`), origin 403 like a never-existed key; AppImage upload deleted the same way; history cleared; profile removed and routes back to local; lab keychain item and bridge removed (receipt `cleanup_confirmed`); ListObjectsV2 + ListObjectVersions on the prefix: 0 objects, 0 versions, 0 delete markers (`cleanup.log`). |
| Tray menu on the final CI build | Menu open, "Capture desktop" run from it, completed; Arch and AppImage (`pictures/omarchy-tray-menu-capture-desktop.png`, `final-appimage/`). |
| AppImage row on the final CI build (`appimage-final/row.log`) | Desktop == screendump; region 0 px; window == `grim -T` 0 px; own window refused; conflicts reported (PRINT, SUPER+SHIFT+S); reload keeps binds; clipboard both ways, PRIMARY unchanged; recording motion 21.0 / 69.6 / 71.1 vs static 0.71; quit leaves Omarchy's 251 binds identical. |
| AppImage upload + Chromium (`final-appimage/`) | Hotkey upload origin 200, opened in Chromium, deleted (origin 403). The Nautilus entry belongs to the installed Arch package, whose launcher refuses while the AppImage runs ("put.gd from the AppImage is running…"): existing mixed-install guard, so Nautilus upload is accepted on the Arch package only. |
| #1304 failure notices (PR #1304 CI AppImage, `notices-1304/`) | Notify recorded with dbus-monitor: Cinnamon m74, GNOME f44, KDE d69 each urgency 2 + `transient` (banner frames). Omarchy: the failure notice was not written to quickshell's `live.json`; after a reboot it did not return (`pictures/omarchy-after-reboot-no-transient-failure-1304.png`; the three notices shown came from builds without #1304). |

The "Captured output does not match frozen output geometry" toasts visible in round-2 frames are the three failures of the
earlier, non-working #1299 attempt (05:53–05:55 UTC, previous resident); every operation of the final resident completed.
Fluidity (7.6 fps in this software-rendered VM) and #1301 (`no_anim` not observable with animations off) are accepted as
documented by the coordinator.

### #1304 re-check on d16c23b22 (transient only on quickshell), 2026-11-08 06:56 UTC

PR #1304 head d16c23b22, CI AppImage `26.1108.4138-dev+gd16c23b2246a` (sha256 f954895633064f9a..., `build-info.json`), overlay d3.
The upload client's "nothing uploaded" failure notice went out with urgency 2 and `transient` (`notice-and-dbus.txt`),
showed on screen (`pictures/omarchy-1304-transient-failure-banner.png`), and quickshell's `live.json` kept its six
put.gd rows unchanged (all from builds without #1304). After a QMP reset (guest uptime 35 s) the same six rows came back
and the new notice did not (`pictures/omarchy-1304-after-reboot-d16c23b.png`). Files in `round2/notices-1304-d16c23b/`.
`round2/notices-1304/n-gnome2.json` is the GNOME (f44) DBus summary of the first revision 7fc3232bf.

Physical desktops on the same d16c23b22 AppImage, each under its own desktop lock (released 07:01 UTC, before the 07:30
nightly desktop check), private profile, Notify recorded with dbus-monitor (`round2/notices-1304-d16c23b/n-*3.json`,
banner frames `notice-*3.png`): Cinnamon m74, GNOME f44 and KDE d69 each sent the failure notice with urgency 2 and
**no** `transient`, as on nightly. Cinnamon shows the banner. GNOME queues it behind the first-run notice. On KDE the frame
is covered by stale `test_gui_tray` notices (#1307, not from this run).

## Round 3 (2026-11-08 07:30 UTC): review fixes, rebased on #1283's review fixes

Build: CI of PR #1293 head 6b26ad9b3 (test merge f39263b83 = `26.1108.4175-dev+gf39263b832e1`, Arch package, `round3/review-arch/build-info.json`),
which is #1293 rebased on B's a56046cd8 with cubic's review fixes (ef2792a42 Hyprland, 20490670b shared layer). The pushed head
d18601484 differs from it only in B's 0e66920c8 (labwc bridge + a portal test). Overlay d3 as before.

- `round3/review-arch/row.log`: full row: desktop/region/window exact, own window refused, conflicts reported, reload keeps
  binds, clipboard both ways, recording motion 20.7 / 69.6 / 62.7 vs static 0.70, quit leaves Omarchy's 251 binds. PASS.
- `round3/region2-review/`: two outputs (Virtual-1 at 0,0 and headless PUTGD-2 at 1280,0), wallpaper only, each case its own
  new operation: region on Virtual-1 only, on PUTGD-2 only, across both — each equal to a grim reference of the layout crop
  (the only difference, in the Virtual-1 case, is the pointer that grim draws and put.gd leaves out). Desktop 2304x800. PASS.
  This is cubic's P1 (a region on a subset of outputs failed with display_changed before ef2792a42).
- `round3/region2-review-attempt1/` and `-attempt2/` are rejected runs, kept for the record: attempt 1 left Hyprland's
  automatic position (Virtual-1 moved to x=2304) so the drag spanned both outputs; attempt 2 had maximized terminals (uniform
  regions) and waited only 1.5 s after the hotkey, so the first drag did not end the selection (the crosshair is still in its
  frame) and two cases compared one older file. With 2.5 s and distinct content every case completed.

## Round 4 (2026-11-08): early press, #1308, #1301, shared-region regressions

**Final head 1f17e9468** (CI test merge `1bb4f1db59bb`, `26.1108.4225-dev+g1bb4f1db59bb`), PR #1293 against nightly. Packages used, newest first:

| Build | Head | Used for |
| --- | --- | --- |
| `1bb4f1db59bb` | 1f17e9468 (final) | Omarchy early-press sweep and keyboard on AppImage and Arch; KDE and Budgie regressions (`head2/`, `regress-kde/`, `regress-budgie/`) |
| `7e661cc13096` | 9296c85bb | Omarchy full row on AppImage and Arch, real upload, Nautilus plugin, Chromium, tray (`head/`, `final-head-arch/`) |
| `df80b792e492` | 8ab07477d | Omarchy on both packages: sweeps on one and two outputs, just after an output appears, exact pixels, rotation, keyboard, `no_anim`, no-resident hotkeys, AppImage real upload through Nautilus Scripts (`fix-appimage/`, `fix-arch/`, `*.out`, `last/`, `noanim-fix-arch/`, `nores-*`, `region2-fix-arch/`) |

Since `df80b792e492` only the catcher's cancel paths changed (pointer capability loss; Esc or right-click on the catcher before the selector has started); no capture, region geometry, recording, shortcut, upload or rotation code. The final-build runs of those paths are listed under "Final build, catcher end paths" below.

Early press. Before the fix a press before the selector mapped went to the window underneath and the drag was lost (`selector-ready/`, `selector-ready-kde/`: Hyprland maps at ~0.19 s, KDE's window is ~0.06-0.10 s). `focus-rules/lsx.log` holds twelve bare layer-shell experiments on Hyprland 0.56.2 with real input; they fixed the design: a layer surface with keyboard `none` gets no pointer focus until the pointer moves; a surface that maps with the keyboard, or turns exclusive, releases every held button and the real release is swallowed; switching none to on-demand after mapping releases nothing but only applies at the next motion. `PressCatcher` (Hyprland only) maps a transparent on-demand surface at the hotkey (~0.05 s on this VM) and relays the drag; the selector maps without the keyboard, switches to on-demand after its first frame, and the catcher holds Esc and keyboard selection until then. `design-v3-arch/` is a rejected design kept for the record: switching in the first commit made the surface map with the keyboard and produced wrong-size selections.

Results on Omarchy, press at 0.06 to 1.5 s after the hotkey, pointer static at the start, a terminal under it: settled one output 72/72 and two outputs 72/72 exact on both packages (`df80b792e492`; the only pixel differences are the pointer grim draws); final build 24/24. A press 1.5 s after the hotkey just after an output appears: 16/16. A press 0.3 s after the hotkey just after an output appears: 11 of 16 (with 3 and 2 losses per package): the compositor had not processed the catcher yet (guest load up to 13 on 2 vCPUs from Omarchy's reaction to the output); each lost press left the selector working for the next drag. Keyboard with a static pointer (Esc before and after the selector maps, arrows and Return): 12/12 per package on `df80b792e492`, 6/6 per package on the final build.

#1308: `HyprlandShortcuts::finish` answered a pause before the re-apply removed the binds. Fixed; 40/40 runs of `test_hyprland` under contention on d69 (4 parallel streams, 3 busy loops).

#1301: with animations on and a 4 s linear layer fade, slurp (Omarchy's own no_anim overridden by a later rule) ramps over 3.5-3.8 s; put.gd's selector appears in one sampling step; a capture with the fade on contains no selector, 0 px against grim (`noanim-fix-arch/`, and the G sections of `fix-*.out`).

Shared-layer regressions on the final build (`regress-kde/`, `regress-budgie/`, VMs on d69 on the wall, retired through guarded cleanup; goldens re-hashed unchanged): KDE Wayland (`kde-provisioned-20261016`, deb) and Budgie (`fedora45-budgie`, AppImage). Each: region hotkey + drag 3/3 exact pixels, desktop capture, Esc 3/3 and right-click 3/3 with the pointer static (selector visible, gone afterwards, no image), drags at 0.15 to 1.5 s 16/16, recording with motion (KDE 5.09 vs still 0.04, Budgie 23.3 vs still 0.11). The press catcher, deferred keyboard and relay are only called from the Hyprland adapter; on these two the helper keeps taking the keyboard exclusively at map, as before.

Mixed-install guard: the Arch package's Nautilus entry refusing while an AppImage resident runs is the documented `installation_mismatch` behaviour; the AppImage-only row uses the Nautilus Scripts entry the integration installs, with a real upload (`last/`).

### Final build, catcher end paths (`scaled/`)

Added after going through which rows ran only on builds from before the press catcher. VM `d5` (fresh `omarchy-hyprland-20261108` overlay), final build `26.1108.4225-dev+g1bb4f1db59bb`, AppImage only and then the Arch package. Pointer static at the start point, four drags per delay, press 0.1 / 0.3 / 1.5 s after the hotkey, so the 0.1 and 0.3 s presses land on the catcher:

| Output | AppImage | Arch | Pixel differences against grim |
| --- | --- | --- | --- |
| Virtual-1 1920x1080 scale 1.25 | 12/12 exact size | 12/12 | max 76 px: the pointer grim draws |
| Virtual-1 90 degrees (transform 1) | 12/12 | 12/12 | max 42 px: the pointer |
| Mixed density, drag on the scale 1 output | 12/12 | 12/12 | max 50 px: the pointer |
| Mixed density, drag on the scale 2 output (600x400 physical) | 12/12 | 12/12 | Arch 711 px, box 27x46 at the region's corner: the pointer at 2x. AppImage the same in 6 trials, 9212 px in the other 6 |

In those six AppImage trials the capture also has a light-blue bar across the top rows of the region, starting 133 logical px into the output, which is where Omarchy's notification layer's card sits (`omarchy-notifications`, 113 + 20 margin); the 12 Arch captures are pixel identical to each other and a later attempt to bring the bar back (`toast.py`, no card on screen) did not. It is not the selector: the selector's namespaces were gone and the hint pill is elsewhere (`appimage-scale2-capture-with-bar.png`).

Catcher end paths on the same build, both packages: right button 0.1 s after the hotkey 4/4 (operation `cancelled`, no layer left, no new image, the next region completes); an output removed while the early press is held 3/3 (operation `display_changed`, no layer left, no image, next region completes). Esc on the catcher is in `head2/` (2/2 per package).

Not exercised live: the catcher's "pointer capability lost during a drag" branch. The VM always has QEMU's vmmouse devices, so unplugging the USB tablet does not take the seat's pointer away. The unplug itself, with the button held, broke the VM for the test: every left drag afterwards was lost, also on freshly started residents, while the right button still worked; a fresh overlay was clean. That run and the one before it are discarded (the VM was retired through guarded cleanup; the scripts are here).
