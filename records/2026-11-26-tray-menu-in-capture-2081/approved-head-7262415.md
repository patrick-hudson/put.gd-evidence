# Approved head 7262415: lab rows

The Sol review changed when the wait starts and how it is timed (a late close restarts the fade; a host that sends "opened" has its first close waited for; a precise timer). These rows rerun the lab on the approved head. Candidate AppImage 26.1126.7129-dev+g7262415116b6, manual CI run 45743811837 on `candidate/tray-menu-2081` at commit 7262415116b6ba3952b337a598b6086179f8750c. The aurora nightly rows replace an earlier aurora run that overlapped another session's guest.

Menu in the picture (caught / tries):

| Desktop | Build | Repeat last region | Monitor | Desktop | Window | Region, screenshot first |
| --- | --- | --- | --- | --- | --- | --- |
| aurora Fedora 45, Plasma 6.8 Wayland | nightly 26.1125.7045 AppImage | 8/8 | 8/8 | 8/8 | 0/8 | 3/3 |
| aurora | candidate 7262415 | 0/8 | 0/8 | 0/8 | 0/8 | 0/3 |
| k72 Kubuntu 26.04, Plasma Wayland | candidate 7262415 | 0/8 | 0/8 | 0/8 | 0/8 | 0/4 |
| f44 Fedora 44, GNOME Wayland | candidate 7262415 | 0/8 | 0/8 | 0/8 | not run | 0/3 |

Recorded wait (`diagnostics.trayMenu.settle`): 454-456 ms on Plasma (`kwin-fadingpopups`, the host's close before the click), 185 ms on GNOME (1 ms waiting for the host's close, then `gnome-popup-animation`).

Desktop hotkey (Ctrl+Shift+3), key press to saved file: aurora nightly 0.46 s, candidate 0.46-0.48 s. f44, paired AppImage runs: nightly 1.52-1.54 s, candidate 1.52-1.54 s. k72: candidate 0.54-0.56 s (one 0.98 s outlier while another session's `putgd-ui-catalog` used about 31 % CPU); the earlier paired AppImage run on k72 had nightly median 0.52 s against candidate median 0.52 s.

k72's first candidate run lost three loop rounds and two frozen-region tries. A session `operation.recent` call answered `history_io` once (the next calls worked; nothing in the resident log), and the host was loaded. A make-up run gave the remaining rounds; the table counts both runs.

Pictures: `2081-aurora-repeat-before-after-7262415.png`, `2081-k72-repeat-before-after-7262415.png` and `2081-f44-repeat-before-after-7262415.png`, Repeat last region from the tray menu, nightly against candidate 7262415.
