# #1815: the emoji scan runs alongside text recognition

Acceptance for [#1815](https://github.com/patrick-hudson/put.gd-desktop/issues/1815), PR [#1824](https://github.com/patrick-hudson/put.gd-desktop/pull/1824), on the CI candidate packages of its head.

- **After:** `0f275bd46502c4c973d761b271418d4b497bdd15`, CI run 44973525777: `putgd-26.1122.6227-dev+g0f275bd46502-x86_64.AppImage` and `putgd_26.1122.6227~dev+g0f275bd46502_amd64.deb` (Ubuntu 26.04).
- **Before:** nightly `d339ef373` for the helper, which is #1817's head `54e1aedf9d17a317ec427887cd46ffe8ae6d9fea`, CI run 44967471715, the same two package kinds.
- **What runs.** Each package's own resident runs from the unpacked package with private XDG directories. Every image goes `text.recognize source=file` through `scripts/fileocr.py`, which records the helper's VmHWM. Nothing was installed.
- **Corpus.** The 176-capture #1428 corpus, the dense 24 MP page (×3), the four 4 MP+ screens (×5), and the 26 region crops of the #1748 round-2 emoji desktop record (`records/2026-11-21-issue-1748-copy-text-emoji-desktops-round-2`, every `*-region.png`, ×3).

## aurora-amd (Ryzen 5 PRO 8500GE, 6 cores and 12 threads, AppImage)

02:17 to 02:28Z, with before and after alternating twice and nothing else running on the host.

| | Before (#1817) | After (#1824) |
| --- | --- | --- |
| Corpus, 176 captures | 75.2 / 75.8 s | 66.8 / 67.7 s (−11%) |
| 4 MP+ screens, mean of medians (×5) | 1.15 / 1.16 s | 0.97 / 0.97 s (−15%) |
| GNOME 4K light / dark | 1.98 / 1.47 s | 1.75 / 1.20 s |
| Dense 24 MP page (×3) | 9.05 s | 8.2 s (−9%) |
| Peak, corpus / dense page | 140 / 203 MiB | 141 / 205 MiB |
| Corpus text against before | | identical, 176/176 (both pairs) |
| #1748 emoji crops | | identical text, emoji included, 26/26 in every run; 299 emoji a pass |

## k72 (i5, 4 cores, Kubuntu 26.04, deb)

| | Before | After |
| --- | --- | --- |
| Corpus | 212.3 s | 194.4 s (−8%) |
| 4 MP+ screens, sum | 13.0 s | 11.6 s |
| Peak, corpus | 133 MiB | 135 MiB |
| Corpus text | | identical, 176/176 |
| #1748 emoji crops | | identical, 26/26 in every run |
| Dense page (16 s budget) | truncated, 66,138–70,602 chars | truncated, 83,839–88,190 chars |

On four cores the dense page reaches the time budget either way. Without the serial scan in front, recognition gets further before the cut, so more of the page is read. On smaller emoji crops the peak is about 15 to 20 MiB higher, because the scan's pages now overlap the engines' start. They peak at 37 to 80 MiB, far under the budget.

The dev-build helper run on aurora (`i1815-dev-e8`, `test_ocr_run` + `putgd-ocr`) agrees: corpus 69.4 → 60.9 s with text identical on 176/176.

## Files

- `aurora-amd/` and `k72/`: one directory per run, with `rows.json` and `summary.json`, plus `.load`, `.log` and `.start`. Also `emoji-*.jsonl` (each crop's text and emoji, three runs) and `dense-e1815.txt`.
- `scripts/`: `accaur-1815.sh`, `k72-1815.sh`, `acc.sh`, `emoji.sh`, `emojicmp.py`, `fileocr.py`, `sum.py`, `cmp.py` and `time5.sh`.
