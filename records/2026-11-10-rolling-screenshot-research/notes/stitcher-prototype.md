# Scrolling-screenshot stitcher: reference prototype

Status, 2026-11-09: built and tested. 77 tests pass, 0 fail, and 5 known limitations are
reported separately (they are not counted as passes). The ASan+UBSan run is clean.
Everything is dependency-free C++20 (standard library only).

## Files

| Path | Lines | What |
| --- | --- | --- |
| `prototype/scroll_stitcher.h` | 178 | `FrameView`, `StitchOptions`, `FrameSignatures`, row rules, `ScrollStitcher` |
| `prototype/scroll_stitcher.cpp` | 707 | signatures, pair rules, fixed bands, offset search, assembly |
| `prototype/scroll_session.h` | 121 | `IScrollInjector`, `IFrameSource`, `IClock`, `SessionOptions`, `ScrollSession` |
| `prototype/scroll_session.cpp` | 231 | settle detection, step planning, recovery, end detection |
| `prototype/synthetic_app.h` | 179 | test-only: document generator, viewport renderer, fake clock/app |
| `prototype/synthetic_app.cpp` | 299 | test-only implementation |
| `prototype/test_main.cpp` | 1008 | test suite, summary table, timing |
| `prototype/build.sh` | 11 | build script (normal and `asan`) |

Only `scroll_stitcher.*` and `scroll_session.*` belong in the product. The `synthetic_*` files
exist only for the tests.

## Build and run (exact commands used)

```sh
cd prototype
./build.sh
#   = nice -n 19 g++ -std=c++20 -O2 -Wall -Wextra scroll_stitcher.cpp scroll_session.cpp \
#       synthetic_app.cpp test_main.cpp -o test_stitcher            (9 s, no warnings)
nice -n 19 ./test_stitcher            # full suite and timing, about 50 s, exit code 0
./build.sh asan
#   = nice -n 19 g++ -std=c++20 -O2 -Wall -Wextra -g -fsanitize=address,undefined \
#       -fno-omit-frame-pointer <same sources> -o test_stitcher_asan   (33 s)
nice -n 19 ./test_stitcher_asan --no-timing   # 2 min 39 s, no sanitizer reports, 74 pass / 0 fail
```

Each build is a single g++ invocation with no parallel jobs. `--no-timing` skips the timing
table. The program prints one line per test and a summary, and exits with code 1 if any test
fails unexpectedly.

## Public API (shape)

```cpp
namespace rollcap {
struct FrameView { const uint8_t* data; int width, height; ptrdiff_t stride; };  // B,G,R,X
struct StitchOptions { /* the suggested fields, unchanged defaults, plus: */
  int edgeThreshold = 48; int flatConflictDelta = 96; int noMoveMaxChangedRows = 2;
  int noMoveMaxStrictRows = -1 /* = max(48, H/10) */; double hintTolerance = 0.25; int hintTolerancePx = 8; };
class FrameSignatures { void compute(const FrameView&, const StitchOptions&); /* per-row data */ };
enum class StepStatus { First, Appended, NoMovement, Reversed, NoMatch, Ambiguous, LimitReached, InvalidFrame };
struct StepResult { StepStatus status; int offset; double score; int appendedRows; int fixedTop, fixedBottom;
                    bool lowConfidence; int evidenceRows; int changedRows; int candidatesEvaluated; };
using RowSink = std::function<void(const uint8_t* bgrxRow, int width)>;  // each final row once, top to bottom
class ScrollStitcher {
  explicit ScrollStitcher(StitchOptions = {}, RowSink sink = {});   // empty sink = internal buffer
  StepResult addFrame(const FrameView&, int hint = kNoHint);
  StepResult addFrame(const FrameView&, const FrameSignatures&, int hint, int hintUncertaintyPx = 0);
  void finish();                       // flushes the first frame (if nothing moved) and the footer
  int outputWidth() const; int outputHeight() const;
  int movingBandTop() const; int movingBandBottom() const; int maxEvidenceStep() const;
  const std::vector<uint8_t>& image() const; std::vector<uint8_t> takeImage();   // internal mode
  size_t memoryBytes() const;
};
// free helpers: sameRowLoose, countChangedRows, countStrictChangedRows, framesDiffer,
//               marginsChanged, classifyRowPair, strictChangeBudget

struct IScrollInjector { virtual bool scrollNotches(int notches) = 0; };   // >0 down, <0 up
struct TimedFrame { FrameView view; int64_t timestampMs; };
struct IFrameSource { virtual std::optional<TimedFrame> nextFrame(int timeoutMs) = 0; };
struct IClock { virtual int64_t nowMs() = 0; virtual void sleepMs(int) = 0; };
enum class SessionResult { EndOfContent, LimitReached, Cancelled, TimeLimit, InjectorFailed,
                           LostTrack, Ambiguous, NoFrames };
class ScrollSession {
  ScrollSession(IScrollInjector&, IFrameSource&, IClock&, SessionOptions = {}, RowSink = {});
  SessionResult run(const std::atomic<bool>* cancel = nullptr);   // always finishes the stitcher
  const SessionStats& stats() const; ScrollStitcher& stitcher();
};
}
```

