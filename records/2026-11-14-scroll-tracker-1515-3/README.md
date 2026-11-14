# Scroll tracker (#1515), round 3: live Chrome failures

The third round on `ScrollTracker`, from live frames recorded on aurora-amd (Aurora, Plasma 6.8.2 Wayland, Chromium) and from the same lab corpus as `2026-11-14-scroll-tracker-1515` (60 recorded sequences, 100 derived ones).

- **Engine:** branch `feat/scroll-tracker-3`, commit `9505b55b208c6ceda4c109afceb3a21d211816c0`, on `feat/scroll-follow` at 113587fd0.
- **Corpus runs:** built with g++ `-O2` and run on d69 (Debian 13, i5-6500T).
- **Live frames:** a lab build of `feat/scroll-session` (dev preset) with this round's engine swapped in. A lab-only patch tees every frame `ScrollSession::feedTracker` hands the tracker into the replay tool's list format. The patch is not in any branch.

Files:
- `tracker-results.json`: this round, one row per sequence (`tools/lab/scroll_tracker_score.py`).
- `tracker-results-before.json`: #1529's merged engine, scored with the same scorer.
- `tables.md`: every sequence.
- Pictures:
  - `news-chrome-you-scroll.png`, `news-chrome-auto.png`: the Al Jazeera article. Before is the helper's live capture with #1529's engine. After is a later live run's frames through this round's final engine. Chrome's own full-page picture is beside them.
  - `python-chrome-auto-undrawn.png`: the Python docs, dark theme, auto-scroll, rows 18,250 to 18,420; the helper's live captures before and after.
  - `github-chrome-antialiasing-switch.png`, `github-chrome-reflow.png`: two pairs of live frames from GitHub PR 1398 in Chromium, auto-scroll.

Results:
- **Corpus:** every placed frame in all 160 sequences is where the page was. No sequence loses a band of the reference against #1529, and 15 gain.
  - Recorded sequences place exactly as #1529 did. Reachable bands equal: 9,359 → 9,372.
  - Derived sequences: 11,322 → 11,341 placed, 295 → 272 skipped. Reachable bands equal: 14,957 → 14,975.
- **Al Jazeera, live:** banner pixels in the page's rows. Counted as rows with 40 or more banner-navy pixels outside the last screen.
  - With #1529's engine: 1,454 rows (a person scrolling) and 2,666 rows (auto-scroll).
  - With this round's: 0. All six runs' frames through the final engine draw the banner only on the last screen.
- **Lost frames:** 20 or 30 in a row on one core of d69, after the image has grown.
  - HN thread, 30,830 rows: max 28.7 ms → 8.4 ms at `-O2`, and 260 ms → 74 ms at `-O0`.
  - GitHub PR, 22,430 rows: max 53.8 ms → 15.1 ms at `-O2`, and 439 ms → 129 ms at `-O0`.
- **Python docs, live:** pure-black cells (Chrome's undrawn tiles) 121,862 → 5,677.
