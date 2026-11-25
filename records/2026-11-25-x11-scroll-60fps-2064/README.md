# X11 scrolling capture at 60 frames a second (#2064, PR #2071)

What was tested: scrolling capture with the X11 source at 60 frames a second, its fallback to 30, and the tracker's wall-clock Lost window. Each row compares CI candidate packages with the published nightly.

- Candidate: commit `d526c7473c4de37d32268bc2815146ec85b312e6`, CI run 45711127721, `26.1125.7090~dev+gd526c7473c4d`. The DEB is unpacked on m74, the RPM on f44 and the AppImage on aurora.
- Baseline: published nightly `26.1125.7045~nightly`, commit `9d9f65eb8f7c4e9a7eddaf8b0c7938b95e805d40`.
- Lab driver `test_scroll_capture_driver`: built from a blobless clone at each commit, with `PUTGD_RELEASE_TAG=v26.1125.7045-nightly` for nightly. Its `build-info.json` is identical to the package's. aurora used the f44-built drivers, which link only system libraries.
- Every desktop run held the desktop lock and the quiet lease, and showed on the display wall.

## m74, Linux Mint 22.3 Cinnamon X11, Firefox 158, region 1920×922

Harness: `harness/run.py`, the #1515 `sess.py` with fixed seeds, a brisk pace (`LAB_PACE=brisk`: 3 to 8 notches every 60 to 200 ms) and a CPU/RSS meter of the helper and Xorg. Batches: `batch.sh` and `rep.sh`. Per-run results are in `data/m74-runs.json`.

| | nightly (30/s) | candidate (60/s) |
| --- | --- | --- |
| You-scroll, normal pace (6 runs): times lost and found again | 3 | 1 |
| You-scroll, brisk pace (8 runs): times lost and found again | 19 (7 runs with a loss) | 8 (5 runs) |
| GitHub PR #1398 auto-scroll | handed back after 266 skipped frames | `end_of_content`, 0 skipped |
| Wikipedia auto-scroll | `end_of_content` | `end_of_content` |
| Frames a second taken | 29 to 30 | 54 to 60 (`sourceRate.delivered` 60) |
| Helper CPU, brisk repeats | 50 to 55% | 70 to 74% |
| Xorg CPU | 10 to 13% | 14 to 17% |
| Peak helper RSS | 362 to 645 MiB | 378 to 650 MiB |
| Fallback | none | never fired |

The first brisk pair alone looked like a regression: the candidate lost the page twice on GitHub and nightly never did. The repeats (seeds 4 to 6) reversed it. Single runs vary a lot (nightly GitHub at seed 2 skipped 93 frames; the candidate skipped 0).

## Cost at 4K (`harness/x4k.py`)

Ruler fixture on a private Xvfb on m74, auto-scroll to the end:

| | nightly | candidate |
| --- | --- | --- |
| 1920×1080 | 29.9/s, helper 48%, Xvfb 9% | 59.7/s, helper 67%, Xvfb 13% |
| 3840×2160 | 26.3/s, helper 99%, Xvfb 23%, 922 MiB | fell back ("the loop missed 37% of the frames"), 27.5/s, helper 102%, Xvfb 25%, 890 MiB |
| 3840×2160, one CPU | 25.5/s | fell back ("the loop missed 73%"), 23.6/s |

## No regression on Wayland

- aurora-amd (Aurora Fedora 45, Plasma 6.8.2 Wayland, Firefox 158, AppImages): 8 of 8 pass on both builds. Wikipedia and GitHub, you-scroll and auto-scroll, about 59.6 frames a second, same CPU (28 to 34%) and RSS. See `data/aurora-runs.json`.
- f44 (Fedora 44 GNOME Wayland, putgd@put.gd and AppIndicator extensions enabled, Firefox 158.0.1): Wikipedia you-scroll and auto-scroll pass on both builds (`done` and `end_of_content`, 0 skipped). GitHub served its error page to the lab browser, and the Python docs redirected, so both are harness failures on both builds. See `data/f44-runs.json`.

## Pictures

- `pictures/m74-results.png`: m74 losses at both paces, GitHub auto-scroll, and helper CPU including the 4K fallback.
