# Scrolling capture: no rows marked as changing from a guessed place while lost (#1795)

Acceptance for [PR #1801](https://github.com/patrick-hudson/put.gd-desktop/pull/1801), which fixes
[#1795](https://github.com/patrick-hudson/put.gd-desktop/issues/1795): after losing the page, the capture
painted GitHub's sticky header over a commit hash in a pull request's table.

**Build under test.** PR head `9183ab95885de037f7fcbd0ad54ea232d1da1cbc` (tree `cd89d86982e8cd4e237fa1aaba5d3c81e76badfb`),
candidate packages from CI run 44954103985: `putgd_26.1121.6104~dev+g9183ab95885d_amd64.deb` (ubuntu24.04) on m74,
`putgd-26.1121.6104~dev+g9183ab95885d-1.fc45.x86_64.rpm` on aurora-amd. The capture helper `putgd-record` is the
packaged binary, unpacked into a private folder (not installed, so the put.gd another campaign had installed
on m74 was left alone). The lab driver (`test_scroll_capture_driver`, which the packages don't ship) was built
from a clean clone at the same commit, and its `build-info.json` is identical to the packages'. The packaged
helper refuses any other identity.

## Replay of the recorded failure

`pictures/d3-before-after.png`: m74 run `firefox-github-user-d-3` (1,545 frames, from the #1557 record
`2026-11-21-scroll-white-boxes-1557`) replayed through nightly `1fdb87c0f` and through the PR head, next to
Firefox's full-page picture. Nightly paints the middle of the commit hash flat (960 px off the reference in
rows 24,433-24,441). The PR head writes it as the page shows it (0 px off). Nothing else in that image changes.

`pictures/p3-sibling-retries-white-boxes.png`: why all the lost-time retries are gated, not only the one the
issue names. With only that retry gated, run p-3 got white boxes over table digits from the sibling retries.
Nightly and #1672 have none there, and the PR head has none.

## Live runs on the candidate packages

| Desktop | Runs | Ended | Height | Skipped frames |
| --- | --- | --- | --- | --- |
| m74, Linux Mint 22.3 Cinnamon X11, Firefox, GitHub PR #1398, "you scroll" | 6 | 6 `done` | all 45,343 of 45,343 rows | 0-157 |
| aurora-amd, Aurora Fedora 45 Plasma Wayland, Firefox, same page | 3 | 3 `done` | all 45,340 of 45,340 rows | 1-2 |

Per run: `m74-cinnamon-runs.jsonl`, `aurora-plasma-runs.jsonl`. `pictures/live-m74-hash.png` shows run pkgc-1 at the
issue's table: the commit hash is whole and matches the reference.

Each capture was compared with Firefox's own full-page picture:
- No flat or white boxes over text outside the PR body's embedded screenshots, and no header strip over the page in any run.
- On aurora, only the page column's two border lines differ (render noise), plus one row in one run.
- On m74, everything else that differs is inside the PR body's embedded screenshots (rows about 1,500-2,100,
  which Firefox draws two ways), single 1-pixel rows, and the image's last rows. The last two are the region's
  bottom-edge line, [#1796](https://github.com/patrick-hudson/put.gd-desktop/issues/1796), which is fixed separately.
- No new errors. The helper logs hold only the portal's app-ID notice, expected for a helper that is not installed.

## Early pass on a lab build with the frame tee (not the gate)

`m74-early-lab-build-tee-runs.jsonl`: 6 runs on a Mint lab build of the same tracker with the frame tee. Results
were worse (2 `lost_track`, 2 short), and the tee lost each run's last frames when the driver stopped (the drain
patch was not applied). On the frames each tee kept, replaying them through nightly and through the PR head gives:
- the same placements in 5 of 6 runs;
- one run better with the PR head;
- one run that differs only inside the embedded screenshots.

The heavy skipping is in the frames themselves: the package runs without the tee skip far less.

## Offline checks

- New tracker test `lost over look-alike tables (+0/+13)`: fails on nightly (4,896 px) and on the PR's first head
  (48 px for +13). Passes at `9183ab958`. `scroll_tracker_contract` 85/85, `scroll_session_contract` pass.
- Replay corpus, 160 sequences in both browsers: identical to nightly.
- Sol review: approved in 3 rounds (gpt-6.2-sol, high).

## Known trade-off

An embedded screenshot that Firefox draws two ways (run d-1, rows 1,511-1,595) is composed as #1672 composed it,
with a 1-row seam. Nightly avoided it there only because a lost-time mark happened to cover it.