Changes from the suggested API:
- `Reversed` reports a negative offset; the stitcher keeps tracking instead of failing.
- `InvalidFrame` reports a size change or bad data.
- `addFrame` has an overload that takes precomputed signatures, because the session already
  computes them for settle detection.
- `hintUncertaintyPx` lets the session say how far its hint may be off.
- A `RowSink` streams output rows. A row reaches the sink only when it is final. The first frame
  is held back until the footer is known.
- `StepResult` gains `lowConfidence`, `evidenceRows`, `changedRows` and `candidatesEvaluated`.

`IFrameSource` contract: return the newest frame, newer than the last one returned, or nothing
when `timeoutMs` runs out. The last returned view must stay valid until another frame is
returned. This lets damage-driven streams, which send nothing while the screen is static, work
unchanged.

## Final algorithm as implemented

### Row signatures (`FrameSignatures::compute`)
- **Compared columns:** `[m, W-m)` with `m = round(0.04 W)`, clamped so that at least `bands`
  columns remain.
- **Bands:** the compared columns are split into `bands = 8` equal bands. For each band and row:
  - **exact hash:** FNV-1a over the 24-bit pixels (X byte masked), run as two interleaved lanes
    for speed, finished with fmix64;
  - **flat bit:** set when every pixel in the band has one colour;
  - **edge hash:** a hash of the x positions where `|ΔB+ΔG+ΔR| > edgeThreshold (48)` between
    horizontal neighbours inside the band, with a bit that says whether the band has any edge.
- **Per row:** a combined row hash, a "row flat" flag with its colour (the whole compared row is
  one colour), and a hash of the margin columns (scrollbar).
- **Size:** 157 bytes per row at 8 bands. The general formula is `16·bands + 29`.

### Row rules
- **Same-y "loose" rule** (used for settle, NoMovement and fixed-band runs): two rows are the
  same when the row hashes are equal, or when at most `bands − minBandsEqual = 2` bands differ.
- **Same-y "strict" count:** the number of rows whose row hash differs at all.
- **Frames "unchanged"** (`framesDiffer` is false) when all three hold:
  - the loose rule finds at most `noMoveMaxChangedRows = 2` changed rows;
  - the strict count is at most `max(48, H/10)` rows;
  - no margin row changed (the session uses this test; in the stitcher, a margin change only
    matters together with a hint, see below).

  The strict budget absorbs a caret or spinner on blank rows. The strict test exists because
  content whose ink always sits in ≤ 2 bands (short lines) passes the loose rule while it
  scrolls. When only the strict test sees change, the fixed-band runs use the strict rule too.
