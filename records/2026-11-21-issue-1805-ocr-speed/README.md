# Issue 1805: OCR speed research raw timings

These are the raw timings behind the recommendation on
[#1805](https://github.com/patrick-hudson/put.gd-desktop/issues/1805): keep and tune Tesseract,
and don't replace it. The follow-ups are
[#1808](https://github.com/patrick-hudson/put.gd-desktop/issues/1808) (the memory gate keeps
large screens on one engine, and the emoji scan can overlap recognition) and
[#1812](https://github.com/patrick-hudson/put.gd-desktop/issues/1812) (the engine cap of 4).
This is research, not acceptance of a put.gd build.

## What was measured

- **Corpus.** The 176 hand-transcribed captures of #1428: the manifest in
  `records/2026-11-13-issue-1428-corpus-index/` and the seven per-desktop records it names.
  The two synthetic 24 px pages of the 178-image set were left out. Accuracy is the character
  error rate against the hand transcripts, and against today's output as "CER vs today", which
  is the `baseline` run of the same host.
- **Synthetic dense page.** `aurora-amd/synth/dense24.png` (SHA-256 `42a4ad5e…b03d037`): the
  dense m74 terminal capture tiled to 6000 by 4000.
- **Tesseract runs** use `bench_ocr_method`: the helper's `recognizeImage` in process, with
  `--budget 16000 --memory 128` as the helper sets them and `OMP_THREAD_LIMIT=1`. The `helper`
  run goes through `test_ocr_run` and the real confined `putgd-ocr`. It gave byte-identical text
  to `baseline` on all 176 captures, on aurora-amd and on k72.
- **One process per capture.** `bench.py` records wall time, CPU time (user plus system, from
  wait4), the child's peak RSS and the engine's own VmHWM (`peakKiB`, which excludes the image
  decode).
- **Labels.**
  - `t-` runs are the 50-capture timing subset in `harness/timing-ids.txt`: every monitor
    capture plus the four densest captures of each other class.
  - `w-`, `g-`, `rapidocr-*` and `hybrid-*` are the engine worker's candidate runs.

## Builds and hosts

- **Source.** Branch `research/ocr-speed-1805` (head `57fc8a450`), from nightly `9f2b98ca7`.
  The research-only knobs are in `harness/research-knobs.patch` and are not for merge. The
  builders built `bench_ocr_method`, `putgd-ocr` and `test_ocr_run` at its intermediate commits,
  adding knobs; no default changed.
- **Tesseract on each host:**

  | Host | Tesseract | Notes |
  | --- | --- | --- |
  | aurora-amd | 5.5.4 (Fedora 45 `putgd-build` toolbox) | Ryzen 5 PRO 8500GE, 6 cores and 12 threads |
  | k72 | 5.5.0 (Kubuntu 26.04) | 4 cores |
  | m74 | 5.3.4 (Mint 22.3) | i5-6500T, 4 cores |

- **English data.** The same `eng.traineddata` on every host, SHA-256
  `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2` (tessdata_fast, 4,113,088
  bytes).

## Validity of each host's timings

- **k72 `t-` runs** are the clean timings: no other job was running, and the load before and after
  each run is in `k72/runs/k72/t-*.load`.
- **m74 `t-` runs.** Load was 2.5 to 3, because another session's replay process used about one
  core. `t-baseline` overlapped the worker's GPU test, so use `t-baseline2`.
- **aurora-amd wall times** in `noinv`, `rows16`, `rows20`, `maxs1` and `maxs2` overlapped the
  worker's RapidOCR runs and another session's compile, so they hold for accuracy only.
  `threads6` ran with the whole machine held. `x-threads8-partial` was stopped and is unused.
  `x-omp-unlimited-partial` is a discarded run without `OMP_THREAD_LIMIT`.

## Results

Per-host tables of every run are in `aurora-amd-runs.md`, `k72-runs.md` and `m74-runs.md`
(made by `harness/compare.py`). The "4K s" column is the mean over captures of 4 MP or more.

- **No change in speed or accuracy:**
  - Tesseract's inverted-line retry off;
  - a 2× or 3× scale cap, or a 20-row text-height target;
  - dictionary off;
  - Sauvola thresholding;
  - 1, 2 or 4 strips per engine;
  - a smaller pixel cap on 4K screens.
- **Worse:**
  - page segmentation 4 breaks editor code and terminals;
  - OpenMP inside one engine is slower than four separate engines;
  - a 1× scale cap makes small interface text fail its bar;
  - reading one line per Tesseract call (psm 7 or 13) is slower and less accurate.
- **The real win is the memory gate (#1808).** With `--memory 0` the text is byte-identical.
  On k72, the screens of 4 MP or more went from 5.18 s to 2.75 s and the 1080p median from 1.15 s to
  0.94 s. The peak rose from 115 to 162 MiB. On the dense 24 MP page, the peak at 4 engines was
  258 MiB, and the job ran under `prlimit --data` at 320, 384 and 480 MiB.
- **The emoji scan overlapped with recognition** (#1808 comment): on m74, the GNOME 4K screens
  took 5.37 and 3.87 s, against 5.89 and 4.43 s with the gate off alone. The text is
  byte-identical.
- **6 engines on aurora-amd** (#1812): the screens of 4 MP or more went from 1.78 s to 1.09 s,
  and the peak was 199 MiB.

### Candidate engines

The engine worker's runs, summarised:

- **PP-OCRv6-tiny**, on ONNX Runtime through RapidOCR, Apache-2.0, is the only candidate that
  survived the deal-breakers. On m74, its engine-only time on a 4K screen was 4.27 s, against
  8.2 s for today's helper. It is slower on 1080p screens and on regions. It peaks at about
  950 MiB on 4K and uses about 2.5 times the CPU-seconds.
- **Dropped:** PP-OCRv5-mobile, PP-OCRv6-small, OnnxTR/docTR, ocrs (CC BY-SA weights),
  EasyOCR and Surya (licence).
- **The hybrid** (a PP-OCR detector, then Tesseract reading each line) is accurate but not faster.
- **GPU:**
  - On the Radeon 740M, WebGPU is slower than the CPU, and ncnn-Vulkan crashes on 4K.
  - On the HD 530, WebGPU is about 10% faster, and ncnn-Vulkan returns wrong text with no error.
  - ROCm and OpenVINO GPU are blocked on this hardware.

Downloaded wheels, models and binaries are listed with their SHA-256 in each host's
`engines/*/SHA256SUMS`. The worker's tools are in `engines/tools*`.
