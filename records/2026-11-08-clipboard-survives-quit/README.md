# Clipboard survives quitting on Budgie and Hyprland (PR #1317)

Stock VMs, no clipboard manager added, on the CI packages of `65e00a8e7` (version `26.1108.4263-dev+g374218010bde`). The last commit after those packages, `9f45d3f0f`, changes only a test. Each `result.json` lists every check; `gtk-paste.png` is the real paste into a GTK window after quit.

| Row | Package | Link: real capture, quit, exact `wl-paste` and real GTK paste | Keeper exits when an app copies | Image: auto-copy and Copy image, exact bytes after quit | No-op cases | Quit time (link, image) | Checks |
|---|---|---|---|---|---|---|---|
| `ck45` Fedora 45 Budgie | AppImage | pass | pass | pass | pass | 1584, 1598 ms | 48 / 48 |
| `ck44` Fedora 44 Budgie | RPM | pass | pass | pass | pass | 3756, 2016 ms | 52 / 52 |
| `ck26` Ubuntu Budgie 26.04 | DEB | pass | pass | pass | pass | 1615, 1425 ms | 47 / 47 |
| `ckoa` Omarchy | Arch | pass | pass | pass | pass | 1110, 881 ms | 51 / 51 |
| `ckoi` Omarchy | AppImage | pass | pass | pass | pass | 735, 693 ms | 46 / 46 |

Budgie rows upload to the real `put.gd/acceptance/` prefix, which lists 0 keys after each run. Omarchy rows upload to the suite's loopback S3 fixture: the live credential bridge doesn't support this golden yet, and the link flow in put.gd is the same. Omarchy's own `wl-paste --watch` history processes were running, as they are on the stock image.

No keeper remains after the final check on any row. The keeper ran at 1.9 to 4.1 MB resident. On the AppImage rows the AppImage mount is released at quit, and the keeper runs from memory on the host's libraries.

With a clipboard manager present (`ck44` clipman, `ckoa` wl-clip-persist), the manager keeps the link and no keeper is left beside it.

Regression, same packages: `ckg` GNOME Wayland (DEB) and `ckk` KDE neon (AppImage) each have put.gd owning the clipboard at quit, quit normally (670 and 1115 ms) and start no keeper. GNOME keeps the image. On KDE it leaves the clipboard at quit; those adapters never call this code, so that's unchanged behaviour.

One earlier `ck44` attempt failed twice with a TLS error to S3 (`s3_transport_unknown`, curl 35) before any keeper was involved; it passed on the next attempt with no change.
