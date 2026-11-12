# Scroll capture fix round 6 — PR #1398 (issue #1376)

Two defects from the review acceptance of 2026-11-11
([record](https://github.com/patrick-hudson/put.gd-evidence/tree/9d54f33ba7450ca38c58bf1baf3a7ccb37d1c756/records/2026-11-11-scroll-review-accept-1398)):
a resize inside the captured rectangle, and Cancel beside Stop.

- Repository `patrick-hudson/put.gd-desktop`, branch `feat/scroll-capture`.
- Before: head `24d4c83a8`, CI run 43107261698, Debian 13 package
  `putgd_26.1111.4677~dev+g2fc87209a36e_amd64.deb` (SHA-256 `99bb63c0…2492`).
- After: head `a48d2221727fe215ec05e8fa7cfd4e8e5994301c` (commits `72e9dda48`, `a48d22217`),
  CI run [43121369161](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43121369161)
  green. Packages of that run, build `26.1111.4679-dev+g73a02816cbf9` (merge commit
  `73a02816cbf9`, second parent `a48d22217`):
  `putgd_26.1111.4679~dev+g73a02816cbf9_amd64.deb` SHA-256
  `eb146b18a6bb026e07d900af68ce5be2acdea8ae3af11dcaf67eea71850e4e3b` on d69,
  `putgd-26.1111.4679~dev+g73a02816cbf9-1.fc44.x86_64.rpm` SHA-256
  `52cf201b8368a75743c016eec002796a529d56c146462a868551212fc545ab93` on f44. No per-host compile.
- Hosts: d69 (Debian 13, Plasma 6.3.6 Wayland, KWin region stream and fake input) and f44
  (Fedora 44, GNOME 50 Wayland, Mutter area stream and remote desktop, Shell extension
  version 22 ACTIVE after a re-login). Driver, fixtures and oracles are the tester's
  (`pass2.py`, `qt_fixture.py`, `resize_window_fixture.py`, `scroll_run.py`, `verify_text.py`
  in the review record); what this round added is in [tools/](tools/).

## Read this first: the acceptance case did not show what it was taken for

The tester's `resize-window` case still ends `end_of_content` with a 960x24,100 image, on
both desktops, three times of three, with the fix. That is not the defect, and the fix does
not change it. The helper logs of the four acceptance images show why: the fixture resizes
its window 5 s after it starts, and at that moment the page was still on its way to the top
(GNOME: first stitched step at 16:33:38.7, capture started 16:33:32.2; Plasma likewise).
No row had been stitched. Every frame the capture stitched showed the new layout from its
first one on: `fixed 39/61` (GNOME) and `fixed 28/90`, then `28/72` (Plasma) are in the very
first `scroll step` lines.

The four acceptance images were checked cell by cell (16 cells a line, the 12 inside the
760 px viewport): each holds every one of the 24,000 ruler rows once, in order, 288,000
cells and no bad one, between the window's gray above, below and beside it. They are the
page as the rectangle showed it for the whole capture. The tester's oracle expected the
960 px ruler and so called the gray wrong. `tools/fix6.py` has the oracle that knows the
viewport (`verify_layout`).

What the acceptance run was meant to test, a layout that changes after rows were committed,
was broken, and worse than reported. That is what this round fixed. A change on the way to
the top is left as it is on purpose: nothing of the earlier layout is in the image, and the
only signals that could tell it from a page that simply looks different at its top would end
captures that are right today. If the coordinator wants that case refused as well, it is a
separate decision; the cost is false ends, not code.

## Defect 1: the layout inside the rectangle changes after rows were committed

Mechanism, proved by the new unit tests on the old code
([unit/new-tests-on-old-code.txt](unit/new-tests-on-old-code.txt): 44 failed, 18 of them
sessions that ended `EndOfContent` with foreign rows) and on Plasma with the old package
([d69/before/](d69/before/)):

- **Narrower.** A row passes the tolerant rule with two of eight bands different. When the
  viewport gets narrower the window's background replaces the page in the same bands of
  every row, every row still passes, rows of both layouts are stitched and the run goes on
  to the end. Old package on Plasma, `mid-narrower-0`: `end_of_content`, 24,000 rows,
  wrong from row 6,450 on (70,200 bad cells).
- **Shorter, or a bar that pins itself to the bottom.** The footer estimate only shrinks, so
  a band that newly stays put at the bottom is appended as page at every step, with the
  page's rows hidden under it. Old package on Plasma: `mid-shorter-0` ends `lost_track` with
  6,810 rows of which the last 100 are the window's gray, `mid-viewport-0` ends `lost_track`
  with 6,810 rows that are wrong from row 6,450 on; both inside an image that says it is
  exact. In the unit tests, at 40 px a notch, the run reaches `EndOfContent`.

The fix is a layout rule in the stitcher, in two parts.

- **Columns** (`ScrollStitcher::columnsChanged`). For each band of columns: how many rows
  of the overlap are neither where the offset says (moved with the page) nor where they
  were (stayed). A band is *steady* while that is at most a tenth of the rows. A band that
  every proved step so far left steady, and that is neither in at least nine rows of ten
  in one step, was repainted as a whole: the step is `LayoutChanged`.
- **Rows** (`ScrollStitcher::barVerdict`). A run of rows that newly stays put at the bottom
  of the frame, beyond the footer estimate, is a bar when the rows that should have
  scrolled out of it contradict it (at least 4, and more than three to one against rows
  that did come out of it). Rows count as proved only up to the last step that showed no
  such run, and the image is cut back to there (`RowTakeBack`; the helper truncates its
  spool). The search is repeated on the area above the run when the full search failed, so
  the rule also speaks when the bar is too tall for the search's tolerance.

The run ends `LostTrack` (`lost_track`, truncated, with the note "the layout inside the
selection changed during the capture; the image ends with the rows from before the
change"). `lost_track` was chosen over `display_changed` because the frames kept their
size, so the display did not change, and because `lost_track` already means "the image so
far is exact", which is now true again. `src/app/ScrollBackend.h` is unchanged.

**Why the signal does not fire on what passed before.** Both parts ask for a change in
*history*, not for a state:

- A side bar, a minimap, a wide scrollbar thumb: a band that never was steady is never
  asked. It stays with the tolerant rule, exactly as before.
- A hover effect, a caret, a painted pointer, a popup: they touch a few rows; the rule needs
  nine rows of ten of the overlap in one band.
- A scrollbar that fades in or out: the side margins (4% each) are not looked at.
- Margins and bands that are static from the first frame: they are in the footer and header
  estimates or are steady by staying, and nothing about them changes.
- Blank rows that happen to be alike at the bottom of two frames (the ordinary
  over-estimate): when the page really moved, the rows above them are what was in them, so
  nothing contradicts.
- A bar that is there in every frame since the page first moved (only the first frame,
  taken before any wheel step, is without it): it becomes the footer, the rows the first
  step took from under it are taken back, and the capture goes on to the end. Before the
  fix this case ended `EndOfContent` with the bar inside the body.
- A band that comes up at the top hides rows that are already in the image; appended rows
  come from the bottom. It is left to the search as before.

Known limits, said in the code: a change confined to the 4% side margins is not seen; a
scrollbar wider than the side margin whose thumb appears over nine tenths of the overlap in
one step ends the capture honestly; a change in place while the page stands still can cost
the rows of the last step (cut back further than needed, still an exact prefix).

### Unit tests

`tests/unit/test_scroll_stitcher.cpp`, `testLayoutChange` (60 checks; the suite is 202
passed, 142 before): five kinds of change (narrower and shorter, narrower, shorter, narrower
by less than a band, shorter from the top) at four step sizes through the stitcher and at
three wheel distances and two moments through `ScrollRun`, each asserting no `EndOfContent`
and that the image is nothing but the document's first rows; the change in place; and the
mirror cases that must still end `EndOfContent` exact: margins and a band that were always
there, a resize on the way to the top (the acceptance case), a bar pinned from the first
scroll on, a scrollbar that fades and a cursor that blinks; and a bar pinned after rows
were taken from under it, which ends `LostTrack` with an exact prefix. All existing checks
pass unchanged. `--full` ([unit/new-tests-on-new-code-full.txt](unit/new-tests-on-new-code-full.txt)):
208 passed, 1 failed; the one failure (`session sweep, constant px/notch`, seed 9) fails the
same way on the old code.

### Desktops, new packages

`E` exact and complete, `H` honest end with an exact prefix, `W` wrong.

| Case | d69 Plasma | f44 GNOME |
|---|---|---|
| Tester's `resize-window` (change on the way to the top) x3 | E3: `end_of_content`, 24,100 rows, 24,000 ruler rows, 0 bad cells of 288,000, as before | E3, the same |
| The same change after rows were committed, window x3 | H3: `lost_track`, 6,450 rows | H3: 6,420 rows |
| Viewport 760x500 where it is x3 | H3: 6,450 rows, layout note | H3: 6,420 rows, layout note |
| Viewport narrower only x3 | H3: 6,450 rows, layout note | H3: 6,420 rows, layout note |
| Viewport shorter only x3 | H3: 6,450 rows, layout note (rows taken back) | H3: 6,420 rows, layout note |
| 24,000 px ruler from its end x2 | E2 | E2 |
| Qt text, 1,500 lines, from its end x1 | E1 (27,022 rows, 1,500 lines) | E1 (28,520 rows) |
| GTK 4 text x1 | E1 (27,000 rows) | E1 (27,000 rows) |
| Browser ruler from top x1 | E1 | E1 |

The change is made by `tools/resize_mid_fixture.py`: the tester's fixture, with the resize
tied to the page's position (it has been at 0 and comes down to 6,000) instead of to a
timer. Every `H` image passes the tester's ruler oracle over every scanline at its own
height. The old package on Plasma, same fixture: window H1, viewport W1, shorter W1,
narrower W1 (`end_of_content`).

## Defect 2: Cancel beside Stop ended the operation `failed`

Mechanism, from the helper logs of the acceptance run and reproduced on Plasma with the old
package (2 of 5 failed, [d69/before/cancel-stop-2](d69/before/cancel-stop-2/result.json)):
in every failing trial the helper received **Cancel first, then Stop**. The two requests are
a millisecond apart on two connections and the resident took the Cancel first. It passed the
Cancel on; the helper answers a Cancel only when its worker has ended. A Cancel left no mark
in the resident, so the Stop that followed was passed on as well. The helper refused it at
once (`scroll_state`, "Nothing is being captured"), that refusal reached the resident before
the Cancel's answer, and an error answer to a command ends the session as failed. With Stop
first the old build was right already (6 of 6 in that order).

Fix (`src/app/ScrollCaptureService.*`): the resident remembers that a Cancel is on its way.
From then on no other command is passed on (`scroll_busy`), the answer to an earlier Stop
(refused, or finished with its image) is answered `cancelled` and changes nothing, and a
`finished` event is ignored. The session ends `cancelled` and the image is discarded. Which
of the two wins is the order in which the resident, one thread, takes them: a Stop whose
image was validated and admitted before the Cancel arrived has ended the session, and that
Cancel is answered `scroll_not_found` like any command for an ended session. The helper
(`ScrollCapture::stop`) answers a Stop behind a Cancel whose worker is still ending with
`cancelled` instead of a state error.

Tests: `tests/integration/test_scroll_service.cpp`, `cancelInFlightDecides`, four rows (Stop
arrives after the Cancel; Stop is refused while the Cancel is on its way; Stop finishes its
image while the Cancel is on its way; the finished event arrives meanwhile). All four failed
on the old resident (`scroll_state`, an admitted image) and pass now; each ends with a next
capture that is admitted.

Desktops, new packages: the tester's case (Stop, 1 ms later Cancel) x5 and Stop then Cancel
50 ms later x3 on each host. d69: 8 cancelled, 0 failed (one trial in the Cancel-first
order). f44: 8 cancelled, 0 failed (three trials in the Cancel-first order). No image
admitted, the screenshot 2 s later shows no ring and no bar
(`cancel-stop-N/screen-2s-later.png`), the next capture is exact on both. f44: Shell pid
3823265 from the re-login to the end, `coredumpctl` lists no gnome-shell core since the
campaign began (`f44/after/shell-core-check.txt`).

## Whole suite

d69, dev tree at the pushed head: `ctest --preset dev --parallel 3` 154 of 154;
`tests/integration/test_mcp.py` 8 OK. The surface pytest on d69 has the same 7 failures as
in the round before (the CI contracts job runs it and passes).

## Cleanup

d69: test package removed (`rc`, as found), package names equal the set before, 1,272
scratch files deleted from exact manifests, lock released 23:58:08 UTC with the cleanup
check. f44: `putgd`, `jasper-libs`, `libmng`, `qt6-qtimageformats` removed together,
package names equal the set before, both extension lists byte-equal to before, one re-login
after, overview closed, wall VNC restarted and active, 1,121 scratch files deleted from an
exact manifest, lock released 00:00:07 UTC with the cleanup check. Nothing was booted.

## For the docs PR (#1408)

1. The layout rule and the step status `LayoutChanged`; it ends `lost_track` with the note
   above. `display_changed` stays the frame-size case only (the sentence that names
   `LayoutChanged` for the frame size needs the distinction: `RunResult::LayoutChanged`
   there, `StepStatus::LayoutChanged` here).
2. Rows are no longer never revised: the last rows can be taken back before the image is
   finished (`RowTakeBack`, the helper truncates its spool).
3. A bar that is there from the first scroll on becomes the footer; one that comes later
   ends the capture; a band at the top is not judged.
4. A layout change on the way to the top is not a change: the image is the layout the
   capture stitched.
5. The limits listed above (side margins, a band that never was steady, a wide scrollbar
   thumb, the change in place).
6. Cancel: once a Cancel is on its way, other commands are `scroll_busy`, a pending Stop is
   answered `cancelled`, a `finished` event is ignored; a Stop admitted first wins and the
   Cancel is `scroll_not_found`. The helper answers a Stop behind an unfinished Cancel with
   `cancelled`.
7. `StitchOptions`: `layoutSteadyFraction`, `layoutBrokenFraction`, `layoutStaticMinRows`,
   `layoutStaticRatio`.
8. The sentence about a rectangle that covers at most two of the eight bands: such a
   rectangle that appears over nine tenths of the overlap's rows in a steady band now ends
   the capture as `lost_track`.
