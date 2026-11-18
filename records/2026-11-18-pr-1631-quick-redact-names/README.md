# PR #1631 (issue #1618) Quick redact names and list: real-capture acceptance

Acceptance of the Quick redact "My username and name" and "My redaction list" categories on three physical lab desktops, with real
captures and real input. Run by a Sonnet test sub-agent on 2026-11-18 (about 07:10 to 07:45 UTC).

## Build under test

- Branch `feat/quick-redact-names`, head `8252b0b46db3db8d3cc35e55d11adf449a7ce44`, tree `fd55dce57e102cffe8f9377818efa4bbc9d4501e`.
- Packages from manual CI run 44254114800 (all jobs green): `release-native-fedora44` RPM, `release-native-ubuntu26.04` DEB, `release-native-ubuntu24.04` DEB.
- Each desktop installed only the putgd package (`dnf install` / `apt-get install ./putgd_*.deb`, dry run read first) and proved the build:
  `putgd-cli diagnostics` and `putgd-cli --version-json` gave `build.gitTree = fd55dce57e102cffe8f9377818efa4bbc9d4501e` on all three.
- Package removed and desktop lock released on each desktop afterwards (f44 `dnf remove --noautoremove` then a gdm restart; k72 and m74 `apt-get remove`).

| Desktop | OS and session | Package | getpwnam name / GECOS |
| --- | --- | --- | --- |
| f44 | Fedora 44, GNOME Wayland (mutter, `putgd@put.gd` extension active after a gdm restart) | RPM fc44 | `patrick` / `Patrick` |
| k72 | Kubuntu 26.04, Plasma Wayland | DEB ubuntu26.04 | `patrick` / `patrick` |
| m74 | Linux Mint 22.3, Cinnamon X11 | DEB ubuntu24.04 | `patrick` / `patrick,,,` |

No lab account has a surname in GECOS, so the surname and "first initial + last name" forms of the name category (`phudson`, `p.hudson`) were not
exercised through the name category. They were exercised through list entries (row 5b).

## How it was driven

