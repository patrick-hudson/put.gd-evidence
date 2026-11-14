# Scrolling capture's session on the tracker, on real pages (#1515)

The helper's scrolling capture session of PR #1528 (`ScrollSession` on `ScrollTracker`), run on
real web pages in both drivers on 2026-11-14:

- **you scroll**: put.gd injects nothing. A relative mouse made through `/dev/uinput`
  (`lab/umouse.py`, `w N` turns its wheel) turns the wheel at a person's pace: bursts of 1 to 5
  notches 0.15 to 0.45 s apart, a pause of 1.2 to 2.2 s now and then, once 5 notches back up a
  little past the middle. It scrolls to the end of the page, then presses Done. When the bar says
  "Lost the page", it scrolls back 2 notches, as the bar asks. On Cinnamon (m74), where
  `/dev/uinput` is root's, the wheel is XTest from the test's own client (`xdotool click 4/5`).
- **auto**: the session starts with auto-scroll on (`driver: putgd`) and is left alone to the
  end. A capture whose auto-scroll handed the page back is finished with Done 15 s later, as a
  person who saw it stop would.

The builds were lab builds of the PR's head (commit 1919b0097, with the tracker of #1529; aurora-amd in the putgd-build toolbox; m74
natively), driven by the lab driver (`test_scroll_capture_driver --driver user|putgd
--stop-file`), with no resident and local files only. The browsers are the baseline's Chrome for
Testing 157 and Firefox 160 (aurora-amd) and the system Firefox 158 (m74). One window opened per
page by the harness, a fresh browser per page. Region: the browser's viewport without its
scrollbar column. Cap: 60,000 px.

