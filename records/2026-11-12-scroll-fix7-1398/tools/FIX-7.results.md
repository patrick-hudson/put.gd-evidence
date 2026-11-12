### The table, from the packages of the final head

Each capture was made with the installed CI package through a private resident
(`scroll.prepare` with the viewport rectangle, maximum height at the Settings maximum, 60,000,
which the helper's memory rule applies as 52,083 rows at these widths). "Halfway, to the top":
the page scrolled to its middle, scroll-to-top on. "From the top": scroll-to-top off. Right after
each capture the browser's own picture of the whole page was taken at the same width (Firefox:
`drawSnapshot` in tiles; Chromium: screen by screen) and the capture compared with it in bands of
64 rows: a band passes when at most 0.2% of its pixels lie in 4x4 blocks whose grey mean differs
by more than 32, at the place in the reference that its bit-equal rows name. Columns the page
pins beside every row (side bars) and Firefox's overlay scrollbar are left out, each with its
reason in the run's `exclude.json`. Every run's result, comparison and helper log:
[runs/](runs/); per site one capture beside its reference: [sites/](sites/).

@SUMMARY@.

@TABLE@

Notes:

- **A. The pull request page in Chromium on m74 ends at 20,480 rows, honestly.** Chromium lays
  the page's sections out as they come into view. At that place one wheel step of 480 px, which
  the browser reports as a scroll of exactly 480 px, leaves the picture where it was: the
  section above grew by as much ([two screens](pictures/m74-chromium-pr-two-screens-480px-apart.png)).
  No offset explains such a frame, the loop goes back, the picture is the old one again, and
  after two tries the capture ends `lost_track` with the rows proved so far, all exact. Before
  this round's last fixes the same place ran into the time limit after 183 s (cause 12). On d69
  and f44, with other viewport heights, the page lays itself out between steps and the capture
  is complete. Begun at row 19,000 the same page on m74 reached its end (probe `mp6`).
- **B. Wikipedia in Chromium on m74, from the top, ends at 1,640 rows, honestly.** On the second
  visit of a session Wikipedia serves its appeal for donations: a block of 640 px at the top
  of the article and, once the reader has scrolled past it, a bar of 104 px pinned to the bottom
  of the viewport ([capture beside reference](pictures/m74-chromium-wikipedia-capture-beside-reference.png)).
  On m74 the bar comes up in the frame of the step itself and goes away again when the loop
  scrolls back, so the reference frame never has it. A step's first frame with the bar has
  more than a tenth of its overlap covered by rows that did not move (104 of at most 801 at one
  wheel step), which no offset passes, and the late-banner rule (cause 6) judges only a step
  whose offset was found. The image has its first 1,536 rows exact and the bar over the last
  104, as the screen had it. Where the bar stood in two frames running (the same appeal on f44
  and d69) it became the footer and the capture is complete, and so it is without the appeal
  (m74 halfway, m74 probe `mp5`). A search that leaves the frame's last rows out when nothing
  passes, as this round added for the first rows (cause 1), would let the rule judge this
  frame too; it is not in this round.
- **C. MDN in Firefox on m74 ends at 16,101 of 18,632 rows, honestly.** One step before the
  page's live example comes into view the browser reports a scroll of exactly 138 px (15,228
  to 15,366; probe `mp2`) while the article's column moves 135 px on the screen and its text is
  drawn anew at another sub-pixel place: no whole number of rows makes the two frames' rows
  equal (best 135: 43% of the rows with ink; [frames](frames/m74-ff-mdn-example/)). Scrolled
  back, the picture is the first one again. The stitcher proves offsets by equal rows and ends;
  the 252 bands it has are exact. Firefox on d69 and f44, and Chromium everywhere, lay the
  same page out without that step and are complete.
- **D.** One band of 256 pixels: a dot the page animates under its bookmark icon.
- **E.** The image's last 100 rows or so show the page's donation bar, pinned to the bottom of
  the viewport when the capture ended, over the page's last rows: as on the screen (a bar the
  page pins to the bottom is in the image once, at its end). The browser's picture, taken
  afterwards, has the page's rows there.