- **Pair classification for the offset search,** row `prev[y+d]` against row `cur[y]`
  (`classifyRowPair`):
  - both rows flat: never evidence. If the colours differ by more than `flatConflictDelta = 96`
    (sum of absolute channel differences), the result is `-2`: not scored, but the candidate
    no longer counts as conflict-free. Otherwise `-1`.
  - row hashes equal: **match** (+1).
  - at most 2 bands differ: **match** if at least one *non-flat* band is equal; otherwise **no
    evidence** (−1). This covers a caret or a short line on an otherwise blank row.
  - more than 2 bands differ: edge-structure rule. If at most 2 bands differ in edge hash and an
    equal band has edges, it is a **match**. This tolerates a hover highlight that recolours the
    background, because edge positions survive the tint. If at most 2 bands differ in edge hash
    but no equal band has edges, the result is **no evidence**: a tint plus a caret or spinner on
    a blank row. Everything else is a **conflict** (0).
- **Score:** `matched / (matched + conflicting)` over evidence rows. "Informative rows in the
  overlap" means rows that are evidence for or against a candidate.

### Fixed header/footer
- The stitcher only compares two frames when the second one moved. It counts the run of rows
  that are the same at the same y from the top (`t`) and from the bottom (`b`).
- The estimate is `min(previous estimate, run)` over moving steps. An over-estimate shrinks
  later, and only steps that moved count. NoMovement frames never update the estimates, so an
  unchanged frame is never mistaken for a full-height header.
- **Reclassification at the first movement:** the first frame is kept as a pending copy and
  emitted only at the first movement, as rows `[0, H − footer)`. Its bottom rows become footer,
  not content.
- **Header** = the first frame's top rows. It is a prefix of the body, so a header estimate
  that shrinks needs no fix-up.
- **Footer shrink:** when the footer estimate shrinks, the next append starts where the body
  ended, so content once hidden under an over-estimated footer is supplied from the current
  frame. Both directions of over-estimate are tested.
- **Footer output:** the footer comes from the last reference frame, written at `finish()`.
- **Retry on a wider band:** if the search returns **NoMatch**, it retries once on a band whose
  runs drop their trailing flat rows. This handles blank content that looked "fixed" at the
  first step. The committed estimates stay conservative. The retry does not run after Ambiguous,
  because it could break a genuine tie: a test caught exactly that wrong answer.

### Offset search (`search`)
- **Candidates:** `d ∈ [−(M − minOverlapRows), +(M − minOverlapRows)]`, where `M` is the height
  of the moving band. Positive and negative offsets are searched the same way, and `d = 0` is
  included.
- **Order:** the hint first, then hint ± 1..16, then the rest by |d|.
- **Pruning:** a candidate is abandoned when its conflicts exceed
  `(1 − max(minScore, best − uniquenessMargin)) · overlapRows`. This is a safe bound, because a
  pruned candidate can be neither best nor a rival.
- **Decision cascade:**
  1. **Passing** candidates: evidence ≥ `minOverlapRows (24)` and score ≥ `minScore (0.90)`.
     Best = highest score (ties: more evidence, then nearer the hint). Rivals = passing
     candidates with score ≥ best − 0.05 and |d − best| > 1.
     - No rivals: accept.
     - Rivals and a hint: take `c1`, the top candidate nearest the hint. It must lie within
       `tol = max(8, 0.25·hint)`. Every other top candidate (outside ±1 of `c1`) must be farther
       from the hint than `max(2·dist + 2, dist + 2·hintUncertainty)`. If so, accept the best
       score within `c1 ± 1`, marked `lowConfidence`.
     - Otherwise: **Ambiguous**.
  2. **No passing candidate, no hint:** accept, as `lowConfidence`, a unique conflict-free
     candidate with ≥ 18 matched rows (¾ of 24), provided no other conflict-free candidate
     outside ±1 has any matched row. Otherwise **Ambiguous** if any candidate is conflict-free,
     else **NoMatch**.
  3. **No passing candidate, hint given:**
     - Partial evidence: take the conflict-free candidate with ≥ 12 matched rows nearest the
       hint, if it is within `tol` and has no competitor.
     - Otherwise a **blind step**: take the conflict-free candidate within `tol` of the hint,
       preferring candidates with any match, then the nearest. It is accepted as
       `lowConfidence` with `evidenceRows == 0`.
     - If neither exists: **Ambiguous** if any candidate is conflict-free, else **NoMatch**.
