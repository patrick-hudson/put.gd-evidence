# PR #1631 (issue #1618) final acceptance at merge candidate 325344749

Final acceptance of Quick redact "My username and name" and "My redaction list" on the merge candidate, on two physical lab desktops (f44 GNOME Wayland, m74 Cinnamon X11), with the installed packages and real captures.
Run by a Sonnet test sub-agent on 2026-11-18 (about 12:20 to 13:00 UTC). Earlier records: `2026-11-18-pr-1631-quick-redact-names`, `2026-11-18-pr-1631-final-recheck`.

## Build under test
- Branch `feat/quick-redact-names`, head `325344749bc46c560335345155ed6013a0679e59`, tree `2f29dea713db1ac4a9ef9831d1628e515dc7fe52`.
- Packages from manual CI run 44299554859 (completed, every job green): `release-native-fedora44` RPM for f44, `release-native-ubuntu24.04` DEB for m74.
- On both desktops `putgd-cli diagnostics` gave `build.gitTree = 2f29dea713db1ac4a9ef9831d1628e515dc7fe52`, equal to `git rev-parse 325344749^{tree}`.
- Method as before: private resident, `putgd-cli editor.open {"source":"desktop"}`, `editor.saveCopy` before and after, pixel check (every mark fully black, nothing outside the marks changed; `*-verify.json`; all passed).
- **k72 was not used.** The nightly desktops check took all three desktop locks at 12:31 UTC (just after f44 was released). f44 and m74 are the two desktops used; m74 became free at 12:53.
  I never waited while holding a lock.

