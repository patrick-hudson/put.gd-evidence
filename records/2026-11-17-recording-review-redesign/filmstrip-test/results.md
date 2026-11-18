# Filmstrip performance

## Answers

1. **A meets both budgets on m74 at 4K60.** The first two of 12 keyframe tiles took **153 / 156 ms** (warm median / p95) and the full strip took **424 / 433 ms**. The cold run took **176 ms** for two and **490 ms** for twelve. **B meets the first-two budget only.** Two exact tiles took **555 / 565 ms**, and all twelve took **2.665 / 2.682 s**. Cold was **582 ms** and **2.837 s**. The published nightly's exact-frame diagnostic took **3.409 / 3.429 s** for twelve, including process startup, per-picture opens and its motion comparison.
2. **A whole-clip pass exceeds the 2 s Stop budget on m74.** Decode-all took **24.35 / 24.43 s** at 4K and **16.04 / 16.10 s** at 1080p, before scaling anything. Reading all packets with `AVDISCARD_NONKEY` took **2.73 / 2.78 s** and **3.86 / 3.87 s**, respectively. Both streams had 90 keyframes and 10,800 video packets, so the keyframe-only pass still traversed the entire clip.
3. **Show the tile for m74 hover.** Exact seek to a scaled viewer frame took **217 / 328 ms** at 4K and **130 / 199 ms** at 1080p with input reuse. Reopening each time raised p95 to **376 ms** and **239 ms**, respectively. The 120 ms value can remain the pause before starting an optional exact request. The decode alone exceeds 120 ms at p95. Keep the tile displayed until an exact result for the current hover arrives.
4. **Use 12 default tiles and up to 24 visible tiles per zoom batch.** Open once, seek backward to the preceding keyframe, submit only its packet, drain frame-thread delay, and scale directly to the tile size. All 24 keyframe tiles took **722 / 739 ms** warm and **846 ms** cold at 4K on m74. At 1080p they took **988 / 1,001 ms** warm and **1,046 ms** cold. The skip flag made little difference when the decoder received one packet per seek. Keep the 1 s first-visible and 2 s initial-strip targets. Use a single cancellable worker, cache by keyframe timestamp, and refine visible tiles lazily at zoom. Keep scrub and Upload independent of the worker.

## Builder coverage

- **m74, gating result.** Intel Core i5-6500T, four logical CPUs, SATA SSD, Linux Mint 22.3, kernel 6.14.0-37-generic. FFmpeg selected five decoder threads and active frame threading. Initial load was 10.21 on four cores while existing shared jobs ran. Timed preflights measured 0.14 active cores for 4K, 0.05 for 1080p and 0.06 for the 4K repeat. A burst of shared work appeared during the first 4K tile run. The table uses the clean repeat for A24, An24, B12 and B24 and retains the initial rows in the raw log. The desktop lease was released after the cleanup check at 03:46:26 UTC.
- **aurora-amd, comparison pending.** The desktop lease is held by the GNOME/Cinnamon GUI fuzz campaign. Acquire attempts at 03:16, 03:31 and 03:45 UTC were denied. The first preflight found a load average of 11.38 on 12 logical CPUs, including a VM and a concurrent compiler. The lease holder was notified that the benchmark needs a slot when cleanup finishes.

## Measurements

Timing columns are milliseconds. Warm columns show median / p95. Per-request columns cover each seek, decode and scale. The first-two columns also include input open. “Other cores” reports host CPU activity excluding the measured process.

### m74 · 4K60

