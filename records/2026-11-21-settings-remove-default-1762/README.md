# Removing the default destination no longer shows "Settings changed elsewhere" (#1762)

Pictures for put.gd-desktop issue #1762, taken on k72 (Kubuntu 26.04, Plasma Wayland, Qt 6.10.2)
on 2026-11-21 with a private resident (own XDG folders, session credentials) started on the real
desktop. Clicks went through the desktop's VNC input; the outside change was made with
`putgd-cli settings.patch`.

Setup: two S3 destinations, "First bucket" the default; the file has no default output object and
every capture action routes to First bucket. Steps: Settings, Destinations, "…" menu, Remove
destination…, confirm; then `putgd-cli settings.patch` sets the capture delay to 5 seconds.

- `1762-1-remove-default.png`: the removal being confirmed (same in both builds).
- `1762-2-before.png`: build of `origin/nightly` f742f83d0 (dev tree, version string reads
  0.0.0-dev.unknown). After the outside change the window shows "Settings changed elsewhere",
  Retry saving and "Changes not saved", though nothing was edited in it.
- `1762-3-after.png`: the same tree with the fix (commit ea24b393e). The window shows the new
  capture delay quietly and still reads "Settings save automatically".

In both runs the file after the removal held only Second bucket, with the capture actions routed
to no destination, and the capture delay was 5 after the outside change.
