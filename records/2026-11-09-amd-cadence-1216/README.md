# #1216: AMD hardware versus software cadence at 1080p60

Result: hardware (`vah264enc`) and software (`x264enc`) encoding have the same cadence at 1080p60 on `aurora-amd`. The 54.38 distinct fps in #1216 came from a timed Plasma notification on screen during the recording, and not from the encoder.

Run on 2026-11-09 with the published nightly `v26.1109.4346-nightly` AppImage (SHA-256 `d72454ab90ff75ef5378f141651d83f2c3b341eaa133b3bc86b4ced4efe2714b`), no compile, driven by `tools/lab/fluidity_run.py`.

## Host

aurora-amd, AMD Radeon 740M (phoenix2), Aurora `testing-45.20261101.2`, kernel 7.2.11-300.fc45, Plasma and KWin 6.8.2, Wayland, DP-2 at 1920x1080 60 Hz, Mesa 26.2.6 radeonsi with VA-API 1.24 (libva 2.24.1, from the host).

- Host: GStreamer 1.28.8, FFmpeg 9.0.2.
- AppImage, which is what recorded: bundled GStreamer 1.24.2 with its `va` plugin, bundled FFmpeg 9.0.2 (libavcodec 63.1.102). The AppImage has no bundled libva, so it uses the host's.
- Software runs set `LIBVA_DRIVER_NAME=none`, so the same AppImage chose `x264enc`. Each run's `started with` line names the encoder that actually ran.

## Method

Each run is one CLI invocation (`batch.py`): 1080p60, monitor target, 10 s, the fluidity fixture full screen on DP-2, a fresh resident, and a working clip analysed by `fluidity.py`. Runs alternate in ABBA order so drift lands on both modes. The recording bar was on screen in every run. Each mode's first run in a set (a fresh private config) also shows the first-run Settings window over the fixture, as the #1216 run did: r01-hw and r02-sw of each set. Those runs are not outliers.

- **set1**: 10 hardware and 10 software runs, no notifications.
- **set2**: 6 hardware and 6 software runs with a timed notification (a blue timeout bar) kept on screen by `notifier.py`, one sent every 3 s with a 7 s timeout.
- **ctrl**: the fixture alone with no recorder, with and without those notifications (`ctrl.py`), four 13 s runs, measured after the first 2 s.

## Summary

Medians, with ranges in brackets. Longest stall shows the range. Skips are frames the clip jumped over.

| Set and mode | n | Distinct fps (range) | Repeats | Skips | Longest stall ms | Early drops | Fixture fps |
|---|---|---|---|---|---|---|---|
| clean, hardware | 10 | 59.81 (59.72–60.0) | 2.0 | 1.0 | 0.0–16.7 | 2 | 59.94 |
| clean, software | 10 | 59.82 (59.73–59.82) | 2.0 | 2.0 | 16.7–16.7 | 2 | 59.89 |
| popup, hardware | 6 | 49.24 (47.05–53.65) | 115.5 | 38.5 | 16.7–33.3 | 619 | 53.77 |
| popup, software | 6 | 50.02 (47.25–51.16) | 109.5 | 43.0 | 33.3–50.0 | 645 | 54.24 |

Every run: recorder frames dropped 0, capture-queue leaks 0.

Fixture alone with no recorder (fixture fps): clean 59.96 and 59.96, with popups 59.96 and 59.97; missed frames 0 in all four.

## Reading it

Hardware and software are equal when the desktop is clean: 59.81 against 59.82 distinct fps, spreads of 0.28 and 0.09. Fixture ticks are about 59.9 in both, so the recorder captured what the desktop showed.

The 54.38 fps recording on `v26.1105.3906` was one recording with a transient, timeout-bar notification on screen: `earlier-v26.1105.3906-hw-frame.png` shows it (a blue bar under "put.gd" on the top popup). The software run from that same report had two persistent warnings and no timeout bar. Its recorder log showed 938 source arrivals and 252 early drops against 699 and 1 for the software run, the same signature set2 produces. In that clip the 60 repeats fall in the first 8 seconds and none after, which fits a popup that expires during the recording (`dist.py`). I did not repeat that exact popup timing; set2 uses a stronger, sustained version of the same condition.

With the popup condition, both encoders lose about 10 distinct fps (49.24 hardware, 50.02 software). The loss needs both the popup and the unthrottled KWin screencast: with no recorder the popups cost the fixture nothing (59.96 clean, 59.96 and 59.97 with popups). During recording, source arrivals roughly double (to about 1300) and the cadence lock drops about 620 early arrivals, some of which are real fixture frames, and the fixture's own frame clock drops to about 54 fps. No encoder dropped frames, and repeats appear as a stall of 33 ms at most in typical runs (one software run reached 50 ms).

## Not established

- Which part of the popup's repaint path (Plasma timeout animation, KWin extra composites, or the cadence lock) contributes most, and whether this is seen at 30 fps. No fix was attempted, per the #1216 scope: it is not encoder-specific.
- Numbers from any other GPU, KWin or Mesa version. This repeats only the Radeon 740M host named in the issue.
- The rest of `~/i1216` on aurora-amd (the working clips, about 15 MB each) stays on that host and is not published here.

## Per-run data

