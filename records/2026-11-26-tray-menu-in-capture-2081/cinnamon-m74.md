# Cinnamon (m74): no menu in captures before or after

Linux Mint 22.3 Cinnamon on X11 (m74), 2026-11-26 03:31-03:42 UTC, under `desktop_lock.py`. Builds: published nightly 26.1125.7045 AppImage and candidate AppImage 26.1126.7129-dev+g7262415116b6 (commit 7262415, merged as #2086). Cinnamon's `desktop-effects-on-menus` was `true`.

**Timing.** Four traces: the host sends `EventGroup` "clicked" for the row and no "opened" or "closed" events. The wall VNC frame over the menu matched the menu-free frame 15-26 ms after the click, so there is no visible fade.

**Menu in the picture** (caught / tries):

| Build | Repeat last region | Monitor | Desktop | Window | Region, screenshot first |
| --- | --- | --- | --- | --- | --- |
| nightly 26.1125.7045 | 0/8 | 0/8 | 0/8 | 0/8 | 0/3 |
| candidate 7262415 | 0/8 | 0/8 | 0/8 | 0/8 | 0/3 |

Cinnamon never had the bug: its menu is gone before the capture is taken. The fix adds its Cinnamon allowance, 184 ms (`cinnamon-menu-effects` in `diagnostics.trayMenu.settle`). Click to saved file: Repeat 0.61-0.67 s → 0.89-0.94 s, monitor/desktop/window 0.83-0.92 s → 1.12-1.19 s. A Cinnamon allowance of one frame (34 ms) would match what was measured.

Desktop hotkey (Ctrl+Shift+3), key press to saved file: nightly 0.81-1.11 s, candidate 0.84-1.21 s. Both builds show the same two clusters, near 0.84 s and near 1.1 s; no tray wait was recorded for a hotkey.