| Mode | N | Warm runs | Cold wall ms | Warm wall ms | First 2 ms cold | First 2 ms warm | Per request ms warm | CPU cores warm | Peak RSS MiB warm | Other cores warm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 12 | 5 | 489.9 | 424.4 / 432.6 | 176.2 | 153.3 / 155.6 | 27.1 / 43.8 | 1.00 / 1.00 | 55.3 / 55.4 | 0.09 / 0.14 |
| An | 12 | 5 | 500.7 | 428.4 / 439.9 | 183.2 | 153.2 / 154.7 | 27.5 / 42.5 | 1.00 / 1.00 | 55.2 / 55.2 | 0.09 / 0.22 |
| A | 24 | 5 | 845.9 | 722.3 / 739.2 | 171.1 | 147.6 / 152.5 | 26.2 / 30.0 | 1.01 / 1.01 | 55.3 / 55.4 | 0.01 / 0.01 |
| An | 24 | 5 | 836.4 | 724.9 / 745.2 | 166.7 | 149.5 / 153.6 | 26.3 / 30.5 | 1.00 / 1.01 | 55.2 / 55.4 | 0.01 / 0.04 |
| B | 12 | 5 | 2836.9 | 2664.7 / 2682.1 | 582.2 | 555.0 / 565.3 | 211.0 / 331.0 | 2.80 / 2.82 | 231.5 / 233.1 | 0.03 / 0.05 |
| B | 24 | 5 | 5491.5 | 5176.2 / 5210.7 | 585.4 | 553.9 / 563.9 | 211.4 / 307.8 | 2.86 / 2.89 | 229.8 / 230.7 | 0.02 / 0.05 |
| D | 30 | 5 | 6821.9 | 6662.5 / 7044.1 | — | — | 217.0 / 328.1 | 2.89 / 2.92 | 232.4 / 233.2 | 0.01 / 0.04 |
| Dopen | 30 | 5 | 8554.2 | 8002.5 / 8678.6 | — | — | 259.7 / 376.2 | 2.59 / 2.81 | 274.3 / 276.0 | 0.02 / 0.04 |
| M | 12 | 5 | 3588.3 | 3409.5 / 3429.4 | — | — | — | 2.45 / 2.46 | 251.9 / 252.4 | 0.02 / 0.05 |
| M | 24 | 5 | 6894.0 | 6580.1 / 6608.6 | — | — | — | 2.49 / 2.50 | 251.6 / 266.5 | 0.03 / 0.05 |
| Cn | — | 5 | 2967.2 | 2733.6 / 2776.9 | — | — | — | 1.04 / 1.04 | 73.7 / 73.8 | 0.01 / 0.03 |
| C | — | 5 | 24431.8 | 24348.3 / 24428.2 | — | — | — | 3.67 / 3.68 | 156.4 / 156.5 | 0.01 / 0.03 |

### m74 · 1080p60

| Mode | N | Warm runs | Cold wall ms | Warm wall ms | First 2 ms cold | First 2 ms warm | Per request ms warm | CPU cores warm | Peak RSS MiB warm | Other cores warm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 12 | 5 | 564.0 | 532.2 / 534.3 | 149.0 | 138.2 / 139.4 | 39.2 / 46.0 | 1.00 / 1.00 | 28.2 / 28.2 | 0.00 / 0.01 |
| An | 12 | 5 | 555.6 | 527.3 / 534.7 | 140.6 | 138.6 / 142.4 | 38.7 / 46.1 | 1.00 / 1.00 | 28.2 / 28.2 | 0.01 / 0.11 |
| A | 24 | 5 | 1046.4 | 987.7 / 1000.6 | 135.3 | 132.5 / 134.2 | 38.5 / 42.2 | 1.00 / 1.00 | 28.2 / 28.2 | 0.00 / 0.07 |
| An | 24 | 5 | 1031.9 | 981.1 / 1001.0 | 135.5 | 132.2 / 134.2 | 38.6 / 42.2 | 1.00 / 1.00 | 28.2 / 28.2 | 0.01 / 0.08 |
| B | 12 | 5 | 1605.3 | 1574.4 / 1580.7 | 324.9 | 320.1 / 322.1 | 126.2 / 175.3 | 2.49 / 2.50 | 75.0 / 75.2 | 0.01 / 0.06 |
| B | 24 | 5 | 3192.0 | 3128.8 / 3145.6 | 312.1 | 300.8 / 318.2 | 124.0 / 185.6 | 2.63 / 2.63 | 75.0 / 75.2 | 0.01 / 0.03 |
| D | 30 | 5 | 4138.9 | 4060.3 / 4231.3 | — | — | 129.6 / 198.5 | 2.57 / 2.67 | 77.5 / 77.8 | 0.02 / 0.02 |
| Dopen | 30 | 5 | 5564.2 | 5203.7 / 5255.7 | — | — | 167.4 / 239.1 | 2.26 / 2.29 | 89.1 / 91.1 | 0.02 / 0.02 |
| M | 12 | 5 | 2319.4 | 2112.0 / 2127.7 | — | — | — | 2.13 / 2.14 | 88.1 / 88.6 | 0.02 / 0.03 |
| M | 24 | 5 | 4459.7 | 4174.8 / 4188.7 | — | — | — | 2.22 / 2.23 | 88.0 / 88.1 | 0.02 / 0.02 |
| Cn | — | 5 | 4096.2 | 3864.1 / 3873.7 | — | — | — | 1.02 / 1.03 | 36.3 / 36.5 | 0.02 / 0.03 |
| C | — | 5 | 16091.5 | 16039.1 / 16098.8 | — | — | — | 3.01 / 3.01 | 56.8 / 56.8 | 0.00 / 0.00 |

