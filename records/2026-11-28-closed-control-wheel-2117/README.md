# Closed controls leave the wheel to the page (#2117, PR #2120)

Live check of patrick-hudson/put.gd-desktop#2120 on two physical lab desktops, 2026-11-28 02:00–02:35 UTC.
Each run used a private resident (own XDG directories) of a dev build of `src/` at 2abc399b1, under
`desktop_lock.py run`, shown on the display wall. Wheel input went through each host's wall VNC server: w0vncserver into
KWin on k72 (Kubuntu 26.04 Plasma Wayland), and X0tigervnc (XTest buttons 4/5) on m74 (Linux Mint 22.3 Cinnamon X11).
The destination pointed at an offline S3 oracle (a lab copy of `tests/fixtures/s3_server.py` that returns the stored
Content-Type, as S3 does) with the synthetic test keys, so Test upload and link passed and Encrypted links was enabled.

Results (values read with `ui.encryptedLinks inspect` and `ui.history inspect` after each step):
- Before, on the published nightly 26.1125.7045 (m74): two notches over History's closed "Upload state" filter set it to
  "Local only" and added a filter chip.
- This PR, on k72 and m74: Encrypted links (enabled, Off) stays Off after 3 notches down, 5 up (the page scrolls) and
  3 down with Ctrl held. History's "Upload state" and the focused "From date" filters stay at Any after 4 notches each
  way, with no active filter. The main navigation stays on History. VNC sends no trackpad pixel deltas, so those weren't covered.

`wheel-2117.png` is the annotated summary. `frames/` holds the full-screen frames it was cut from.
