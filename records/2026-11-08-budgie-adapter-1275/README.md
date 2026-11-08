# Budgie adapter acceptance (#1275, PR #1283)

The `budgie-wayland` adapter (Budgie 10.10 on labwc) and the shared
compositor-neutral Wayland layer (`src/platform/wayland/`), tested on
2026-11-08 UTC.

Builds:

- **F45 RPM** from 663513670 (`putgd-26.1108.4108~dev+g663513670e75-1.fc45`).
- **F45 RPM** from 2b9402b2f (`putgd-26.1108.4143~dev+g2b9402b2f29d`).
- **CI run 42442172315 packages** (head 2b9402b2f merged onto nightly 598de46c, so `2f3d0fcea014`):
  - Fedora 44 RPM;
  - Ubuntu 26.04 and 24.04 DEBs;
  - AppImage, sha256 `0739573403…`.

Real sessions ran in QEMU VMs made from the Budgie goldens: `fedora45-budgie`, `fedora44-budgie`, `ubuntu-budgie-2604` and `ubuntu-budgie-2404`. Keyboard and pointer input came from QMP, never `wtype`. The headless runs used labwc 0.20.2 with the real Budgie 10.10.3 labwc bridge, and Magpie on Mir 2.29. They are supporting evidence only.

## Images

`images/` holds the annotated pictures used in the PR and the docs:

- `budgie-shortcut-conflict.png`: `Print` is reported as a conflict that names Budgie's own screenshot binding.
- `budgie-print-kept.png`: a real `Print` press still opens Budgie's own screenshot dialog.
- `budgie-control-center-edit.png`: an edit made in Control Center shows in Settings as "Active · Ctrl+Shift+F8".
- `budgie-region-recording.png`: during a region recording, the control bar and the dimming sit outside the recorded rectangle, and no dialog appears.
- `budgie-window-unavailable.png`: on labwc 0.9, the window hotkey gives a notification that names the missing protocol.

`frames/` holds unannotated VNC frames. The `b1-` frames are from the F45 session:

- hotkey runs `s1` to `s3`;
- selector `s4`;
- region recording `rr-recording`;
- tray menu;
- notification;
- dark theme;
- portal file dialog `fd1`;
- About link opened in Firefox.

The other frames:

- `b2-desktop-two-heads-rotated-scaled.png` is put.gd's desktop capture of the F45 two-head VM. One output is rotated 90°, the other is at scale 1.5.
- `b3-f1-window-unavail.png` is the F44 window-unavailable notification.

## Headless logs

`headless/`:

- `budgie-session-labwc-0.20.2.log`: the Budgie bridge session. Covers bind, Print conflict, unbind, rebind and quit cleanup, monitor and window recording through `wlr-capture`, and a hotkey with no resident.
- `region-virtual-pointer-labwc.log`: a region drag through the layer-shell selector with a virtual pointer. Every pixel matches exactly, both live and screenshot-first.
- `magpie-mir-2.29-run3-pass.log` and `magpie-mir-2.29-run4-window-recording-none.log`: Magpie 58a0d7a on Mir 2.29. Window recording gave no clip in 2 of 4 runs; follow-up #1296.
- `ctest-full.log`: 142/143. The one failure, `capture_preparation_x11`, fails the same way on a nightly baseline on the same host.

## Acceptance

| Row | Result |
|---|---|
| Region drag exact pixels, live and screenshot-first | pass. F45 real session: 200x150, all 30,000 px the fixture colour, no outline. U26: 300x180 live and 260x140 screenshot-first. Headless: exact, live and screenshot-first. Multi-head exact pixels: headless only, because QMP tablet coordinates are not 1:1 on multi-head |
| Escape and right-click: no publication, no clipboard change | pass (F45, U26; right-click headless) |
| Window: active external client, content only, or unavailable naming the protocol | pass. F45: 420x300 client content. F44 and U26: `window_unavailable` naming ext-foreign-toplevel-image-capture-source, no region fallback |
| Own windows refused by app ID | pass (integration test) |
| Desktop: all outputs, fractional scale, rotated output | pass. F45 two heads, rotated 90 plus scale 1.5: the composite matches the framebuffers |
| Display change during selection gives `display_changed` | pass (F45 real session, headless) |
| Bridge hotkeys Ctrl+Shift+1/2/3 with a real QMP keyboard | pass (F45, F44, U26, AppImage) |
| Budgie Print conflict reported, Budgie's binding kept | pass (F45, U26) |
| Rebind, unbind and uninstall leave rc.xml clean | pass (F45, F44, U26) |
| Control Center edit shows in Settings | pass (F45, U26) |
| Hotkey with no resident is harmless | pass (F45, U26, headless) |
| Clipboard import while unfocused, paste into a GTK app, PRIMARY unchanged | pass (F45, U26, U24, headless, Magpie) |
| Recording: no dialog, cursor visible, motion | pass. F45 window motion 3.38, U26 region 97.5, U24 region 105.8 |
| fps at 1080p60 | measured. F45 steady state 31–34 distinct/s, which equals the fixture's own rate in a software-rendered 2-vCPU VM. The first ~4 s are sparse because of x264enc warm-up; the source delivered every frame. U26: 25 distinct/s with the same shape. Not compared with KDE: the fixture window never showed on KWin in the neon VM |
| Region recording excludes the bar | pass (F45, U26, U24) |
| Recording audio A/V sync | not run |
| Tray, notifications, file dialogs, theme, link open | pass. On U26 the tray glyph is missing (#1294). Nemo upload: pass (U26, U24; F45 has no Nemo). The upload-link open was not done: no credentials in the guests |
| Resident memory vs KDE, same VM type | F45 RPM idle PSS 5.9 MB, post-use 6.9 MB. F45 AppImage idle 7.5 MB (+0.9 MB AppRun), post-capture 20.5 MB. KDE neon 6.8.1 AppImage on the same host: idle 6.9 MB, post-capture 14.7 MB |
| Installed package startup | pass: F45 and F44 RPM, U26 and U24 DEB, F45 AppImage |
| Ubuntu Budgie 24.04 (X11) | pass through the `cinnamon-x11` adapter |
| Magpie / Mir 2.29 (headless) | capture, window capture, clipboard, monitor recording: pass. Shortcut status is truthful (`none`). Window recording passed in 2 of 4 runs (#1296). Region not tested |
