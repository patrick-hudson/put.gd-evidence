# Tray menu and action bar layout (#1532): catalog pictures

Offscreen `putgd-ui-catalog` renders from CI, not desktop acceptance. "After"
pictures come from the `ui-catalog` artifact of CI run 43643204150, build
`26.1114.5029-dev+gb91a65c2ee63` (PR #1532 head f63d24d merged onto nightly).
"Before" pictures come from the `ui-catalog` artifact of nightly CI run
43632367083. Boxes were drawn on the renders afterwards to call out the change.

- `bar-1060-before-after.png`: at 1,060 px the band kept one row by shortening
  labels; now it keeps the full labels and wraps its second group.
- `bar-1440-before-after.png`: one row at the new default 1,440 px window, with
  Capture region as a split button.
- `bar-large-text.png`: text × 1.5 (`PUTGD_TEXT_SCALE=1.5`), wrapped in reading order.
- `status-band-delay.png`: the Capture delay control set to 5 seconds and its
  menu, and the Capture region menu.
- `tray-before-after.png`: the Qt fallback tray menu (the same table as the
  dbusmenu export), idle, and its Capture output submenu.
- `tray-native-layout.txt`: the native dbusmenu layout in ten states.
- `command-band-measurements*.json`: one-row and two-row widths per state.
