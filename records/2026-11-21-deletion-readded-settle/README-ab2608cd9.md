# Retaken after pictures for #1776 at ab2608cd9

Sol round 2 (S5) changed the still-there message to point at Advanced file details for the file's exact
name and version, so the after pictures were retaken with that build: same host (aurora-amd, Plasma 6.8
Wayland, real session, VNC wall frame, desktop lock), same fixture and driver as this record's README, branch
`fix/deletion-readded-settle` at `ab2608cd9`.

- `after2-still-there.png` / `-annotated.png`: the retry found the recorded file and kept the entry; the
  message now names Advanced file details.
- `after2-gone.png` / `-annotated.png`: with the file gone the deletion ended `already_missing` and the entry
  was released (`forgetBlocker` empty), unchanged from the earlier frame.

The earlier `after-*` files show `db36fc8b9`; the `before-*` files show nightly `f742f83d0`.
