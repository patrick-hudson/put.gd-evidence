# Tray menu kept out of captures started from it (#2081, PR #2086)

Choosing a capture from put.gd's tray menu caught the closing menu in the picture: the capture started at the click, while the tray host's menu was still drawn or fading out. This record holds the lab counts and before/after pictures for PR #2086.

**Builds.** Before: published nightly 26.1125.7045 (DEB on k72, RPM on f44, AppImage on d69; AppImage on k72 and f44 for the hotkey comparison). After: candidate AppImage 26.1126.7127-dev+g5d4e998a0403 from the manual CI run 45740122150 on branch `candidate/tray-menu-2081` (commit 5d4e998a0, tree 02474e9a4c34), and on d69 a scratch dev build of the same change (df899c7fa).

**Method.** Each run held a `desktop_lock.py` lock and used a private lab resident in the builder's real desktop session. A uinput tablet opened the tray menu with real clicks (right click on Plasma, left click on GNOME) and chose a row. The saved picture was compared over the menu's rectangle with a menu-free frame; a mean difference over the threshold counts as "menu in the picture". Timing traces log the host's dbusmenu Event calls (dbus-monitor) against the wall VNC frames over the menu's rectangle.

**Menu in the picture** (caught / tries)

| Desktop | Build | Repeat last region | Monitor | Desktop | Window | Region, screenshot first |
| --- | --- | --- | --- | --- | --- | --- |
| d69 Debian 13 Plasma 6.3 Wayland | nightly | 8/8 | 8/8 | 8/8 | 0/8 | 3/3 |
| d69 | fix (scratch build) | 0/8 | 0/8 | 0/8 | 0/8 | 0/3 |
| k72 Kubuntu 26.04 Plasma Wayland | nightly | 8/8 | 8/8 | 8/8 | 0/8 | 3/3 |
| k72 | candidate | 0/8 | 0/8 | 0/8 | 0/8 | 0/3 |
| f44 Fedora 44 GNOME Wayland | nightly | 8/8 | 8/8 | 8/8 | fails, no focused window | — |
| f44 | candidate | 0/8 | 0/8 | 0/8 | not run | 0/3 |

Live region selection (the default) was 0/4 on d69 and 0/1 on k72 with the nightly, because the grab follows the drag. A 3 s capture delay was 0/6.

**Timing.** Plasma (d69, k72, aurora): the host sends "closed" about 1 ms before "clicked", and the menu fades out until about 0.47-0.50 s after the click. GNOME (f44): "clicked", then "closed" 1-6 ms later, and the menu is gone about 0.17 s after the click. The candidate recorded a 455-456 ms wait on Plasma (`kwin-fadingpopups`) and a 185 ms wait on GNOME (`gnome-popup-animation`, after the host's close).

**Hotkeys are not delayed.** Desktop capture by Ctrl+Shift+3, key press to saved file, same package type:

| Desktop | Nightly AppImage | Candidate AppImage |
| --- | --- | --- |
| k72 | 0.51-0.58 s, median 0.52 s | 0.51-0.60 s, median 0.52 s |
| f44 | 1.48-1.74 s, median 1.50 s | 1.49-1.52 s, median 1.51 s |

After the candidate's hotkey runs, `diagnostics.trayMenu.settle` still showed the earlier tray row, so no hotkey went through the menu wait.

**Pictures.** `2081-k72-repeat-before-after.png` and `2081-f44-repeat-before-after.png`: Repeat last region from the tray menu with the nightly (menu caught, boxed red) and with the candidate (menu gone, same area boxed green).
