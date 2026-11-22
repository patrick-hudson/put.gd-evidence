# #1812: text recognition on up to eight engines

Acceptance for [#1812](https://github.com/patrick-hudson/put.gd-desktop/issues/1812), PR [#1817](https://github.com/patrick-hudson/put.gd-desktop/pull/1817), on the CI candidate packages of its final head.

- **After:** `54e1aedf9d17a317ec427887cd46ffe8ae6d9fea` (tree `c2ddf2be4de87a09464c34643f452bb46d119ed1`), CI run 44967471715: `putgd-26.1122.6195-dev+g54e1aedf9d17-x86_64.AppImage` and `putgd_26.1122.6195~dev+g54e1aedf9d17_amd64.deb` (Ubuntu 26.04).
- **Before:** #1809's head `609c8a64e014ade30f3689ea6289c897ace8a77d`, which is nightly `b55d8e331` for the helper, CI run 44960759852, the same two package kinds.
- **What runs.** Each package's own resident runs from the unpacked package (AppImage `--appimage-extract`, deb `dpkg -x`) with private XDG directories. Every capture goes `text.recognize source=file` through `scripts/fileocr.py`, which records the helper's VmHWM. Nothing was installed on either host.
- **Corpus.** The 176 hand-transcribed #1428 captures, plus the dense 24 MP synthetic page (`dense24.png` from the #1805 harness) three times and the four 4 MP+ screens five times.

## aurora-amd (Ryzen 5 PRO 8500GE, 6 cores and 12 threads, AppImage): 8 engines

Pair 3 (`pkga-before-3`, `pkga-after-3`, 01:37 to 01:42Z) had nothing but these runs on the host. Pairs 1 and 2 agree; pair 1's before overlapped another session's build.

| | Before (4 engines) | After (8 engines) |
| --- | --- | --- |
| Corpus, 176 captures | 86.1 s | 78.5 s (−9%) |
| 4 MP+ screens, mean of medians (×5) | 1.31 s | 1.16 s (−11%) |
| GNOME 4K light / dark | 2.21 / 1.70 s | 2.00 / 1.49 s |
| Dense 24 MP page (×3) | 12.8 s | 9.0 s (−30%) |
| Peak, corpus | 90 MiB | 138 MiB |
| Peak, dense page | 139 MiB | 204 MiB |
| Text against before | | identical, 176/176 (all three pairs) |

Every class's median error is unchanged. The memory budget is 320 MiB, with a 312 MiB gate and `RLIMIT_DATA` at 480 MiB. The dense page reports `truncated: true` in both packages, with the same 211,696 characters.

## k72 (i5, 4 cores, Kubuntu 26.04, deb): nothing changes

| | Before | After |
| --- | --- | --- |
| Corpus | 215.6 s | 214.5 s |
| Peak | 129 MiB | 134 MiB |
| Dense page | 15.6 s, truncated at the 16 s budget, 70,602 chars | 15.7 s, the same 70,602 chars |
| Text | | identical, 176/176 |

## Dev-build runs that chose the change (aurora-amd, `test_ocr_run` + `putgd-ocr`)

Engine counts were set with `taskset` (CPUs 0-3, 0-5, 0-11).
- **`i1812-dev2-*`: cuts that follow the engine count.** The text differed from 4 engines on 47 captures at 6 engines and 29 at 8, within the quality bars.
- **`i1812-dev3-*`: the memory-gate fix.** Before it, with 8 engines a GNOME 4K screen ran on one engine: a task measured beside seven engine starts showed 79 MiB, so every extra worker found no room and quit. In `i1812-4k-*` the dark screen took 3.08 s at 8 engines against 1.86 s at 4. After it, every engine takes tasks.
- **`i1812-dev4-*`: the shipped change, cuts kept as for four engines.** Text was identical to today's helper on 176/176 at 4, 6 and 8 engines. Corpus 76.5 / 69.3 / 69.4 s; dense page 13.8 / 10.5 / 10.5 s.

On aurora's 12 threads, six and eight engines gave the same times.

## Files

- `aurora-amd/`, `k72/`: one directory per run, holding `rows.json` (per-capture text, times, peak) and `summary.json`, plus the `.load` (uptime before and after) and `.log` files. `dense*.txt` holds the dense-page lines.
- `scripts/`: `acc.sh` and `accaur*.sh` (packaged runs), `fileocr.py` (from the #1808 record), `time*.sh` and `k72check.sh` (dev-build runs), and `sum.py` and `cmp.py` (summaries and text identity). `bench.py` is on branch `research/ocr-speed-1805` under `tools/research/ocr1805/`.