- **Outcomes:**
  - `d = 0`: **NoMovement**. This is an in-place change; the reference is refreshed.
  - `d < 0`: **Reversed**. The reference moves back. Rows already emitted below it are
    remembered, so later steps append only new rows. The bounce test checks this.
  - `d > 0`: **Appended**.
- **Scrollbar cue:** if two frames are "unchanged" but the margin (scrollbar) changed and a hint
  is given, the hint is tested against the pixels. This makes a blank region taller than the
  viewport work when the scrollbar is inside the region.

### Append
- Each step appends the current frame's rows `[body − curOrigin, H − footer)`. Normally these
  are exactly the `d` new rows; more rows are appended when the footer estimate shrank, and
  fewer (or none) after a Reversed step.
- A candidate that would leave a gap returns NoMatch.
- `maxOutputRows` counts header + body + current footer. The append is truncated at the limit
  and the step returns `LimitReached`; every later step also returns it.
- NoMatch and Ambiguous never touch the output or the reference.

### Session (`ScrollSession::run`)
1. **First frame:** wait for a settled frame, then call `addFrame` with no hint.
2. **Settle:**
   - **Rule:** the frame has *settled* when no frame differed from its predecessor for
     `settleMs = 120` after the injection.
   - **"Differed":** decided by `framesDiffer` over the current moving band, with at most 2
     loose-rule rows changed allowed. A caret, a spinner, or a hover confined to ≤ 2 of 8 bands
     never keeps a frame "moving", and a scrollbar movement always does.
   - **Timeout:** the hard limit is `stepTimeoutMs = 1500`. After a timeout the latest frame is
     used anyway.
   - **No frames:** a stream that delivers nothing while static counts as settled.
3. **Step planning:**
   - The first step is 1 notch; it measures px-per-notch.
   - **Notch count:** `round(0.60·band / pxPerNotch)`, reduced until it is at most `0.75·band`,
     and always ≥ 1.
   - **Evidence limit:** the step is also capped by `maxEvidenceStep()`, the largest step that
     keeps ≥ 36 rows of the reference frame that have ink in > 2 bands inside the overlap (or
     ≥ 12 such rows when the frame has fewer). Without this cap, a frame whose lower part is
     blank forces a blind step, and the hint is then wrong when the step hits the end of the
     document. The constant-px sweep found that case.
   - **Blind steps:** a step with no evidence is limited to 1 notch when the measured
     px-per-notch range exceeds 3 %.
   - **Re-measuring:** px-per-notch is re-measured from every verified (not `lowConfidence`)
     step whose offset is ≥ 0.7 × hint. A smaller offset is a final partial step and keeps the
     old value.
4. **Hint:** `round(pxPerNotch · notches)`. The uncertainty is `notches · (max − min measured
   px-per-notch)`.
5. **End detection:** `NoMovement` after an injection sets "end pending". The session waits
   `endConfirmDelayMs = 400` and injects the same notch count again. A second NoMovement means
   `EndOfContent`. Movement instead is counted as a false end; this covers a dropped event or a
   lazy load.
