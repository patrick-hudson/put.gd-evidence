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
