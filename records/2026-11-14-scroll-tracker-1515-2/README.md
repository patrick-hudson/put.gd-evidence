# Scroll tracker (#1515), round 2: excluded rectangle and the cookie box

The second round on `ScrollTracker`, replayed on the same lab corpus as `2026-11-14-scroll-tracker-1515`: 60 recorded sequences and 100 derived ones, built and run on d69 from the PR branch `feat/scroll-tracker-2`.

- `tracker-results.json`: this round, one row per sequence (`tools/lab/scroll_tracker_score.py`).
- `tracker-results-before.json`: the merged engine of #1527, rescored with the same scorer, for the comparison.
- `tables.md`: every sequence.
- `stackoverflow-first-screen-*.png`, `stackoverflow-last-screen-*.png`: Stack Overflow's cookie box before (#1527) and after, at the image's first screen and at its end, in Firefox and Chrome.
- `excluded-box-guide-chrome.png`, `excluded-bar-guide-chrome.png`: the user guide replayed with put.gd's bar painted into every frame (a pattern that changes from frame to frame) and excluded, as a box over the middle and as a bar across the bottom.