6. **NoMatch or Ambiguous:**
   - (a) Re-settle and retry the newest frame against the reference without injecting. This
     covers a frame that was not final yet.
   - (b) If `allowScrollBack` (the default) is set, inject `−notches`, settle, and match against
     the reference with hint 0. This must give NoMovement, Appended or Reversed. Then halve the
     notch cap. The cap doubles again after 3 verified steps.
   - (c) If a single notch fails twice: `LostTrack` ("enlarge the region").
   - An Ambiguous first step with no hint: `Ambiguous`.
7. **Stops:**
   - end of content;
   - `maxOutputRows` (`LimitReached`);
   - the external cancel flag;
   - `totalTimeLimitMs = 180000`;
   - injector failure (`scrollNotches` returns false);
   - `LostTrack`.

   Every exit calls `finish()`. The partial image is always a gap-free exact prefix plus the
   footer, as the cancel, time-limit, injector-failure and LostTrack tests check.

**Recovery without scrolling back up:** the only possible recovery is step 6(a). It helps when
the failure was transient, for example a late repaint, a frame taken before the animation ended,
or a short-lived overlay. A jump past the overlap cannot be reconnected by scrolling further
down: every later frame is even further from the last stitched frame, so continuing would
create a gap. With `allowScrollBack = false` the session therefore stops with `LostTrack` and
keeps the exact prefix. The test "accelerating app, scroll-back disabled" shows this.

### Defaults: what changed from the suggestions and why
- **`StitchOptions` values:** all the suggested numbers are unchanged: 0.04, 8, 6, 24, 0.90,
  0.05 and 32000. The *rules* around them changed:
  1. **Match rule:** the suggested rule was "≥ 6 of 8 bands equal". Alone it matches a blank row
     with a short line, so the rule also requires an equal **non-flat** band. When no non-flat
     band is equal, a small difference counts as *no evidence* rather than a conflict. Without
     that, a caret or spinner on a blank row costs 2 × its height in conflicts at the true
     offset.
  2. **Edge-structure rule:** a hover highlight recolours the whole row, so every band hash
     changes. At 60 % steps on a 300-row viewport it dropped the true score below 0.9. Edge
     positions survive the tint, so the edge rule rescues those rows.
  3. **Score scope:** flat rows never enter the score, as suggested. Clearly different flat
     colours still remove a candidate from the conflict-free set. When this conflict was scored,
     a header's flat rows aligning with table borders turned a periodic tie into a false
     "unique" answer. That was the only wrong *verified* step ever observed, and the fix was
     regression-tested.
  4. **NoMovement:** NoMovement needs both the loose and the strict rule (see Row rules).
  5. **Hint uncertainty:** the hint tie-break takes the hint's uncertainty into account. With
     ±10 % px-per-notch jitter, a 465 px hint was 23 px off inside a 24 px-period table.
  6. **Partial-evidence and blind-hint rules:** these are new. A flat block or blank region
     taller than the overlap is required by the test document and otherwise never matches.
- **Session constants:** `settleMs` is 120 as suggested. `endConfirmDelayMs` (400) is new. The
  0.60 and 0.75 step fractions are as suggested.

## Tests (all from one run; PASS unless marked)

**Stitcher**, document width 480, hint = true offset unless stated otherwise:

