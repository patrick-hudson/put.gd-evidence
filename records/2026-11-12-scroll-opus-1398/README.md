# Scroll capture, a fresh pass — PR #1398 (issue #1376)

A bounded pass over the acceptance of 2026-11-12
([accept3 record](https://github.com/patrick-hudson/put.gd-evidence/tree/318c314485e37943df8c332eb4aaa3d2ddc1815e/records/2026-11-12-scroll-accept3-1398)).

- Repository `patrick-hudson/put.gd-desktop`, branch `feat/scroll-capture`.
- Before: head `dbe04eedc`. After: head `70d708fb9` (commits `eb606a9c2`, `68d86d226`, `70d708fb9`).
  CI run [43280455095](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43280455095): every job passed.
- Packages of that run, build `26.1112.4721-dev+ga74da8018785` (CI merge `a74da8018785`, parents
  nightly `e2feda178` and the head `70d708fb9`):
  - `putgd_26.1112.4721~dev+ga74da8018785_amd64.deb` (ubuntu24.04, m74), SHA-256 `febdf55a1167b77ac2f7702ec7ad037c8f7b54bc22d36b2805a3cfff566c27f8`
  - `putgd_26.1112.4721~dev+ga74da8018785_amd64.deb` (debian13, d69), SHA-256 `e5fe87c341e6a39bd6d10e5a81b5411813144adbcb7069d265af1ffb994c0fe2`
- Hosts: m74 (Mint 22.3, Cinnamon X11), d69 (Debian 13, Plasma 6.3 Wayland). No compile on a host
  for the desktop tables; builds and unit tests on d69 only.
- Drivers: the tester's `pass2.py`, `fix6.py`, `late_fixture.py`, `controls7.py`, `replay-late-oracle.py`
  and FIX-7's `live7.py`, pointed at a scratch directory of this pass; the case scripts of this pass
  are here (`opus_cases.py`, `opus_host.sh`, `opus_live.sh`, `stop_resident.py`, `endtime.py`).
  On d69 every cap was lowered to 30,000.

## 1. False completion (m74, `new-nonfixed`, operation acff15cd) — fixed and proved

**Mechanism** (from the operation's helper log; reproduced by a unit test that fails on the old
loop). The fixture rebuilds its whole 960x24,000 picture for every wheel event (130 to 200 ms each)
and paints once no event is waiting. After the way up: step 1 (1 notch) moved 60 px. Step 2
(6 notches, hint 360) showed 60 px: the page had painted its first notch only, and the loop took that
for the last, partial step of the page. Step 3 was still for its 552 ms and its fresh frame agreed
(the page was busy). Step 4 moved 300 px 36 ms after its own wheel step: the rest of step 2. Steps 5
and 6 were still for 552 ms each while the page worked through about 12 queued notches; two still
steps in a row ended the capture `end_of_content` at 1,020 rows. The fixture log has the page at
1,140 px when it was closed; the capture had seen 420.

**What tells the end from "not answered yet".** Waiting longer alone proves nothing. A page answers
its wheel steps in the order they came: once a step **up** visibly moves the page up, everything
sent before it has been answered, and none of it took the page past what the image ends on. One
notch more **down** than up must then bring back exactly the picture it ended on; a page that is not
at its end goes a notch further.

**Change** (`src/record/ScrollRun.cpp`, `ScrollRun::proveEnd`; commits `eb606a9c2`, `70d708fb9`):

- Where the run has a reason to doubt a still step, the end is proved that way. The reasons: an
  earlier still step was followed by movement after all; the last step moved all it asked (a page
  that runs out of content stops partway); or the page's answer takes longer than the picture's
  settle time (a short step may then have been seen halfway).
- An unanswered step up is sent again, twice as large with twice the patience (1, 2, 4 notches),
  because a view overscrolled at its edge spends the first steps back.
- Where one notch more than up is too far down to place from where the step up went (a notch near
  half the band), it comes back down in two steps.
- Not answered, or not back where it ended: `lost_track`, note "the page did not answer a wheel step
  up and back down, so the end of the content is not proven". Further down: the capture goes on, and
  the time the page took becomes the least the loop waits for an answer.
- Without such a reason the old rule stands (two still steps), except that the confirming step is
  one notch (more is only more for a busy page to work through) and gets twice the response time.
- Why the proof is not run at every end: three existing tests forbid any wheel-up step once a
  capture with scroll-to-top has begun (see "Existing tests" below), and I did not edit them.

**Failing, then passing test.** `test_scroll_stitcher`, `session a page slower than the wait is not
at its end` (24 sessions: a page that works through its notches one by one at 60, 120 and 250 ms a
notch, painting when idle, or painting a step's first notch at once and the rest when idle; 40 and
60 px a notch; viewports of 600 and 800). Old loop ([new-tests-on-dbe04eedc.txt](unit/new-tests-on-dbe04eedc.txt)):
4 complete, **20 `EndOfContent` early** (640 to 1,500 rows of about 3,500 to 4,000). New loop:
14 complete, 10 honest ends with an exact prefix, none early.

**Desktops** (every RGB pixel against the tester's replayed generator, `replay-late-oracle.py`):

| Fixture | m74 Cinnamon | d69 Plasma |
| --- | --- | --- |
| `new-nonfixed` (V1) x3 | `end_of_content`, 24,000 of 24,000, exact, x3 (81 s each) | `end_of_content`, 24,000 of 24,000, exact, x3 (48 to 60 s) |
| `new-fixed` (counter) x3 | `end_of_content`, 24,036, exact, x3 | `end_of_content`, 24,036, exact, x3 |

Before, on m74: one false completion (1,020 rows) and one full image with 2,259 wrong tail pixels.
Every non-fixed capture ended through the proof (`Reversed -60`, then `Appended 60`, no new rows),
and the loop's patience rose to the page's demonstrated answer time (slowest response 1,081 ms).

**True end, before and after** (from the last step that appended rows to "ended"; before = the
tester's runs on `dbe04eedc`):

| Capture | m74 before | m74 after | d69 before | d69 after |
| --- | --- | --- | --- | --- |
| 24,000 px ruler from its end | 2.22, 2.23 s | 2.00, 2.05 s | 2.34 to 2.44 s | 2.01, 3.53 s ¹ |
| Qt text | 2.46 s | 3.00 s | 3.35 s | 2.55 s |
| GTK 4 text | 3.35 s | 3.49 s | 3.46 s | 3.19 s |
| Browser ruler from top | 1.47 s | 1.64 s | 1.68 s | 1.68 s |

¹ That capture's way to the top had a 656 ms response (16.9 s instead of 6.2 s), and the still step
waits three times the slowest response; the proof itself took 0.55 s in both d69 ruler runs.

## 2. Live pages that end early — one cause found and fixed, four left, each with its cause

All seven early ends report the same guard, "a single notch scrolls further than the overlap
allows". That is the loop's last word after two failed one-notch steps, not a cause. From the
cells' helper logs (accept3 `m74-review`/`d69-review` archives):

| Cell | What the log shows | Cause |
| --- | --- | --- |
| d69 Chromium PR, top | 1 notch = 180 px. A step of 51 px (the late bar came up), then a 1-notch step of 309 px: its own 180 and the 129 the step before lacked. 309 was learned as the distance a notch; every 2-notch step of 360 then counted as "short" against 618, so nothing corrected it; at one notch, offset 180 (score 1.00, 707 evidence rows) tied with a rival 129 px from the hint 309: Ambiguous, twice | a step seen halfway taught the distance a notch — **fixed** |
| m74 Chromium PR, both modes | Ambiguous offset -811 for hint 120; the way back finds the reference | the page lays itself out anew under the viewport (FIX-7 note A); no offset is proved |
| m74 Firefox MDN, both modes | NoMatch, no candidate at all, at 2 and 1 notch | text drawn anew at another sub-pixel place (FIX-7 note C) |
| m74 Firefox Wikipedia, half | NoMatch, no candidate; the donation bar from row 2,048 | a bar over more than a tenth of the overlap in the step's own frame (FIX-7 note B) |
| d69 Firefox Wikipedia, top | NoMatch, no candidate, at 2 and 1 notch; footer 104 (the donation bar) | not isolated; same family as the m74 Wikipedia cell |

**Change** (commit `eb606a9c2`): after a step that fell short of its hint, the next step's hint
uncertainty grows by what it lacked, and that step teaches nothing about one notch. No match rule
was weakened. A smaller wheel step does not exist (one notch is the injectors' smallest), and the
loop already goes back and halves to one notch; neither helps the four other cells, which are
content the stitcher cannot prove by equal rows.

**Desktops** (FIX-7's band oracle, `live7.py verify`: a band of 64 rows passes when at most 0.2% of
its pixels lie in 4x4 blocks whose grey mean differs by more than 32; not the tester's strict
all-column oracle, which was not run):

| Cell, x2 | Result | Rows | Bands | Class |
| --- | --- | --- | --- | --- |
| d69 Chromium PR, top | `height_cap` x2 | 30,000 of 44,692 | 468 of 469 ² | capped (before: `lost_track` at 3,827); 180 px a notch kept, no Ambiguous step |
| m74 Chromium PR, top | `lost_track` x2 | 37,400 and 37,280 of 44,707 | 584 of 585, 582 of 583 ² | honest partial (before: 20,480 of 34,765; the page has grown) |
| m74 Firefox MDN, top | `lost_track` x2 | 16,101 of 18,632 | 252 of 252 | honest partial, unchanged |
| m74 Firefox Wikipedia, half | `end_of_content` x2 | 24,116 of 24,117; 24,755 of 24,756 | 375 of 377; 385 of 387 ³ | complete (before: `lost_track` at 2,163) |
| d69 Firefox Wikipedia, top | `end_of_content` x2 | 24,115 of 24,117 | 377 of 377; 376 of 377 ⁴ | complete, but the page came without the donation appeal (24,117 rows; before 24,504): not a proof for that cell |

² All but one band match, 60 rows further on in the reference: the Chromium reference's gap
(FIX-7 note G); the one band is the gap's. ³ Run 0: two bands one row off (a paragraph drawn anew,
FIX-7 note T); run 1 (with the appeal): the last 115 rows, the donation bar pinned over the page's
last rows as on the screen (FIX-7 note E). ⁴ 288 pixels at x 1,380..1,408 near the top, not looked at.

## 3. Judged

**(a) A top bar that appears only after 300 px is not in the image.** Deliberate, in the code
(FIX-7 cause 1; `ScrollStitcher::addFrame`, the comment above the `headerVerdict` use: "the bar
itself is in none of the image's rows, as in the browser's own picture"). I agree: at scroll 0 the
page has no bar, no scroll position shows the bar above row 0, and a browser's full-page picture has
none. A bar at the top of the image would show a state the page is never in. A docs point, not a
defect; not changed.

**(b) The last rows on Cinnamon.** The bar paints an opaque fill and draws no shadow of its own; on
X11 Muffin draws one around it, and the bar sat 10 px below the rectangle, left-aligned with it (the
contaminated columns, x 0..455, are the bar's, not the rectangle's width). Changed (commit
`68d86d226`, `ScrollBar::place`): 32 px on X11. No unit test (placement needs a live X11 surface).
Proved on m74 by the fixtures above: counter and non-fixed images exact to the last row (before:
1,334 and 2,259 tail pixels).

## 4. A fresh read of the comparisons FIX-7 loosened

- **Tie-breaking by hint admitted a wrong image, shown by a failing test.** A step seen halfway
  makes the next one move more than its hint, and among rows that repeat the tie rule picked the
  offset beside the hint: 60 px for 200 asked, then 340 taken for 196, a table missing from an
  image reported `EndOfContent`. Test `session a step seen halfway is not matched beside its hint`
  (12 sessions, a long table of repeating rows): old loop, one wrong image (`split s4 px100 v300`,
  bad from row 1,177); new loop, 10 exact and 2 honest ends. Fixed by the same change as item 2,
  in the run loop, not in the match rule.
- **Rows the same when equally bright** (`columnLightTolerance`, quarter bands): read, no defect
  found. A quarter counts as moved at a distance only with at least 24 different rows equal bit for
  bit there; brightness only lets the overlap's other rows pass; a column that fits at more than
  8 distances is dropped. Not tested adversarially beyond the tester's equal-brightness fixture.
- **Rows taken from the next frame** (the edge guard) and **the nearest column that stayed**: read,
  no defect found; controls (GTK 4 text, which the latter was added for) pass on both desktops.

## Controls, final head

| Control | m74 Cinnamon | d69 Plasma |
| --- | --- | --- |
| 24,000 px ruler from its end x2 | `end_of_content`, 24,000 exact, x2 | `end_of_content`, 24,000 exact, x2 |
| Qt text x1 | `end_of_content`, 22,519 rows, 1,500 lines, one pitch | `end_of_content`, 27,022 rows, 1,500 lines |
| GTK 4 text x1 | `end_of_content`, 24,000 rows, 1,500 lines | `end_of_content`, 27,000 rows, 1,500 lines |
| Browser ruler from top x1 | `end_of_content`, 2,400 exact | `end_of_content`, 2,400 exact |
| Sticky header and footer x1 | `end_of_content`, 24,080 exact | `end_of_content`, 24,080 exact |
| Committed resize x1 | `lost_track`, 6,420, exact prefix (honest) | `lost_track`, 6,450, exact prefix (honest) |
| Minimap x1 | `lost_track`, 600, strip and column exact (honest) | `lost_track`, 600, strip and column exact (honest) |

## Unit, ctest, MCP, CI

- `test_scroll_stitcher` on the final run loop: 252 passed, 0 failed ([output](unit/test_scroll_stitcher-70d708fb9.txt)).
  The new tests on the old loop: 2 failed ([output](unit/new-tests-on-dbe04eedc.txt)).
- `--full` ([output](unit/test_scroll_stitcher-70d708fb9-full.txt)): 258 passed, 1 failed, the same
  one as before this pass (`session sweep, constant px/notch`, seed 9; FIX-6 and FIX-7 have it).
  An intermediate state of this pass had two more honest early ends there (a lost wheel step in a
  300-row viewport); `70d708fb9` fixed them.
- d69 dev tree at `70d708fb9`: `ctest --preset dev --parallel 3` 155 of 155 ([log](unit/ctest-70d708fb9.log));
  `tests/integration/test_mcp.py` 8 tests OK ([log](unit/mcp-70d708fb9.log)).
- CI run 43280455095 on `70d708fb9`: success. CodeRabbit and cubic skipped these pushes; no
  review, inline comment or "Outside diff range" section came in.

## Existing tests that encode a narrower expectation (not edited)

`tests/unit/test_scroll_stitcher.cpp`: "way to the top longer than the old 15 s" requires every
negative wheel event to be -10 (line 2868 at `70d708fb9`), "way to the top, steps grow" requires the last
two to be 10 (line 2888), and "scroll to top first, page opened halfway down" forbids a -10 once a step
down was sent (line 2468). Together they forbid any wheel step up after a capture with scroll-to-top has
begun. That is why the end proof runs only where a still step is in doubt, not at every end; with
those filters limited to the way up, it could run at every still step.

## What is not fixed, and why

1. **A residual of item 1.** Where no doubt is raised (no earlier false end, a short last step, and
   a page that answers within the settle time), the end still rests on two still steps (the second
   with one notch and twice the patience). A page that paints a step's first notch at once and then
   works through a backlog longer than about three response times, faster than 120 ms a notch, can
   still be taken for its end. Not seen on a desktop; inside the unit test's range it ends honestly.
2. **m74 Chromium PR, m74 Firefox MDN, Firefox Wikipedia with its donation bar**: content that equal
   rows cannot prove (re-layout under the viewport, sub-pixel redraw, a bar over a tenth of the
   overlap in the step's own frame). Proving these needs a measure other than equal rows, which the
   brief rules out. They end honestly.
3. The misleading note "a single notch scrolls further than the overlap allows; enlarge the region"
   on those ends: not changed (a wording change in a user-visible note, outside this pass's scope).

## For the docs PR (#1408)

1. The end proof: when it runs, what it sends (a step up of 1, 2, 4 notches with patience x1, x2, x4,
   then one notch more down, in two steps where that does not fit), what ends it (`lost_track` with
   the note above), and that the page visibly moves up and back at the end of such a capture.
2. Without doubt: the confirming still step is one notch and waits twice the response time.
3. After a short step the hint is less sure by what that step lacked, and that step teaches no
   distance a notch.
4. On X11 the bar keeps 32 px from the rectangle (10 elsewhere).
5. Known limits: the three content kinds in "What is not fixed", item 2.

## Cleanup

- m74: lock released 19:07 UTC verified clean; the test package removed (`putgd` is `rc` as before,
  now naming this pass's version); Chromium (installed for this pass) purged; the package list and
  APT manual marks equal to the lists saved before; no browser, resident or fixture left; 2,595
  scratch files deleted from an exact manifest.
- d69: lock released 19:25 UTC verified clean; the same for the package, `chromium` and
  `chromium-common`; the put.gd section of `kglobalshortcutsrc` equals the tester's restored state
  and `kwinrc` has the tester's snapshot digest; the signer's pre-existing `gpg-agent` left alone;
  2,409 scratch files deleted from an exact manifest. The dev tree `~/work/s1376/src` now holds
  `70d708fb9`'s files.
- At most one desktop lock was held at a time, with heartbeats. No Ctrl+Alt+F<n>, no key or button
  injected; injected input was the capture's own wheel and pointer motion at windows this pass opened.
