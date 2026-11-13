# Issue 1428: Copy text from the hotkey, the tray entry and the window button with the real helper, m74

The first package that holds both the real `putgd-ocr` and the command band button and tray entry: CI run 43382317494 of put.gd-desktop #1439 (the integration branch at `5c925f891`, after #1442 and #1438 merged), merge commit `0c577368074d68d2e29aef448058b007eca7e6a7`, version `26.1113.4814~dev+g0c577368074d`, Ubuntu 24.04 DEB sha256 `bd050cb6fb901079ba6b9dcf8162e1efc5663e468d175a0b0dd713c2652bc66a`.

Desktop: m74, Linux Mint 22.3 Cinnamon X11, adapter `cinnamon-core-x11`, distribution Tesseract 5.3.4. Each trigger selected the same 282 x 240 px region over 12 lines of a synthetic text window, and the clipboard was read back with `xclip` after a sentinel had been put there.

| Trigger | Paste | Timings from `text.inspect` | Helper |
| --- | --- | --- | --- |
| Hotkey, Ctrl+Shift+9, real key events | 518 characters, 12 lines | spawn 15, engine start 155, recognize 342, total 520 ms | peak RSS 46,568 kB, exit 0 |
| Tray entry, dbusmenu `Event(41, "clicked")` | the same 518 characters | spawn 19, engine start 152, recognize 349, total 529 ms | peak RSS 46,904 kB, exit 0 |
| Window button "Copy text", real pointer click | the same 518 characters | spawn 21, engine start 155, recognize 345, total 529 ms | peak RSS 46,908 kB, exit 0 |

- In all three pastes 517 of 518 characters are right: line 1 reads "text Fixture" for "text fixture", as in the first-light run on this desktop. The receipt says `"passed": false` for that reason alone (the script compares the lines exactly).
- Resident RSS / PSS: 8,208 / 4,363 kB before, 22,000 / 12,575 kB right after, 8,424 / 5,396 kB 180 s after the third capture. None of libtesseract, libleptonica, liblept, libZXing, libcurl or libarchive in its maps then; libgomp is mapped. No `putgd-ocr` process afterwards.
- No text operation left in the journal, and the fixture's words in no file under the resident's private folders.
- `pictures/window-before-click.png` is the frame the click position was read from; `pictures/selector-after-click.png` is the selector that click opened (put.gd hides its own window while selecting, as for a capture).

Method as in `2026-11-13-issue-1428-first-light` (`scripts/text_proof.py --first-light`, `scripts/helper_watch.py`).

Two things to know when reading the numbers:
- Another session was running its own `putgd-ocr` tests on m74 over SSH during this run (134 helper processes whose parent was `test_ocr_run`). The watcher saw them; they are removed from the published receipt and log, which keep the three runs whose parent was this resident. The host was therefore not idle.
- `putgd-ocr --version` still printed nothing and exited 5 on this build.

No put.gd package was installed on m74 before the run, and none is installed after it; the lock was released with the tool's cleanup check passing.
