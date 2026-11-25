# Auto-scroll pacing after a missed first measurement (#2000, PR #2020)

The question: after its first step settled without measuring how far a notch moves the page, does auto-scroll get a measurement later, instead of staying at one notch a step for the whole capture?

## Builds

- Before: put.gd nightly 26.1124.6905, commit 97110f6335c3, git tree eadbbdc70f2b. Its session code is the same as nightly fe463abed.
- After: PR #2020 at head 8ad80f463439. That is the package `putgd-26.1125.6942~dev+g8ad80f463439-1.fc44.x86_64.rpm` from CI run 45534392428, git tree 08b683739f4e.
- 6150e8ad6 adds only a stricter assertion to the session test.

The live runs used the unpacked RPMs' `putgd-record`. The lab driver `test_scroll_capture_driver` was built from a blobless clone at the same commit, and its build-info.json is byte-identical to the package's (`harness/unpack.sh`, `harness/capture.sh`).

## 1. Session test: Sol's d69 case (`1-session-steps-before-after.png`)

The setup is a synthetic damage-only stream at 40 px a notch, with a 3.5 s stall after the first step's first moving frame. It was built on d69 with `harness/steps.cpp`, against the session sources of each build.

| Build | Steps | px/notch | Time | Image |
| --- | --- | --- | --- | --- |
| nightly | 78 | 0 (never measured) | 32.3 s | 3,342 rows, exact |
| PR | 25 | 40 | 19.2 s | 3,342 rows, exact |
| either, no stall | 24 | 40 | 9.5 s | exact |

The new `testMeasureAfterAnUnmeasuredStep` fails on nightly and passes on the PR. The whole session test passes 75 of 75 at 6150e8ad6.

## 2. Live: f44, Fedora 44, GNOME Shell 50.6 Wayland (`2-live-f44-gnome-firefox.png`)

Setup:
- Physical f44 session, shown on the display wall.
- putgd@put.gd and AppIndicator extensions enabled (`live/nfr/extensions.txt`).
- Desktop lock and quiet lease held throughout.
- Firefox 158.0.1 with `mousewheel.default.delta_multiplier_y` 35 (about 23 to 40 px a notch). At Firefox's default of 132 to 198 px a notch, every step is 1 to 2 notches on this 963-row region, measured or not.

Pages:
- `harness/creep.html`: a page that moves 1 px on every animation frame for 3.5 s after the first wheel notch. This forces the first step to run out of time unmeasured.
- en.wikipedia.org/wiki/Linux.

| Page | Build | Steps | Measured at progress event | End | Image |
| --- | --- | --- | --- | --- | --- |
| creep | nightly | 94 | 41 | end_of_content, 48.2 s | 24,994 rows = page |
| creep | PR | 96 | 42 | end_of_content, 49.2 s | 24,994 rows = page |
| Wikipedia | nightly | 85 | 8 | end_of_content, 43.0 s | 24,094 rows = page |
| Wikipedia | PR | 101 | 9 | end_of_content, 50.0 s | 24,094 rows = page |

### Result

No regression. The live run does not reproduce #2000 on GNOME with Firefox.

GNOME's area stream sends only changes, but Firefox keeps sending a few unchanged frames after the page stops. Those frames prove the page at rest, so nightly measures on the step after the creep, the same as the PR.

The first creep version moved 2 px every 50 ms, and those still frames let nightly measure too. Its runs are kept on the host only.

The PR asked for one more fresh frame on the creep page than nightly (4 against 3). That is the new request, on the step after the unmeasured one.

On Wikipedia, both builds took one fresh frame, at the start. The changed code path did not run once the step size was known. The difference in steps comes from the measured px/notch drifting with Firefox's wheel acceleration: 23 to 31 on nightly, 23 to 39 on the PR.

The stuck case needs a stream that goes silent right after the last moving frame, as Xvfb grabs and the session test's stream do.

## Files

- `live/{nfr,pfr}/runs/firefox-{creep,wiki}-auto/`: `result.json`, `driver.log`, `helper.log`. The `nfr` runs are nightly, the `pfr` runs are the PR.
- `harness/`: the f44 port of the #1999 aurora harness (`sess.py`, `live7.py` with GNOME session environment, a measured viewport rectangle and `LAB_FF_WHEEL`), the creep page, the step probe and the chart script.
