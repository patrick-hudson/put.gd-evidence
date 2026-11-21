# Tray icon activity stages (fix/tray-activity-stages)

What was tested: the tray icon's new stage tints and the check badge, rendered by
`putgd-ui-catalog` (offscreen Qt, dark and light panel tints) from a dev build of
put.gd-desktop commit `a6e5399f2` (branch `fix/tray-activity-stages`, based on nightly
`994c04218`), built on f44 (Fedora 44, `cmake --preset dev`).

- `tray-stages.png`: Idle, Capturing (accent `#E8B66D` / `#8F5B20`), Processing (`#8DB4E8` /
  `#2F5E9E`), Uploading 50% (green fill `#62D69B` / `#1F7A4A` over the processing blue),
  Complete (green with the bottom-right check badge), Failed (clears after 8 s), and the
  unchanged recording badges, each at 48 px and the 16/20/24 px tray sizes.
- `tray-stages-seasonal.png`: November's turkey and December's tree through the stages. The
  check badge sits bottom-right, so neither glyph is swapped for the plain mark.

Result: every stage renders in its own tint on both panel tones; the seasonal glyphs keep
their head and star with the check badge. On the same build, ctest `gui_tray`,
`gui_theme_contrast` and `native_tray_integration` passed on f44, including the new check
that a real (fixture) upload's `diagnostics.trayIcon.history` reads capturing, processing,
uploading, complete, idle.
