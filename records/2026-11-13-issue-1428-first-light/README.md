# Issue 1428: first light of Copy text with the real helper, m74 and d69

The first runs of Copy text on real desktops with the real `putgd-ocr` from a CI-built package: a real hotkey press, a region dragged over a window of synthetic text, and the text read back from the clipboard by a client that is not put.gd.

**Package.** CI run 43374707146 of the packaging pull request (put.gd-desktop #1438, head `14b487034`), which built merge commit `6ab1a80605bf71538e8837e6e92ba974ea21d7fb`, version `26.1113.4778~dev+g6ab1a80605bf`. That tree holds the resident item (#1440), the engine (#1431) and the packaging item; it does not hold the command band button or the tray entry (#1442), so the hotkey is the trigger here.

| | m74 | d69 |
| --- | --- | --- |
| Desktop | Linux Mint 22.3, Cinnamon X11, adapter `cinnamon-core-x11` | Debian 13, Plasma Wayland, adapter `kde-wayland` |
| Package | Ubuntu 24.04 DEB, sha256 `07eb2cc0570fe7760bbca0c60948c356448e2fca4df9e5de7ea645734ba0c849` | Debian 13 DEB, sha256 `bafca955f869b9c5041fb7691983415b98166c5003c5db6753ce573ecb696b0f` |
| Engine libraries (distribution) | libtesseract5 5.3.4, liblept5 1.82.0, libzxing3 2.2.1, tesseract-ocr-eng 4.1.0 | libtesseract5 5.5.0, libleptonica6 1.84.1, libzxing3 2.3.0, tesseract-ocr-eng 4.1.0 |
| Hotkey | Ctrl+Shift+9, bound as asked | Ctrl+Shift+9, which KDE reports as `Ctrl+(` |
| Region | 282 x 240 px over 12 lines of a text window | 278 x 216 px over the same 12 lines |
| Paste | 518 characters; 517 right: line 1 came back as "text Fixture" (capital F), the other 11 lines exact | 518 characters, all 12 lines exact |
| Stage timings (`text.inspect`) | spawn 28 ms, engine start 153 ms, recognize 353 ms, copy 0 ms, total 543 ms | spawn 22 ms, engine start 143 ms, recognize 364 ms, copy 0 ms, total 538 ms |
| Helper | peak RSS 47,056 kB (46.0 MiB), lived 543 ms, exit code 0, no signal; no `putgd-ocr` process afterwards | peak RSS 48,024 kB (46.9 MiB), lived 537 ms, exit code 0, no signal; none afterwards |
| Resident before (RSS / PSS) | 8,288 / 4,714 kB | 8,688 / 4,490 kB |
| Resident right after | 21,504 / 12,306 kB | 27,184 / 11,078 kB |
| Resident 180 s after | 8,400 / 4,808 kB | 9,632 / 5,034 kB |
| Resident's mapped files 180 s after | 68 files; none of libtesseract, libleptonica, liblept, libZXing, libcurl, libarchive; libgomp is mapped | 101 files; none of those; libgomp is mapped |
| Left behind | no text operation in the journal; the fixture's words in no file under the resident's private folders | the same (the two kept region captures of the Repeat check are the only operations) |

**Repeat last region (d69).** Before the text capture, a region capture of a 300 x 100 rectangle was kept as a local copy. After the text capture (278 x 216), `repeat` was invoked: `capture.repeat.remembered` was true and the picture it saved is 300 x 100. Repeat still uses the earlier rectangle.

## How it was measured

- `scripts/text_proof.py --first-light` on each desktop, under that desktop's lock. It starts the installed resident in the running session with private configuration, data, state and cache folders, assigns the hotkey through `settings.patch` (it is unassigned by default), opens the fixture, puts a sentinel on the clipboard, presses the hotkey with real key events (`tools/lab/host_input.py`, kernel uinput devices), drags the region with real pointer input, and pastes with `xclip` (X11) or `wl-paste` (Wayland).
- The region was read off one frame of the desktop taken with the fixture up (`pictures/`), because the text sits wherever the desktop put the window.
- **Helper peak and exit:** `scripts/helper_watch.py`, run as root, listens on the kernel's process connector. It sees the helper's exec and exit without touching the resident or wrapping the helper, polls `/proc/PID/status` about every half millisecond while it lives (785 and 793 samples) and keeps the last `VmHWM`, the kernel's own high-water mark, which only grows. The exit code is the one in the kernel's exit event. The helper's parent was the resident's PID in both runs.
- **Resident memory:** `Rss` and `Pss` from `/proc/PID/smaps_rollup`, 20 s after the hotkey was assigned and the fixture opened ("before"), about 1.5 s after the paste ("right after"; on d69 after the Repeat capture too), and 180 s after the text capture ended. On d69 the earlier region capture and the Repeat capture fall inside that window, so its numbers include them.
- **Maps:** every file path in `/proc/PID/maps` of the resident at the 180 s mark; the full list is `firstLight.mappedFiles` in each receipt.
- The paste was compared with the fixture's lines exactly. The m74 receipt says `"passed": false` for that reason alone: one letter of 518 differs.

## Not shown

- `putgd-ocr --version` printed nothing and exited 5 on this build (the helper has no version switch yet; the packaging worker reported it on the issue).
- One small region per desktop. Nothing here is a statement about accuracy, large regions, several languages, QR codes or speed in general.
- Both desktops already had the distribution's Tesseract, Leptonica and ZXing libraries installed (the engine work put them there), so `apt-get install ./putgd_*.deb` had nothing further to fetch: the dependency lines were satisfied, not exercised from a clean system.
- No put.gd package was installed on either desktop before the run (other sessions install and remove their own), and none is installed after it.

Everything on screen was synthetic: a text window the run opened, and put.gd's own window.
