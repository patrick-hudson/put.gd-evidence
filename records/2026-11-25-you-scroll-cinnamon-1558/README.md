# Issue #1558 — Cinnamon X11 You-Scroll Verification (2026-11-25)

- Code commit: `1a890fef11f02b9120f07e7a759b16715307bae8` (CI run `45682467950`, `26.1125.7067~dev+g1a890fef11f0`)
- Baseline nightly: `26.1125.7045~nightly`
- Hosts verified with official CI packages under desktop + quiet leases:
  - `m74` (Linux Mint 22.3 Cinnamon X11, DEB): normal user-scroll 9/9 `done` (0 lost, up from 4/7 on baseline nightly and 6/9 on Round 1 60 fps alone); auto-scroll 2/2 `end_of_content` (0 skips); 57.5–59.8 fps.
  - `f44` (Fedora 44 GNOME Wayland, RPM, AppIndicator active): 4/4 passed (`G-u1`, `G-a1`, `W-u1`, `W-a1`), 0 skips.
  - `aurora-amd` (Aurora Fedora 45 KDE Plasma Wayland, AppImage): 4/4 passed (`G-u1`, `G-a1`, `W-u1`, `W-a1`), exact heights.

## Pictures

- `pictures/before-after-github-A4.png` — GitHub PR #1398 (`A-4`, seed 104): baseline `lost_track` at 2,164 / 43,041 px (30.0 fps, 1,316 skips) vs after `done` at 43,041 / 43,041 px (59.8 fps, 0 skips).
- `pictures/before-after-stackoverflow-Bso1.png` — StackOverflow #11227809 (`Bso-1`, seed 301): baseline `lost_track` at 36,698 / 54,119 px (29.9 fps, 657 skips) vs after `done` at 54,119 / 54,119 px (58.2 fps, 8 skips).
- `pictures/live-desktops-verification.png` — Live desktop screenshots from `m74` (Cinnamon X11), `f44` (GNOME Wayland), and `aurora-amd` (KDE Plasma Wayland).
