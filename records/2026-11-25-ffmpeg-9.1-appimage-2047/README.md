# FFmpeg 9.1 AppImage recording acceptance (#2047)

**Result: PASS** for the three scoped native-desktop recording/export scenarios. No source change was built on the lab. The candidate was the exact CI AppImage from [run 45606650620](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45606650620), which completed successfully. The AppImage job itself succeeded before the download.

- Candidate: `putgd-26.1125.7048-dev+g847ff4cf4cbb-x86_64.AppImage` (189,962,744 bytes); SHA-256 `3c9bc0bd38f64f030ef78e40d647f8f313541ba21a170ef8cd585265316139ff`. The hash was rechecked on all three builders.
- Commit `847ff4cf4cbba30b9fde260a82a93375fe8ccbd6`; expected and observed diagnostics `build.gitTree` on **each** host `07d9da15d2e97dfbdb9d9ec3ca6f011b3582e416`.
- Candidate FFmpeg 9.1; the CI media runtime receipt is included.

## Functional acceptance

| Row | Aurora Plasma Wayland | f44 GNOME Wayland | m74 Cinnamon X11 |
|---|---|---|---|
| Candidate tree and hash | Pass | Pass | Pass |
| Real native recording with moving bars and ball | Pass | Pass | Pass |
| System audio (440 Hz), microphone (1 kHz bursts) | Pass | Pass | Pass |
| MP4 H.264 + AAC: full decode and motion | Pass | Pass | Pass |
| WebM VP9 + Opus: full decode and motion | Pass | Pass | Pass |
| GIF: all frames decoded, silent by design | Pass | Pass | Pass |
| WebP: all frames decoded, silent by design | Pass | Pass | Pass |
| MP4 and WebM real fullscreen ffplay on wall (Fedora WebM witness caveat below) | Pass | Pass | Pass |
| Both trim ends, middle cut and review blur | Pass | Pass | Pass |
| Edited MP4 duration, blur and A/V sync | Pass | Pass | Pass |
| Clean exit and desktop lease release | Pass | Pass | Pass |

The fixture used GStreamer `videotestsrc pattern=smpte100 horizontal-speed=6` and `pattern=ball` as two moving panes, plus synchronized white flashes and 1-kHz bursts. They were composited inside the project’s fullscreen magenta cover to prevent capture of unrelated desktop windows; not two separate top-level windows. The lab’s private output and virtual microphone carried distinct synthetic signals, never a physical microphone. The control was a recording of the identical fixture frozen to one frame. All four outputs came from the same A/V working recording; GIF and WebP intentionally drop audio. Native video/audio decoding used distro FFmpeg; animations used Pillow frame-by-frame. No reliance on the AppImage for export decoding. The GNOME lock validated its enabled and ACTIVE AppIndicator tray host. All three were real, wall-visible desktop sessions under the lab’s desktop and quiet leases.

## Measurements

The motion score below is mean absolute luma difference over all pairs 15 frames apart after scaling to 160×90 (0–255); the JSON field `motionMeanLag1s` uses a 15-frame lag, not a literal one-second interval for 30fps clips. Separately, the two pane scores compare RGB differences in three retained keyframes; both panes independently move far more than the frozen control. Audio is decoded mono PCM RMS dBFS, and the tone amplitudes separately prove both sources. Offset is nearest mic burst vs visual flash, with the median and maximum absolute values in milliseconds.

