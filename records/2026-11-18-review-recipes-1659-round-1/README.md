# Recording review recipes, Sol round 1

Live checks ran on Debian 13 Plasma Wayland (`d69`) and Linux Mint Cinnamon X11 (`m74`) against the packages from CI run `44287865139`. Both desktops reported version `26.1118.5424-dev+g652b83781a90` and `diagnostics.build.gitTree` `ebb93c833833c9edc2a4c8236e06002e743264a2`.

Lab implementation `8ac4b6709c51d5c1d2e666b57c9528ffedb01361` on `fix/1651-review-recipes`.

| Interaction | d69 | m74 |
| --- | --- | --- |
| Playback and speed | Passed, `r1b` | Passed, `r1b` |
| Cut flow and decoded exports | Passed, `r1b` | Passed, `r1b` |
| Format menu and decoded exports | Passed, `r1c` | Passed, `r1b` |
| Save a copy and Copy path | Passed, `r1d` | Passed, `r1b` |
| Registered Qt Save a copy, cancel and accept | Passed, `r1d` | d69-specific check |
| Status actions | Partial, `r1d` | Partial, `r1b` |
| Advice | Partial, `r1d` | Partial, `r1b` |

The terminal artifacts certify the original receipt SHA-256, the secret scan, and coverage export. A receipt can contain earlier attempts from its batch. The table identifies the receipt for each reported result. Raw recordings were retained privately at the lab.

The first Plasma chooser attempts stopped when the file list still lacked the private directory witness after Open. The corrected sequence in `r1d` rechecked the exact directory in the field before the second Open. Cinnamon `r1a` found zero controls for the Play object name. Its runner exited before the final audit. Recovery verified native clipboard restoration and closed the exact private resident. Cinnamon `r1b` used the live Play accessibility name and push-button role.

## Sol findings

- **R1.** The d69 chooser used guarded input to navigate to the private output directory, then entered a fresh basename. It verified the directory in the owned Files tree and exact filename before accepting.
- **R2.** The m74 recipe used the app-owned Qt chooser. The registered review portal variant explicitly blocks until it can bind the request to a window.
- **R3.** The loaded d69 profile refuses automatic ScreenCast consent in the contract test. Live d69 receipts show native `kde-screencast` capture.
- **R4.** Retention contracts reject an existing media root and a symlinked descendant. The live runners retained synthetic media under their own private sibling directories.
- **R5.** The save and retry recipes verify that the expected path appears on the clipboard only after the app's Copy path action. The lab reads the clipboard for this check.
- **R6.** `dialogs.review_save_copy_fallback` passed live on d69 as `dialog.review-save-copy`, including Escape cancellation and acceptance of a fresh filename.
- **R7.** Status actions verified Retry, Copy path and Dismiss. Advice verified export failure Details, Escape and Try again. Both rows report `blocked` for the remaining coverage. Show in folder, size and format recovery and the Recording error dialog remain unexercised.
- **R8.** Both desktops selected 2× in the live speed menu and checked the playhead against elapsed time. Plasma measured 1.91× over 1.257 s and Cinnamon measured 2.22× over 1.413 s. The format menu covered MP4 H.264, MP4 H.265, WebM VP9, GIF and animated WebP with decoded exports.

## Lock cleanup

Each desktop's release receipt records verified cleanup. The d69 lease ended at 15:14:21 UTC, before m74 was acquired. The m74 lease ended at 15:50:03 UTC. These checks ran on the two physical desktops.

## Contracts

`python3 tools/ci/contracts.py lab` passed. The CI surface pytest set passed with 449 passed and one skipped.
