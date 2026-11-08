# GNOME 50: one logout finishes setup

Acceptance for [#1315](https://github.com/patrick-hudson/put.gd-desktop/pull/1315) on real GNOME 50 sessions (disposable VMs on d69 and f44). Each row used a real logout through GNOME and a typed password at the GDM greeter.

Build tested: CI run 42518096522 for PR head `a2c36cc07`, packages `26.1108.4241-dev+g3c74c18b23f4` (merge of `2b5e1b2d3` and `a2c36cc07`). SHA-256 prefixes: DEB `10173ea6`, RPM `7794a70e`, AppImage `901f8125`. Directories below hold the transcript and screenshots for each row.

## Proof of the mechanism

`g1` (Ubuntu 26.04, GNOME Shell 50.1, nightly 26.1108.4139): after installing the DEB, `gnome-extensions enable putgd@put.gd` reported "does not exist". Setting `org.gnome.shell enabled-extensions` before one real logout and login left the extension ACTIVE at v19 (`g1/proof.txt`).

## GNOME 50 rows (final packages)

| Row | Directory | Result |
| --- | --- | --- |
| Fresh user, DEB, Ubuntu 26.04 (GNOME 50.1) | `g2z` | PASS: `login_required` and the notification, one logout, `ready`, ACTIVE v19. The pre-existing list is kept exactly: `['user-theme@gnome.org', 'dash-to-dock@example.org', 'putgd@put.gd']`. Real Ctrl+Shift+1/2/3 made region, window and desktop captures. |
| Fresh user, RPM, Fedora 44 (GNOME 50.0) | `f2z` | PASS: same flow. Fedora's own entry kept: `['background-logo@fedorahosted.org', 'putgd@put.gd']`. Hotkeys pressed outside the Activities overview. |
| AppImage from the installer's path (`~/.local/bin/putgd.AppImage`) | `g3z` | PASS: owned copy installed with its marker, one logout, ACTIVE, hotkeys captured. Then `--remove-gnome-extension` removed the copy and the setting; a second run found nothing (`g3z/remove-transcript.txt`). |
| AppImage downloaded by hand (`~/Downloads`) | `g4z` | PASS: same flow. |
| System copy with an AppImage | `g5z` | PASS: no user copy created; loaded from `/usr/share`. |
| `disable-user-extensions` true | `g5z` | PASS: `user_extensions_disabled`, notification, nothing changed; turning extensions on again went straight to `ready` with no logout. `gnome-extensions disable` reports `disabled_by_user` and stays off. |
| Foreign user copy | `g6z` | PASS: `foreign_user_copy`, files unchanged (SHA-256 verified), settings unchanged. |
| AppImage update to a newer extension | `g7z` | PASS: owned v18 loaded, copy replaced by v19, `gnome_extension_updated` and its message. Window and desktop captures kept working, region refused with the existing `helper_outdated`. After one logout, ACTIVE v19 and all hotkeys captured. |

Session methods, `putgd-cli` and the MCP helper (`get_desktop_setup`, `recheck_desktop_setup`, through the locked `tools/mcp` environment) were driven against the real resident on the final build (`mcp-final.txt`).

## Other desktops

Quick checks on CI packages of `89e59f883`, the same setup code path; later commits change only GNOME code and the recheck deadline. Each resident answered `desktop.setup` with `not_applicable`, and no gnome-shell data directory appeared.

| Desktop | Directory |
| --- | --- |
| KDE Plasma Wayland | `p1kde` |
| Linux Mint Cinnamon X11 | `p5cin` |
| Ubuntu Budgie 26.04 | `p6bud` |
| Hyprland (Omarchy) | `p4hyp` |

## Pictures

`annotated-notification.png` and `annotated-tooltip.png` show build `26.1108.4241-dev+g3c74c18b23f4` on Ubuntu 26.04 GNOME 50.1.

## Lab notes

- The installer rows used the same `cp`, `chmod` and path as `packaging/install.sh`; the script's closing note is covered by `tests/releases/test_installer.py`. The public installer can only deliver a published build, not an unmerged one.
- A resident started over SSH outlives a logout with a dead session bus, so the rows quit it first, as a real logout would.
- Before an output is chosen, the hotkeys correctly answer "No output is enabled"; the rows set a local output to prove capture.
- VM `p1kde` ran about seven minutes without a wall tile because another worker held those wall ports.
