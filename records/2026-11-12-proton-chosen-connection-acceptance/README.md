# Proton chosen-connection acceptance: blocked by exact-head CI

Requested PR: https://github.com/patrick-hudson/put.gd-desktop/pull/1414

Requested head: `dcfa09b3b1ef8cd98efc6a566dcc3f51378c25c8` (`perf/proton-link-faster`).
CI run: [43147820138](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43147820138).
Checked 2026-11-12 UTC. **No build was tested.** The `contracts` job failed; the user required stopping on CI failure and prohibited testing another build. Other jobs were still running when the failure was observed. No CI packages were downloaded, compiled or launched.

## Failure

Job: [contracts](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43147820138/job/130949675151).
Step: `Release, packaging and CI tool contracts`.

```text
FAIL: test_repository_tests_use_the_scaled_helpers (__main__.WaitLint.test_repository_tests_use_the_scaled_helpers)
tests/integration/test_proton_transport.cpp: 1 qwait at line 312: use putgd::test::settle(ms) for fixed time, or a PUTGD_TRY/STEADY macro to wait for an outcome
Ran 20 tests in 1.584s
FAILED (failures=1)
Failed: tests/ci/test_flake_tools.py
##[error]Process completed with exit code 1.
```

`ci-failure.log` retains the timestamped excerpt. `ci-status.json` records the exact head and completed failing step. This is a CI contract failure; it establishes no Proton desktop failure or success.

## Host results

| Host | Intended desktop / package | Previous round | This round |
| --- | --- | --- | --- |
| d69 | Debian 13 Plasma Wayland / debian13 .deb | 15/15 | Not run; 0/15 executed |
| k72 | Kubuntu 26.04 Plasma Wayland / ubuntu26.04 .deb | 15/15 | Not run; 0/15 executed |
| m74 | Mint 22.3 Cinnamon X11 / AppImage | 15/15 | Not run; 0/15 executed |
| f44 | Fedora 44 GNOME Wayland / AppImage | 9/15; six captures not testable | Not run; 0/15 executed |

No desktop or Proton locks were acquired. No app/helper processes were started, so no run-created helper could be left behind. No final helper inventory was performed. No links were created and `revoke-all` was not run; nothing from this attempt needed revocation. No GUI acceptance evidence was captured.

## Previous times beside this attempt

Seconds, using the earlier record's measurement conventions. Each cell is **previous → current**; NR means not run, not a zero time. There are no new timing measurements and no speed comparison can be made.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| `file-64k` | 5.39 s → NR | 5.56 s → NR | 5.3 s → NR | 4.97 s → NR |
| `text-small` | 4.03 s → NR | 3.78 s → NR | 5.67 s → NR | 4.63 s → NR |
| `after-cancel` | 3.95 s → NR | 3.81 s → NR | 5.06 s → NR | 3.68 s → NR |
| `file-1m` | 6.59 s → NR | 7.84 s → NR | 11.74 s → NR | 13.9 s → NR |
| `file-8m` | 9.26 s → NR | 7.95 s → NR | 10.7 s → NR | 8.42 s → NR |
| `batch-3` | 12.45 s → NR | 16.89 s → NR | 11.29 s → NR | 10.33 s → NR |
| `back-to-back` | 5.9, 11.41 s → NR | 9.02, 12.7 s → NR | 5.52, 9.16 s → NR | 8.82, 12.21 s → NR |
| `desktop-now` | 7.22 s → NR | 6.76 s → NR | 8.88 s → NR | not testable (`gnome_extension_missing`) → NR |
| `desktop-delay3` | 4.91 s after countdown → NR | 4.5 s after countdown → NR | 5.27 s after countdown → NR | not testable (`gnome_extension_missing`) → NR |
| `desktop-delay3-again` | 7.27 s after countdown → NR | 6.08 s after countdown → NR | 8.27 s after countdown → NR | not testable (`gnome_extension_missing`) → NR |
| `monitor-delay3` | 6.59 s after countdown → NR | 4.69 s after countdown → NR | 7.79 s after countdown → NR | not testable (`gnome_extension_missing`) → NR |
| `cancel-countdown` | cancelled; helper gone 0.01 s → NR | cancelled; helper gone 0.01 s → NR | cancelled; helper gone 0.01 s → NR | not testable (`gnome_extension_missing`) → NR |
| `history-picture` | 5.69 s → NR | 8.78 s → NR | 5.79 s → NR | not testable (`gnome_extension_missing`) → NR |
| `link-answers` | HTTP 200 → NR | HTTP 200 → NR | HTTP 200 → NR | HTTP 200 → NR |
| `revoke-all` | 15 revoked; 2.54–4.85 s each → NR | 15 revoked; 2.49–4.82 s each → NR | 15 revoked; 2.67–4.33 s each → NR | 10 revoked; 2.5–3.82 s each → NR |

## Requested additions

| Host | Back-to-back helper count | Sequential screenshots 1 / 2 / 3 (upload-stage, total) |
| --- | --- | --- |
| d69 | Unmeasured | Unmeasured |
| k72 | Unmeasured | Unmeasured |
| m74 | Unmeasured | Unmeasured |
| f44 | Unmeasured | Not attempted; missing GNOME extension expected from previous record |

Prepared observer counts distinct `(PID, /proc/PID/stat starttime)` pairs whose comm begins `putgd-proton-ru`, sampling every 10 ms across the original back-to-back case through helper exit. It was not run. It would count observed processes, with brief-process sampling limits, rather than claim an exec audit.

## Scripts and scope

Read the PR body and fetched evidence origin before reading the baseline from `origin/main` at `fb48c9152bdce74fb99fe9b6ba612f171f14bb5b`. The `.original` scripts are byte-identical to the previous record. The other scripts are **prepared, never executed against a desktop**: wrapper paths/purpose changed to private new scratch; the Python harness adds socket-path preflight, the process observer, and three sequential captures after the original 15, followed by revocation of their links. The original 15 case bodies otherwise remain intact. `desktop_lock.py` was read from product `origin/nightly` for preparation; only its read-only `status` command was executed.

CI was watched with `gh run watch 43147820138 --interval 60` and that local watcher was stopped once the job failure was confirmed. `gh run view --job ... --log-failed` refused while the overall run was in progress; the completed job log was retrieved with the jobs logs API. Its first retrieval required `--allow-escape-sequences`; the second retrieval succeeded. No retry of CI or desktop cases occurred. The shared product checkout was not edited, switched or built.

Not covered: all requested desktop cases, all new timing, actual GNOME capture behavior on this build, helper handover, sequential storage-host hint effects, leftover-helper behavior, and link revocation on this build. The previous record's results do not establish acceptance for this head.
