# PR #1631 (issue #1618) final acceptance recheck at head 31de163ea

Recheck of Quick redact "My username and name" and "My redaction list" on the final head, on the three physical lab desktops, with real captures. Run by a Sonnet test sub-agent
on 2026-11-18 (about 09:55 to 10:15 UTC). It follows the first record `2026-11-18-pr-1631-quick-redact-names`, whose pictures still apply (the UI is unchanged).

## Build under test

- Branch `feat/quick-redact-names`, head `31de163ea8cf...` (`31de163ea8cfa940aedca3ebe14060ff90ac9625`), tree `7ddff6b7adf6b6d41f13d99b54b7c1de937edca9`.
- Packages from manual CI run 44278467267: `release-native-fedora44` RPM, `release-native-ubuntu26.04` DEB, `release-native-ubuntu24.04` DEB. At download time every package, test, sanitizer and
  contracts job was green; only `packages / sbom`, `appimage-pipewire` and `appimage-sources` were still running.
- On every desktop `putgd-cli diagnostics` gave `build.gitTree = 7ddff6b7adf6b6d41f13d99b54b7c1de937edca9`, which equals `git rev-parse 31de163ea^{tree}`.
- Same method as the first record: private resident, `putgd-cli editor.open {"source":"desktop"}`, `editor.saveCopy` before and after, pixel check (`scripts/` and the first record's `verify.py`):
  every mark rectangle fully black, nothing outside the marks changed. Every row below passed it (`*-verify.json`).
- One desktop lock at a time (k72, then f44 for all f44 rows in one lock, then m74); each released with `--verified-clean`; packages removed; no process left.

## Results

| Row | k72 | m74 | f44 |
| --- | --- | --- | --- |
| 1 Terminal prompt, "My username and name" | pass, 2 marks | pass, 3 marks | pass, 3 marks |
| 3 GitHub profile, list `Patrick Hudson` | pass, 3 marks | pass, 6 marks | pass, 5 marks |
| 4 Issue 1618, `#\d{4}` and `(?i)\bquick redact\b` | pass, 17 marks | pass, 20 marks | pass, 16 marks (`#1631` chip not read by OCR) |
| 5 Near misses | pass, same as before | pass, same as before | pass, same as before |
| 2 (F1) delete one suggestion, re-run, undo | not run | **pass** (was fail) | not run |
| 3 Full real name `Patrick Hudson` | not run | not run | **pass** |
| 4 Settings: `(a+)+$` refused; `(foo\|bar)+`, `\bJIRA-\d+\b` save | not run | not run | **pass**, in Settings UI with real input and over `settings.patch` |
| 4 Slow but allowed pattern keeps the editor responsive | not run | not run | **pass** |
| 4 `#\d{4}` still marks the issue number | pass (`#1618`, `#1631`) | pass | pass (`#1618`; `#1631` unread by OCR) |
| 4 `\s` pattern matches `quick` and `redact` across a wrapped line | not run | not run | **FAIL** |
| 5 Agents: `editor.view removeSuggestions`, then `edit_shape_missing` | not run | not run | **pass** |
| 6 Diagnostics bundle, no word or pattern | not run | not run | **pass** |

Rows 1, 3, 4 and 5 show no regression against the first record: the same words are covered on the same pages (`*/r*-analysis.txt`, `*/r*.json`).

### F1 on m74 (fixed)
`m74/r6-cli-run.txt`, `m74/r6-rerun-dismissed.log`, `m74/r6-every-other-delete.log`. The same near-miss page and sequence that failed before:
quick redact (9 marks), move mark 1 (keeps `suggested: "name"`), delete mark 9 (`patrick-hudsonx.`), Quick redact again adds 0 (before: 1, at a new rectangle `[594,785,220,35]`), undo brings mark 9 back,
a hand mark survives. A second run deleted every other mark (5 of 9) one at a time and re-ran Quick redact after each deletion: 0 re-added, 4 marks left, one undo gives 5.

### Full real name on f44 (`f44/r3b-fullname-*`, `f44/gecos-*.txt`)
- Original GECOS saved first: `f44/gecos-original-line.txt` = `patrick:x:1000:1000:Patrick:/home/patrick:/bin/bash`.
- `sudo -n chfn -f "Patrick Hudson" patrick` (rc 0). `getent` then showed `patrick:x:1000:1000:Patrick Hudson:/home/patrick:/bin/bash` (`gecos-changed-line.txt`).
  The new name was read by the editor: `Hudson` is covered, and nothing but the full name provides it (before the change the surname was never covered).
- The restore ran in the same script as the capture, from an EXIT trap (`scripts/gecos.sh`): `getent passwd patrick` afterwards is the original line, `cmp` identical (`gecos-restored-line.txt`, `gecos-final-line.txt`;
  checked again after the package removal and a gdm restart).
- "My username and name" only, on a page showing the names. Covered: `Patrick Hudson`, `patrick-hudson`, `PatrickHudson`, `Hudson, Patrick`, `phudson`, `p.hudson`, `patrick__hudson` (OCR read it as `patrick_` `hudson`),
  and `Hudson` in `Hudson Bay`. Not covered: `patricks`, `pattern`, `hudsonia`. As the plan says. See `f44/r3b-fullname-analysis.txt`. The URL bar `file:///home/patrick/...` was covered too (login).

### Patterns on f44
- `f44/r4-settings-patch.txt`: `(a+)+$` is refused with "Pattern 1: This pattern can run for a very long time (a repeated group inside a repeat). Simplify it."; `(foo|bar)+`, `\bJIRA-\d+\b` and the `\s` pattern save.
  In the Settings window (`f44/ui-frames/wall-s-bad.png`): the same message shows in place and in the footer, config.json keeps the earlier patterns; `(foo|bar)+` and `\bJIRA-\d+\b` typed on two lines saved (`wall-s-ok.png`).
- `f44/r4-slow.txt`: five patterns that pass the shape check (`(?:.*){6}Q$`, `.*.*.*.*.*.*.*.*Q$`, `(\w|\d)+\d+\d+\d+Q`, `\b\w*\w*\w*\w*\w*\w*Z\b`, `[a-z]*...[a-z]*!`) against the issue page.
  Each `redactText` answered in 1.3 s while `editor.inspect` polled every 0.1 s (slowest 0.055 s). The first two were reported skipped (`skippedPatterns: [0]`); the other pattern `#\d{4}` still added its marks (7 in total).
- **FAIL: `(?i)\bquick\sredact\b` does not match across a wrapped line.** On the issue page `Quick` at the end of a line and `redact` at the start of the next (rows at y 965 and 986) stay uncovered, as with the literal-space pattern before.
  On a controlled page (`scripts/wrap.html`: a 430 px justified column, so every line is full width, with "quick redact" in 12 paragraphs, one of which breaks between `quick` and `redact`, P3) both
  `(?i)\bquick\sredact\b` (`f44/r4c-wrap-s-*`) and `(?i)\bquick redact\b` (`f44/r4d-wrap-space-*`) cover the five paragraphs where the phrase stays on one line (6 marks incl. P1) and **not P3**. The wrap join does not
  reach user patterns here, or the wrap evidence did not fire for plain HTML text. This is unchanged from the first record's F2.

### Agents on f44 (`f44/r5-agent.txt`)
Quick redact name+list on the issue page: 20 marks (10 name, 10 list), plus one hand mark. `editor.view {"action":"removeSuggestions"}` removed 20 and left the hand mark;
one `undo` brought all 20 back (one undo step), `redo` removed them again; a second call returned `edit_shape_missing` ("There are no suggested marks to remove").

### Diagnostics on f44 (`f44/r9-run.txt`, `f44/r9b-diagnostics.json`)
Saved words `Patrick Hudson`, `build-host-7`, `Zebrafish Quartz` and patterns `#\d{4}`, `ZQX-\d{3}`. Bundles with and without names, 7 files each, every file decompressed and searched for each word, each pattern, `Zebrafish`, `Quartz`, `ZQX`.
No hits. The only matches were key names: `config.redacted.json` shows `{"count": 3}` and `{"count": 2}`, and `logs/putgd.jsonl` holds config-rejected lines that name the key `/preferences/quickRedactPatterns/0` and the fixed error text, not any pattern.

## Other notes
- f44 `#1631` chip: OCR did not read that small text in this run (it did before), so no mark. A recognition limit, not the matcher.
- Wrapped-line `quick`/`redact` is the only failure. Everything else passed.
