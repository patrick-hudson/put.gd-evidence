# Scrolling capture: the region's bottom-edge line stays out of the page (#1796)

Evidence for [PR #1813](https://github.com/patrick-hudson/put.gd-desktop/pull/1813), which fixes
[#1796](https://github.com/patrick-hudson/put.gd-desktop/issues/1796). On Cinnamon, Firefox's page ends one row above the
selected region, so every frame's last row is a dark line, and pieces of it were written into the page as stray lines.

**Build under test.** PR head `588b9f28f7a1b2c528c2bf38551ece4a72bde8cc`, candidate packages from CI run 44965981263:
`putgd_26.1122.6188~dev+g588b9f28f7a1` (ubuntu24.04 DEB) on m74, the fedora45 RPM on aurora-amd. The capture helper is the
packaged `putgd-record`, unpacked into a private folder. The lab driver was built from a clean clone at the same commit,
and its `build-info.json` is identical to the packages'.

## Replay

`pictures/q4-edge.png`: m74 run `firefox-github-user-q-4` (from the #1557 record `2026-11-21-scroll-white-boxes-1557`),
every recorded frame replayed through nightly `4030f0330` and through the PR's final head `588b9f2`, next to Firefox's
full-page picture at image row 24,795. Nightly draws the edge line across the table row and the white margin; the PR
doesn't, except for a 16-px piece in the scroll bar's column at the far right, kept on purpose (see below).

The 7 recorded runs (d-1 to d-4, p-1, p-3, q-4) replayed at the final head: every long edge-line piece is gone.
All 295 row ranges that change move closer to the reference, and none moves away. 2-cell pieces can remain in the
scroll bar's column, which the review kept on purpose.

## Live runs on the candidate packages

| Desktop | Runs | Ended | Height | Skipped frames |
| --- | --- | --- | --- | --- |
| m74, Linux Mint 22.3 Cinnamon X11, Firefox, GitHub PR #1398, "you scroll" | 6 | 6 `done` | all 45,343 of 45,343 rows | 1-36 |
| aurora-amd, Aurora Fedora 45 Plasma Wayland, Firefox, same page | 3 | 3 `done` | all 45,340 of 45,340 rows | 1-2 |

Per run: `m74-cinnamon-runs.jsonl`, `aurora-plasma-runs.jsonl`. Each capture was compared with Firefox's own full-page picture:
- On m74, the only dark edge line is the image's last row, where the region's edge belongs. No stray line is in any page row. The #1795 package runs on nightly-equivalent code had single 1-px edge lines in page rows.
- The only boxes on m74 are inside the PR body's embedded screenshots, which Firefox draws two ways (unchanged from nightly).
- Aurora (no edge line there): no boxes.

## Offline checks

- New tracker test `a dark line on the frame's last row is not drawn into the page`: 520 stray pixels on nightly, 0 at the PR head. 86/86 under UBSan.
- Replay corpus, 160 sequences in both browsers: identical to nightly at the final head.
- Sol review: approved in 3 rounds (gpt-6.2-sol, high). Two constructed page-rule cases were found and fixed.
