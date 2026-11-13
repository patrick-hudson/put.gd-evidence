# Issue 1428: the Copy text pipeline on five desktops, with a stand-in helper

Receipts for put.gd-desktop pull request #1442 (issue #1428, item 4b). Each run starts Copy text three ways (the real hotkey, the tray entry, the window button), selects a 400 x 160 region with real pointer input, and reads the clipboard back with a client that is not put.gd.

**What this shows and what it does not.** The packages are the ones CI built for the pull request. They hold no `putgd-ocr`, so a stand-in was placed where the resident looks for it: `scripts/fake-putgd-ocr.py`, a 40-line script that speaks the text-job protocol and answers with one fixed line naming the size of the image it was handed. A paste of `put.gd fake helper 1428: region 400 x 160` therefore shows that the selected region travelled from the trigger through the desktop's adapter, the resident and the helper exchange to the clipboard. It says nothing about recognition, speed or memory of the real engine.

| Desktop | Where | Package | Result |
| --- | --- | --- | --- |
| Linux Mint 22.3, Cinnamon X11 | m74, physical | Ubuntu 24.04 DEB, run 43370645143, `26.1113.4769~dev+gc74a2a3cc206` | hotkey, tray, window: passed |
| Debian 13, Plasma Wayland | d69, physical | Debian 13 DEB, same run | hotkey, tray, window: passed |
| Fedora 44, GNOME Wayland (Shell extension 23) | f44, physical | Fedora 44 RPM, run 43374022759, `26.1113.4776~dev+g777c543055a2`, sha256 `d7718c59…` | hotkey, tray, window: passed |
| Fedora 44, Budgie 10.10.2 on labwc 0.9.6 | lab guest on d69, fresh overlay of `fedora44-budgie` | AppImage, run 43374022759, sha256 `82191d40…`, extracted | hotkey, tray, window: passed |
| Omarchy 4.5.0, Hyprland 0.56.2 | lab guest on d69, fresh overlay of `omarchy-hyprland-20261108` | the same AppImage, extracted | hotkey, tray, window: passed |

Run 43370645143 built the merge commit of pull request head `84c6f4f66`; run 43374022759 built the merge commit `777c5430` of head `dde4d0a0d` (the same change rebased onto the integration branch with the engine; the only difference in this pull request's own files is how the `copy-text` glyph is drawn).

## How

- `scripts/text_proof.py` runs on the desktop itself. It starts the installed resident in the running session, sets `Ctrl+Shift+9` for the `text` action, and for each trigger puts a sentinel on the clipboard, starts Copy text, waits for the operation to reach `acquiring`, drags the region, waits for the terminal record and pastes. The m74 and d69 runs used an earlier revision of the same script (before the GNOME and guest options were added).
- **Hotkey:** real key events. On the builders they come from `tools/lab/host_input.py` (kernel uinput devices); in the guests from the VM's own QMP socket (a tablet and a keyboard), forwarded into the guest for the run (`scripts/guest_run.sh`).
- **Tray entry:** the menu's own `com.canonical.dbusmenu` `Event(41, "clicked")` sent to put.gd's tray item, which is what a panel sends. No pointer click on a panel was made.
- **Window button:** a real pointer click. On X11 the window position is read with `xdotool`, on Plasma through a temporary KWin script. GNOME, labwc and Hyprland were handled by keeping one frame of the desktop and reading the button's centre off it; the frames are in `pictures/` with the button boxed (drawn with put.gd's own editor, headless).
- **Paste:** `xclip` on X11, `wl-paste` on Wayland.
- On the builders the resident ran with private configuration, data, state and cache folders; in the guests it ran as the guest's user would run it. After each run: no text operation left in the journal, and the stand-in's line in no file under those folders (`recognizedTextOnDisk` in the receipts).
- On f44 the package and the stand-in were installed under the desktop lock, the session was restarted once so that the Shell loaded extension 23, and afterwards both were removed and the session restarted again so that the Shell holds no removed extension. The AppIndicator extension, found disabled, was turned on for the tray entry and left on, which is the builder's documented state.
- Both guests were stopped and their overlays retired with `lab.py cleanup` and a completion manifest (`scripts/retire.py`). The goldens were not written to (checksums matched before launch).

## Files

| Path | What |
| --- | --- |
| `receipts/*.json` | One receipt per desktop: build identity, adapter, the hotkey binding as the desktop reports it, each trigger's sentinel, terminal record and paste. `d69-plasma-wayland-repeat.json` is a second, hotkey-only run that checks `capture.repeat.remembered` stays false after a text capture. |
| `logs/*.log` | The script's output for the three later runs. |
| `pictures/gnome-window.png`, `budgie-window.png`, `hyprland-window.png` | The frame each window click was read from. The guests' frames also show the notification of the trigger before ("Copy text, Copied 41 characters"). The Hyprland window is 1256 px wide and shows the narrow labels. |
| `pictures/m74-selector-crop.png` | A crop of the selector on Cinnamon during the hotkey trigger. |
| `scripts/` | The driver, the stand-in helper, the guest runner and the guest retirement script. |

Everything on screen is synthetic: a text window the run opened itself, or a disposable guest's desktop.
