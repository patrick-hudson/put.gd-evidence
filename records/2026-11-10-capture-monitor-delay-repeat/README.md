# Capture monitor, delayed capture and Repeat last region (#1363)

Pictures and check logs for put.gd-desktop pull request #1368, taken on 2026-11-10.

## The build

| | Version | Commit |
| --- | --- | --- |
| After | `26.1110.4432-dev+ge7313b3ce650`, git tree `afd2899a1087` | PR #1368 at `d81726760` (the version's own hash is the PR's merge commit; the tree is the head's) |
| Before | `26.1109.4404-dev+g32a9a763e350` | nightly at `32a9a763e`, where the work started |

Every "after" picture and every log is from the PR head's own CI packages: the DEB for
Ubuntu 24.04 (Mint Cinnamon), the DEB for Ubuntu 26.04 (Ubuntu GNOME 50.1, Kubuntu Plasma
6.6), the AppImage (Fedora 45 Budgie on labwc 0.20) and the Arch package (Omarchy,
Hyprland 0.56). All sessions are lab virtual machines with two monitors, 1280x800 and
1024x768, except the before and after pairs, which use one 1280x800 monitor.

## Pictures

The boxes, arrows and red labels were drawn with put.gd's own image editor, through the
session methods the MCP helper's `open_editor`, `edit_image` and `save_editor_copy` call.
The white captions over each panel were written the same way. Pillow only cropped and
arranged the screen captures.

| File | Shows |
| --- | --- |
| `01-band-before-after.png` | The window's command band before and after: the new Capture monitor button |
| `02-tray-before-after.png` | The tray menu on Cinnamon before and after: Repeat last region, Capture monitor, the Capture delay submenu |
| `03-shortcuts-before-after.png` | Settings, Shortcuts before and after: the two new rows, not set by default |
| `04-rail-menu-desktops.png` | The capture buttons' context menu on all five desktops: Repeat last region and Capture delay with its four choices |
| `05-tray-menu-desktops.png` | The tray menu on all five desktops with the three new entries |
| `06-countdown-desktops.png` | The countdown on all five desktops |
| `07-two-monitors-one-capture.png` | A two-monitor desk and the Capture monitor result: the monitor under the pointer alone, at its own size |
| `08-delay-keeps-open-menu.png` | A delayed capture: an application's open menu with its hovered row stays through the countdown and is in the capture; the countdown is not |
| `09-repeat-refusal.png` | Repeat last region with nothing to repeat: the notice and the History entry |
| `10-desktop-support-gnome.png` | Desktop support details on GNOME while an older extension is still loaded: the Monitor capture and Delayed capture rows with the reason |
| `11-window-100.png` | The window at 100%, 1280 px wide: every command in full |
| `12-window-150.png` | The window at 150% (1920x1200 output, scale 1.5): Window, Monitor and Desktop shorten first |
| `13-checks-cinnamon-gnome.png`, `14-checks-plasma-budgie-hyprland.png` | The check driver's output on each desktop, as text in `logs/` |

## Logs

`logs/cinnamon.log`, `gnome.log`, `kde.log`, `budgie.log` and `hyprland.log` are the output of
`scripts/checks.py` on each guest: 15 checks, 0 failed on each. They cover Capture monitor
with the pointer on each monitor and the whole desk, Repeat last region with its two
refusals and the restored layout, a delayed desktop capture whose countdown is found in a
screendump and is absent from the saved image, a delayed live region, a click on the
countdown, `operation.cancel`, a lock during the countdown and a capture after unlocking.
Each log starts with the build and its git tree.

`logs/gnome-old.log` is GNOME with the lab image's older extension (version 1) still
loaded and version 20 packaged: `monitor`, `repeat`, delayed captures and, as before this
change, a region capture answer `helper_outdated`; a desktop capture completes.

On Hyprland the Repeat line notes the compositor's cross cursor in the last 11 px of the
selected capture. Hyprland paints software cursors (which a virtual machine gets) into
some frames although put.gd asks for no cursor; the region selector is not changed by this
pull request.

## Scripts

`scripts/` holds what produced this record: `checks.py` (the checks), `vmdrive.py` and
`shot.sh` (single steps and screendumps), `pics-*.sh` (the raw pictures), `compose.py` and
`compose_logs.py` (cropping, arranging and the call-out lists), `annotate.py` and
`annotate-all.sh` (drawing the call-outs with put.gd's editor). They expect the lab tool
`tools/lab/lab.py` of the put.gd-desktop tree and the guests named in them.
