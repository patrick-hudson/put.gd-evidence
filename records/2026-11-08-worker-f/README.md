# Worker F: SDK instructions, ReviewWindow gates, diagnostics ordering

Baseline source: 9fb653676, nightly. Test source: c8004908c (PR #1272).
Documentation source: 4057bf752 (PR #1271, merge FIRST).
Private source exports/builds: d69 and k72 ~/work/wf1108. Both used distro dynamic Qt and the official locked AWS SDK 1.11.924 via read-only symlink to ~/work/wd1107/build/sdk. No workstation builds, desktop work or desktop claims. d69 Qt 6.8.2/GCC14.2; k72 Qt6.10.2. Baseline configure failure (SDK source license path) and corrected read-only source symlink retained in logs; no SDK reprovisioning.

#1264: Original worker C 60-second timeout is retained at the issue and its pinned evidence, https://github.com/patrick-hudson/put.gd-evidence/tree/235299d7d18fa29826ebcfbf190930c5ba1b1357/records/2026-11-07-worker-c-dev . Later original 56.56/48.32s passing retries do not prove a fix.

New before/after profiling: six concurrent offscreen processes, six copies of the complete inventory on each side, same host/SDK/Debug build, no retries and no outer timeout for diagnostic completion. Before six full suites: 75.88–80.90 seconds. After 24 area runs (six copies each): layout 18.28–23.73, footer 25.06–31.24, workspace 20.95–24.54, actions 4.45–6.22 seconds. The original full gate would exceed its 60-second limit under this repeatable load. This is a six-slot synthetic load, not a replay of worker C's mixed full-CTest job ordering.

Qt XML logs supply per-function durations; function-timings.csv gives before/after medians for EVERY function. XML inventories match at 95 functions / 142 rows, each run six times. All 124 test/data/lifecycle method bodies are byte-identical (methods.txt); assertions, width sweeps, data and waits are preserved. The footer width sweep dominates: median 31.611s before /29.025s after. Other large functions: mutedIndicatorStaysClearOfTheWindowControls 8.233/7.869s; frameGatesCoverThePreviewAspectRatio 4.347/4.685s. Explicit settle literals total only 312ms before loop repetitions; most work is layout/render sweeps rather than a timed-out wait. Splitting bounds each gate; no claim of reducing total functional work.

Actual registered CTest validation: ctest --preset dev -j6 -R '^gui_review_window_' (four entries available, no extra load), 4/4 pass, no retries: layout12.57/footer17.11/workspace14.38/actions3.66 seconds. All retain TIMEOUT60. Saved JUnit and full logs in d69-after.tar. check_test_waits passes.

#1267: unchanged test, 50/50 fresh processes on k72, both data rows and both revisions each, no retry. The metadata accessible-name wait includes the new revision. UiSessionFixture connects service.statusChanged to invalidate; UiSession applies settings and diagnostics together before statusChanged, rejecting stale generations. No race in the alleged ordering; leave test unchanged and issue closed as not planned. Logs in k72-stress.tar.

#1263: SDK docs contract fails on baseline stale references and passes with docs PR #1271; sdk-before/after.log retain this. Grep also found historical .907 statements in history and the dated golden preparation record; these remain accurate records. The current Aurora build guide now requires lock matching and fresh isolated provisioning.

All resolved runtime socket paths were checked before launch (51–58 UTF-8 bytes, limit107). Private runtime directories mode0700. Harnesses and logs retained in archives. Builder cleanup receipts show zero worktree processes. No processes killed, desktop locks acquired, or SDK prefixes changed. No new out-of-scope follow-ups found. CI remains separate from these local results.
