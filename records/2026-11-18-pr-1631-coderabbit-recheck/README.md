# PR #1631 (issue #1618) CodeRabbit-fix recheck at 1f883eeaf

Short recheck after the CodeRabbit fixes (#1656, #1657): matching on text as shown, marks per visual row, regression, Settings limits. One desktop: m74 (Linux Mint 22.3, Cinnamon X11).
Run by a Sonnet test sub-agent on 2026-11-18 (about 14:30 to 14:37 UTC). X11, so no session restart at any point (the nightly lease window rules).

## Build
- Head `1f883eeafd71...` (`1f883eeaf`), tree `40a6f367c3bc2cd5c57ad3f59605dfaa97148239`. Manual CI run 44317950408 completed green. Package: `release-native-ubuntu24.04` DEB, installed with `apt-get install ./putgd_*.deb` (dry run read first).
- `putgd-cli diagnostics` `build.gitTree = 40a6f367c3bc2cd5c57ad3f59605dfaa97148239`, equal to `git rev-parse 1f883eeaf^{tree}`.
- Method as before: private resident, `editor.open {"source":"desktop"}`, `editor.saveCopy` before and after, pixel check (marks fully black, nothing outside the marks changed; `*-verify.json`, all pass).

## Results
| Row | Result |
| --- | --- |
| 1 Patterns see the text as shown (`^Café$`, `[A-Z]{3}-\d+`; list word `Patrick Hudson`) | **pass** |
| 2 Marks per visual row (`ALPHA-\s*BETA`) | **pass** on a wrapped column; see note on a sidebar layout |
| 3 Regression: terminal prompt with "All of these" | pass |
| 3 Regression: `(a+)+$` skipped with the new wording, `#\d{4}` lands | pass |
| 3 Regression: close mid-run, no `--match-patterns` left | pass |
| 4 Settings: `projectalpha` and `ProjectAlpha` both kept; 500 spaces + `x` refused | pass |

### 1 (`m74/r1-text-*`)
Window with lines `Café`, `cafe`, `ABC-12`, `abc-34` and `Our GitHub user is patrick-hudson today.`, patterns `^Café$` and `[A-Z]{3}-\d+`, list word `Patrick Hudson`.
Covered: `Café`, `ABC-12`, and `patrick-hudson` (list words stay normalized; the mark also took the neighbouring `is`, which is the usual padding). Not covered: `cafe`, `abc-34`. 3 marks, pixel check passes.

### 2 (`m74/r2b-rows-wrapped-*`, `m74/r2-rows-*`)
Pattern `ALPHA-\s*BETA`. Layout (`scripts/p3.html`): a 430 px text column where `ALPHA-` ends one line and `BETA` starts the next, with `LEFTSIDE words here` far left of `ALPHA-` on its row and `RIGHTSIDE words there` far right of `BETA` on its row.
Result: 2 marks, one per row: `[613,208,156,36]` over `ALPHA-` and `[428,260,117,34]` over `BETA`. `LEFTSIDE`, `RIGHTSIDE` and the rest of both rows are untouched; no pixel outside the two marks changed (`r2b-rows-wrapped-verify.json`, 0 changed outside).
The marks run a little past the word on their row (the pad: `o` of `on` before `ALPHA-`, `t` of `then` after `BETA`).
Note: in the layout where the sidebar text sits to the right of `ALPHA-` and to the left of `BETA` on those same rows (`scripts/p2.html`) there is no match at all (0 marks, `m74/r2-rows-*`), because OCR puts the sidebar words between `ALPHA-` and `BETA` in the line text, so `ALPHA-\s*BETA` cannot match. I take that to be as designed (the two rows are not a wrap of one line); say if the brief meant this layout to match.

### 3 (`m74/r3a-terminal-*`, `rA-*`, `rB-log.json`)
- Terminal, all seven categories: `patrick@mint-builder:`, the `/home/patrick/...` line and the prompt covered (6 marks across two terminal windows).
- Patterns `(a+)+$`, `(?:(?=.*+).)+\d`, `#\d{4}`, list word `build-host-7`: with real input (Quick redact menu, All of these) the panel reads "Added 7 suggested redactions / Pattern 1 didn't finish and was skipped." (`m74/ui-frames/crop-panel.png`, `wall-ui-skipped.png`); `rA-ui-verify.json` passes.
  `#1631` is covered (mark over `Issue #1631 mentioned here and`), `build-host-7` and the email too. Via CLI: 1.39 s, `skippedPatterns: [0]`, `editor.inspect` slowest 0.057 s, no gap over 0.5 s.
  The second pattern `(?:(?=.*+).)+\d` matches whole rows that contain a digit (URL bar row, clock row); that is what it means, not a fault.
- Close mid-run: the `--match-patterns` child 1647093 (child of editor 1647059) was found 1.41 s into the run; after Discard it was gone in 0.071 s, `kill 0` fails, the editor has no children (`rB-log.json`).

### 4 (`m74/r4-settings.txt`, via `settings.patch`; config.json read after each)
Two words `projectalpha` and `ProjectAlpha`: both kept in config.json. A pattern of 500 spaces plus `x` (501 characters as written): refused, "Pattern 1: A pattern is longer than 500 characters." and config.json unchanged.
Controls: 499 spaces + `x` (500) saves; `x`*500 saves; `x`*501 refused.

## After the run
m74 lock released with `--verified-clean`; package removed (`apt-get remove`); resident, browser, terminal stopped by unit; no put.gd process and no `--match-patterns` process on f44, k72 or m74 (PID listings). Not used: f44, k72.