| Test | Result |
| --- | --- |
| Exact reconstruction, viewports 300/800/1400 × step patterns 15 %, 60 %, 90 %, random 10–85 %, all ending with a clamped partial final step, 10 seeds each (12 rows, 120 runs) | PASS, all exact |
| Exact reconstruction **without hint**, text/noise/gradient document, 300/800/1400 × 15 %/60 %, 5 seeds (6 rows) | PASS, 0 Ambiguous or NoMatch |
| Sticky header only / footer only / both (40/30 px), viewports 300 and 800, 3 seeds (6 rows) | PASS, exact; final `fixedTop`/`fixedBottom` equal the truth |
| Header over-estimated at frame 2 (step 1 gave 90, truth 40) | PASS, final 40, exact |
| Footer over-estimated at frame 2 (step 1 gave 71, truth 30) | PASS, final 30, exact |
| Hover + caret + animated block + scrollbar + header + footer, viewports 300/800 × 60 %/random, 3 seeds (4 rows) | PASS, exact outside the noise pixels; the noise is present in the output |
| Periodic table: exact hint → 100; hint off by 3 → 100; no hint → Ambiguous, output untouched; hint midway between periods → Ambiguous | PASS (4 rows) |
| Blank overlap: hint → 90 (partial evidence 11 rows); no hint → Ambiguous, untouched | PASS (2 rows) |
| Flat block taller than the overlap: hint → 200; no hint → Ambiguous | PASS (2 rows) |
| No overlap (step 320 > band 300), 12 positions, with and without hint | PASS, 24/24 NoMatch, output untouched |
| End of document (same frame, caret and spinner animating) | PASS, NoMovement |
| Bounce: 0 → 150 → 120 (Reversed −30) → 270 (appends 120) → 420 | PASS, exact |
| Negative offset in the middle of the document | PASS, Reversed −80 |
| `maxOutputRows = 1000` with header and footer | PASS, height 1000, prefix + footer exact |
| Small in-place change (10 rows) | PASS, NoMovement |
| Large in-place change (140 rows) | **KNOWN-LIMIT**, NoMatch: never appends, but cannot continue |
| Blank taller than the viewport, scrollbar inside the region, hint | PASS, every step appended at the hint |
| Blank taller than the viewport, no scrollbar | **KNOWN-LIMIT**, NoMovement |
| Short lines only (all ink in ≤ 2 bands) | PASS, Appended 120 (needs the strict rule) |
| Signature memory | PASS, 157 B/row |

**Session** (fake app: smooth ease-out animation 150–350 ms, 20 fps capture, 16 ms reaction,
clamps at the end):

| Test | Result |
| --- | --- |
| 40, 53, 100 and 120 px/notch × viewports 300 and 800 (8 rows) | PASS, EndOfContent, exact |
| Header + footer + all noise, 53 px; noise at viewport 300 | PASS |
| Dropped 3rd injection; dropped first injection | PASS (one false end each, confirmed) |
| Lazy load at 60 % of the document, 250 ms after reaching the end | PASS, full document |
| Lazy load slower (2000 ms) than the confirm delay | **KNOWN-LIMIT**, ends at the lazy boundary with an exact prefix |
| Elastic bounce at the end (overshoot frames seen) | PASS, overshoot never stitched |
| Damage-only frame stream | PASS |
| Slow animation 400–700 ms | PASS |
| Accelerating app (×2.5 for bursts of ≥ 3 notches) | PASS, recovered by 1 scroll-back |
| Accelerating app with scroll-back disabled | PASS, LostTrack, exact prefix |
| One notch larger than the overlap (290 px on 300) | PASS, LostTrack with message |
| Cancel; 3 s time limit; injector failure | PASS, exact prefix each |
| `maxOutputRows = 2500` | PASS, height 2500 |
| Blank taller than the viewport, scrollbar | PASS, exact |
| Blank taller than the viewport, no scrollbar | **KNOWN-LIMIT**, wrong after a false end |
| Document shorter than the viewport | PASS, EndOfContent, 1 frame |
| **Sweep, constant px/notch:** 16 seeds × 4 px values × 2 viewports, widths 480/640/1024, random header, footer, noise, drop, elastic and damage-only (128 runs) | PASS, 128/128 exact; 0 wrong steps of any kind |
| **Sweep, ±10 % random px/notch per injection** (64 runs) | **KNOWN-LIMIT**: 42 exact; 21 inexact *only* through blind steps; 1 stopped early (LostTrack) with an exact prefix; 0 wrong verified steps, 0 wrong partial-evidence steps, 28 wrong blind steps |

The session sweep checks every stitch attempt against ground truth and sorts wrong offsets by
confidence: verified, partial evidence or blind. Any wrong *verified* step fails the test.

