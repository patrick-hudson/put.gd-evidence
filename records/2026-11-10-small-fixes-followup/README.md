# Small fixes: paint cost and native Cinnamon follow-up

PR1378 final head8bd8ab3a6b57b5bc21953d0033094f1731306dbb adds a sanitized
visible-source cache. PR1380 remains04ee694dd2523652c06cc8f78560f1bd92e81981.
Baseline nightly cdac6e4b3174b59e0292b2a16af9abdd110e7514. All builds/tests
on builders; no workstation builds/tests. No package run was started.

## Paint measurements

See paint-table.md and three raw CSV files: f44, Fedora44, GCC16.2.1,
distro Qt6.11.2, dev/Debug builds, offscreen1200x800 canvas at Fit.
3840x2160=8.29MP and6000x4000=24MP. Small mask600x50 at100,100; large mask
has100-pixel border.20 warmups and300 samples per row, no trimmed outliers.
A scratch-only subclass wraps EditorCanvas::paintEvent with QElapsedTimer;
removing the class's final declaration permits that instrumentation, with no
paint-body change. QWidget::render setup is excluded. Header final was restored
before building the final-head native picture. Shared-builder wall times include
scheduler outliers (40ms on the cached no-mask row); every maximum is retained.

Original PR's24MP small mask mean84.90ms versus nightly8.71ms confirms the
coordinator's concern. Cached mean8.89ms; the large-mask cached mean9.80ms
versus nightly8.92ms. Cache means add less than1ms across all rows. The old
per-paint allocation/copy/free is removed, not merely shifted inside the timer.

One sanitized source-window cache:4 bytes per source pixel,33,177,600 bytes
at full4K or96,000,000 at full24MP, plus geometry keys. The existing effect-tile
cache has its separate64MiB bound. Keys are source area, crop and intersecting
redaction rectangles. Unrelated annotation edits reuse it. Mask/crop changes
(including undo/removal) release stale data immediately; area changes replace
on next paint. No intersecting mask, hide and destruction release it. Previous
raster is released before replacement allocation. Cold invalidation still incurs
a copy once; warm repaint measurements do not claim to remove that cold cost.
Original fractional property test remains unchanged. New test compares reused
and fresh canvases across mask, crop, zoom, removal, undo and hide/show. Full
editor_contract and gui_editor_window PASS17.39s on f44; CI42742245790 green
at the exact final head. New CodeRabbit body read, no outside-diff findings or
threads; its generic docstring warning is unchanged from the prior review.

Final-head a-cached-head-final.png: actual EditorWindow on Aurora native
Plasma/Wayland Qt6.11.2, exact f44-built cache-head binary, Fit77%. Driver is
identical to the prior record's pg-pictures-round.cpp; only source/label changes.
Production editor renderer adds labels/arrows. Aurora visibly idle before/after,
lease02:35:51-02:36:18UTC, clean receipt retained. Temporary copied binary and
private XDG directories removed. This refresh supersedes the earlier after image.

## m74 native X11/Qt6.4.2

m74 Mint22.3, Cinnamon6.6.4, physical X11 :0, native wall5974. Source branch
built under /home/patrick/work/pg1380 using its own dev preset and the official
SDK1.11.924 from i1361's existing prefix. Helper, resident, CLI and test source
are from PR1380. For the baseline, only src/capture/main.cpp is restored from
nightly and helper rebuilt; that is the entire branch diff. The resident source
is identical on both branches. Exported scratch builds have unknown development
version; committed-source identities here and SHA256s in pg1380-binaries.txt
identify the tested executables. No installed package was changed.

capture_preparation_x11 PASS7.93s, unchanged strict test. Physical functional
run m14/fixed: real Ctrl+Shift+F12 shortcut maps selector; drag400,300 to800,550
creates one400x250 synthetic PNG in private local output; Escape cancels without
another output file. Saved selector/drag frames and exported synthetic PNG are
retained. Private profiles contain no remote destination/credentials.

Own helper PID3909215: xprop and xwininfo show the160x160 warm-up XID0x4c00006
IsUnMapped. The1x1 mapped Qt child is intentionally embedded in the native
selector (NativeRegionOverlay), not an extra top-level warm-up surface.
The first normal-cursor attempt m13 had a valid static seed and skipped warm-up
altogether; our overly strict expectation of an unmapped window was wrong.
XCURSOR_RESIZED=1, scoped to the test processes, exercises the actual changed
fallback/warm-up path for functional and timing checks without changing desktop
settings. Original attempt/window inventory and failure console are retained.

Timing uses a mapping-only observer derived from tests/performance/bench_capture.cpp,
with the original exact child PID/start/device/inode and override-redirect
ownership checks. CLOCK_BOOTTIME plus the existing helper /proc startTicks
provides a kernel-start-to-map estimate with10ms quantization. No paint or
compositor-presentation timing is claimed. The original white-pixel paint witness
could not recognize the current outline; its failed run is preserved (m14).
Initial mapping-only trials (m15/m16) sent Escape at MapNotify before the
keyboard grab, leaving a selector active; the next hotkey was rejected busy.
The final observer repeats Escape until that exact helper PID/start exits before
the next trial. Timing ends at mapping, so the cancellation fix does not shorten
measured startup. Original failures and logs are retained, not counted as passes.

m17/m18: two opposite-order batches,5 warmups then30 measured starts/build/batch,
60 measured starts per build. All60 complete and cancel on each build:

| Metric, milliseconds | Nightly mean / worst | Fixed mean / worst |
| --- | ---: | ---: |
| Hotkey to validated map |74.21 /134.67|80.20 /140.65|
| Helper kernel start to observed map, upper estimate |70.66 /127.85|75.69 /134.18|

Per-trial actual helper latency is approximately within [upper-10,upper]ms;
mean intervals overlap: nightly60.66-70.66ms, fixed65.69-75.69ms. Observed
upper-estimate mean is5.03ms higher. This does NOT establish sub10ms non-regression
or equality. There is no reliable finer helper-start timestamp in this observer;
that limitation is explicit in the PR and annotated terminal. No claim that
the observed difference is zero, and no cherry-picking runs/order. No further
product change was made based on this inconclusive fine-scale comparison.

pg-m74-terminal.png is an actual cropped xterm capture on physical m74. Its
coloured header annotates the source, scenario and results. Frame fills the
terminal surface and was visually checked. Source scripts and raw probes are
included. The terminal summary has the same uncertainty qualification.

## Cleanup and limits

Primary m74 lease02:24:24-02:32:54UTC (8.5min), clean receipt. A stale critical
notice from the first unconfigured standalone resident remained after it quit
(the copied test set omitted the UI executable). Subsequent runs start with a
private prewritten accepted configuration. Brief cleanup lease02:33:40-02:34:30UTC
removed only that put.gd notice through Cinnamon's current-notification API;
console visibly idle and lease released clean. No compositor restart/logout,
no user apps touched. No owned process, VM, tunnel or lock retained. Source/SDK/
binary caches and exported private test results remain for reproducibility.
No full release desktop matrix, package, memory campaign or workstation test ran.
No merge, watches, subagents, source-doc edits or manual version bump.
