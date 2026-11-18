# Recording review recipes, Sol round 2

The changes are at `6b266c636a22e3af4902e2f5368c7bf793f88faf` on `fix/1651-review-recipes`. Both physical desktops ran the #1635 packages from CI run `44287865139`. The resident reported version `26.1118.5424-dev+g652b83781a90` and gitTree `ebb93c833833c9edc2a4c8236e06002e743264a2` on both.

| Desktop | Save a copy and Copy path | Retry and Copy path | Live 2× speed menu and playback | Lock released (UTC) |
| --- | --- | --- | --- | --- |
| d69, Plasma Wayland | Passed | Passed | 1.94–2.05× over at least 1.185 s | 16:09:36 |
| m74, Cinnamon X11 | Passed | Passed | 1.94–2.04× over at least 1.260 s | 16:22:43 |

- **R5.** Both checks use an exact target-side clipboard comparison. The target returns false before Copy path and true after it. The comparison keeps clipboard text on the target. The regression tests cover mismatches, an absent selection and a reader error containing private bytes.
- **R8.** Each playhead sample is bracketed by monotonic clock reads on the target. The entire rate interval must fit the 2× tolerance. SSH transit time is outside the measurement.
- **R9.** The Wayland chooser polls for the directory marker with a five-second wait budget. A second Open requires the exact folder in the owned field and the live guarded Open control. The bounded retry ran on d69 in `review.save-copy`, `review.status-actions`.

The `review.status-actions` receipts verify Retry, Copy path and Dismiss. The full row remains blocked for Show in folder and size or format recovery. Each batch therefore returned exit 1, with desktop cleanup, final secret scan and coverage export verified. The leases were held one at a time and released after cleanup.

The lab contract group passed. The CI surface pytest set reported 464 passed and 1 skipped.