## Timing

Intel i9-9880H at 2.3 GHz, single thread, `nice 19`, shared workstation with load average
about 6, so numbers vary by about 20 % between runs. Each value is the median of 7 runs. The
steps are 60 % of the frame on a text, noise and gradient document.

| Region | Signatures per frame | Search + append, with hint | Search + append, no hint | Frame size |
| --- | --- | --- | --- | --- |
| 1280×800 | 2.3–3.2 ms | 0.9–1.0 ms | 1.7–1.8 ms | 3.9 MB |
| 1920×1080 | 4.6–5.6 ms | 1.8 ms | 3.1–3.2 ms | 7.9 MB |
| 3840×2160 | 18–22 ms | 6.7–8.2 ms | 12.3–14.2 ms | 31.6 MB |

Worst case for the search, where sparse text means almost no candidate is pruned: 6.8–7.5 ms
at 1920×1080 and 30–32 ms at 3840×2160.

"Search + append" covers the same-y comparisons, the fixed-band runs, the offset search and the
row copy. The session also computes signatures for **every** captured frame for settle
detection. At 4K and 30 fps that is about 60 % of one core. See the porting notes.

## Peak memory

For a W × H region, N output rows, footer F rows and 8 bands:
- **Stitcher signatures:** 157·H bytes for the reference. The `FrameView`-only `addFrame`
  overload adds another 157·H temporarily.
- **Pending first frame:** 4·W·H, kept until the first movement and then freed.
- **Footer copy:** 4·W·F.
- **Search scratch:** about 50·H bytes (four int arrays and one byte array over 2·H
  candidates).
- **Output:** 4·W·N in internal mode. The `std::vector` can transiently double while it grows;
  call reserve or use a sink. With a `RowSink` the stitcher keeps no output.
- **Session:** two more signature sets, 2 × 157·H.

Example, 3840×2160 at N = 32000: about 33 MB pending + 1.4 MB signatures (stitcher and session)
+ 154 KB per 10 footer rows, plus a 491 MB output in internal mode, or only about 35 MB when
streaming to a sink.
The caller's own frame buffers are extra.

## Known limitations and suggested handling

1. **Featureless regions taller than the overlap** (blank space, flat colour blocks) can only be
   crossed by trusting the hint (a blind step). The output is exact when px-per-notch is
   constant, as the 128-run sweep shows. With ±10 % jitter, a third of the runs had a flat or
   blank region a few pixels too tall or too short. Text and other informative content is never
   wrong (0 wrong verified steps).

   Handling: evidence-aware planning, 1-notch blind steps when px-per-notch varies, and the
   scrollbar cue. Report `lowConfidenceSteps` to the UI, and consider reading the scrollbar
   thumb position as a second measurement.
2. **A blank region, or a viewport-filling periodic region scrolled by a multiple of its
   period, without a scrollbar in the region:** consecutive frames are identical, so the session
   sees NoMovement. It either ends early, or confirms, moves on, and then mis-sizes the blank.

   Handling: tell users to include the scrollbar in the selection, because margin changes
   count as movement. Optionally use a longer, multi-notch end confirmation.
3. **Periodic content with an uncertain hint** gives Ambiguous. The session recovers by scrolling
   back and halving. If the scroll-back itself is ambiguous (periodic content plus jitter),
   it stops with LostTrack and an exact prefix (1/64 jitter runs).
4. **Large in-place content changes while visible** (placeholders replaced by images, video, or
   animations wider than 2 bands) give NoMatch and eventually LostTrack. The output is never
   wrong.

   Handling: re-settle longer. The stitcher could also learn "volatile rows" (rows that change
   between settled frames at the same y) and exclude them from scoring.
5. **Lazy load slower than `endConfirmDelayMs` (400 ms)** ends early with an exact prefix.

   Handling: make the delay configurable, or offer "continue capture".