| Host / format | Seconds | Decoded frames | Motion / control | Bars / ball motion | Audio dBFS | 440 Hz / 1 kHz amplitude¹ | A/V median / max abs ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| aurora-amd / control | 4.600 | 138 | 0.0022 / 0.0022 | 0.489 / 0.081 | — | — | — |
| aurora-amd / mp4 | 12.600 | 378 | 10.5092 / 0.0022 | 127.400 / 9.301 | -13.31 | 0.01699 / 0.9910 | -6.7 / 40.0 |
| aurora-amd / webm | 12.608 | 378 | 10.5170 / 0.0022 | 127.209 / 9.287 | -13.34 | 0.01702 / 0.9996 | -7.0 / 40.0 |
| aurora-amd / gif | 12.530 | 188 | 3.4303 / 0.0022 | 127.036 / 9.173 | — | — | — |
| aurora-amd / webp | 12.532 | 181 | 3.9878 / 0.0022 | 126.715 / 10.101 | — | — | — |
| aurora-amd / edited | 8.567 | 257 | 9.7618 / 0.0022 | 71.171 / 9.487 | -13.39 | 0.01699 / 0.9949 | -6.7 / 40.0 |
| f44 / control | 5.000 | 150 | 0.0023 / 0.0023 | 0.647 / 0.134 | — | — | — |
| f44 / mp4 | 13.067 | 392 | 10.5182 / 0.0023 | 128.482 / 9.369 | -13.12 | 0.01690 / 0.9917 | -16.7 / 50.0 |
| f44 / webm | 13.074 | 392 | 10.5144 / 0.0023 | 128.740 / 9.362 | -13.15 | 0.01697 / 1.0071 | -17.0 / 50.0 |
| f44 / gif | 13.000 | 195 | 4.1571 / 0.0023 | 126.345 / 9.159 | — | — | — |
| f44 / webp | 12.999 | 187 | 4.3921 / 0.0023 | 125.831 / 10.239 | — | — | — |
| f44 / edited | 9.033 | 271 | 9.7634 / 0.0023 | 41.180 / 9.706 | -13.12 | 0.01691 / 0.9910 | -16.7 / 50.0 |
| m74 / control | 4.167 | 125 | 0.0006 / 0.0006 | 0.075 / 0.001 | — | — | — |
| m74 / mp4 | 12.167 | 365 | 10.8794 / 0.0006 | 126.228 / 10.288 | -13.16 | 0.01703 / 0.9908 | -40.0 / 40.0 |
| m74 / webm | 12.174 | 365 | 10.8835 / 0.0006 | 126.112 / 10.221 | -13.10 | 0.01701 / 1.0089 | -47.0 / 47.0 |
| m74 / gif | 12.130 | 182 | 2.9777 / 0.0006 | 126.382 / 9.415 | — | — | — |
| m74 / webp | 12.132 | 179 | 3.9144 / 0.0006 | 126.326 / 10.859 | — | — | — |
| m74 / edited | 8.133 | 244 | 10.1025 / 0.0006 | 64.272 / 10.551 | -13.17 | 0.01704 / 0.9907 | -40.0 / 40.0 |

¹ 440 Hz median and 1 kHz peak amplitude over 10-ms windows. GIF/WebP have no audio by design. All tested video streams decoded to their expected frame count and each exported keyframe passed the cover/edge gate. All two-frame player witnesses passed it as well.

## Review edits and encoders

| Host | Capture/live encoder | MP4 export encoder² | Original → edited (s) | Kept time per review (s) | Trim start/end (s) | Cut (s) | Mean bars horizontal edge contrast before → after |
|---|---|---|---|---|---|---|---|
| aurora-amd (plasmashell 6.8.2) | vah264enc | h264_vaapi | 12.600 → 8.567 | 8.567 | 1.000 / 1.033 | 4.000–6.000 | 2.206 → 0.966 |
| f44 (GNOME Shell 50.6) | x264enc | libx264 | 13.067 → 9.033 | 9.033 | 1.000 / 1.033 | 4.000–6.000 | 1.521 → 1.046 |
| m74 (Cinnamon 6.6.9) | vah264lpenc | h264_vaapi | 12.167 → 8.133 | 8.133 | 1.000 / 1.033 | 4.000–6.000 | 1.709 → 0.988 |

² The resident saveCopy receipt reports status/size/duration but not the helper’s encoder name. The helper’s supported `--export` diagnostic on a 1.5 s slice of the same working clip, with the same format, codec and output size, reports actual encoder selection. On all three hosts it reported `libvpx-vp9` / `libopus`, `gif`, and `libwebp_anim` for the other formats. Live encoder is directly from `recording.inspect`. The MP4 review returns to the previously capped 1280-pixel edge after animated output selection, as documented; the blur comparison maps both sizes into source canvas coordinates.

