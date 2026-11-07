# Settings GUI split — worker E, issue #1226

Final source: 65570e6cfbea194c90e734d1f3287d80e21992c0, based on nightly c424570c896e29fd18a9f6b20180cad0ee27ae11. Code PR #1265, docs-only companion #1266; neither merged by worker.

Host: d69 / Debian 13, distro Qt 6.8.2, C++20 Debug dev preset, Ninja jobs=2; AWS SDK 1.11.924 at ~/work/wd1107/build/sdk read-only. SSH/offscreen widget testing only; no graphical acceptance or desktop session use. Socket preflight passed; private TMPDIR=/tmp/we1226-t and XDG_RUNTIME_DIR=/tmp/we1226-r. Sources exported with git archive; every tracked file verified against final source SHA-256 manifest. Binary SHA-256 files identify exact tested builds.

Old direct test passed, with isolated startup unlock skipped as designed. Final `ctest --preset dev -R '^gui_settings_'` passed 9/9, without retries. Each complete area suite under 45 seconds; 90 second guards, startup unlock 60 seconds. Preliminary 1149914e5 run also passed 9/9; final rebuild includes shared CMake area list and inline header helpers. Preliminary JUnit was emitted relative to CTest's binary directory; collection's first attempted move from the source-relative path missed it, then copied it from build/dev/evidence/settings.xml. Tests themselves passed. Both JUnit reports preserved.

Actual binary inventories: 209 functions and 297 function/data-row entries in old and union of all eight new binaries, sorted lists identical including multiplicity; functions.diff and datatags.diff are empty. 250 method bodies (209 tests, 41 data providers) preserved unchanged apart from boundary whitespace; see source-parity.json.

| Entry | d69 seconds |
| --- | ---: |
| `old gui_settings (direct)` | 181.67 |
| `gui_settings_appearance` | 35.50 |
| `gui_settings_general` | 29.94 |
| `gui_settings_capture` | 20.85 |
| `gui_settings_shortcuts` | 3.05 |
| `gui_settings_destinations` | 44.56 |
| `gui_settings_credentials` | 19.77 |
| `gui_settings_updates` | 12.49 |
| `gui_settings_advanced` | 20.34 |
| `gui_settings_startup_unlock` | 0.44 |

`check_test_waits.py` passed; 214 CI-tooling unit tests passed with one skip. Retry ledger and stress-suite selection discover registered names dynamically; TestPolicy labels and timeout scaling cover every new entry. Current docs updated separately; historical references retain their original identities. Review's pre-existing diagnostics snapshot ordering concern is tracked as #1267 without changing assertions.

No app code changed. No worker processes remained in the builder worktree at cleanup (cleanup.json). No desktop lock acquired. Builder sources, old binary and build products retained under ~/work/we1226; no test/compile processes remain. Reproduction scripts are included; ordinary Settings tests skip startup unlock, which the private-bus CTest entry runs explicitly. Baseline configure initially lacked the packaging SDK source license; corrected by read-only symlink build/dependencies to ~/work/wd1107/build/dependencies, in addition to build/sdk.
