# Scroll capture fix round 7 — PR #1398 (issue #1376): live web pages

The acceptance of 2026-11-12
([record](https://github.com/patrick-hudson/put.gd-evidence/tree/fb48c9152bdce74fb99fe9b6ba612f171f14bb5b/records/2026-11-12-scroll-accept2-1398))
found three things: every capture of a real web page ended `lost_track` a few steps in with
the browser's link panel and a line stitched into the image; a column that scrolls at its own
rate (a minimap) came out as a mosaic in an image reported complete; and a build with no region
selector admitted a wrong image for a rectangle named on the command line.

- Repository `patrick-hudson/put.gd-desktop`, branch `feat/scroll-capture`.
- Before: head `0bbf42fd2`. After: head `@HEAD@` (commits `6d8ae9801`, `44c824a32`,
  `bada70f1b`, `6915a619a`, `8d3848808`, `1a9066b3b`, `@HEAD@`), CI run @CIRUN@.
- Packages of that run, build `@BUILD@` (CI merge commit `@MERGE@`, second parent the head):
@PACKAGES@
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