Blur strength 48 over the bars inset was visible in the decoded edited frames. The actual trim edges snap inward to the recorded frame grid, so the measured duration decreases by 4.033 s rather than precisely 4.000 s. The retained durations and decoded edited files agree to within one frame. The edited exports retain both audio signals with A/V offsets well below 200 ms. Independently compared edited ball-pane frames around and after the cut against their expected source ticks (±1 frame): mean luma difference for the correct mapping versus leaving the cut in was Aurora 0.923 vs 9.188, f44 0.928 vs 9.227, and m74 1.201 vs 9.964. This supports the content join, not just the duration change; details are in `cut-content-check.json`.

## Failures and recovery

- Aurora first attempt: the distro FFmpeg analyzer rejected the obsolete `-vsync` option (not a candidate recording/export failure). The original receipt is preserved; corrected analyzer uses `-fps_mode passthrough` in a fresh run. No product failure remained.
- Aurora first playback attempt: windowed ffplay completed but the screen evidence gate found an uncovered bottom edge and deleted those screenshots. Full-screen replay subsequently produced two independently cover-checked, distinct wall frames for each MP4 and WebM; both players exited 0.
- Fedora’s original WebM fullscreen playback completed and the two saved wall frames passed the cover gate, but their hashes were identical. The saved Fedora WebM screenshots establish visible playback, not its change over time; full independent decode proves the clip contains motion. A repeat visual-witness check was blocked: the scheduled nightly retained its guest and still held the Fedora desktop lease (blocked, explicit cleanup recovery required). No other session’s lock was broken.
- No functional row needed a stable comparison. The separately requested AAC comparison uses the published stable artifact.

## Evidence and cleanup

Per-host `receipt.json` contains diagnostics identity, capability and control replies, recording progress, exact edit and output settings, full decoder probing and metrics, encoder diagnostics, and gate results. `pane-motion.json` contains the independent keyframe comparison. `frames/` contains only gated exported and playback keyframes. All residents and test processes were stopped; raw clips and receipts stay as private evidence, while the temporary AppImages and extracted runtime directories were removed from the builders. The temporary Mint distro FFmpeg package was installed only for independent decoding and then removed; the preexisting native packages on f44 and m74 were not changed. Physical desktop leases released before the nightly check at 12:15 UTC. Unrelated files, apps and sessions were left unchanged. No put.gd-desktop source branch was pushed.

## Aurora AAC default-coder comparison

One 60.567 s real candidate recording, system audio only, SHA-256 `186b35028a5ac95032d777f34e1228442687de18b04faf098f36e3d1538d1b6a` (working MKV). Both bundled helpers exported that identical input through the production export engine’s `--export` diagnostic under one quiet lease; default native AAC coder, no override. Stable `v26.1124.6926` AppImage SHA-256 `d20ce6362e01cc97f739d137112dd3330d32f4033ac00b5d6e0d14afb21396a0`, matched published SHA256SUMS. Three interleaved exports each.

| Build | Wall times (s) | Median wall (s) | CPU times (s) | Median CPU (s) | Encoder | volumedetect mean dBFS | Audio duration (s) |
|---|---|---:|---|---:|---|---|---|
| candidate | 6.490, 6.311, 6.309 | 6.311 | 38.100, 37.976, 38.111 | 38.100 | encoder=h264_vaapi + AAC | -16.1, -16.1, -16.1 | 60.567, 60.567, 60.567 |
| stable | 7.723, 7.678, 7.736 | 7.723 | 39.392, 39.292, 39.406 | 39.392 | encoder=h264_vaapi + AAC | -16.1, -16.1, -16.1 | 60.567, 60.567, 60.567 |

Candidate median wall change: -18.3%; median CPU change: -3.3%. All six exports decoded without errors, contained non-silent native AAC, and kept the recorded duration. Audio was measured using distro FFmpeg, not subjectively listened to. CPU is child process user+system time, measured separately from elapsed wall time. Candidate MP4 files were 1,796,065 bytes versus 1,385,898 stable (+29.6%); stream bitrate was video 104,039 versus 95,851 bit/s and audio 129,707 versus 83,777 bit/s. The input, H.264 hardware path and output duration were identical. The new FFmpeg version produced higher actual audio bitrate on this synthetic tone workload; the increase is an observation, not proof that the coder is the sole cause. Maximum decoded volumedetect was −2.8 dBFS candidate versus −2.4 stable. This is a small three-run synthetic workload comparison, not a general performance claim.

