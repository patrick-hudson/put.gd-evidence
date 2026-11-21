# Remove from History only for a deletion that ended without removing the file (#1763)

What was checked: History's new **Remove from History only…** button and its confirmation, for a
file whose deletion ended `unsupported_safe_removal` after an interrupted attempt saved a `phase`
checkpoint.

- Host: k72, Kubuntu 26.04, Plasma Wayland, real session (frame from the host's loopback VNC wall),
  under the k72 desktop lock.
- Build: dev build of put.gd-desktop branch `fix/deletion-checkpoint-way-out`, commit `ce503b8d9`
  (tree synced without `.git`).
- Window: the production `HistoryWindow` with the GUI test fixture's synthetic destination; one
  clipboard upload; its deletion journal set to `unsupported_safe_removal` with a `phase` checkpoint.
  The driver clicked **Remove from History only…** and the frame shows the confirmation.
- Annotations drawn with put.gd's own editor (headless resident, `editor.apply`, `editor.saveCopy`).

Result: the button sits beside **Retry deletion**, and the confirmation first says the file may
still be at its destination and that put.gd will stop tracking it.

Files: `remove-from-history-only.png` (raw crop), `remove-from-history-only-annotated.png`.
