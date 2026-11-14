# Scrolling capture gives the pointer back (#1514)

Evidence for [PR #1520](https://github.com/patrick-hudson/put.gd-desktop/pull/1520), part of
[#1514](https://github.com/patrick-hudson/put.gd-desktop/issues/1514). Recorded 2026-11-14.

## What was tested, where, on which build

- **Before:** the published nightly AppImage `v26.1113.4757-nightly` (extracted, so that KWin's
  desktop entry could name its `putgd-record`).
- **After:** a dev build of the PR head `4630ddcb0` (k72: built on k72; m74: built on m74 with
  its Qt 6.4.2). The k72 row "first commit 552cc0d, no watch" is the PR's first commit, before the
  watch layer was added.
- **Hosts:** k72, Kubuntu 26.04, Plasma 6.6.6 Wayland, one 1920×1080 output at scale 1; m74,
  Linux Mint 22.3, Cinnamon X11, one 1920×1080 output. One desktop lock at a time.
- **Page:** Firefox in kiosk mode on `https://en.wikipedia.org/wiki/Linux`, opened afresh before
  every try. Region `470,200,980,720`. Scroll to the top first on (the default). Local save only, in
  a lab directory; nothing uploaded. Each resident ran with its own config, data and cache.
- **The try** (`tools/trial.py`): start a capture through `putgd-cli scroll.prepare` and
  `scroll.start`; 2 s later (random start: 2 to 6 s) move a second pointer from the middle of the
  screen to the bar's Stop at 600 px/s, one event every 10 ms, and click. Two input paths:
  - **VNC**: pointer events through the builder's wall VNC server on its loopback port
    (w0vncserver on k72, X0tigervnc on m74). Every event is an absolute position.
  - **uinput**: a relative mouse made through `/dev/uinput` (`tools/umouse.py`, flat pointer
    acceleration), after one VNC event that puts the pointer in the middle of the screen. This is
    what a real mouse does: it moves from wherever the pointer is.
- **Read from the helper's debug log** (`PUTGD_RECORD_DEBUG_LOG`): the time of `scroll: paused by
  pointer` against the first motion (both on the monotonic clock), and every `scroll inject ...
  pointer ... sent` after the first motion. "First click stopped it": the session ended `done` with
  `endReason: stopped` within 8 s of the click.

The nightly's first click "works" with VNC only because every VNC event puts the pointer back at
an absolute position; put.gd still moved it 4 to 8 times. With a relative mouse, as a person has,
the nightly pulled the pointer back and the click landed on the page (0 of 10 on both hosts).

With random start times 2 of 10 relative tries of the first commit on k72 began while the pointer
was inside the page for a wheel step: nothing of the helper's saw that motion on Wayland, the
pointer was put back on its rest once, and the click missed. The PR's second commit adds the
watch (a clear layer surface over the output with holes only at the wheel points), and the k72
"this PR" rows are with it.

## The 10-try tables

### k72 (Plasma 6.6.6 Wayland)

| Build | Input | First click stopped it | Paused after the first motion (ms) | put.gd pointer moves after the first motion |
| --- | --- | --- | --- | --- |
| v26.1113.4757-nightly | VNC | 10 of 10 | never | 4, 4, 4, 4, 4, 4, 4, 4, 4, 4 |
| v26.1113.4757-nightly | uinput | 0 of 10 | never | 13, 63, 13, 64, 13, 64, 64, 64, 64, 13 |
| first commit 552cc0d, no watch | uinput, random start | 8 of 10 | 3 to 38 (median 12) | 0, 0, 0, 0, 1, 0, 0, 0, 1, 0 |
| this PR | VNC | 10 of 10 | 1 to 15 (median 11) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| this PR | uinput | 10 of 10 | 1 to 15 (median 7) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| this PR | uinput, random start | 10 of 10 | 1 to 16 (median 12) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |

### m74 (Cinnamon X11)

| Build | Input | First click stopped it | Paused after the first motion (ms) | put.gd pointer moves after the first motion |
| --- | --- | --- | --- | --- |
| v26.1113.4757-nightly | VNC | 10 of 10 | never | 6, 6, 6, 6, 6, 6, 6, 8, 8, 6 |
| v26.1113.4757-nightly | uinput | 0 of 10 | never | 35, 81, 18, 18, 18, 78, 18, 18, 18, 78 |
| this PR | VNC | 10 of 10 | 0 to 12 (median 2) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| this PR | uinput | 10 of 10 | 0 to 14 (median 5) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |
| this PR | uinput, random start | 10 of 10 | 0 to 20 (median 5) | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 |

"Never" in the nightly rows: the nightly has no pause. Its moves count every pointer motion it
sent from the first motion until the session ended: with uinput the click missed Stop, so the
capture ran on until the driver stopped it through `scroll.stop` (or a click on the page ended it
`lost_track`). A pause time under 1 ms is a leave event that the helper saw before the driver's
own clock read finished. The raw rows are in `tries/`.

## Hand checks (both hosts, PR head build)

| Check | k72 | m74 |
| --- | --- | --- |
| A static page (`tools/page.html`) captured without a pause, then again paused by the mouse halfway (`pausedBy: pointer`) and resumed with the bar's Resume: same PNG | same SHA-256 `213ac2c7…`, 6,792 px, `end_of_content` both times | same SHA-256 `213ac2c7…`, 6,792 px, `end_of_content` both times |
| The page at its end; the mouse moves to Stop and clicks while the capture scrolls to the top | paused by the pointer, then `stopped`, 720 px (the viewport), `topReached: false` | the same |
| A region that fills most of the screen (`700,30,1200,1030`, one 1920×1080 output) | the bar beside it, at its left, level with its bottom; the pointer rests on it | (not run) |

The nightly's `placeBar` tried only below and above the region, then other screens: with one
screen it hides the bar for that region. The two-monitor case is the unit test
`scrollBarStaysBesideALargeRegion` (`tests/unit/test_bar_placement.cpp`).

## Pictures

- `before-k72-nightly-bar.png`, `before-m74-nightly-bar.png`: the nightly during a capture; the
  pointer is held outside the region between wheel steps and the bar says nothing about the mouse.
- `after-k72-capturing.png`: "Move the mouse to pause" while capturing; the pointer rests on the bar.
- `after-k72-paused.png`, `after-m74-paused.png`: after the user moved the mouse; the user's
  pointer stays where they put it.
- `after-bar-states.png`: the bar's states from the UI catalog; Stop has one place in all of them.
- `after-k72-bar-beside-large-region.png`: the bar beside a region that fills most of the screen.

## Automated tests (k72, PR head)

`scroll_stitcher_contract` (pause and resume against the synthetic application: nothing sent
while paused in 24 pause points on the way down and to the top, the same image as unpaused; a
page moved while paused, placed and not placed; Stop while paused; a pause at its limit),
`scroll_service_integration` (paused state and reason in `scroll.inspect`, `scroll.pause`,
`scroll.resume`, Stop and Cancel while paused), `scroll_capture_x11` (another X client moves the
pointer during a capture on Xvfb: paused, no injected event for a second, the pointer left where
it was moved, Resume goes on), `bar_placement_contract`: all passed.

## Tools

`tools/` holds the drivers as run: `trial.py` and `tries.sh` (the tries), `umouse.py` (the uinput
mouse, run with `sudo -n`), `checks.py` (the hand checks), `rfbshot.py` and `pauseshot.py`
(framebuffer pictures through the VNC server), `resident.sh` and `mkconfig.py` (a resident with
its own local-only configuration), `annotate.py` (the call-outs), `tables.py` (these tables) and
`page.html`.
