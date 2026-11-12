# Scroll capture fix round 7 — PR #1398 (issue #1376): live web pages

The acceptance of 2026-11-12
([record](https://github.com/patrick-hudson/put.gd-evidence/tree/fb48c9152bdce74fb99fe9b6ba612f171f14bb5b/records/2026-11-12-scroll-accept2-1398))
found three things: every capture of a real web page ended `lost_track` a few steps in with
the browser's link panel and a line stitched into the image; a column that scrolls at its own
rate (a minimap) came out as a mosaic in an image reported complete; and a build with no region
selector admitted a wrong image for a rectangle named on the command line.

- Repository `patrick-hudson/put.gd-desktop`, branch `feat/scroll-capture`.
- Before: head `0bbf42fd2`. After: head `dbe04eedc` (commits `6d8ae9801`, `44c824a32`,
  `bada70f1b`, `6915a619a`, `8d3848808`, `1a9066b3b`, `dbe04eedc`), CI run [43202012192](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43202012192).
- Packages of that run, build `26.1112.4716-dev+g0311647141ff` (CI merge commit `0311647141ff59a02edfb61518fa31080aad4b6d`, second parent the head):
  - `putgd_26.1112.4716~dev+g0311647141ff_amd64.deb` (debian13, d69), SHA-256 `4c6119b03d34de56c6fc9b597801ef55b3c44604a4eb5f9093e1043e568928c3`
  - `putgd_26.1112.4716~dev+g0311647141ff_amd64.deb` (ubuntu24.04, m74), SHA-256 `6ebe37cd7aa5e27d50b31d1d5db15b468135bf381fb710471dc2fd90910181d0`
  - `putgd-26.1112.4716~dev+g0311647141ff-1.fc44.x86_64.rpm` (fedora44, f44), SHA-256 `3d24eb2bdd612a45e7098905190105ce644df6e67525c392a8d01f8d79dbee38`
  No compile on a host for the tables below.
- Hosts: d69 (Debian 13, Plasma 6.3.6 Wayland), m74 (Mint 22.3, Cinnamon X11), f44 (Fedora 44,
  GNOME 50 Wayland, Shell extension version 22 ACTIVE after a re-login). Browsers: the
  distributions' own Firefox (as installed) and Chromium (installed for this round, removed
  afterwards), fresh profiles, signed out, maximized.
- Driver and tools of this round: [tools/](tools/) (`live7.py` drives the browser through its
  own remote protocol and compares; `controls7.py` runs the fixture controls on the tester's
  `pass2.py`/`fix6.py`).

## Problem 1: live websites

### What was wrong, each proved

Each cause below was seen on a desktop, and each but the twelfth is reproduced by a unit test
that fails on the code before its fix ([unit/](unit/)).

1. **A sticky header that comes late was never a header.** The header estimate only shrank.
   GitHub's bar that appears once the title has scrolled away (60 rows) then contradicted
   every offset in every later step: at 207 px a notch a two-notch step keeps 537 rows of
   overlap, 60 of them the bar, 11% conflicts against a limit of 10%. That is the
   `NoMatch … hint 414` in every one of the 16 acceptance logs, the halving down to one notch
   (scores 0.90 to 0.93), and the end "a single notch scrolls further than the overlap
   allows". Fix: a run of rows that newly stays put at the top is taken for a header when it
   shows something and the rows that should have scrolled into it contradict it
   (`headerVerdict`, the mirror of FIX-6's rule for the bottom); the frame in which the bar
   first shows is matched in its interior (the band without its first quarter). The bar hides
   rows that are in the image already and appended rows come from the bottom, so no row is
   lost; the bar itself is in none of the image's rows, as in the browser's own picture.
2. **The pointer rested on the page.** It was parked a third of the way down for the whole
   capture, on whatever scrolled under it. A browser shows the address of a link under a
   resting pointer in a panel at the bottom of the viewport, in the very rows the next step
   appends. Fix: on every desktop the pointer now waits outside the rectangle while frames
   are read (`RunOptions::restAway`), comes in for the wheel step only, stays 30 ms and
   leaves; a visit of 90 ms is shorter than the 80 ms *without motion* a browser waits before
   it shows the panel (the second motion of the visit restarts that wait). What the user's
   own pointer had called up before the capture gets 450 ms to go.
   (Where the place the pointer comes in at is itself a link, a browser may still show the
   panel for a moment: note S below.)
3. **The line across the image was the rectangle's last row.** The viewport as the browser
   reports it is one or two rows taller than what the desktop shows of it: the panel's edge
   is blended over the last row (Cinnamon) or the last two (Plasma). Blended, the row is
   never the same twice, so it was no footer, and every step appended it. Fix: the edge
   guard. The last 8% of a frame's moving band (at least 24 rows) is not written out with
   its frame; the next frame shows those rows away from the edge and they are taken from
   there. A panel, a border or a floating button at the bottom edge is then in the image's
   last rows only, where it is on the screen.
4. **Two side bars are more than the tolerant rule forgives.** Wikipedia's contents and tools
   columns, MDN's two navigation columns: four to six of the eight compared bands do not move
   with the page, the rule forgives two, and every row with something in a side bar
   contradicted every offset. Such a capture ended at its first step (found with the first
   package of this round). Fix: where the search over the bands finds no offset, cannot
   decide, or finds "changed in place", a search by quarter bands proves which columns are the
   page's (they moved as one piece by the offset, the column under the pointer among them)
   and which are something else (they stayed, or moved part of the way), and compares rows
   over the rest (`columnSearch`).
5. **A browser draws the same text twice differently.** In a block that scrolls sideways (a
   code listing) Firefox rasterizes the same glyphs with other antialiasing after the page
   has moved: 150 of 783 rows not bit-equal at the true offset in one step of the Python
   documentation, and every capture ended there. In the quarter-band search a quarter of a row
   is the same when it is equal bit for bit or as bright within 6 of 765; measured on that
   step, no row at the true offset had more than a quarter of its quarters further apart,
   and one row off 188 of 784 rows had.
6. **A banner that slides in at the bottom ended the capture.** FIX-6's rule ends a capture
   when a bar comes up at the bottom late, because the step that first showed it appended its
   rows as page. Wikipedia's appeal for donations is such a bar. Where the helper asks for it
   (`StitchOptions::lateBarIsFooter`), a bar that shows something, came up in the last frame
   alone, and is no taller than that step was long becomes the footer: its rows are taken
   back and the next frame, which shows the page's rows above the bar, supplies them. Window
   background under a viewport that got shorter (FIX-6's case) is one flat colour and stays a
   change of layout; the FIX-6 tests pass unchanged, and so does the committed-resize fixture
   on the desktops (below).
7. **FIX-6's column rule fired on a side bar that sticks.** A band that had moved with the
   page and then stays is, in the one step in which it sticks, neither. A band with a quarter
   that moved as one piece by a distance of its own is now left to the own-pace rule
   (Problem 2), which wants two such steps in a row.
8. **On Plasma the pointer's own visits were a shake.** A pointer that goes back and forth
   over more than a hundred pixels several times a second is, to KWin, a pointer its user
   shakes to find it: KWin blew it up to many times its size, the region stream's frames
   came in bursts 350 ms apart while that lasted, the way to the top "never came to rest"
   and captures ended `lost_track` or `time_limit` (second package of this round, d69). The
   wheel is now turned 48 px inside the edge the pointer waits beyond (64 px of travel); the
   classic park places follow where nothing scrolls there.
9. **Tied offsets and a hint a quarter off.** On GNOME one step moved 924 px where 528 were
   asked (three wheel steps arrived late). The pull request page has tables that repeat every
   505 px and differ in a heading and a few numbers, which the tolerant rule forgives; one
   table less (419 px) looked the same, lay within a quarter of the hint, and was taken: a
   table went missing from an image that ended `end_of_content`. Among tied offsets the hint
   now decides only within the wheel's own spread plus 8% of the hint; farther off the step is
   ambiguous and the loop goes back.

10. **Between two side bars the bands followed the bars, not the page** (found with the fifth
    package of this round; a wrong image, the worst of the round). Two forms of one thing. In
    the first step of the CSS reference page the two navigation columns travel 91 px to where
    they stick while the page moves 138; the columns are six of the eight bands, the page's
    text the two the tolerant rule forgives, and 91 was a proved offset: 47 rows gone
    (Chromium, Cinnamon; the frames are in the record). Further down, in a listing of short
    lines, the columns stay and the same rule calls the step "changed in place" with a score
    of 0.92: the reference frame was replaced and the rows in between were lost, 792 in an
    image that ended `end_of_content` (Firefox, GNOME), 1,104 in one that ended `lost_track`
    (Firefox, Cinnamon). Fix: an offset the bands prove is checked against the quarter bands
    (`contradicted`: two quarters that show something in an eighth of the rows and mostly not
    what they showed), and the quarter-band search now takes the page to be what moved nearest
    the pointer, as a piece or, where lines are too short to prove a distance, by the one
    distance at which seven in ten of the rows a quarter shows are equal bit for bit. The
    bands' offset stands unless the quarters prove another. Where something moved near the
    pointer and nothing is proved, "changed in place" becomes ambiguous: the loop goes back
    and the capture ends honestly instead of losing rows.
11. **The wait for a step's answer began after the pointer had left.** With the pointer
    waiting outside, a page that answers the wheel at once (Plasma) had answered before the
    wait began; frames from before the wait did not count as the answer and every step waited
    out its limit: 1.6 s a step, 101 s for the pull request page from the top. The answer is
    now counted from the wheel step.
12. **A step that added nothing reset the count of failed steps.** Where one wheel step moves
    the picture by more than a viewport and back (Chromium lays the pull request page's
    sections out as they come into view), "changed in place, no rows" alternated with
    "ambiguous" 229 times and the capture ran into its time limit. Only a step that appended
    rows resets the count now; such a page ends `lost_track` with what was proved.

13. **A regression of this round, found by a control and fixed.** The quarter-band search of
    cause 10 took any column that fits at another distance for one that moved. A column of
    line numbers' tens digits fits one line up and one line down as well as where it is; at the
    end of the GTK 4 text control on Plasma, where the wheel moves nothing and the view shows
    its edge effect, "changed in place" became ambiguous, and the capture, with all 1,500 lines
    in it, ended `lost_track` (head `1a9066b3b`, d69). The nearest column that tells anything
    and stayed where it was now ends the search (`dbe04eedc`); checked with that build on d69
    before the push (`end_of_content`, 27,000 rows, 1,500 lines) and by a unit test that fails
    on `1a9066b3b` ([unit/new-test-on-1a9066b3b.txt](unit/new-test-on-1a9066b3b.txt)).

Not a cause: lazy loading of pictures. No capture of the five pages ended for it.


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

60 captures: 42 complete, 12 capped, 6 honest partial.

| Site | Browser | Desktop | Mode | Result | End reason, rows of page | Bands exact of compared | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (a) pull request | Chromium | d69 Plasma | halfway, to the top | complete | `end_of_content`, 34,748 of 34,750 | 541 of 543 | G |
| (a) pull request | Chromium | d69 Plasma | from the top | complete | `end_of_content`, 34,748 of 34,750 | 541 of 543 | G |
| (a) pull request | Chromium | m74 Cinnamon | halfway, to the top | honest partial | `lost_track`, 20,480 of 34,765 | 319 of 320 | A, G |
| (a) pull request | Chromium | m74 Cinnamon | from the top | honest partial | `lost_track`, 20,480 of 34,765 | 319 of 320 | A, G |
| (a) pull request | Chromium | f44 GNOME | halfway, to the top | complete | `end_of_content`, 34,729 of 34,729 | 540 of 543 | G |
| (a) pull request | Chromium | f44 GNOME | from the top | complete | `end_of_content`, 34,729 of 34,729 | 540 of 543 | G |
| (a) pull request | Firefox | d69 Plasma | halfway, to the top | honest partial | `top_not_reached`, 36,479 of 36,481 | 570 of 570 | S |
| (a) pull request | Firefox | d69 Plasma | from the top | complete | `end_of_content`, 36,479 of 36,481 | 570 of 570 |  |
| (a) pull request | Firefox | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 36,501 of 36,502 | 571 of 571 |  |
| (a) pull request | Firefox | m74 Cinnamon | from the top | complete | `end_of_content`, 36,501 of 36,502 | 571 of 571 |  |
| (a) pull request | Firefox | f44 GNOME | halfway, to the top | complete | `end_of_content`, 36,485 of 36,485 | 571 of 571 |  |
| (a) pull request | Firefox | f44 GNOME | from the top | complete | `end_of_content`, 36,485 of 36,485 | 571 of 571 |  |
| (b) Wikipedia | Chromium | d69 Plasma | halfway, to the top | complete | `end_of_content`, 23,937 of 23,939 | 373 of 375 | E |
| (b) Wikipedia | Chromium | d69 Plasma | from the top | complete | `end_of_content`, 23,298 of 23,300 | 365 of 365 |  |
| (b) Wikipedia | Chromium | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 23,299 of 23,300 | 365 of 365 |  |
| (b) Wikipedia | Chromium | m74 Cinnamon | from the top | honest partial | `lost_track`, 1,640 of 23,939 | 23 of 26 | B |
| (b) Wikipedia | Chromium | f44 GNOME | halfway, to the top | complete | `end_of_content`, 23,304 of 23,304 | 365 of 365 |  |
| (b) Wikipedia | Chromium | f44 GNOME | from the top | complete | `end_of_content`, 23,943 of 23,943 | 373 of 375 | E |
| (b) Wikipedia | Firefox | d69 Plasma | halfway, to the top | complete | `end_of_content`, 24,754 of 24,756 | 385 of 387 | E |
| (b) Wikipedia | Firefox | d69 Plasma | from the top | complete | `end_of_content`, 24,115 of 24,117 | 377 of 377 |  |
| (b) Wikipedia | Firefox | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 24,116 of 24,117 | 375 of 377 | T: 2 bands, a paragraph drawn anew |
| (b) Wikipedia | Firefox | m74 Cinnamon | from the top | complete | `end_of_content`, 24,116 of 24,117 | 376 of 377 | D |
| (b) Wikipedia | Firefox | f44 GNOME | halfway, to the top | complete | `end_of_content`, 24,094 of 24,094 | 377 of 377 |  |
| (b) Wikipedia | Firefox | f44 GNOME | from the top | complete | `end_of_content`, 24,094 of 24,094 | 377 of 377 |  |
| (c) Python docs | Chromium | d69 Plasma | halfway, to the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Chromium | d69 Plasma | from the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Chromium | m74 Cinnamon | halfway, to the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Chromium | m74 Cinnamon | from the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Chromium | f44 GNOME | halfway, to the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Chromium | f44 GNOME | from the top | capped | `height_cap`, 52,493 of 110,440 | 821 of 821 |  |
| (c) Python docs | Firefox | d69 Plasma | halfway, to the top | capped | `height_cap`, 52,083 of 111,991 | 814 of 814 |  |
| (c) Python docs | Firefox | d69 Plasma | from the top | capped | `height_cap`, 52,083 of 111,991 | 814 of 814 |  |
| (c) Python docs | Firefox | m74 Cinnamon | halfway, to the top | capped | `height_cap`, 52,083 of 111,974 | 814 of 814 |  |
| (c) Python docs | Firefox | m74 Cinnamon | from the top | capped | `height_cap`, 52,083 of 111,974 | 814 of 814 |  |
| (c) Python docs | Firefox | f44 GNOME | halfway, to the top | capped | `height_cap`, 52,083 of 110,214 | 814 of 814 |  |
| (c) Python docs | Firefox | f44 GNOME | from the top | capped | `height_cap`, 52,083 of 110,214 | 814 of 814 |  |
| (d) MDN | Chromium | d69 Plasma | halfway, to the top | complete | `end_of_content`, 18,627 of 18,629 | 292 of 292 |  |
| (d) MDN | Chromium | d69 Plasma | from the top | complete | `end_of_content`, 18,627 of 18,629 | 292 of 292 |  |
| (d) MDN | Chromium | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 18,628 of 18,629 | 292 of 292 |  |
| (d) MDN | Chromium | m74 Cinnamon | from the top | complete | `end_of_content`, 18,628 of 18,629 | 292 of 292 |  |
| (d) MDN | Chromium | f44 GNOME | halfway, to the top | complete | `end_of_content`, 18,629 of 18,629 | 292 of 292 |  |
| (d) MDN | Chromium | f44 GNOME | from the top | complete | `end_of_content`, 18,629 of 18,629 | 292 of 292 |  |
| (d) MDN | Firefox | d69 Plasma | halfway, to the top | complete | `end_of_content`, 18,673 of 18,675 | 289 of 292 | T: 3 bands, the rotated headings of a table |
| (d) MDN | Firefox | d69 Plasma | from the top | complete | `end_of_content`, 18,673 of 18,675 | 289 of 292 | T: 3 bands, the rotated headings of a table |
| (d) MDN | Firefox | m74 Cinnamon | halfway, to the top | honest partial | `lost_track`, 16,101 of 18,632 | 252 of 252 | C |
| (d) MDN | Firefox | m74 Cinnamon | from the top | honest partial | `lost_track`, 16,101 of 18,632 | 252 of 252 | C |
| (d) MDN | Firefox | f44 GNOME | halfway, to the top | complete | `end_of_content`, 18,649 of 18,649 | 291 of 292 | T: 1 band, a line with an emoji one row lower |
| (d) MDN | Firefox | f44 GNOME | from the top | complete | `end_of_content`, 18,649 of 18,649 | 292 of 292 |  |
| (e) repository | Chromium | d69 Plasma | halfway, to the top | complete | `end_of_content`, 4,715 of 4,717 | 74 of 74 |  |
| (e) repository | Chromium | d69 Plasma | from the top | complete | `end_of_content`, 4,715 of 4,717 | 74 of 74 |  |
| (e) repository | Chromium | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 4,716 of 4,717 | 74 of 74 |  |
| (e) repository | Chromium | m74 Cinnamon | from the top | complete | `end_of_content`, 4,716 of 4,717 | 74 of 74 |  |
| (e) repository | Chromium | f44 GNOME | halfway, to the top | complete | `end_of_content`, 4,717 of 4,717 | 74 of 74 |  |
| (e) repository | Chromium | f44 GNOME | from the top | complete | `end_of_content`, 4,717 of 4,717 | 74 of 74 |  |
| (e) repository | Firefox | d69 Plasma | halfway, to the top | complete | `end_of_content`, 4,711 of 4,713 | 74 of 74 |  |
| (e) repository | Firefox | d69 Plasma | from the top | complete | `end_of_content`, 4,711 of 4,713 | 74 of 74 |  |
| (e) repository | Firefox | m74 Cinnamon | halfway, to the top | complete | `end_of_content`, 4,712 of 4,713 | 74 of 74 |  |
| (e) repository | Firefox | m74 Cinnamon | from the top | complete | `end_of_content`, 4,712 of 4,713 | 74 of 74 |  |
| (e) repository | Firefox | f44 GNOME | halfway, to the top | complete | `end_of_content`, 4,712 of 4,712 | 74 of 74 |  |
| (e) repository | Firefox | f44 GNOME | from the top | complete | `end_of_content`, 4,712 of 4,712 | 74 of 74 |  |

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
- CI run [43202012192](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43202012192) on the final head: success (16 jobs passed, 3 skipped by path rules).

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
none of the 60 live captures ended for this rule. Something that changes without moving (a
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

