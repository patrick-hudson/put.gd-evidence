# Retry deletion settles a deletion stopped by a destination added back (#1772)

What was checked: History's deletion status for a file whose deletion saved a `phase` checkpoint and ended
`unknown` through a destination since removed from Settings, after an S3 destination for the same place
(endpoint and bucket) was added back under a new ID.

- Host: aurora-amd, Aurora Fedora 45, Plasma 6.8 Wayland, real session; frames from the host's loopback
  VNC wall at 1920x1080, cropped to the window. Taken under the aurora-amd desktop lock.
- Window: the production `HistoryWindow` and `HistoryService` in the GUI test fixture, with a synthetic
  provider registered as `s3` (no network). The record and its interrupted deletion journal are seeded;
  each **Retry deletion** runs the real retry path (`HistoryService::runDelete`).
- Builds: dev build of put.gd-desktop branch `fix/deletion-readded-settle` (tree synced without `.git`).
  Before: `src/app/HistoryService.cpp` from nightly `f742f83d0`. After: the branch's code at `db36fc8b9`.
- Annotations drawn with put.gd's own editor (headless resident from the same build, `editor.apply`,
  `editor.saveCopy`).

Result:
- `before-still-there`: every retry stops with `destination_readded`; after the file is gone the
  deletion still stays `unknown` and the entry protected (`forgetBlocker` = `deletion`).
- `after-still-there`: the retry checked the recorded file read-only through the destination added back,
  found it, kept the deletion `unknown` and says to delete the file at the destination and retry.
- `after-gone`: with the file gone, the retry ended the deletion `already_missing`; the row says
  Deleted from destination and the entry is released (`forgetBlocker` empty).

Files: raw crops `*-still-there.png`, `after-gone.png`; annotated `*-annotated.png`.
