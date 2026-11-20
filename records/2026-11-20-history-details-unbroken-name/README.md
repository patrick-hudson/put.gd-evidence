# History details pane with a long unbroken file name (PR #1722)

Pictures for put.gd-desktop PR #1722, which keeps a file name with no break opportunity
(such as `Tier1-<32 hex>`; a hyphen never breaks before a digit) inside the History details pane.

- Before: nightly `v26.1120.5780-nightly` (commit `cd33d3059`), Tier 1 nightly row on k72 (Kubuntu 26.04 Plasma Wayland guest,
  1280 × 746 History window), cell `s3_region_upload`, attempt 2. The pane is wider than the window: **Copy link** is cut
  off at the right edge and the details close button is pushed out of view. The cell failed with
  `placed rectangle [1180, 476, 117, 36] falls outside compositor frame [0, 0, 1280, 746]`.
- After: PR #1722's CI packages (manual CI run 44659325111, head `6c38999e2`), the same cell on the same k72 guest
  profile through the nightly controller code. The name wraps inside the pane, the close button shows, and
  **Copy link** is whole. The cell and the whole k72 and aurora-amd rows passed (14 of 14).

Frames are the surface driver's own uncropped frames from those receipts, with a caption band and boxes added.
