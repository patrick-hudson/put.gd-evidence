# Review-body findings: GNOME setup, Hyprland binds, wlr-capture

Evidence for PRs #1320 and #1321, which fix CodeRabbit findings left outside the diff on earlier PRs. All runs use CI AppImages on VM overlays.

## GNOME 50.1 (Ubuntu 26.04 golden, d69)

`gnome/run-final-head.log`, CI AppImage `3e669333d` (production code identical to the #1320 head, whose last commit only corrects a test path); the before build is `a2c36cc07`, #1315's head. The Shell ran extension v18 from an owned user copy, `~/.local/share/gnome-shell` was read-only (a real failed update), and the before and after builds ran in turn with the same fixtures:

| | Before (`a2c36cc07`) | After (`3e669333d`) |
|---|---|---|
| `desktop.setup` | `login_required`, "log out and back in" | `install_failed`, naming the path |
| Notification | "…log out and back in…" (`gnome/before-failed-update.png`) | "could not install…" (`gnome/refusal-notification.png`, `refusal-and-notification.log`) |
| Symlink `.putgd-extension-old-<32 hex>` | target's files deleted (`victim: []`) | target untouched |
| `.putgd-extension-backup` and a real dir with `notes.txt` | files deleted | untouched |

With the directory writable again, `desktop.setup.recheck` wrote v19 and asked for a logout, and a real logout and typed login reached `ready` with v19 loaded. The stale directory with put.gd's exact name and contents is removed.

## Hyprland 0.56.2 on Omarchy (d69)

`omarchy/run-final-head.log`, CI AppImage `28caec991`. Rebinding, moving to and from an F key, unbinding and quitting left `reloadsIssued` at 0 and a third-party runtime bind (`rt:other-program`) in place, with Omarchy's 251 binds identical. A real Ctrl+Shift+9 press still fired. A bind sharing put.gd's key took the reload path (`reloadsIssued` 1), which restores the configuration's binds and, as documented, drops other programs' runtime binds. `shutdown()` on the event socket followed by a reload put.gd never hears: its binds came back on reconnect. An added headless output dropped `desktop` from `targets`, and removing it restored `desktop`. `omarchy/unbind_probe.sh` is the `hl.unbind` measurement.

## Budgie (Fedora 45 golden, two heads, f44)

`budgie/transcript.txt`, CI AppImage `28caec991`: `wlrCapture.outputs` 2, `desktop` not in `targets`, `targetReasons.desktop` set, `recording.prepare` refused with that reason.

`settings-region-capture-annotated.png` is the renamed Settings row from the CI catalog render.