- **G. The Chromium reference of the pull request page has 60 rows the page does not.** For
  its picture the harness turns sticky elements into relative ones; the page's bar that sticks
  once the title has scrolled away then takes 60 rows of room at row 960
  ([picture](pictures/chromium-pr-capture-beside-reference-gap.png)). From there every band of
  the capture is exact 60 rows further on in the reference (counted as exact above); the band
  across the gap and the one or two at the reference's end are the ones that are not. Firefox's
  reference of the same page, taken without touching the page, has no gap, and the Firefox
  captures are exact band for band.
- **S. The pull request page on d69: slow steps, and one capture that could not prove the
  top in time.** The pointer comes in 48 rows inside the rectangle's top edge at its middle
  (cause 8). On this page that place is in the page's own sticky bar, on the link of the
  branch name; Firefox and Chromium answer each visit with their link panel at the bottom
  left of the viewport ([screens](pictures/d69-firefox-pr-link-panel-and-entry-point.png)).
  The panel is inside the rows the edge guard holds back (cause 3) and is in none of the
  images, 570 of 570 bands exact; but the picture is not at rest until the panel has gone, a
  second or so after each step: 40 to 125 s for this page on Plasma (the other four pages:
  0.4 s a step), and in one capture the way to the top took 91.7 s for 59 steps and ran into
  its 90 s limit. That capture says `top_not_reached`, truncated, although its image is the
  whole page. On Cinnamon and GNOME the visit is over before the panel shows (29 to 42 s).
  Not fixed in this round: the wait for rest would have to leave the held rows out, or the
  pointer come in elsewhere.
- **T.** Text the browser draws differently on the screen at that scroll position than in its
  full-page picture, the same characters: a few hundred to 2,000 pixels a band. Pictures:
  [a line one row lower](pictures/f44-firefox-mdn-line-one-row-off.png),
  [rotated headings](pictures/d69-firefox-mdn-rotated-headings.png).

Python's documentation page is 110,000 to 112,000 rows; every capture of it ends `height_cap`
at the applied maximum with all its bands exact.

### Controls, final head

On d69 and m74 with the same packages, a fresh private resident, default settings
([controls/](controls/)):

| Control | d69 Plasma | m74 Cinnamon |
| --- | --- | --- |
| 24,000 px ruler from its end, twice | `end_of_content`, 24,000 rows exact, twice | `end_of_content`, 24,000 rows exact, twice |
| Qt text, 1,500 lines | `end_of_content`, 1,500 lines, constant pitch | `end_of_content`, 1,500 lines, constant pitch |
| GTK 4 text, 1,500 lines | `end_of_content`, 1,500 lines, constant pitch | `end_of_content`, 1,500 lines, constant pitch |
| Browser ruler from the top | `end_of_content`, 2,400 rows exact | `end_of_content`, 2,400 rows exact |
| Sticky header and footer | `end_of_content`, 24,080 rows exact | `end_of_content`, 24,080 rows exact |
| FIX-6 committed resize | `lost_track`, 6,450 rows, exact prefix (an honest end) | `lost_track`, 6,420 rows, exact prefix (an honest end) |
| Minimap at a third of the rate (Problem 2) | `lost_track`, 600 rows, strip and column exact | `lost_track`, 600 rows, strip and column exact |

On the head before (`1a9066b3b`) the GTK 4 text control on d69 ended `lost_track` (cause 13).

### Checks

- d69 dev tree at the final head: `ctest --preset dev --parallel 3` 155 of 155 passed
  ([log](unit/ctest-dbe04eedc.log)); `tests/integration/test_mcp.py` 8 tests OK
  ([log](unit/mcp-dbe04eedc.log)); `test_scroll_stitcher` 250 passed, 0 failed
  ([output](unit/test_scroll_stitcher-final.txt)).
- CI run @CIRUN@ on the final head: @CISTATE@.