Files: `lab/sess.py` (the harness, on top of the baseline's `live7.py` browser control),
`lab/umouse.py`, `lab/score.py` (the comparison), `lab/pictures.py`, `aurora.json` and `m74.json`
(every run's numbers).

## Comparing with the browser's own picture

`score.py` gives two numbers per run against the browser's full-page picture in 64-row bands,
leaving out what the page pins and the scrollbar:

- **strict**: the tracker scorer's comparison (`tools/lab/scroll_tracker_score.py`, a band is
  equal when at most 0.5% of its pixels differ by more than 24). It was made for browser pictures
  against browser pictures. Against the screen it fails text that the screen draws with
  subpixel antialiasing (Firefox on X11), and pages laid out at 1,920 px for the browser's
  picture but at 1,905 px on the screen (a centred page is 7.5 px off).
- **tolerant**: both grey and blurred a little, at the horizontal shift that fits best; a band
  is equal when at most 1% of its pixels differ by more than 16 grey levels.

A capture with every row in its place scores high on the tolerant number. The strict one is
given for comparison with #1527.

## Results

`aurora.json` (Chrome), `aurora-ff.json` (Firefox) and `m74.json` hold every run. "Image / page" is
the image's height over the page's `scrollHeight` after the capture. The baseline is the
published nightly 26.1113.4757 on the same desktop in the morning (#1515), run 1.

### Plasma 6.8.2 (aurora-amd), Chrome for Testing 157

| Page | Driver | End | Image / page px | Placed / skipped | s | Bands strict | Bands tolerant | Baseline (nightly, same desktop) |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| Search | you scroll | `done` | 3,995 / 3,995 | 119 / 0 | 12 | 6/61 | 23/61 | lost_track 891 / 4,220 (Google) |
| Search | auto-scroll | `end_of_content` | 3,951 / 3,951 | 173 / 0 | 11 | 4/60 | 24/60 |  |
| User guide | you scroll | `done` | 3,392 / 3,392 | 94 / 0 | 9 | 51/51 | 51/51 | whole, side bar repeated |
| User guide | auto-scroll | `end_of_content` | 3,392 / 3,392 | 147 / 0 | 11 | 51/51 | 51/51 |  |
| Wikipedia "Linux" | you scroll | `done` | 23,943 / 23,943 | 565 / 0 | 33 | no reference | no reference | lost_track 13,491 / 23,304 |
| Wikipedia "Linux" | auto-scroll | `end_of_content` | 23,304 / 23,304 | 1268 / 0 | 45 | no reference | no reference |  |
| MDN `position` | you scroll | `done` | 18,629 / 18,629 | 475 / 0 | 31 | 249/289 | 249/289 | whole |
| MDN `position` | auto-scroll | `end_of_content` | 18,629 / 18,629 | 899 / 0 | 36 | 249/289 | 249/289 |  |
| GitHub PR 1398 | you scroll | `done` | 44,423 / 44,491 | 1891 / 716 | 221 | 11/694 | 51/694 | lost_track 23,751 / 44,491 |
| GitHub PR 1398 | auto-scroll | `lost_track` | 37,377 / 44,491 | 3523 / 1074 | 605 | 13/584 | 260/584 |  |
| Python `stdtypes` | you scroll | `height_cap` | 60,000 / 110,440 | 1796 / 0 | 79 | 937/938 | 937/938 | height_cap 52,493 |
| Python `stdtypes` | auto-scroll | `height_cap` | 60,000 / 110,440 | 2608 / 0 | 106 | 368/938 | 507/938 |  |
| HN front page | you scroll | `done` | 1,186 / 1,186 | 22 / 0 | 6 | 0/19 | 16/19 | whole |
| HN front page | auto-scroll | `end_of_content` | 1,186 / 1,186 | 22 / 0 | 9 | 0/19 | 16/19 |  |
| HN thread | you scroll | `height_cap` | 60,000 / 86,434 | 1639 / 0 | 68 | 0/938 | 935/938 | lost_track 8,631 and 18,351 |
| HN thread | auto-scroll | `height_cap` | 60,000 / 86,434 | 3160 / 0 | 98 | 0/938 | 935/938 |  |
| Stack Overflow | you scroll | `done` | 53,906 / 54,266 | 1356 / 3 | 76 | 3/840 | 23/840 | lost_track 891 |
| Stack Overflow | auto-scroll | `done` | 53,009 / 53,153 | 1756 / 22 | 77 | 2/827 | 10/827 |  |
| Al Jazeera (cookie banner) | you scroll | `done` | 7,497 / 7,499 | 239 / 324 | 29 | 4/111 | 7/111 | lost_track 5,571 / 7,516 |
| Al Jazeera (cookie banner) | auto-scroll | `lost_track` | 1,083 / 7,497 | 31 / 1599 | 60 | 1/10 | 3/10 |  |

Notes:

- Wikipedia in Chrome: Chrome's full-page picture failed, as in #1527.
- Stack Overflow and GitHub in Chrome: Chrome's picture is laid out differently from the page
  that was scrolled (#1527), so its bands say nothing.
- Search and HN in Chrome: the picture is laid out at 1,920 px and the screen at 1,905, so a
  centred page is 7.5 px off.
- GitHub in Chrome: Chrome lays the long pull request out anew as it comes into view, near
  20,000 px. The tracker is lost there.
  - You scroll: the person scrolls back when the bar says so, and the capture goes on.
  - Auto-scroll: five steps back did not find the page, it handed the page back, and Done after
    15 s left it `lost_track`.
- The Al Jazeera article in Chrome is wrong in both modes (see below).

### Plasma 6.8.2 (aurora-amd), Firefox 160

| Page | Driver | End | Image / page px | Placed / skipped | s | Bands strict | Bands tolerant | Baseline (nightly, same desktop) |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| Search | you scroll | `done` | 2,750 / 2,750 | 36 / 0 | 7 | 42/43 | 43/43 | whole / failed (Bing) |
| Search | auto-scroll | `done` | 949 / 949 | 1 / 0 | 22 | 14/15 | 15/15 |  |
| User guide | you scroll | `done` | 3,393 / 3,393 | 47 / 0 | 9 | 51/51 | 51/51 | whole, side bar repeated |
| User guide | auto-scroll | `end_of_content` | 3,393 / 3,393 | 142 / 0 | 11 | 51/51 | 51/51 |  |
| Wikipedia "Linux" | you scroll | `done` | 24,094 / 24,094 | 404 / 0 | 33 | 375/377 | 377/377 | lost_track 17,779 / 24,094 |
| Wikipedia "Linux" | auto-scroll | `end_of_content` | 24,094 / 24,094 | 1332 / 0 | 48 | 373/377 | 377/377 |  |
| MDN `position` | you scroll | `done` | 18,678 / 18,678 | 265 / 0 | 28 | 288/290 | 290/290 | whole |
| MDN `position` | auto-scroll | `end_of_content` | 18,678 / 18,678 | 911 / 0 | 37 | 287/290 | 289/290 |  |
| GitHub PR 1398 | you scroll | `done` | 46,171 / 46,171 | 897 / 1 | 51 | 720/722 | 722/722 | whole |
| GitHub PR 1398 | auto-scroll | `end_of_content` | 46,171 / 46,171 | 2451 / 0 | 87 | 722/722 | 722/722 |  |
| Python `stdtypes` | you scroll | `height_cap` | 60,000 / 110,214 | 1081 / 0 | 75 | no reference | no reference | height_cap 52,083 |
| Python `stdtypes` | auto-scroll | `height_cap` | 60,000 / 110,214 | 3248 / 0 | 110 | no reference | no reference |  |
| HN front page | you scroll | `done` | 1,288 / 1,288 | 7 / 0 | 6 | 19/20 | 20/20 | whole |
| HN front page | auto-scroll | `end_of_content` | 1,288 / 1,288 | 20 / 0 | 7 | 20/20 | 20/20 |  |
| HN thread | you scroll | `height_cap` | 60,000 / 103,477 | 1020 / 0 | 63 | no reference | no reference | lost_track 4,117 |
| HN thread | auto-scroll | `height_cap` | 60,000 / 103,477 | 3200 / 0 | 104 | no reference | no reference |  |
| Stack Overflow | you scroll | `done` | 53,088 / 53,218 | 865 / 0 | 58 | 81/828 | 129/828 | lost_track 13,095 and 14,215 |
| Stack Overflow | auto-scroll | `end_of_content` | 52,565 / 52,565 | 2688 / 0 | 95 | 808/821 | 816/821 |  |

Notes:

- Search under auto-scroll: Bing answered with its human check, one screen tall. Auto-scroll
  found nothing that scrolls, handed the page back, and Done kept the screen.
- Python and the HN thread: Firefox could not take its own picture of a page over 100,000 px.
- The Al Jazeera article did not load in Firefox through Marionette in three tries (25 s each),
  so it was not captured.
- Stack Overflow, you scroll: the page put an advertisement between two answers after the person
  had passed it. The browser's picture, taken after, has it, and every band below it is
  shifted. Under auto-scroll the page was steady and matches.

### Cinnamon X11 (m74), Firefox 158

| Page | Driver | End | Image / page px | Placed / skipped | s | Bands strict | Bands tolerant |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| User guide | you scroll | `done` | 3,393 / 3,393 | 42 / 0 | 8 | 50/52 | 51/52 |
| User guide | auto-scroll | `end_of_content` | 3,393 / 3,393 | 53 / 0 | 10 | 50/52 | 51/52 |
| Wikipedia "Linux" | you scroll | `done` | 24,117 / 24,117 | 301 / 0 | 35 | 347/377 | 374/377 |
| Wikipedia "Linux" | auto-scroll | `end_of_content` | 24,117 / 24,117 | 411 / 0 | 38 | 345/377 | 375/377 |
| Python `stdtypes` | auto-scroll | `height_cap` | 60,000 / 111,974 | 1066 / 0 | 82 | 151/938 | 937/938 |
| Stack Overflow | you scroll | `done` | 54,105 / 54,136 | 615 / 0 | 75 | 23/843 | 206/843 |
| Stack Overflow | auto-scroll | `done` | 52,565 / 52,565 | 966 / 41 | 88 | 98/820 | 801/820 |

Stack Overflow, you scroll: the same advertisement shift (130 px from 13,300 px, 31 px from 19,700 px;
`lab/drift.py`). The image shows the page as the screen did.

### Frames while scrolling

- Plasma 6.8.2 (KWin's region stream with the heartbeat): 18 to 26 frames a second on long
  pages, 23 at the median. The loop took 98% of the frames the stream delivered (694 of 708 on
  Wikipedia).
- Cinnamon (`ximagesrc`): 28 to 30 frames a second.
- While lost, the tracker takes about a second a frame on a 20,000-row image (its search of the
  whole image).

## Open defects found

- **Chrome under auto-scroll, Python's documentation (dark), Plasma**: 141,277 pure black cells
  (1% of the image) from about 17,000 px down, in the columns right of the text. They are not
  there when the person scrolls, and not in Firefox under auto-scroll on Plasma or on Cinnamon.
  Most likely Chrome's not-yet-drawn tiles while it scrolls fast, taken in by the tracker.
  `shortfall-python-chrome-auto-black-cells.png`.
- **The Al Jazeera article in Chrome** (cookie banner at the bottom, sticky header).
  - You scroll: the capture ends `done` with 324 of 563 frames skipped, and the banner's dark
    band is drawn in strips through the image. `shortfall-news-chrome-you-scroll-banner-strips.png`.
  - Auto-scroll: lost at 1,083 px.
  - The usable band between the header and the banner leaves little evidence, and a blank
    stretch in it leaves none.


## Pictures

`bar-states.png`: every state of the bar (UI catalog, dark).

`guide-chrome-auto.png`, `python-chrome-you-scroll-top.png`, `wiki-firefox-auto-cinnamon-top.png`:
captures beside the browser's own picture.

`shortfall-python-chrome-auto-black-cells.png`, `shortfall-news-chrome-you-scroll-banner-strips.png`:
the open defects above.

`acceptance-checklist.md`: what the acceptance round on GNOME, Hyprland and Budgie checks.
