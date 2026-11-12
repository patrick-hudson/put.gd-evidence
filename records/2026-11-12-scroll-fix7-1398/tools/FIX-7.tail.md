## Problem 2: a column that scrolls at a different rate

Chosen: **an honest end.** The capture ends `lost_track`, truncated, with the note "a part of
the selection scrolls at a pace of its own (a minimap, a column with a parallax effect), so no
single image shows it beside the page; the image ends with the rows from before it moved". For
the acceptance fixture the image is the first viewport, 600 rows, strip and main column exact.

Why not "like a fixed band": a fixed band is on the screen beside every row the way the image
shows it. A strip at a third of the page's rate is not: by the time the page has moved a
viewport, the strip's row that belongs beside a page row has left the screen, so no tall image
can hold both, whatever is proved per row. What *is* proved per row is that the strip moves on
its own: per quarter of a band (27 px at 960), at least nine rows in ten of the overlap equal
bit for bit at one distance that is neither the page's nor none, 24 different rows among them,
and fewer than half at the page's distance and where they were; in two steps in a row
(`ScrollStitcher::paceOf`, `ownPace`). The image is cut back to the rows from before the first
of the two.

Checked against Problem 1's pages: a side bar that sticks or comes unstuck moves part of the way
in one step only (Wikipedia's contents column, MDN's and the Python documentation's side bars);
none of the @RUNS@ live captures ended for this rule. Something that changes without moving (a
video, an advertisement that rotates) has no such distance and is left to the tolerant rule as
before. The side margins (4% each) are not looked at, as in FIX-6.

Tests (`testLivePages`): the minimap at a third of the rate at three wheel distances, from the
top and from the end with scroll-to-top (six sessions; on the old code all six end
`EndOfContent` at 4,800 rows with the strip wrong from row 600); and what must still run to the
end: a strip that never moves, a side bar that sticks after 90, 150 and 400 px (on the old code
FIX-6's column rule ended these at 660 rows), a video in a column.

## Problem 3: builds with no region selector

Chosen: **unavailable for every caller**, as before commit `bcb2fe411`. `probeScroll` reports
`available: false`, reason `region_unavailable`, when the build has no selector; the helper's
`prepare` refuses on the probe; the resident refuses `scroll.prepare` with or without a
rectangle (`scroll_unavailable`, reason `region_unavailable`). No small provable fix exists: on
such a build the ring, the bar and the heartbeat are ordinary windows the compositor places,
inside the rectangle among other places, and focus and stacking of the fixture change with them.
Verified by test, not on a guest: `tests/integration/test_scroll_service.cpp`
`noSelectorNoCapture` (was `noSelectorNeedsARectangle`; its second half expected the rectangle
to be admitted and now expects the refusal, nothing prepared, no session).

## Tests added

`tests/unit/test_scroll_stitcher.cpp`, `testLivePages`, 48 checks (the suite is
250 passed; 202 before, all unchanged and passing):

- a sticky header of 48, 80 and 120 rows that comes after 150 px, at three wheel distances; one
  whose text changes on the way;
- the link panel under a pointer that cannot leave (the edge guard alone) and under one that
  waits outside; the panel on the screen when the capture begins;
- the pointer comes in just inside the edge it waits beyond; where nothing scrolls there the
  centre is next;
- a blended line in the rectangle's last row;
- a page between two side bars that stick, with and without a header that sticks, at three
  wheel distances; short lines between the same bars (moved, not changed in place);
- a banner of 40 and 120 rows that slides in after wheel event 2 and 5 becomes the footer;
  window background that comes up is still a change of layout;
- the minimap cases and their mirrors (Problem 2);
- the edge guard at the stitcher: a panel over the last rows of every third frame; rows that
  wait below a frame that moved back and a little on;
- tables that repeat and a step that moved farther than the overlap;
- lines that begin alike between two side bars with the wheel over blank paper, at two wheel
  distances (on the previous head of this round: `EndOfContent` with 712 rows of 3,600);
- a page that scrolls at once (on the previous head: 600 ms a step; now 275);
- a column of tens digits under a faint tint, nothing moved (on `1a9066b3b`: `Ambiguous`).

On the old code 24 of the first 28 fail ([unit/new-tests-on-old-code.txt](unit/new-tests-on-old-code.txt)),
each with a symptom of the acceptance: `LostTrack … a single notch scrolls further than the
overlap allows` for every late header, the panel in the body from row 676, the line at row 599,
`EndOfContent` with the strip wrong from row 600. The three checks added last fail on the
previous head of this round ([unit/new-tests-on-8d3848808.txt](unit/new-tests-on-8d3848808.txt)).
`--full`: 255 passed, 1 failed, the same one as before this round (`session sweep, constant
px/notch`, seed 9; FIX-6 has it). Real frames: [frames/](frames/) holds the six frames of the
reference page's first steps in Chromium on Cinnamon; `tools/replay7.cpp` puts them through the
stitcher (previous head: offset 91 where the page moved 138; this head: 138).

`tests/integration/test_scroll_service.cpp`: `noSelectorNoCapture`.
`tests/fixtures/ScrollSynthetic.*`: `FakeAppSpec::scene` (a page that knows where it is
scrolled to, the clock and the pointer).

## For the docs PR (#1408)

1. **The pointer.** On every desktop it waits outside the rectangle while frames are read and
   comes in for each wheel step (`RunOptions::restAway`, `leaveDelayMs` 30, `awayLingerMs` 450);
   the wheel is turned `entryInset` (48 px) inside the edge it waits beyond, then at the classic
   park places (rule 7 has four places now). Without a place outside (the rectangle covers its
   output) it stays parked as before. `restAwayToTop` (Hyprland) is the same thing for the way
   up only and is now covered.
2. **Rows that wait (the edge guard).** `StitchOptions::edgeGuardFraction`/`edgeGuardMinRows`:
   the last rows of a frame's moving band are written out from the next frame. "Rows are never
   revised" needs the sentence; `outputHeight()` counts them; `RowTakeBack` is also used by the
   own-pace rule and the banner; `ScrollStitcher::setTrustedFrom`.
3. **A header that comes late** is taken as a header (`headerVerdict`); the frame in which it
   first shows is matched in its interior (`edgeTopFraction`). It is in none of the image's rows.
4. **The search by quarter bands** (`columnSearch`, `locate`, `contradicted`): when it runs
   (no offset, ambiguous, changed in place, an offset two quarters contradict), what it proves
   (the page is what moved nearest the pointer), `columnLightTolerance`, `columnMovedFraction`,
   `ScrollStitcher::setWheelColumn`; "changed in place" becomes ambiguous when something moved
   and nothing is proved; the nearest column that stayed where it was ends the search; the bar
   and header rules judge rows the way the offset was found.
5. **A pace of its own**: `StepResult::ownPace`, the note, the cut back; FIX-6's column rule
   leaves a band with such a quarter to it. `ownPaceMaxWith`.
6. **A banner that slides in** becomes the footer (`lateBarIsFooter`, set by the helper); this
   narrows FIX-6's "a bar that comes later ends the capture" to bars that show nothing, came up
   over more than one frame, or are taller than the last step.
7. **Tied offsets**: `tieHintTolerance` (8% of the hint plus the wheel's spread; `hintTolerance`
   stays for an unproved candidate).
8. **No selector, no capture**: `scroll.capabilities` says `available: false`,
   `region_unavailable`; `scroll.prepare` with `rect` is refused there too (CLI and MCP pages,
   the failure-code page).
9. **The control loop**: a step's answer is counted from the wheel step, not from the start of
   the wait; only a step that appended rows resets the count of failed one-notch steps.
10. **Known limits to state**: a fixed or sticky side bar is in the image beside every row, as
    on the screen (a browser's own full-page picture shows it once); a bar the page pins to the
    bottom is in the image once, at its end, over the page's last rows; a page's own late
    header is not in the image; a capture of a page taller than the cap ends `height_cap`; a
    page that lays itself out anew under the viewport while it is scrolled (Chromium on a long
    pull request page), or that draws its text at another sub-pixel place after a step, ends
    `lost_track` with the rows proved; a bar that comes up in a step's own frame and covers
    more than a tenth of the viewport ends the capture the same way.

## What on live pages still does not work

Stated plainly; none of these puts a wrong row into an image.

1. **Chromium, the pull request page, m74**: ends `lost_track` at 20,480 of 34,765 rows (note
   A). The page re-lays itself out under the viewport; a capture cannot be complete there
   without trusting an offset that nothing proves.
2. **Chromium, Wikipedia with its donation appeal, m74, from the top**: ends `lost_track` at
   1,640 rows (note B). A search that leaves the frame's last rows out when nothing passes
   would let the late-banner rule judge the frame; not done in this round.
3. **Firefox, MDN, m74**: ends `lost_track` at 16,101 of 18,632 rows (note C). The page's text
   is drawn at another sub-pixel place after one step; proving that step needs a measure
   other than equal rows, which this round was told not to weaken.
4. **The pull request page on Plasma is slow** (40 to 125 s), and one capture in four of
   Firefox's said `top_not_reached` for an image that was whole (note S).
5. **A bar the page pins to the bottom** (Wikipedia's appeal) is over the image's last hundred
   rows when it is there as the capture ends (note E); the page's own last rows are under it,
   as on the screen.
6. **The harness's Chromium reference** of the pull request page has a gap the page does not
   (note G); the comparison allows for it, the capture is not affected.

## Review threads

No comment from CodeRabbit, cubic or a person arrived on this round's pushes (inline comments,
review bodies and "Outside diff range" sections read at 12:07 UTC and again before the report):
21 threads, none unresolved, the last review from 2026-11-11. Nothing to answer; no review was
requested.

## Cleanup

- No desktop lock held; every lock of this round was released with the cleanup check.
- d69, m74: the test package removed (`putgd` is `rc` as before the round; the version the
  entry names is now this round's), Chromium purged, the package lists otherwise equal to the
  lists saved before the round. d69: the dev recorder's desktop entry removed, `kbuildsycoca6`
  run; KWin was restarted once in this round after a GPU hang (i915, during a 60,000-row
  capture and a tall reference picture on an earlier head), the wall's VNC unit restarted with
  it.
- f44: the test package and its three dependencies removed, Chromium and the three packages
  that came with it removed, the package list equal to the list saved before the round; the
  two extension lists written back and equal after the last re-login.
- No browser, resident, fixture or harness process left on any host; the scratch directories
  `~/work/sf7` on the three hosts deleted file by file from a manifest.

