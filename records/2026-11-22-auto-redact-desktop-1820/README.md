# Auto-redact on upload: desktop acceptance for PR 1826 (issue 1820)

Desktop acceptance of "cover chosen kinds of sensitive text automatically on upload": Settings → Capture →
Text recognition, each kind Off / Warn / Redact automatically, Apply to all kinds, the covered upload with no
prompt, the mixed prompt, the unfinished check, agent control, file uploads and the local `-original` copy.
Every value in every fixture is a test value: documented card test numbers, the AWS documented example key,
a generated `ghp_` token, a generated JWT and hex secret, `example.com`/`example.org` mail, 555-01xx and Ofcom
drama-range phones, and documentation IP ranges.

## Builds tested

GitHub builds the PR merge ref, so each package's commit is a merge of `nightly` and the PR head. The resident's
diagnostics reported exactly these trees on every desktop before any check ran.

| Label | PR head | CI run | Built commit (merge) | Tree | Packages (SHA-256) |
| --- | --- | --- | --- | --- | --- |
| a0aa444 | `11ddd09a7` | 44976758566 | `a0aa444834f1` (nightly `36e33ad` + head) | `262d8b27562421ce9025632f101896b787d3c645` | DEB 24.04 `d1d93fea…`, DEB 26.04 `e67a7365…`, RPM fc44 `78e6c894…`, AppImage `21cc7814…` |
| b24 | `b24f81aec` | 44981499203 | `9571d58e52c2` (nightly `4608d91` + head) | `b5b68a17399632d4fe3c408e4261afd6c2e619e7` | DEB 24.04 `7d6521f3…`, DEB 26.04 `ecc08967…`, RPM fc44 `ec338808…`, AppImage `1f0f48a8…` |
| gate | `f171a1118` (final) | 44984276629 | `b00481900f25` (nightly `4608d91` + head) | `9fcd81134232cda71f338dad182340292fec4784` | DEB 24.04 `056bbe92…`, DEB 26.04 `b4427eae…`, AppImage `9df08a62…` |

The broad matrix ran on a0aa444. b24 is the confirmation pass on the near-final head (Settings, prompts and
pictures). gate is the final head, after the matcher froze. Its rows are the gating evidence for the matcher.
b24 and gate differ only in the matcher; the UI, prompt, notification and archive behaviour are identical.

## Desktops

| Desktop | Host | Session | Package |
| --- | --- | --- | --- |
| Linux Mint 22.3 Cinnamon 6.6 | m74 (physical) | X11, 1920×1080 | DEB ubuntu24.04 |
| Kubuntu 26.04 Plasma 6.6 | k72 (physical) | Wayland, 1920×1080 | DEB ubuntu26.04 |
| Fedora 44 GNOME 50.6 | f44 (physical) | Wayland, 1920×1080, AppIndicator and `putgd@put.gd` ACTIVE after a GDM re-login | RPM fedora44 |
| Omarchy 4.5 Hyprland 0.56 | d69 VM, `omarchy-hyprland-20261108` overlay | Wayland, 1280×800 | AppImage (b24; scope cases 1, 2, 4 and the tray; the later matcher changes are covered by the m74/k72 gate rows) |
| Fedora 45 Budgie 10.10.3 labwc | d69 VM, `fedora45-budgie` overlay | Wayland, 1280×800 | AppImage (gate) |

## Method

- A private resident per desktop (its own XDG config, data, state and cache folders) on the real compositor,
  driven by `putgd-cli` from `tools/driver.py`. A loopback HTTP receiver kept every uploaded object byte for byte;
  Keep a local copy was on unless a row says otherwise.
