# Budgie adapter acceptance, round 2 (#1275, PR #1283)

Before #1283 merged, the coordinator asked for the remaining acceptance items:

- the upload link opened in the real browser;
- A/V sync;
- #1294, the tray glyph on Ubuntu Budgie 26.04;
- #1295, window capture unavailable shown in the UI;
- #1296, Magpie window recording, plus the Magpie region row;
- a same-host fps comparison with KDE.

Round one is in [2026-11-08-budgie-adapter-1275](../2026-11-08-budgie-adapter-1275/).

Builds:

- **CI run 42451753403**: head 4c57728c8 merged onto nightly, so `1fa5cde67a8b`.
  - Ubuntu 26.04 DEB, sha256 `02c3af07…`.
  - Fedora 44 RPM, sha256 `ca38e5d4…`.
  - AppImage, sha256 `4b515d28…`.
- **The #1295 screenshots** come from CI run 42453451587 (head 18852a0fb). That commit only gives the wrapped reason its full height.
- **Link open and A/V sync** used the round-one packages: the F45 RPM of 2b9402b2f, and the U26 CI DEB `2f3d0fcea014`. Neither path changed afterwards.

Input in the VMs came from QMP. Frames are VNC grabs.

## Results

| Item | Result | Evidence |
|---|---|---|
| Upload link opens in the real default browser: F45 | **pass**. Window capture uploaded to `put.gd/acceptance/b1275-65ee433b7a43/`. `history.openLink` (route `portal`) opened Firefox, which loaded the object. Cleanup: object deleted through put.gd's delete.prepare/confirm, so the prefix lists 0 keys; history cleared; profile removed; keyring entry deleted (receipt `cleanup_confirmed`) | `images/budgie-f45-link-open.png` |
| Upload link opens in the real default browser: U26 | **pass** (sub-worker B4). Snap Firefox loaded `put.gd/acceptance/b1275-05facb11c7a9/…`; the same cleanup ran, and the prefix lists 0 keys | `images/budgie-u26-link-open.png` |
| A/V sync, F45 (`wlr-capture`, system audio from PipeWire's null sink, put.gd's own `--av-marker` played by GStreamer `playbin`) | WebM median **+7.5 ms**, spread 34 ms. MP4 median **−13.3 ms**: −13.3/+20 in steady state; the first two pairs read −113 ms | numbers here |
| A/V sync, U26 | MP4 median **−16.7 ms**, WebM median **+7.5 ms**. Steady state is within one frame. The first pairs read −50 to −126 ms | numbers here |
| fps at 1080p60, same host and VM type (f44, 2 vCPU, software rendering, quiet host) | Budgie F45: **31.5** distinct frames/s against a 36.6 fps fixture; longest stall 1.55 s, at start. KDE neon 6.8.1: **13.6** distinct frames/s against a 22 fps fixture; longest stall 0.37 s | numbers here |
| #1294 tray on U26 | **fixed**. The tray host is `ayatana-indicator-application-service`, which ignores `IconPixmap`. put.gd now also names its glyph: `IconName` `putgd_tray_<pid>_<n>`, `IconThemePath` `$XDG_RUNTIME_DIR/putgd/tray`, with the dash-free name. F44 and F45 (budgie-daemon tray) still use the pixmap. The dbusmenu "too many keys" warnings are gone: unbound entries no longer send an empty shortcut | `images/budgie-tray-named-icon.png`, `frames/*-trayfinal.png`, `frames/u26-tray-glyph-written-by-putgd.png` (the PNG put.gd wrote) |
| #1295 window capture unavailable shown in the UI (U26, labwc 0.9.3) | **fixed**. The Capture window button carries the alert badge and names the protocol in its tooltip. Settings → Advanced → Desktop support details shows a Window capture row with the full reason | `images/budgie-window-unavailable-ui.png` |
| #1296 Magpie window recording | **fixed** (root cause found by B5). Once `cancel` answers, `capabilities.active` is null, but the old helper can still be exiting, and a prepare in that window was refused with `recording_active`. Now one such prepare waits for the exit. Reruns: Magpie 5/5 fresh sessions, 12/12 window clips, cancel-then-prepare driver 5/5 (was 0/5); labwc 6/6 and 5/5. On the real F45 AppImage: 5/5 cancel-then-window-prepare rounds, clips with motion 15.4–18.6 | `magpie/` (results.txt, exitgap.txt, test-before-after.txt) |
| Magpie region (headless, `zwlr_virtual_pointer`) | **pass**, exact pixels, live and screenshot-first, 2 fresh sessions. 200x150 = 30,000 px, all the fixture colour. A drag across a 32 px white corner square gives exactly 1,024 white px at (0,0,31,31). Right-drag cancels | `magpie/results.txt` |

## Notes

- **A/V sync early pairs.** In the first seconds the encoder can't keep up in a 2-vCPU software-rendered VM, so frames are dropped at the capture queue (seen in the recorder's debug log). When the flash's own frames are dropped, the flash is found a few frames late, which gives the negative early offsets. The timestamps are correct: steady-state pairs sit within one frame. This is the same effect as the fps start stall.
- **F45 live credentials.** Fedora 45 Budgie's Secret Service is oo7-daemon, whose login collection is locked under autologin and ignores `SetAlias`. So the lane used a private gnome-keyring on `/dev/shm`, reached by its unique bus name, for both the credential bridge and the resident. oo7 was left untouched. Key set 2 was read only on the builder and passed through the bridge's stdin.
- **New Magpie finding (#1305).** After about 6 capture sessions on one window, Magpie stops repainting that window, while labwc never does.