6. **Fixed-position noise wider than 2 of 8 bands** (a wide animated banner) costs score and can
   stop settling, which then falls back to `stepTimeoutMs`. A hover that changes text colour or
   weight, or adds wide borders, is not covered by the edge rule.
7. **Under-estimated footer:** if the footer changes in more than 2 bands between frames, its
   rows become part of the moving band and are appended repeatedly. This is not tested.

   Handling: never let a later step's bottom run end *below* the committed footer, or detect
   repeated blocks at the end of the body.
8. **Fractional scaling and resampled frames:** the design assumes content moves by whole
   pixels and rows repeat bit-exactly. On outputs where the compositor resamples (GNOME/KDE
   fractional scaling, or scaled capture), rows will not hash equal. This is untested and the
   most important thing to check on real hardware. If it fails, the hashes need to be quantised
   or tolerant, for example luminance quantised to 4 bits.
9. **The edge rule can match rows that differ only in colour** (identical glyph shapes, for
   example a syntax-highlight change). This is rare, and the score threshold still applies.
10. **Short-lived 1 px movements spaced more than 120 ms apart** can make settle fire early.
    The stitch stays correct, because it is pixel-based; only the hint and px-per-notch suffer.
11. **Only vertical scrolling and same-size frames:** a size change returns `InvalidFrame`. The
    image includes the margin columns from whichever frame emitted each row, so scrollbar
    fragments appear in the output; crop or repaint the margins if that matters.

## Porting to Qt 6

- **Frames:** use `QImage::Format_RGB32` (or `ARGB32`/`ARGB32_Premultiplied`, whose byte 3 is
  masked out) and map it directly:
  `FrameView{img.constBits(), img.width(), img.height(), img.bytesPerLine()}`.
  `Format_RGBX8888` also works on little-endian, because the hash ignores channel order and the
  edge test sums R+G+B.
- **Frame lifetime:** the `IFrameSource` adapter should keep the last returned `QImage` alive
  (an implicitly shared copy is enough), because the session may use it after a timeout. Feed it
  from the PipeWire thread through a latest-frame mailbox (a mutex and a condition variable;
  `nextFrame(timeout)` waits on it).
- **Threading:** run `ScrollSession::run()` on a worker `QThread`. `IClock` maps to
  `QElapsedTimer` plus `QThread::msleep`. Cancel through a `std::atomic<bool>` that the UI sets.
- **Streaming output:** pass a `RowSink` that writes into a pre-allocated `QImage` of width W and
  height `maxOutputRows`, keeping a row counter (`memcpy` to `scanLine(n++)`), then `copy()` the
  used height at the end. For very large captures, sink into tiles or a temporary file. The rows
  arrive in final order: the header first and the footer last (from `finish()`). No row is ever
  revised.
- **CPU cost:**
  - Compute signatures once per captured frame and pass them to
    `addFrame(view, sig, hint, unc)`, as the session does.
  - At 4K, consider running the settle check on every second frame, or on a subset of rows
    (the signature code is per row, so a row stride is a small change).
  - Keep the offset search on the worker thread: 7–14 ms typical, about 32 ms worst case.
- **Injection:** wheel notches through the RemoteDesktop portal (`NotifyPointerAxisDiscrete`),
  libei, or XTest buttons 4/5. The pointer must stay over the content. Parking it close to the
  scrollbar column avoids most hover effects, which helps even though hover is tolerated.
- **Diagnostics:** `SessionOptions::onStep` receives every stitch attempt with its hint and
  notch count; log it. `SessionStats` has steps, notches, the px-per-notch range, retries,
  scroll-backs, halvings, false ends, low-confidence steps and settle timeouts.
- **UI:** show `lowConfidenceSteps > 0` as "parts of the image could not be verified" (only
  blank or flat regions are affected), and map `LostTrack`, `Ambiguous` and the other results
  to messages. `stats().lastError` already holds one.
