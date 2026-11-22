# Scrolling capture: a look-alike half a screen back no longer wins over the place that goes on (#1797)

Evidence for the #1797 fix ([PR](https://github.com/patrick-hudson/put.gd-desktop/pulls?q=1797)), branch `fix/scroll-jump-lookalike-1797`,
head `416850099d0be37eaf97d0b79fe6ddeabce4b2c0`.

## Real-use check

#1797 described a synthetic scene: a jump of more than a screen over repeating tables placed frames one table short. To see
whether real fast scrolling does this, the 7 recorded GitHub PR #1398 runs from m74 (Cinnamon X11, Firefox, from record
`2026-11-21-scroll-white-boxes-1557`) were replayed keeping only every 4th, 8th, 12th, 16th or 24th frame. This gives
jumps up to two screens over the page's repeating tables. Each kept frame's place was then compared with the place the
full replay gave it (`stride-nightly.log`, `stride-pr.log`).

- The synthetic shape (a same-direction look-alike after a jump of more than a screen) caused no wrong placement on real frames.
- Three other mechanisms did, each about one table period (1,010-1,242 rows) short, with every later frame shifted:
  1. **Turn back to a look-alike while following** (this fix). After moving +552 rows and a pause, the pair took −596
     (cells 0.987 on 103 rows) over the true +414 (0.967 on 181 rows): run d-1 every 4th frame, 98 frames wrong; run
     q-4 every 8th, 4 wrong. With the PR: 0 and 0.
  2. A place found again by the image lookup after a lost stretch: d-4 every 8th, 11 wrong, 5,540 rows short. Not changed.
  3. A frame 1,242 rows on judged "no movement" after ambiguous skips, which then becomes the reference: q-4 every 4th,
     39 wrong. Not changed.

`pictures/d1-placements.png`: run d-1, every 4th frame. Nightly runs a table short from frame 76 on; the PR follows the
true places.

## Offline checks

- The 7 full recordings replay pixel-identical to nightly. The 160-sequence corpus is identical to nightly.
- New tracker test (seed 790 of a randomized search, kept exactly): nightly misplaces 11 frames, the PR none. 87/87 under UBSan.
- 4,000 randomized look-alike scenes: wrong placements 31,599 → 31,200 (60 scenes better, 10 worse).