A private resident per desktop (private `XDG_*` folders, session environment taken from the desktop's own session process, `systemd-run --user --scope`),
driven through `putgd-cli` session methods (`editor.open {"source":"desktop"}`, `editor.recognize`, `editor.apply`, `editor.inspect`, `editor.saveCopy`,
`settings.get/patch`, `diagnostics.bundle`). Real input over the wall VNC (`tools/lab/rfb.py`) for the editor UI rows (6) and the Settings UI row (8), both on f44.
The windows captured were the desktop's own terminal (ptyxis, Konsole, gnome-terminal), file manager (Nautilus, Dolphin, Nemo), Firefox on the two GitHub pages,
and a local page or text editor for the near misses. Scripts are in `scripts/`.

Pixel check (`scripts/verify.py`): the original capture is saved with `editor.saveCopy` before any mark, the marked export after. For every mark rectangle
every exported pixel must be opaque black (so no original pixel can remain under it), and no pixel outside the marks may differ. All 22 desktop rows
below passed this check (`*-verify.json`).

## Results

Pass means the row's check held. Evidence paths are relative to this record; each row has `NAME-orig.png`, `NAME-red.png`, `NAME.json` (marks and covered words) and `NAME-verify.json`.

| Row | f44 (GNOME Wayland) | k72 (Plasma Wayland) | m74 (Cinnamon X11) |
| --- | --- | --- | --- |
| 1 Terminal prompt, "My username and name" | pass, 3 marks (title, `/home/patrick/...` line, prompt): `f44/r1-terminal-*` | pass, 2 marks (path line, prompt): `k72/r1-terminal-*` | pass, 3 marks: `m74/r1-terminal-*` |
| 2 File manager | pass, 1 mark on the `/home/patrick` location bar: `f44/r2-filemanager-*` (see failure F3) | pass, 2 marks (title path, breadcrumb): `k72/r2-filemanager-*` (F3) | pass, breadcrumb `patrick` and location bar: `m74/r2a-breadcrumb-*`, `m74/r2-filemanager-*` |
| 3 GitHub profile, list `Patrick Hudson` | pass, 3 marks: `f44/r3-webpage-*` | pass, 3 marks: `k72/r3-webpage-*` | pass, 6 marks (also URL bar and window title): `m74/r3-webpage-*` |
| 4 Issue 1618, patterns `#\d{4}` and `(?i)\bquick redact\b` | pass, 15 marks, `(?i)` works: `f44/r4-patterns-*` (F2) | pass, 17 marks: `k72/r4-patterns-*` (F2) | pass, 20 marks: `m74/r4-patterns-*` (F2) |
| 5 Near misses | pass: nothing covered wrongly, see below: `analysis/*-r5-*` | pass, same | pass, same |
| 6 Editing suggestions | pass (real input): `analysis/f44-r6-ui-flow.txt` | pass via CLI, Remove suggestions not drivable by CLI (F4): `analysis/k72-r6-cli.txt` | **FAIL**: a deleted suggestion was added back (F1): `analysis/m74-r6-cli.txt`, `analysis/m74-r6-rerun-dismissed-jitter.txt` |
| 7 Runaway pattern `(a+)+$` | pass: `analysis/f44-r7-runaway.txt` | not run (one desktop) | not run |
| 8 Settings UI | pass (real input): `analysis/f44-r8-settings-ui.txt` | not run | not run |
| 9 Diagnostics bundle | pass, no word or pattern anywhere, only `{"count": N}`: `analysis/f44-r9-diagnostics.txt` | not run | not run |
| 10 Agents (`terms`, bad pattern) | pass: `analysis/f44-r10-agents.txt` | not run | not run |

Row 5 detail (same on all three desktops). Text: `patricks`, `pattern`, `pat`, `Hudson Bay`, `hudsonia`, `patrick@d69:~$`, `/home/patrick/projects/demo`, `Patrick's`, `Patrick,`,
`phudson2`, `p.hudson`, `Hudson, Patrick`, `users`, `username1`, `patrickson`, `patrick-hudsonx`.
- With name and list on (list `Patrick Hudson`): covered `patrick@d69:~$`, `/home/patrick/projects/demo.`, `Patrick's`, `Patrick,`, `Patrick` in `Hudson, Patrick`, and `patrick-hudsonx.`
  (the name part `patrick` ends at `-`, an allowed edge). Not covered: `patricks`, `pattern`, `pat`, `Hudson Bay`, `hudsonia`, `users`, `username1`, `patrickson`, `phudson2`, `p.hudson`.
  `Hudson Bay` is not covered because these accounts have no surname; with the saved entry `Patrick Hudson` it matches only as a whole, as the issue says.
- 5b, one-off `terms` `["Hudson","Pat"]` (category list): covered `pat`, `Hudson` in `Hudson Bay`, `p.hudson`, `Hudson,` in `Hudson, Patrick`; not covered `patricks`, `pattern`, `hudsonia`, `phudson2`, `patrick-hudsonx`.
  `a` before `pat` is covered too, because the padded mark overlaps it (F5).
- Nothing was covered that breaks the issue's rules. Files: `analysis/*-r5-nearmiss-name-and-list.txt`, `analysis/*-r5b-*.txt`.

## Failures and findings

**F1 (row 6, m74, real defect): a deleted suggestion is added back when a later run reads a box that differs by pixels.**
The editor remembers deleted suggestions by exact rectangle (`QList<QRect>::contains` in `EditDocument::dismissed`, src/editor/EditDocument.h:103, filled at
EditDocument.cpp:183, checked at EditorWindow.cpp:1210). A re-run recognizes the page again with the other marks applied as black, and the matched word box moves by a few pixels.
m74 reproduction (`analysis/m74-r6-rerun-dismissed-jitter.txt`, deterministic on two runs): marks 1 to 9 over the near-miss page, removed mark 9 `[593,784,222,40]` over `patrick-hudsonx.`,
Quick redact again created mark 10 `[594,785,220,35]` over the same word (`counts name: 1`). Undo then undid the new mark instead of restoring the deleted one.
On f44 (real input) and k72 (CLI) the boxes came out identical, so the re-run skipped the deleted mark there. The skip works only when OCR boxes are pixel-identical between runs;
it needs a tolerance (for example overlap above 50%) on `dismissed`.

**F2 (rows 4, all desktops): `(?i)\bquick redact\b` did not match `Quick` at the end of a wrapped line and `redact` at the start of the next** ("open Quick / redact in the Redact tool panel",
the line ended about 30 px short of the column edge). The other 8 to 11 occurrences per page were covered, including `(Quick redact` and `Quick redact)`. This is the "wrap evidence" rule in the plan, so it may be by design;
a reader would expect the phrase covered. Not a bug in the pattern engine.

**F3 (rows 2, recognition limits, not the matcher):** f44: the selected text in Nautilus's location bar (light text on the blue selection) was not read until the selection was cleared
(first run: 0 marks). k72: Dolphin's small location-bar text was read as `ck/|`; I set Dolphin's `ShowFullPathInTitlebar`, and the title and breadcrumb were read and covered.
Rows 3 and 4 on f44 and k72: the URL bar's `/patrick-hudson` was not read (OCR returned `github.com,`); on m74 it was read and covered.
Truncated tab titles such as `(Patrick Hud` are not whole words and stay visible. These match "Suggestions only. Recognition can miss text."

**F4 (row 6): "Remove suggestions" has no session method**, so `putgd-cli` and MCP cannot drive it (the menu entry works with real input on f44). Agents can remove each suggested mark with `editor.apply remove {shapeId}` (used on k72 and m74).

**F5 (by design, worth knowing): a mark covers the whole word box plus padding.** Neighbouring characters and short words are hidden too: `What happen[s. Quick redact (]he menu`, `a` before `pat`, and the marks reach outside the terminal window edge on f44.

**F6 (incidental, environment):** running `putgd` (the launcher) with a private `XDG_RUNTIME_DIR` and no display in its environment aborted with SIGABRT and printed a `putgd-crash` report on f44
(exit 134). It happened while I opened the Settings window by hand; the resident was unaffected. Not part of the feature.

Lab notes (not product): m74's user manager has a stale session environment (`DISPLAY=:2`, `XDG_CURRENT_DESKTOP=wlroots`, `WAYLAND_DISPLAY=wayland-0`) and a failed `gnome-terminal-server.service`; apps and
the resident need the environment of the `cinnamon` process and a hand-started `gnome-terminal-server`. k72's Kate exited at once (not investigated; a local page in Firefox was used for row 5). f44 had a stale user
`putgd-file-manager-*` path/service pair from an older test (`/tmp/ta1532fn`) looping every second, which stopped the lock release; I stopped those two units by exact name.

## Not covered

- Rows 7 to 10 ran on f44 only (the brief says one desktop). Row 6's real-input part ran on f44 only.
- Surname parts of the name category (see the table at the top). A saved list entry `Patrick Hudson` was never tested against `PatrickHudson`, `patrick_hudson` or a recognizer-split `patrick-` `hudson` on a real capture.
- Aurora and d69 were not used.

## Pictures for the PR

Made on f44 (GNOME Wayland): the editor UI there is clearest on the light desktop theme. Annotated with put.gd's own editor (headless resident from the same RPM, `editor.apply` rectangle, arrow, text, crop; `scripts/annotate.py`).
All five are in `pictures/`: `menu.png` (Quick redact menu with the two new entries and Remove suggestions), `settings.png` (Settings, Capture, Text recognition with both boxes filled),
`selected.png` (a selected suggested mark with "Suggested: My username and name" in the panel over the real terminal capture), `term-before.png` and `term-after.png`.
