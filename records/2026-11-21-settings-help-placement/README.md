# Settings help opens under its own field (#1787, PR #1789)

In Settings → Destinations → an S3 destination → Advanced connection settings, clicking a
field's help button showed its explanation at the bottom of the panel, below Secret-store
reference, instead of under that field. PR #1789 changes `Ui::helpButton` so the control's own
form row takes the note. Before, the first form row in the window whose field held the control
won. The "Where files go" form holds the whole connection panel as one row, so that outer row
took every connection setting's note.

## Builds

- Before: published nightly 26.1121.6060 (`putgd-26.1121.6060-nightly-ubuntu26.04-x86_64.deb`,
  SHA-256 `4b318b19010eebf79863bf70a013a2b24004857be3bc2e41e3a8dceec20e45d7`).
- After: PR head `52bcb0dca8bf105c50dbe5d35c8fe5acb84adb1a`, packages from CI run 44933380085,
  shown in the app as 26.1121.6098-dev+g52bcb0dca8bf.
  - k72: `putgd_26.1121.6098~dev+g52bcb0dca8bf_amd64.deb`, SHA-256
    `6bfdf4025405ed694709e812e84315449a43fa763e5488bf0b632d4147674718`.
  - f44: `putgd-26.1121.6098~dev+g52bcb0dca8bf-1.fc44.x86_64.rpm`, SHA-256
    `b71c7d0bbfeb5e9e4ba4e5a7a13291065e2a21b991768c8866650e1e14a1ed7e`.

Each package was unpacked into a private folder and run as a private resident with its own
`XDG_*` folders and runtime directory on the real desktop session. It had one synthetic S3
destination with no stored credentials. Clicks went through the wall VNC, and pictures are crops
of the put.gd window.

## Hosts

- k72: Kubuntu 26.04, Plasma 6.6 on Wayland, under desktop lock sessions `i1787-k72` (before)
  and `i1787-k72b` (after).
- f44: Fedora 44, GNOME on Wayland, under desktop lock session `i1787-f44`.

## Result

| Desktop | Panel | Help buttons clicked | Under its own field | Hidden on second click |
|---|---|---|---|---|
| k72, nightly 6060 | Advanced connection settings | Storage class | No: bottom of the panel | not checked |
| k72, PR head | Advanced connection settings | Use a custom endpoint, Storage class, Connect timeout, Request timeout, Minimum transfer speed, Low-speed window, Addressing, Secret-store reference | Yes, all 8 | Yes, all 8 |
| k72, PR head | Links | Upload access request | Yes | Yes |
| k72, PR head | Settings → General | Unlock saved credentials, Add Upload with put.gd to the right-click menu, Folders, Status | Yes, all 4; the checkbox's help spans the full row | Yes, all 4 |
| f44, PR head | Advanced connection settings | the same 8 | Yes, all 8 | Yes, all 8 |
| f44, PR head | Links | Upload access request | Yes | Yes |
| f44, PR head | Settings → General | the same 4 | Yes, all 4 | Yes, all 4 |

Use a custom endpoint's help leaves blank space above and below the text on both desktops.
That row is built by `Ui::settingRow` and placed through the `inlineHelpRow` path, which this
change does not touch, so nightly behaves the same.

## Files

- `before-k72-storage-class.png`, `after-k72-storage-and-request.png` and
  `after-f44-storage-class.png` are the annotated before/after pictures.
- `k72-*.png` and `f44-*.png` are contact sheets of every toggle, each help button on and then off.
- `catalog-62b-destination-connection-help.png` is the new `putgd-ui-catalog` frame, rendered
  offscreen on aurora-amd from the PR head.

Offscreen checks on aurora-amd (Fedora 45, Qt 6.11.2): the new GUI test
`helpOpensUnderItsOwnField` fails with nightly's `Ui.cpp` (six connection rows 66–334 px below
their field) and passes with the fix. All 13 `gui_` tests pass, and the catalog renders all 275
frames.