### set1 hardware
| Run | Distinct fps | Repeats | Skips | Longest stall ms | Dropped (recorder) | Leaked (capture queue) | Source arrivals | Early drops | Fixture fps |
|---|---|---|---|---|---|---|---|---|---|
| r01-hw | 59.72 | 3 | 1 | 16.7 | 0 | 0 | 692 | 1 | 59.84 |
| r04-hw | 59.81 | 2 | 1 | 16.7 | 0 | 0 | 694 | 1 | 59.93 |
| r05-hw | 59.91 | 1 | 0 | 16.7 | 0 | 0 | 683 | 0 | 59.92 |
| r08-hw | 59.81 | 2 | 1 | 16.7 | 0 | 0 | 676 | 2 | 59.94 |
| r09-hw | 59.81 | 2 | 2 | 16.7 | 0 | 0 | 694 | 2 | 59.94 |
| r12-hw | 59.91 | 1 | 1 | 16.7 | 0 | 0 | 694 | 1 | 59.95 |
| r13-hw | 59.72 | 3 | 2 | 16.7 | 0 | 0 | 693 | 2 | 59.96 |
| r16-hw | 59.72 | 3 | 2 | 16.7 | 0 | 0 | 670 | 2 | 59.95 |
| r17-hw | 59.81 | 2 | 2 | 16.7 | 0 | 0 | 693 | 2 | 59.91 |
| r20-hw | 60.00 | 0 | 0 | 0.0 | 0 | 0 | 696 | 0 | 59.94 |

### set1 software
| Run | Distinct fps | Repeats | Skips | Longest stall ms | Dropped (recorder) | Leaked (capture queue) | Source arrivals | Early drops | Fixture fps |
|---|---|---|---|---|---|---|---|---|---|
| r02-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 710 | 2 | 59.87 |
| r03-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 710 | 2 | 59.95 |
| r06-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 698 | 2 | 59.95 |
| r07-sw | 59.73 | 3 | 2 | 16.7 | 0 | 0 | 694 | 2 | 59.92 |
| r10-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 711 | 3 | 59.86 |
| r11-sw | 59.73 | 3 | 1 | 16.7 | 0 | 0 | 707 | 1 | 59.81 |
| r14-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 707 | 2 | 59.96 |
| r15-sw | 59.73 | 3 | 2 | 16.7 | 0 | 0 | 693 | 2 | 59.76 |
| r18-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 700 | 2 | 59.95 |
| r19-sw | 59.82 | 2 | 2 | 16.7 | 0 | 0 | 707 | 2 | 59.85 |

### set2 hardware (popup)
| Run | Distinct fps | Repeats | Skips | Longest stall ms | Dropped (recorder) | Leaked (capture queue) | Source arrivals | Early drops | Fixture fps |
|---|---|---|---|---|---|---|---|---|---|
| r01-hw | 53.65 | 68 | 26 | 33.3 | 0 | 0 | 1261 | 603 | 56.10 |
| r04-hw | 47.05 | 139 | 63 | 33.3 | 0 | 0 | 1245 | 592 | 53.09 |
| r05-hw | 48.43 | 124 | 24 | 33.3 | 0 | 0 | 1343 | 636 | 50.65 |
| r08-hw | 51.54 | 91 | 28 | 33.3 | 0 | 0 | 1258 | 574 | 54.29 |
| r09-hw | 49.94 | 108 | 64 | 16.7 | 0 | 0 | 1304 | 644 | 55.99 |
| r12-hw | 48.54 | 123 | 49 | 33.3 | 0 | 0 | 1294 | 635 | 53.25 |

### set2 software (popup)
| Run | Distinct fps | Repeats | Skips | Longest stall ms | Dropped (recorder) | Leaked (capture queue) | Source arrivals | Early drops | Fixture fps |
|---|---|---|---|---|---|---|---|---|---|
| r02-sw | 51.16 | 97 | 41 | 33.3 | 0 | 0 | 1365 | 685 | 54.94 |
| r03-sw | 48.25 | 129 | 26 | 33.3 | 0 | 0 | 1327 | 651 | 50.77 |
| r06-sw | 50.07 | 109 | 45 | 33.3 | 0 | 0 | 1310 | 629 | 54.37 |
| r07-sw | 50.98 | 99 | 34 | 33.3 | 0 | 0 | 1326 | 639 | 54.12 |
| r10-sw | 47.25 | 140 | 71 | 50.0 | 0 | 0 | 1313 | 635 | 53.76 |
| r11-sw | 49.98 | 110 | 46 | 33.3 | 0 | 0 | 1383 | 698 | 54.38 |

## Files

`combined.json` holds every number, `set1/` and `set2/` the per-run JSON, the recorder debug logs and the fixture ticks. `ctrl/` holds the fixture-only control. `set1/hw/frames/`, `set1/sw/frames/`, `set2/hw/frames/` and `set2/sw/frames/` hold one mid-recording frame each from those first runs, `set1/hw/frames/record-r09-hw.png` is a later clean run, `final-desktop.png` is the clean desktop after the campaign, and `earlier-v26.1105.3906-hw-frame.png` is the frame from the run #1216 reported. The scripts are `batch.py`, `report.py`, `notifier.py`, `ctrl.py` and `dist.py`.
