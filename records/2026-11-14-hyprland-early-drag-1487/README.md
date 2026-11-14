# Hyprland: early drag and post-reload region capture end with capture_geometry (issue 1487)

Cause, before/after and guest checks for put.gd-desktop issue 1487. All runs were on fresh two-head Omarchy 4.5 (Hyprland 0.56) overlays of the immutable golden `omarchy-hyprland-20261108`, with Virtual-1 1280x800 at 0,0 and Virtual-2 1024x768 at 1280,0, and Region bound to Ctrl+Shift+F9. Each overlay was retired through guarded `lab.py cleanup` with the manifest kept in its folder.

| Folder | Host | Build | What it shows |
| --- | --- | --- | --- |
| [published-nightly-w3n1](published-nightly-w3n1) | f44 | published `26.1113.4757-nightly` (466449a4c, tree 4346aa6e) | Round B's reload sequence fails on the published nightly, so it predates PR 1471 |
| [diagnostic-w3d1](diagnostic-w3d1) | d69 | `26.1113.4909-dev+gc6efaea792cb` (nightly 61e30e4b6 plus [temporary logging](diagnostic-w3d1/diagnostic-logging.patch), never merged) | The cause, in [region.log](diagnostic-w3d1/region.log) |
| [fix-w3d2](fix-w3d2) | d69 | `26.1114.4944-dev+gb04d12bea038` (branch `fix/hyprland-early-drag-1487`, manual CI run 43539034083) | Every check passes |

## The reload case is not a regression

On the published nightly ([rows](published-nightly-w3n1/rows.jsonl)):
- My sequence passed with no reload and after each of two `hyprctl reload`s: hotkey, wait for the selector layer, then a virtual-pointer drag from (300,300) to (600,500).
- Round B's exact sequence failed 3 of 3 with `capture_geometry`, including with no reload: the pointer was moved to (300,300) before the hotkey and the drag used `--steps 8`.

The reload is incidental. What matters is that the pointer is already at the drag's start point when the drag begins.

## Cause

In each failing session, [region.log](diagnostic-w3d1/region.log) on the diagnostic build shows the same sequence:

1. The hotkey maps the press catcher's two layer surfaces.
2. Hyprland enters the head-0 surface at the true position (`local=300,300`), then immediately leaves it.
3. Hyprland enters the head-1 surface with `local=-2260,300`. That is outside the surface, as if the output's offset had been taken twice; the correct value would be -980.
4. The catcher took that position, so a press with no motion in between was relayed at (-980,300).
5. The selector anchored there, and the selection was (-980,300) 1580x200.
6. The region helper refuses a rectangle outside the layout, which surfaces as `capture_geometry`.

Motion events on the same surface carry correct positions (local -943 is global 337), so only the enter position is wrong.

An ordinary drag passes because its first motion actually moves the pointer, which hands focus to the selector before the press. When the pointer is already at the start point (round B's sequence), the press reaches the catcher.

Timing does not matter. Through the real QEMU tablet, presses 60, 250 and 600 ms after the key all failed, as did the driver-speed drag ([rows](diagnostic-w3d1/rows.jsonl)). Early Esc passed.

## Fix

- `PressCatcher` uses a pointer-enter position only when it lies inside the entered surface, and otherwise keeps the last position reported in this catch. Positions from pointer motion are used as before.
- A press at no known position is not relayed, so the selector opens as usual.
- The selector ignores a relayed press that lies outside every output.

## Checks on the fixed build

[Rows](fix-w3d2/rows.jsonl), with both heads' frames per case. Every capture is position-checked against the independent QMP frame of its head, taken after the operation ended: crop at the expected rectangle, mean absolute difference. A crop shifted by 20 px gives 6.4 to 29.8, so 0.0 pins the position.

| Case | Result | Size | Diff vs frame |
| --- | --- | --- | --- |
| Ordinary live region | completed | 300x200 | 0.0 |
| Screenshot-first region | completed | 300x200 | 0.061 |
| Round B sequence, no reload | completed | 300x200 | 0.0 |
| Round B sequence after reload 1 | completed | 300x200 | 0.0 |
| Round B sequence after reload 2 | completed | 300x200 | 0.0 |
| Early drag, driver speed, head 0 | completed, the early drag itself | 300x200 | 0.0 |
| Early drag, QEMU tablet 60 / 250 / 600 ms after the key, head 0 | completed, the early drag itself | 300x200 | 0.0 |
| Early drag, driver speed, head 1 | selector opened normally; second drag completed | 300x200 | 0.0 |
| Early drag, QEMU tablet 60 / 250 / 600 ms, head 1 | selector opened normally; second drag completed | 300x200 | 0.0 |
| Early Esc | cancelled | - | - |

On head 1, Hyprland gives no in-surface enter position, so the early press is not taken and the selector opens for a normal drag. No case ended in an error, and none captured a rectangle other than the one dragged.

The [`rows.jsonl`](fix-w3d2/rows.jsonl) lines say `passed: false` for the completed captures. That is a bug in the driver's pass test, `(diff or 99) < 10`, which treats a 0.0 difference as missing. Their `size` and `meanDiffVsFrame` fields are the results above; [`w3drive.py`](fix-w3d2/w3drive.py) in this record has the corrected test.

## Scripts

`w3drive.py` (cases, run on the QEMU host), `qmp_early.py` (hotkey and tablet drag on one QMP connection) and `vm-w3.sh` (launch and install) are in each run folder. Each folder also holds the run's launch, install and state receipts and its cleanup manifest.