The first cold trial started with 0% of the clip pages resident. Warm trials started with 100%. Each complete pass verified a 2,000 ms maximum keyframe gap, 90 keyframes and no B-frames. The nightly reported mean luma differences of 29.646 and 30.166 for 12 and 24 samples at 4K, and 29.720 and 30.240 at 1080p.

Raw timings are in [m74-4k.jsonl](m74-4k.jsonl), [m74-4k-quiet-repeat.jsonl](m74-4k-quiet-repeat.jsonl) and [m74-1080p.jsonl](m74-1080p.jsonl).

The fixtures and binary are retained in `~/work/put.gd-videoed/work/council/test/run.N4Bo1q` on m74.

| Clip | Bytes | SHA-256 |
| --- | ---: | --- |
| `4k.mkv` | 329,212,869 | `4f048348f9ad6d9a8c0f5f7c6db568d7753dbb5c194d254c02a8cbcc0b64a5c3` |
| `1080p.mkv` | 244,449,606 | `27fa5555db048ccf6ef2964f4ce89c3b4b491747695d6a112c4e2f8470cd4bda` |

## Fixture and reproduction

The fixture program draws an engineering documentation workspace with smoothly changing scroll offsets, two page layouts, a periodically foregrounded terminal, and a moving arrow pointer. The 10800 timestamps are generated offline at 60 fps. This keeps the inputs at 180 s and the same frame count across hosts. The official nightly's recorder captures in real time and can adapt or drop frames under load. The fixture uses the production software encoder settings without the live capture stage or an audio track.

The m74 generator used distro GStreamer 1.24.2, x264 plugin 1.24.1, libx264 0.164.3108, and Qt 6.4.2. It ran offscreen at nice 10. x264 uses two encoder threads on the four-core Mint host.

| Canvas | GStreamer x264 preset | Configured bitrate | Keyframe interval | B frames |
| --- | --- | ---: | ---: | ---: |
| 3840 × 2160 | ultrafast | 20,000 kb/s | max 120 frames | 0 |
| 1920 × 1080 | superfast | 12,441 kb/s | max 120 frames | 0 |

The remainder of each encoder string was `threads=2 sliced-threads=false rc-lookahead=10 sync-lookahead=0`, followed by `h264parse ! matroskamux`. On a quiet machine the generator command sequence is:

