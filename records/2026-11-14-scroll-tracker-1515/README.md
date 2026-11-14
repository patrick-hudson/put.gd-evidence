# Scroll tracker (#1515): replay of the lab corpus

The new matching engine, `ScrollTracker`, replayed on the lab corpus of 2026-11-14: 60 recorded sequences of 10 pages in Chrome 157 and Firefox 160, in three styles (a wheel notch per settled frame, bursts of 600 px, continuous frames during a smooth scroll), and 100 sequences derived from them (every 3rd and 6th continuous frame, notch frames played backwards, down-up-down, and a frame of another page spliced in).

Built and run on d69 (Debian 13, i5-6500T) from the PR branch `feat/scroll-tracker`. The corpus itself is not here; it stays on the lab host.

- `tracker-results.json`: one row per sequence, from `tools/lab/scroll_tracker_score.py`: frames, placed, skipped, worst position error against the browser's scrollY, and the 64-row bands of the image equal to the browser's own full-page picture, with the pinned rectangles left out.
- `stitcher-results.json`: today's `ScrollStitcher` on the notch and burst sequences, fed as the control loop does.
- `tables.md`: the tables of the pull request.
- Pictures: the tracker's image beside the browser's full-page picture (and today's stitcher for the user guide), the two synthetic cases from the unit tests, and the Stack Overflow shortfall (the cookie box drawn at the first screen).

The lab's search page is Bing in both browsers: Google showed the headless browsers a bot check.