- Fixtures: 14 synthetic screens rendered with Liberation fonts by `tools/fixtures.py` (dark and light
  terminal, browser form, chat, code editor, spreadsheet, 10–13 px text, 44 px text, low contrast, matches on the
  image edges, several matches per line and across lines, near misses only, list words and login, a dense
  9 px page), shown 1:1 fullscreen by a GTK window (`tools/viewer.py`) and captured as a monitor capture. The
  exact glyph box and whole-word box of every token are in `fixtures/truth-redacted.json` (secret values replaced
  by descriptions). Real apps: Konsole (Breeze dark at the default size, BlackOnWhite at Hack 16), xterm (dark
  12 pt, light 14 pt; GNOME Terminal's D-Bus service timed out on m74), Firefox kiosk on an HTML checkout form,
  Kate and xed on a Python settings file.
- Pixel check (`tools/check.py`): changed pixels = upload ≠ the archived `-original.png`. Every changed pixel
  must be opaque black. Every token of a Redact kind must have its whole glyph box opaque black. Every other
  token (near misses, Off kinds, Warn kinds after Upload anyway) must have no changed pixel. Changed pixels
  outside the covered tokens' words, padded 2 character widths sideways and 45% of the line height, count as
  over-covering; slivers up to 4 px thin are padding. The `-original.png` was compared with the fixture to
  prove the capture showed it 1:1. On GNOME the fullscreen viewer sat 19 px up after a fullscreen toggle, and
  the check used that offset. The pointer adds about 100 px of difference on the VMs.
- Real-app windows have no glyph truth. Their original and upload are paired in pictures and read by eye,
  and every changed pixel was checked to be opaque black.
- "Covered N …" was read from the resident log's `Notification shown` `notificationText`, and on Plasma
  and GNOME also from the desktop's own banner.
- Classes for misses: **(a)** an under-cover of a format listed in #1820's Done-when, in an ordinary
  surrounding; **(b)** anything else (recognition limits, unusual surroundings); **over-cover** (#1838
  padding or the key rule's segment covers); **count** (covered, but the notification count differs).

## Results

### Case 1: every kind on Redact automatically (agent report mode, monitor capture)

Every capture on every desktop and build uploaded with no prompt and `state: completed`. On every run,
`sensitive.covered` matched the notification's "Covered …" line, every changed pixel was opaque black, and the
archived copy equalled the upload byte for byte. The `-original.png` equalled the capture (0 differing pixels
against the fixture on m74, k72 and Budgie). Expected/covered tokens, per build:

| Fixture | a0aa444 (m74, k72, f44 identical) | b24 (m74, k72) | gate (m74 and k72 identical) | Remaining misses on gate, class |
| --- | --- | --- | --- | --- |
| F01 terminal dark | 15/17: `KEY_ID=AKIA…` missed; ghp_ URL token's first 24 chars visible | 17/17 | 17/17 | none; segment over-cover of prompt/`export` |
| F02 terminal light | 5/6 | 5/6 | 5/6 | IPv6 `…:7334/64` — (b) recognition |
| F03 browser form | 5/5; Luhn near miss covered as phone, `112` visible | 5/5, near miss untouched | 5/5, near miss untouched | none |
| F04 chat | 7/7 | 7/7 | 7/7 | none |
| F05 code editor | 10/11 (quoted key missed) | 11/11 | 11/11 | none |
| F06 spreadsheet | 10/12 (dashed Visa, MC missed; Amex as phone) | 9/12 (all 3 dashed cards missed) | **12/12** | none |
| F07 small text | 4/6 | 5/6 | 5/6 | 11 px email — (b) recognition |
| F08 large text | 3/3 | 3/3 | 3/3 | none |
| F09 low contrast | 5/6 | 5/6 | 5/6 | `198.51.100.23` #505050 on #2a2a2a — (b); count note |
| F10 edges | 5/5 | 5/5 | 5/5 | none; key segment over-cover across a row (over-cover), bottom full-width cover not counted (count) |
| F11 multi/across lines | 16/17 | 16/17 | 16/17 | `+1 555⏎010 0123` first half — (b) recognition |
| F12 near misses only | 2 near misses covered as phones | nothing covered | nothing covered | none |
| F13 list and name | 6/6 | 6/6 | 6/6 | none |
| F14 dense 9 px page | 11/11 (k72, m74), no deadline hit | — | — | — |

Real apps on gate (m74): xterm dark and light, the Firefox form and xed are fully covered, with the Luhn near-miss row untouched.
Real apps on gate (k72): Konsole dark is covered except the ~11 px email (recognition limit, #13); Kate has every key, the quoted key, the soft-wrapped JWT, the email and the IPs covered, but the wrapped hex tail `edc` stays visible (#8, class a), and this time the grey comment's `acme-build-7` / `JIRA-2210` weren't covered (they were on b24 with the window elsewhere: recognition limit, class b). Picture `misses/gate-real-kate-top.png`.
VMs, case 1 (7 fixtures each, 1280×800): Omarchy on b24 and Budgie on gate gave the same results as above,
plus two class (b) recognition limits seen only on the 1280×800 pages: the prompts read as `Llab@build-07…`
(an extra leading `L`), so the 3-letter login stayed visible in 5 of 8 prompts, and F05's grey comment line
wasn't read at all.

### Case 2: mixed Redact (card, key, list) + Warn (email, phone), IP and name Off

| Desktop | Build | Prompt shows only Warn kinds + "put.gd already covered 3 card numbers." + covered preview | Upload anyway keeps covers, Warn kinds uncovered (pixel check) | Redact and upload: editor with covers + suggestions, all covered | Cancel: local copy only (on) / nothing (off) | Tray bring-back | Hotkey region capture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| k72 | a0aa444 | pass | pass, "Covered 3 card numbers." | pass, 6 marks, no `-original`, no Covered line | pass / pass | pass (first click) | pass (Ctrl+Shift+F9, exact crop) |
| m74 | a0aa444 | pass | pass | pass | pass / pass | pass: 5 of 6 single clicks; the very first didn't, observed once and not reproduced in 4 retries | pass |
| m74 | b24 | pass ("an email address and a phone number") | pass, archive copy = upload, original = capture | pass | pass / pass | — | — |
| f44 | a0aa444 | pass | pass (after Alt+Tab) | — | — | **left click opens put.gd's tray menu; status row "Preparing upload…"; no raise item** | — |
| f44 | b24 (with #1831) | pass | pass | — | — | tray left click still opens the menu; **the notification "A capture is waiting for your decision" → Show brings it back** | — |
| Omarchy | b24 | pass (+ waiting notification with Show) | pass | — | — | pass (tray icon in the bar) | — |
| Budgie | gate | pass (+ waiting notification with Show) | pass | — | — | pass (tooltip "Waiting for your decision") | — |
| k72, m74 | a0aa444, b24 | 13 fixtures in agent mode: pauses only where a Warn kind is left; `operation.decide upload` keeps every Redact cover (pixel check) | | | | | |

### Case 3: Off kinds untouched

Only card on Redact, the rest Off (F02, F04, F06, F11 on k72 and m74): no Off-kind token changed. The only changed
pixels were card covers (a date that shares a CSV word with a card is covered with its word, by design).

### Case 4: unfinished check still prompts, with every kind on Redact automatically

| Reason | How | Seen on | Result |
| --- | --- | --- | --- |
| `language_missing` | second recognition language `zzz` | k72, m74, f44 (a0aa444); m74, k72 (b24); Omarchy (b24); Budgie (gate) | always paused; on-screen title "put.gd couldn't finish checking this capture" with the covered kinds and the reason; Upload anyway kept every cover (pixel check); notification had **no** Covered line |
| `recognition_failed` | 5400×4400 (23.8 MP) dense 9 px file, via `upload.files` | k72, m74 (a0aa444) | paused after about 21 s; Upload anyway uploaded |
| `too_large` | 5200×5000 (26 MP) file | k72, m74 (a0aa444) | paused at once |
| deadline / `truncated` | 1920×1080 dense 9 px screen (F14) | k72, m74 | not reached: completed in about 22 s, 11/11 cards covered |

### Case 5: agent control

`settings.patch` of `kinds` through `putgd-cli` on every desktop. The MCP helper (`tools/mcp`, locked `uv sync`) on k72:
`patch_configuration` with `kinds`, `perform_action monitor`: all-Redact completed on its own with
`sensitive.covered`; mixed paused in `sensitive_text_found` with `found {email:1, phone:3}` and `covered {list:2}`,
and `decide_upload upload` completed it with the covers kept (pixel check pass for both). m74 has no `uv`, so the
MCP run is k72 only.

### Case 6: file-manager style upload

`upload.files` with 2 files and with all 13 fixture files (k72, m74, a0aa444): each file covered exactly as its capture
was. 13 objects uploaded and 13 `<name>-original.png` copies archived, byte-identical to the user's files. The user's
files were unchanged (sha256), and the private `covered/` staging folder was empty afterwards. One notification
gave the totals ("13 files uploaded. Covered 15 email addresses, …").

### Settings

- Real Settings window, Apply to all kinds → Redact automatically, on k72 and m74: all seven kinds saved as `redact`.
- Older `{"enabled": true, "categories": ["card"]}` (b24, m74 and k72): Settings shows Card numbers = Warn and the
  other six Off; the config file's SHA-256 was unchanged after opening and browsing Settings; changing one choice
  rewrote it as `kinds` with card kept on warn.

## Misses and notes

| # | Build | Where | What | Class | Status on gate | Picture |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | a0aa444 | F01, real terminals | `AWS_ACCESS_KEY_ID=AKIA…` not covered | (a) | fixed | `misses/a0-F01-key-after-equals-and-ghp-url.png` |
| 2 | a0aa444 | F01 | `https://ghp_…@github.com/…`: first 24 chars visible | (a) | fixed | same |
| 3 | a0aa444 | F05, Kate | quoted `"AKIA…"` not covered | (a) | fixed | `misses/a0-F05-quoted-key.png` |
| 4 | a0aa444, b24 | F06 | dashed cards in a table row after an IPv4 | (a) | fixed on gate | `misses/a0-F06-dashed-cards.png`, `misses/b24-F06-dashed-cards-regression.png`, `misses/gate-F06-dashed-cards-covered.png` |
| 5 | a0aa444 | F03, F12, real apps | Luhn-failing 4-4-4-4 covered as a phone, part left visible | near miss covered | fixed | `misses/a0-F03-luhn-near-miss-covered-as-phone.png`, `misses/a0-F12-near-misses-covered-as-phone.png` |
| 6 | a0aa444 | Kate | soft-wrapped JWT: only the last visual line covered | (a) | fixed on b24 | `misses/a0-real-kate-jwt-hex-quoted.png` |
| 7 | b24 | xed | `"“AKIA…"` (recognition adds a curly quote) not covered | (a) | fixed on gate | `misses/b24-real-xed-quoted-key-missed.png`, `misses/gate-real-xed-covered.png` |
| 8 | a0aa444, b24 | Kate | soft-wrapped 64-hex secret: 3-letter tail `edc` on the next line visible | (a) | **open on gate (k72 Kate)** | `misses/b24-real-kate-hex-tail-edc.png`, `misses/gate-real-kate-hex-tail-edc.png` |
| 9 | all | F02 | IPv6 `2001:db8::8a2e:370:7334/64` | (b) recognition | open | `misses/gate-F02-ipv6-recognition-limit.png` |
| 10 | all | F07 | 11 px sans email | (b) recognition | open | `misses/gate-F07-11px-email-recognition-limit.png` |
| 11 | all | F09 | `198.51.100.23` #505050 on #2a2a2a | (b) recognition | open | `misses/gate-F09-dark-ip-recognition-limit.png` |
| 12 | all | F11 | phone split across lines: first half | (b) recognition | open | `misses/gate-F11-phone-split-recognition-limit.png` |
| 13 | a0aa444 | Konsole default ~11 px | email not covered (covered at Hack 16) | (b) recognition | — | `misses/a0-real-konsole-dark-email-missed.png` |
| 14 | a0aa444 | Konsole BlackOnWhite | CSV `2,5555-5555-5555-4444,…`, `2,5555-` visible | (b) recognition (matcher covers the exact word) | — | `misses/a0-real-konsole-light-dashed-card-partial.png` |
| 15 | VMs | 1280×800 F01, F05 | `Llab@…` read with an extra `L`; grey comment not read | (b) recognition | open | `misses/b24-omarchy-F01-Llab-recognition-limit.png`, `misses/b24-omarchy-F05-comment-not-recognized.png` |
| 16 | all | F01, F10 | key segment covers take whole terminal lines or a long row (prompt, `export`, a date 700 px away) | over-cover (segment) | open | `misses/gate-F01-all-keys-covered.png`, `misses/gate-F10-segment-over-cover-and-count.png` |
| 17 | all | F10, F09 | a cover over a phone/IP or a dark card+phone row not counted by kind | count | open | same |
| 18 | a0aa444, b24 | f44 GNOME | tray left click opens the menu, whose status row reads "Preparing upload…" while the prompt waits; no menu item raises the prompt | #1806 behaviour | the waiting notification's Show brings it back (b24) | `pictures/f44-b24-tray-left-click-opens-menu.png`, `pictures/f44-b24-waiting-notification-show.png`, `pictures/f44-b24-prompt-restored-by-show.png` |
| 19 | a0aa444 | m74 | first tray click after covering didn't restore the prompt | observed once | not reproduced in 4 retries | — |

## Pictures

- `pictures/settings-annotated.png`: m74, b24 build, Settings → Capture → Text recognition with per-kind choices and the Apply to all kinds menu.
- `pictures/prompt-annotated.png`: m74, b24 build, the mixed prompt: the Warn kinds, "put.gd already covered 3 card numbers." and the covered preview.
- `pictures/pair-F01-annotated.png`, `pair-F03-annotated.png`, `pair-F04-annotated.png`, `pair-F13-annotated.png`: before (the archived `-original.png`) and after (the uploaded object) on m74, b24 build.
- Per-desktop frames in `pictures/` (prompts, editor, unfinished prompt, tray bring-back, the GNOME menu and notification).

All annotations were drawn with put.gd's own editor in a headless private resident of the b24 package
(`tools/annotate.py`: `editor.open`, `editor.apply` rectangle/arrow/text in `#D7263D`, width 4, `editor.saveCopy`).

## Files

- `runs/<desktop>[-final|-gate].jsonl`: one line per check: operation id, state, `sensitive`, notification text,
  pixel-check summary and archive checks. `runs/*-receipt.json`: driver receipts with build diagnostics and state timelines.
- `runs/m74-b24-f06-recognize.json`: what recognition returned for F06's card cells.
- `fixtures/`: the 1920×1080 fixtures and their token boxes, with secrets replaced by descriptions.
- `tools/`: the driver, viewer, fixture generator, pixel checker, review and annotation scripts.

## Lab notes

- Every physical desktop was taken with `tools/lab/desktop_lock.py` from `origin/nightly`, one at a time, and released
  `--verified-clean`. Installed packages were removed after each pass. On f44 the RPM was removed with
  `--noautoremove` and GDM restarted, so `putgd@put.gd` is gone and AppIndicator is ACTIVE.
- The Omarchy (`o1`) and Budgie (`b1`) overlays on d69 were stopped with `lab.py reset`. `lab.py cleanup` refused to
  delete their disks ("Recorded base is outside its canonical golden/base root") because the run checkout
  (`~/work/a21lab`) isn't the one that holds the goldens. After checking that no `qemu` process existed and that nothing
  had either disk open (`fuser`), every file in each run directory was deleted by exact path with `rm -f`, and the
  empty directories were removed with `rmdir`: `o1` (26 entries, including `disk.qcow2` 252,968,960 bytes, 11
  preflight PPMs, `qemu.log`, `qmp.sock`, `state.json`, the run identity and `vars.fd`) and `b1` (15 entries, including
  `disk.qcow2` 66,781,184 bytes). The goldens were never touched. The guests' driver receipts are in `runs/omarchy-receipt.json`
  and `runs/budgie-receipt.json`.