```bash
g++ -std=c++20 -O2 fixture.cpp -o fixture $(pkg-config --cflags --libs Qt6Gui gstreamer-app-1.0)
export XDG_RUNTIME_DIR=$(mktemp -d /tmp/pf.XXXXXX)
test "$(printf %s "$XDG_RUNTIME_DIR/putgd/session.sock" | wc -c)" -le 107
export QT_QPA_PLATFORM=offscreen
nice -n 10 ./fixture 3840 2160 2 4k.mkv
nice -n 10 ./fixture 1920 1080 2 1080p.mkv
```

The extracted nightly AppImage is [26.1117.5114](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1117.5114-nightly), SHA-256 `923dccaedfde8a67e331c95a3d28daba96c90edaa6d44ded1f73306ba228771f`. The harness links to its bundled FFmpeg 9.0.2 (libavcodec and libavformat 63, libavutil 61, libswscale 10) and bundled Qt. The release notice identifies FFmpeg commit `946fcce07b6dcd0331c8cc609192aeff5e1924f8`, which supplied the headers. The compiler used m74's installed Qt 6.4.2 headers.

```bash
chmod u+x nightly.AppImage
nice -n 10 ./nightly.AppImage --appimage-extract > extract.log
curl -fLsS --retry 2 https://codeload.github.com/FFmpeg/FFmpeg/tar.gz/946fcce07b6dcd0331c8cc609192aeff5e1924f8 | tar -xz
(cd FFmpeg-946fcce07b6dcd0331c8cc609192aeff5e1924f8 &&
  ./configure --disable-everything --disable-x86asm --disable-programs > ../ffmpeg-headers.log)
bash build_bench.sh
python3 run_bench.py 4k.mkv 4k.jsonl
python3 run_bench.py 1080p.mkv 1080p.jsonl
```

Sources in this directory are `fixture.cpp`, `bench.cpp`, `build_bench.sh`, `run_bench.py`, and `summarize.py`. The first harness link selected mixed Qt libraries and failed. Linking the nightly's Qt explicitly fixed it. No dependency packages were installed.

## Timing definitions

- A and An open one input per batch, seek backward to each tile, submit just the key packet, drain frame-thread delay, and scale directly to 128 × 72 BGRA. An additionally sets `AVDISCARD_NONKEY`. The benchmark keeps the exporter's auto-selected FFmpeg thread count and frame/slice threading.
- B opens one input per batch and decodes forward from each seek until the first PTS at or after the target, as in `previewFrame`. It converts the full decoded frame to BGRA, copies it to a QImage and scales it smoothly to 128 × 72. A and B request the same bin centers as the published diagnostic. The centers for the first and last tile are processed first. “First 2” includes input open, seek, decode and scale.
- M is end-to-end execution of the nightly's `putgd-record --motion CLIP N`. It opens an input for each exact preview, scales to 320 pixels wide and compares consecutive previews. Motion intensity appears in the raw logs.
- C and Cn read all clip packets in order. C decodes every frame. Cn sets `AVDISCARD_NONKEY` and keeps only keyframes. Neither converts nor scales the frames.
- D uses the exact seek path with 30 uniformly random times in each seeded repeat and 1010 × 568 output. It measures individual seek-to-scaled-frame latencies with a reused input. Dopen, where run, includes reopening for every request like today's preview helper. Neither includes scheduling latency ahead of the benchmark or a hover debounce.
- Each case begins with one cold clip-file run checked with `mincore` after file-specific `POSIX_FADV_DONTNEED`, followed by five warm runs with prefetched, verified file pages. The cold run can warm its own later requests. CPU cores are process user plus system CPU seconds divided by elapsed seconds. Other cores are total host active CPU minus that process's CPU. Peak RSS comes from the process's `ru_maxrss` or GNU time for M.
- Warm results are median / nearest-rank p95. With five warm batches, the batch p95 is the slowest observed batch. Per-request percentiles pool all warm requests. This is a headless media benchmark. It measures production decoder settings and CPU work for an unedited clip, with no GUI paint, active cover masks, GPU decoding, or simultaneous playback.
