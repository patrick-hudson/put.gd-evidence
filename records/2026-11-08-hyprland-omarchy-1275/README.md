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
