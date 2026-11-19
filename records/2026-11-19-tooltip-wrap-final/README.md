# Long tooltips wrap to a reading width (final build)

This record covers PR #1694 at commit 05501ec22a0777623c509972ae0beb4af6904411, the head Sol reviewed in round 3. The next commit, 67c005082c737f94d413a745e1ece656f0b31019, changes only menu and drop-down list tooltips, which these pictures do not show. It replaces the pictures in record 2026-11-19-tooltip-wrap, which show the first design. Sol's round 1 replaced that design.

What was tested: hovering over controls with long tooltips in the real put.gd Settings window, before and after the change, on two desktops.

- **Cinnamon X11:** m74, Linux Mint 22.3, 1920x1080, physical desktop. The pointer was moved with xdotool and the frame captured with `import -window root` 2.5 s later.
- **Plasma Wayland:** k72, Kubuntu 26.04, 1920x1080, physical desktop. The pointer was moved through the desktop's VNC server (`tools/lab/rfb.py`) and the frame captured the same way.
- **Before:** nightly 26.1118.5367 AppImage. **After:** the PR head built on each host with the dev preset (`putgd`, `putgd-ui`, `putgd-cli`). Each run used a private put.gd profile.
- The red boxes mark the tooltip, found by comparing the frame with a frame that has no tooltip there.

Result: on both desktops, long tips that were one line across the screen are now wrapped to about 45 characters and start at the pointer. Qt and the compositor place them. On X11 a tip near the right screen edge opens to the left of the pointer. On Plasma Wayland, KWin keeps it on screen against the edge.

An offscreen check on k72 also confirmed two more cases: a drop-down list row's tooltip (a long audio device ID) wraps while the row's stored tooltip text stays unchanged, and a tooltip holding a long file name with no spaces breaks inside the name. The review window's tooltip hover test passes under ctest on k72.

The light and dark schemes differ only because the AppImage and the build tree picked different schemes; that is not part of this change.