## Results
| Row | f44 | m74 |
| --- | --- | --- |
| A Runaway patterns `(a+)+$`, `(?:(?=.*+).)+\d`, `#\d{4}` + list word, "All of these" | **pass** (CLI and real input in the editor menu) | pass (CLI) |
| B Close mid-run: helper gone, no child left | **pass** | pass |
| C No patterns: no `--match-patterns` child ever | **pass** | pass |
| D Real-package patterns `\bJIRA-\d+\b`, `(?i)\bquick\sredact\b`, incl. wrapped line | **pass** (also closes last run's failure) | not run |
| E Settings save-time check (real input) | **pass** | not run |
| F1 Terminal prompt, name category | pass | pass |
| F2 GitHub profile, list `Patrick Hudson` | pass | pass |
| F3 Near misses | pass | pass |
| F4 Delete suggestions, re-run: not re-added; `removeSuggestions` via `editor.view` | pass | pass |
| G Diagnostics bundle scan | **pass** | not run |

### A: runaway patterns (`f44/rA-log.json`, `rA-ui-*`, `m74/rA-log.json`)
Saved `(a+)+$`, `(?:(?=.*+).)+\d`, `#\d{4}` and list word `build-host-7`. Page with a 44-character `a...ab` line, an issue number, the list word, a mail address and other text.
- f44 (CLI): `redactText` with all seven categories answered in 0.93 s; `skippedPatterns: [0]`; `editor.inspect` polled every 0.1 s during the run: 6 polls, slowest 0.076 s, no gap over 0.5 s.
  The `--match-patterns` child appeared 0.90 s into the run. Counts: email 1, key 1, list 6, name 1. Marks cover the heading with `#1631`, the list word and the email (`rA-log.json`, `rA-ui-red.png`).
- f44 (real input): Quick redact menu, All of these on the same page: panel "Added 9 suggested redactions / Pattern 1 took too long and was skipped." within 0.4 s (`f44/ui-frames/panel-skipped-t04-and-t14.png`, and unchanged 1 s later).
  `rA-ui-verify.json`: 9 marks fully black, nothing else changed.
- m74 (CLI): 1.41 s, `skippedPatterns: [0]`, 10 polls, slowest 0.08 s, email 1, key 1, list 4, name 1.
- Only pattern 1 (`(a+)+$`) was named as skipped. Pattern 2 `(?:(?=.*+).)+\d` was not skipped on this input (it finished inside the budget), so the "names the slow patterns" claim was shown for one pattern.
  The brief expected 2 to 3 seconds; here the run ended in 0.4 to 1.4 s because the child hit its own limit before the 2 s deadline.

### B: close mid-run (`f44/rB-log.json`, `m74/rB-log.json`)
A larger text page so recognition takes about 1.5 s. While the match helper ran (found as a child of the editor PID from `/proc/<editor>/task/*/children`, 1.35 to 1.74 s after the start), `editor.cancel` (Discard):
- f44: helper 1466042 gone 0.064 s later (`kill 0` fails, `/proc/1466042` absent); editor gone, no child left; the pending `redactText` answered `editor_closed`.
- m74: helper 1570936 gone 0.065 s later; same result, pending call `editor_finalizing`.
- No `--match-patterns` process afterwards.
Note: the first f44 attempt (with a short page) finished before the helper started, so it recorded `helper: null`; the rerun is the evidence.

### C: no patterns, no child (`rC-log.json`)
`quickRedactPatterns: []` saved, Quick redact with all categories. `/proc/<editor>/task/*/children` sampled every 5 ms for the whole run (2 runs on f44, 1 on m74): the only child ever seen was `putgd-ocr`; never `--match-patterns`.
`skippedPatterns` null. (A `null` value for the key is refused by settings.patch with a config_invalid error; `[]` works.)

### D: real-package patterns (`f44/rD-wrap-*`, `f44/rD-issue-*`)
Saved `\bJIRA-\d+\b` and `(?i)\bquick\sredact\b`. Controlled justified page: both JIRA ids covered; `quick redact` covered in every paragraph, including the wrapped one (P3: `quick` at the end of one line and `redact` at the start of the next, two marks).
On the #1618 issue page the wrapped `Quick` / `redact in` is covered too (`rD-issue-*`, 11 marks). The previous recheck's only failure is closed.

### E: Settings save-time check, real input (`f44/ui-frames/wall-e1.png`, `wall-e2.png`, `wall-e3.png`)
- `(`: refused in place, "Pattern 1: This pattern does not compile: missing closing parenthesis at offset 1." (nothing saved).
- `a*`: refused, "Pattern 1: This pattern matches empty text." (nothing saved).
- `(a+)+$`, `\C` and `(?<=ID-)\d+` typed on three lines: saved (config.json `quickRedactPatterns` = those three).

### F (rF*)
- F1 terminal: f44 3 marks (title, `/home/patrick/...`, prompt); m74 3 marks.
- F2 profile with list `Patrick Hudson`: f44 3 marks; m74 6 marks (also URL bar and title).
- F3 near misses: unchanged from before on both. Name category covers `patrick@d69:~$`, `/home/patrick/projects/demo.`, `Patrick's`, `Patrick,`, `Patrick` in `Hudson, Patrick`, `patrick-hudsonx.`;
  not `patricks`, `pattern`, `pat`, `hudsonia`, `users`, `username1`, `patrickson`, `phudson2`. One-off terms `["Hudson","Pat"]` cover `pat`, `Hudson` in `Hudson Bay`, `p.hudson`, `Hudson,`. (`*-analysis.txt`)
- F4 (`rF4-run.txt`, same on both): Quick redact name = 7 marks; deleted 3 of them one at a time; Quick redact again added 0; one undo gave 5 marks; with a hand mark, `editor.view {"action":"removeSuggestions"}` left only the hand mark;
  one undo brought the suggestions back; a second call returned `edit_shape_missing`.

### G: diagnostics (`f44/rG-run.txt`, `f44/r9c-diagnostics.json`)
Saved words `Patrick Hudson`, `build-host-7`, `Zebrafish Quartz` and patterns `#\d{4}`, `ZQX-\d{3}`, `(a+)+$`. Bundles with and without names: every file of each (7) decompressed and searched for each word, pattern, `Zebrafish`, `Quartz`, `ZQX`: no hits.
Only key names matched: `config.redacted.json` shows `{"count": 3}` for both lists; `logs/putgd.jsonl` holds config-rejected lines naming `/preferences/quickRedactPatterns/0` and fixed text, never a user pattern.

## Failures
None in these rows. Notes: the brief's "panel names the slow patterns" showed one name (see A); OCR does not read a few small items (for example the URL bar text, truncated tab titles), as before.

## After the run
Packages removed on f44 (`dnf remove --noautoremove`, then a gdm restart) and m74; residents and apps stopped by exact unit or PID; locks released with `--verified-clean`; no `--match-patterns` process on any of f44, k72, m74 (PID listings checked).
