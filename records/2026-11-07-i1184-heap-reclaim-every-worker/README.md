# #1184: idle heap reclamation after every journal worker (A/B)

What was tested: whether a bare read-only call leaves freed heap resident in the put.gd resident, before and
after put.gd-desktop PR #1262 (`background()` arms the idle heap reclamation when any worker finishes).

- Host: d69 (Debian 13), headless. Resident under `dbus-run-session` (private bus), `QT_QPA_PLATFORM=offscreen`,
  private XDG roots at `/tmp/i1149b/w2`, `PUTGD_STARTED_FOR_UPLOAD=1`, no UI process. The seeded 10,000-row history
  tree `/tmp/i1149b/w2-seed/w2` was copied in for every run; its stale `resident.lock` was removed.
- Builds (CI `release-appimage` artifacts, extracted and run through `AppRun`, same host and sequence):
  - base `775f878b2b29` (nightly, the PR's base), CI run 42412781803, `26.1107.4057-dev+g775f878b2b29`
  - fix `9776a6431d9b` (PR #1262 head), CI run 42412339097, `26.1107.4058-dev+g9776a6431d9b`
  - SHA-256 in `appimage-sha256.txt`.
- Sequence (`tools/m1184.py`): start, 140 s for the startup trim, the 60 s cleanup pass and their releases. Then per block,
  for each of `operation.recent`, `operation.inspect <id>`, `history.detail <id>` from `putgd-cli`: `history.list`
  (trims on both builds) and 11 s quiet, sample, the one call, samples 5 s and 35 s after. The
  `allocatorReclamationCount` read from `diagnostics` before and after gives the reclamations the call caused. 3 blocks
  per run, runs in the order base, fix, base, fix: 6 blocks per build and call.
- Metric: resident `Anonymous` from `/proc/PID/smaps_rollup`, MiB, per-block medians (`tools/sum1184.py`).

## Result

| Build | Call | Blocks | Before | 5 s after | 35 s after | Retained | Reclamations |
|---|---|---|---|---|---|---|---|
| `775f878b2b29` | `history.detail` | 6 | 4.09 | 4.22 | 4.22 | +0.12 | 0 |
| `9776a6431d9b` | `history.detail` | 6 | 4.10 | 4.09 | 4.09 | -0.01 | 1 |
| `775f878b2b29` | `operation.inspect` | 6 | 4.11 | 4.23 | 4.23 | +0.13 | 0 |
| `9776a6431d9b` | `operation.inspect` | 6 | 4.11 | 4.09 | 4.09 | -0.02 | 1 |
| `775f878b2b29` | `operation.recent` | 6 | 4.09 | 7.73 | 7.73 | +3.64 | 0 |
| `9776a6431d9b` | `operation.recent` | 6 | 4.10 | 4.16 | 4.16 | +0.06 | 1 |

On the base, a bare `operation.recent` keeps 3.64 MiB of freed heap resident (the issue measured 3.3 to 3.4 MiB on
f44), and `operation.inspect` and `history.detail` keep about 0.12 MiB each. None of them causes a reclamation. On the
fix, each call causes one reclamation 2 s after its worker ends, and the resident is back to its starting size within
5 s. Every block on both builds gave the same picture (`runs/*/result.json`). Unit test:
`OperationsTest::readOnlyJournalWorkRearmsHeapCleanup` (passes in PR CI).
