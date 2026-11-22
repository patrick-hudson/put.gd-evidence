# Scrolling capture: the window's scroll bar no longer stretches a held-back header down the page (#1837)

Evidence for the #1837 fix, branch `fix/scroll-heldback-bar-1837`, head `e2d8f5f6c6535d69ba1d49b40f26bc68a46105d5`.

**The recorded failure.** m74 (Linux Mint 22.3 Cinnamon X11), Firefox, GitHub PR #1398, "you scroll", run
`firefox-github-user-bx-2`. It was captured with the lab frame tee, all 1,263 frames kept, on a tracker equal to nightly
`4608d913a`. Replaying the frames reproduces the live capture pixel for pixel. After a step of 806 rows, `bars()` joined
the page's header to the window's scroll bar, which stands still at the frame's right edge (cells 238-239 of 240). The
joined part, full width and 280 rows tall, passed as a bar. It held back the rows below the header that only that frame
showed, and `finish()` painted them flat: 17,573 px missing over three lines of text.

`pictures/bx2-before-after.png`: that place replayed through nightly and through the fix, next to Firefox's full-page picture.

## Candidates, replayed on the same frames

- Nightly: 17,573 px missing.
- #1557's parked commit `6d50e245e`, rebased on nightly: 5,700 px missing, still white boxes over words.
- This fix (cells in the frame's two outermost columns no longer join a bar up or down): 0.
- Two dropped variants: measuring a bar's height by the rows it spans a quarter of the width in (by cell count, then by
  extent) broke a unit test, "floating animated player over article column". With one block row added it also broke
  "the view moves down in easing steps".

## Other checks

- All 13 complete real recordings (`replays-and-run.txt`): the same or closer to Firefox's picture (bx-2 91,463 → 67,017
  off-reference pixels; p-3 −386; d-1, d-4 a few less). The other differences are 1-pixel shifts under 40 levels along x 405-408.
- Replay corpus, 160 sequences: identical to nightly.
- 89/89 tracker tests under UBSan.
- **Trade-off:** 4,000 randomized scenes have 8 that are clean on nightly and now lose one header-width row (300-486 px), and
  2 with more wrong placements. Each of those 8 has a header with a 1-px border, whose block rows are joined only by that
  border down the frame's edges. The test `a bordered header loses at most one header-width row (known limit)` keeps
  one of them (seed 120: 38 px before, 486 after).
- No synthetic scene reproduced the real failure: three hand-built scroll-bar strips were not learned as standing still
  the way a browser's scroll bar is. The recorded-frame replay above is the regression evidence.
