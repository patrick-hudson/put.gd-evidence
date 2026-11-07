# GNOME: dragging a modal dialog dragged the whole put.gd window

Patrick's report (2026-11-07, f44 scratch build 7300a32): dragging the editor's
**Custom color** dialog moved the entire editor window with it.

## Cause

GNOME ships `[org.gnome.mutter:GNOME] attach-modal-dialogs=true`
(`/usr/share/glib-2.0/schemas/00_org.gnome.shell.gschema.override` on Fedora 44;
a plain `gsettings get` over SSH without `XDG_CURRENT_DESKTOP=GNOME` reports
`false` and hides it). Mutter attaches every modal dialog to its parent and moves
the parent when the dialog is dragged. Since Qt 6.8, Qt Wayland marks modal
windows through `xdg-dialog-v1` (`xdg_wm_dialog_v1`), so every put.gd modal on
GNOME became attached. Fedora 44 ships Qt 6.11; the AppImage bundles Qt 6.12.

## Probe (probe/)

`main.cpp` is a 30-line Qt app: a parent window plus a `QColorDialog`.
`drive.py` drags the dialog title through `tools/lab/host_input.py` (uinput).
f44 GNOME 50, Qt 6.11.2:

| Case | Parent moved with the dialog |
| --- | --- |
| frameless parent, `QColorDialog::getColor` (modal) | yes (`modal-before/after.png`) |
| decorated parent, `getColor` | yes |
| `Qt::WindowModal` `QColorDialog` | yes |
| non-modal `QColorDialog` | no |
| `getColor` with `QT_WAYLAND_DISABLED_INTERFACES=xdg_wm_dialog_v1` | no (`np-after.png`) |

k72 Kubuntu 26.04 Plasma 6.6 (KWin), Qt 6.10, modal `getColor`: the dialog moved
alone (`k-before.png`, `k-after.png`). Not reproducible on Plasma. Mint 22.3
Cinnamon (X11, Qt 6.4) has `org.cinnamon.muffin attach-modal-dialogs=false`.

## Fix acceptance (frames/), f44, real put.gd editor

Same steps for both builds: open a file in the editor, restore the window,
Highlight, the **+** custom color swatch, then drag the dialog title 200 px
right and 150 px down.

- `before-open.png`, `before-drag.png`: unfixed build 7300a32; the editor moved
  with the dialog and the main window shows behind it.
- `after-open.png`, `after-drag.png`: fixed build; the dialog moves, the editor
  stays where it was. The dialog opens centered on the editor instead of
  attached under its header.
- `after-block.png`: clicking Arrow behind the open dialog does nothing; the
  editor stays blocked and the dialog stays above it.
- `after-ok.png`: picking a color and pressing OK adds the recent swatch.
- `fd0.png`, `fd1.png`: Save a copy (GNOME portal chooser) also moves alone.

The image in the editor canvas is a k72 screenshot of the probe, so it shows a
color dialog of its own.
