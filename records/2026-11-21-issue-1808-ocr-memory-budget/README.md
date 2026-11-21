# Issue 1808: text recognition memory budget raised to 320 MiB

Acceptance for [put.gd-desktop#1809](https://github.com/patrick-hudson/put.gd-desktop/pull/1809), which raises the `putgd-ocr` job budget that gates extra recognition engines from 128 to 320 MiB for English (384 MiB at most with other languages) and `RLIMIT_DATA` from 192/288 to 480/576 MiB.

**Build.** CI packages from head `609c8a64e014ade30f3689ea6289c897ace8a77d` (tree `7825beb760b0e64b0655b4a37f38785f8250f24b`, CI run 44960759852): DEB `putgd_26.1121.6186~dev+g609c8a64e014_amd64.deb` (ubuntu26.04, sha256 `002d0860e5c35a99d94b9f3d212526b0c50dbbd66e435d9ac3ddb53840b4419a`) and AppImage `putgd-26.1121.6186-dev+g609c8a64e014-x86_64.AppImage` (sha256 `183585d8d1352a23f6b105cc172b1a036e3d71ed4a50b182e5695d47044b1529`). `putgd-ocr --version-json` reported that commit. The aurora before is the published nightly 26.1121.6060 AppImage (sha256 `e1495a3d2b831fc507b445b28c22934c210b08df58c7cff44ad6bf0b955d3cc5`), which differs from the candidate in `src/ocr` and `TextJob` only by this change.

**Method.** The 176-capture corpus (`records/2026-11-13-issue-1428-corpus-index`) went through each package's own resident and helper: a private, offscreen resident (`scripts/fileocr.py`) is asked for `text.recognize` with `source: file` and the result read with `text.inspect`. Times are the job's `totalMs` (spawn to result). The peak is the largest `VmHWM` of the `putgd-ocr` child, sampled every 5 ms. The scorer is the #1805 harness (`bench.py`, branch `research/ocr-speed-1805`). On k72 the before is today's helper built from the #1805 research tree (nightly with its bench-only knobs off), linked to the same distro `libtesseract`, and driven by `test_ocr_run`. A test driver cannot talk to a CI-built helper, because the handshake requires the same build manifest.

## Results

| Host, input | Before | After | Peak before → after |
| --- | --- | --- | --- |
| k72 DEB, all 176 captures (sum) | 186.3 s | 180.8 s, 181.5 s | 124 → 130 MiB |
| k72, 1080p screens (median of 22) | 1.12 s | 1.06 s, 1.04 s | 76 → 113 MiB |
| k72, screens of 4 MP or more (mean of 4) | 4.07 s | 3.14 s, 3.06 s | 112 → 130 MiB |
| k72, GNOME 4K light / dark | 6.04 / 7.58 s | 5.81 / 4.30 s, 5.53 / 4.26 s | 95 → 130 MiB |
| k72, dense 24 MP page (cut at 16 s) | 48,546 characters | 66,138 to 70,602 characters | 117 → 172 MiB |
| aurora-amd AppImage, all 176 (sum) | 59.9 s, 60.2 s | 62.1 s, 69.7 s (second run under load from another session) | 82 → 90 MiB |
| aurora-amd, GNOME 4K light / dark | 2.11 / 1.63 s | 2.06 / 1.83 s | 82 → 90 MiB |
| aurora-amd, dense 24 MP page (same 211,696 characters) | 15.35 s | 12.8 s | 123 → 139 MiB |

- **Text.** Byte-identical to the before on 176 of 176 captures in every after run: twice on k72 and twice on aurora-amd.
- **Failures.** None. No job in the corpus or on the dense page was stopped by `RLIMIT_DATA`.
- **Peak.** The highest measured peak is 172 MiB (the dense 24 MP page on k72), inside the 320 MiB budget. The corpus peaks at 130 MiB.
- **Speed.** On k72 large screens are 23% faster on average. On aurora-amd the AppImage's bundled engine peaks at only 82 to 90 MiB, so the 128 MiB gate never limited it there and the corpus is unchanged. Only the dense page, which reached the old gate, finishes faster. The real helper gains less than the #1805 in-process benchmark did: a 4K job spends its first second or so on one thread, in the emoji scan and page analysis, before the engines start.
- **Load.** The `*.load` files record `uptime` before and after each run. k72 had no other jobs. The aurora-amd runs overlapped another session's `run95` jobs from 23:29 to about 23:38 UTC, which slowed `i1808-appimg-after2` most.

## Live Copy text on a 4K screen (k72)

`scripts/live4k.sh` ran a nested KWin Wayland session (`kwin_wayland --virtual`, 3840x2160) with plasmashell, KWrite and the installed candidate package's resident. `text.recognize` with `source: monitor, copy: true` captured the whole 4K output through KWin's ScreenShot2, recognized it and copied the text. `live-4k-k72/frame.png` is the same screen, captured by Spectacle right after.

- State `completed`, 4,317 characters, `copyStatus: copied`, not truncated.
- `totalMs` 3,728 (spawn 149, engine start 129, recognition 3,352).
- `wl-paste` gave exactly the recognized text.
- The helper ran four threads and peaked at 157 MiB (160,944 KiB).

The put.gd window opened on its first start and covers part of KWrite. The Konsole window did not appear.

## Confinement

`ocr_confinement_integration` passed in PR CI at this head on Ubuntu 24.04 and 26.04 (run 44960790716). Its probe now uses the helper's 576 MiB data limit.

## Files

- `k72/`, `aurora-amd/`: rows and summaries of each run (`rows.json` holds the text), `*.load`, and `cmp-*.json` (`scripts/cmp.py`).
- `dense24.txt`: the dense page runs.
- `live-4k-k72/`: the 4K frame, the result, the paste and the logs.
- `scripts/`: the drivers.
