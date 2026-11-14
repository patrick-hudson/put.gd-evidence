# Scrolling capture pointer release, round 2 (#1514, PR #1520)

After the acceptance of 4630ddc on GNOME, Hyprland, Budgie and Plasma 6.8.2
([record](https://github.com/patrick-hudson/put.gd-evidence/tree/a9c4f54a9292d42138e84349581a21b41bcfb31e/records/2026-11-14-scroll-pointer-release-1520-acceptance)).
Recorded 2026-11-14 after 13:30 UTC. Final PR head 2cc507826 (tree ad79b29c), CI run 43608251978 (packages) and 43608260119 (PR).

## Where

- **k72**, Kubuntu 26.04, Plasma 6.6.6 Wayland, one 1920×1080 output, a dev build of each commit on k72 (KWin's fake input through a desktop entry for that binary). Lock held 13:31 to 13:42, 13:54 to 13:58, 14:32 to 14:46 UTC.
- **Omarchy guest** on f44 (golden `omarchy-hyprland-20261108`, Hyprland 0.56.2, software rendering, 2 vCPUs, output set to 1920×1080), the CI AppImage of each commit (runs 43593107098, 43602081126, 43604105318, 43606585913, 43608251978) and the published `v26.1113.4757-nightly`, extracted. Guest load average 1.7 to 3.0 (`data/*/load.txt`); f44 itself had no other guest or build and a load of 1.4 to 2.1. The overlay was retired with `lab.py cleanup` and a completion manifest; its tile was on the wall at port 5985 while it ran.
- Page: Firefox kiosk on `https://en.wikipedia.org/wiki/Linux`, region `470,200,980,720`, local save only.
- Tries as in [round 1](https://github.com/patrick-hudson/put.gd-evidence/tree/a8481f83a23c158d28824cd3728974f68e214eef/records/2026-11-14-scroll-pointer-release-1514): a uinput relative mouse with flat acceleration, 600 px/s, an event every 10 ms; "fixed" starts 2 s in, "random" 2 to 6 s in. On Hyprland the start is one relative jump to the middle of the screen computed from `hyprctl cursorpos` (the acceptance worker's driver); **"steer"** reads `hyprctl cursorpos` before every event and moves at most 6 px toward Stop, as a person steers by eye (a test change, shown beside the open-loop rows). VNC: the wall VNC server on k72.

## Untouched captures (seconds, steps, end)

| Desktop | Build | Captures |
| --- | --- | --- |
| k72 | nightly | 27.9 s / 59 / end_of_content, 28.1 s / 59 / end_of_content |
| k72 | 1b07533 | 28.4 s / 59 / end_of_content, 28.3 s / 59 / end_of_content (same images as the nightly) |
| Hyprland guest | nightly | 93.8 s / 71, 86.4 s / 67, 83.3 s / 69, all end_of_content |
| Hyprland guest | 1b07533 | 68.8 s / 51, 77.6 s / 55, 66.1 s / 51, all end_of_content |
| Hyprland guest | 0f2db0a | 64.9 s / 51 end_of_content |
| Hyprland guest | b14d79f | 69.6 s / 51 lost_track (end proof, full height) |
| Hyprland guest | 35469c2 | 71.2 s / 51 end_of_content, 75.2 s / 51 lost_track (end proof, full height) |
| Hyprland guest | 2cc5078, watch on | 69.1 s, 87.3 s, 71.5 s, all end_of_content |
| Hyprland guest | 2cc5078, watch off (`PUTGD_SCROLL_WATCH=0`) | 70.2 s, 69.2 s, 61.0 s, all end_of_content |

Median frame spacing in the 2cc5078 A/B: 118 ms with the watch, 106 ms without, nightly 104 ms.
The two `lost_track` ends are the end proof (`ScrollRun::proveEnd`, unchanged by this PR): after one notch up, the page answered the step down later than the response wait and the fresh frame caught it halfway. All their rows are there.

## Tries

| Desktop | Build | Tries | First click stopped it | Paused after the first motion (ms) | put.gd pointer moves after the first motion |
| --- | --- | --- | --- | --- | --- |
| k72, Plasma 6.6.6 | 1b07533 | fixed | 10 of 10 | 1 to 13 (median 3) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| k72, Plasma 6.6.6 | 1b07533 | random | 10 of 10 | 1 to 16 (median 4) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| k72, Plasma 6.6.6 | 1b07533 | VNC | 10 of 10 | 2 to 18 (median 4) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| k72, Plasma 6.6.6 | 0f2db0a | random | 10 of 10 | 5 to 18 (median 12) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 |
| k72, Plasma 6.6.6 | b14d79f (superseded) | random | 7 of 10 | 1 to 16 (median 6) | 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| k72, Plasma 6.6.6 | 35469c2 = 2cc5078 code | random | 10 of 10 | 1 to 15 (median 4) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| Omarchy guest, Hyprland 0.56.2 | 1b07533 | fixed | 10 of 10 | 0 to 125 (median 81) | 0, 0, 0, 0, 1, 0, 0, 0, 0, 0 |
| Omarchy guest, Hyprland 0.56.2 | 1b07533 | random | 7 of 10 | 0 to 198 (median 1) | 1, 0, 0, 0, 0, 0, 1, 0, 1, 0 |
| Omarchy guest, Hyprland 0.56.2 | 1b07533 | steer | 10 of 10 | 0 to 198 (median 86) | 0, 0, 0, 0, 0, 0, 1, 0, 1, 0 |
| Omarchy guest, Hyprland 0.56.2 | 0f2db0a | fixed | 10 of 10 | 0 to 239 (median 51) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| Omarchy guest, Hyprland 0.56.2 | 0f2db0a | random | 8 of 10 | 0 to 193 (median 75) | 0, 0, 0, 1, 0, 1, 0, 0, 0, 0 |
| Omarchy guest, Hyprland 0.56.2 | 0f2db0a | steer | 10 of 10 | 0 to 903 (median 62) | 0, 0, 1, 0, 0, 0, 1, 0, 0, 1 |
| Omarchy guest, Hyprland 0.56.2 | 35469c2 | fixed | 9 of 10 | 0 to 194 (median 83) | 0, 0, 0, 0, 0, 0, 0, 1, 0, 0 |
| Omarchy guest, Hyprland 0.56.2 | 35469c2 | random | 8 of 10 | 1 to 215 (median 88) | 0, 0, 0, 1, 0, 0, 0, 0, 1, 0 |
| Omarchy guest, Hyprland 0.56.2 | 35469c2 | steer | 10 of 10 | 0 to 164 (median 0) | 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 |

What the misses were (helper logs in `data/`):
- 1b07533 Hyprland random: the guest delivered the hand's events 100 to 200 ms late; the next visit went out before the helper knew (fixed in 0f2db0a: the event's own time).
- 0f2db0a Hyprland random: the first event was an enter, which has no time (b14d79f tried an enter rule; it fired falsely on k72 three times; 35469c2 decides by the next motion event only and closes the gate before anything else).
- 35469c2 Hyprland fixed 1, random 2: the helper's move landed within a few ms of the driver's single centering jump, which the driver had computed from a cursor position read just before; no timed event from before the helper's move exists then. With steering by eye: 10 of 10.

## Tools

`tools/` as run; `data/` the raw rows and helper logs.
