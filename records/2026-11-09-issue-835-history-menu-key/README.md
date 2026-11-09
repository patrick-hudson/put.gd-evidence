# Issue 835: History row menu and the Menu key

Run 2026-11-09 on disposable QEMU/KVM overlays on d69, cinnamon-x11 (Mint, Qt 6.4.2) and
gnome-provisioned (Ubuntu 26.04 GNOME Wayland, Qt 6.10). "Before" is the published
26.1109.4346-nightly package. "After" is `putgd`, `putgd-cli` and `putgd-ui` compiled
from the fix (m74 for Cinnamon, k72 for GNOME) and installed into the overlay.

`keyprobe.cpp` is an LD_PRELOAD event filter that records what Qt delivered and accepts nothing.
`witness.py` drove the guests; `results.md` holds the event sequences.

Frames: `before-cinnamon-nightly-after-one-esc.png` and `after-cinnamon-fix-after-one-esc.png`.
The red and green boxes and captions were added afterwards.
