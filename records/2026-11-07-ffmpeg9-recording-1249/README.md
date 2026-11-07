# FFmpeg 9.0.2 recording acceptance — PR #1249

**Acceptance is blocked. Mint and Kubuntu pass. Aurora has a reproducible candidate-only HEVC VA-API corruption failure. Ubuntu is incomplete because its guest exhausted the recording disk reserve. Fedora was unavailable under another live desktop lock.**

Only the staged AppImages were tested; no native DEB/RPM package, package installation, GitHub artifact download, workstation recording/encoding, source checkout change or PR code change was performed. All acquired physical locks passed cleanup and were released. The Ubuntu VM was visible on its dedicated wall tile, stopped after final preflight, and its disposable overlay was retired through guarded cleanup; its golden was preserved.

The candidate is `26.1107.4044-dev+g33af4071b5fa` (CI run 42397650358, build commit `33af4071b5fa68e9b50a91f0f2d8aaa386856c64`), supplied for PR head `71e618956316aa4a8a0badf456095d3e867fe2ad`. Baseline is `26.1107.4036-dev+g369f001b66a9` (CI run 42392437798). All five hosts matched both staged SHA-256 digests before testing:

- Candidate: `d59c2e68bd7bbf4d6864bab36a291dc3035adb145af9362c516296e78ccaa83b`
- Baseline: `31761f85cfb1cbe94dc3d5528a078cccd8b85c4920fd2740e9fa5b5e2a8982ed`

Capture used the real X11, Mutter or KWin desktop path with private configuration and synthetic content. Each format's builds were interleaved on the same host. Pattern captures retained about 6.2–6.8 seconds while omitting a 2-second pause; marker captures omitted a 3-second pause. Final moving clips retained nonzero motion after resume. Default full-frame helper/Pillow scores and all failed attempts remain in per-run results. The table uses mean absolute 8-bit grayscale differences of eight decoded samples, from 1 second to 150 ms before clip end, to exclude the initial bar before the explicit `recording.overlay visible:false` acknowledgement. The same stable sampling window measured retained still controls as **0.000** on Mint, Kubuntu and Aurora (Aurora uses its retained MP4/WebM/GIF controls as the common still control; WebP's control frame gate rejected its copy). Pillow decodes GIF/WebP; exact AppImage helpers decode H.264/VP9. H.265 uses distro FFmpeg.

¹ A/V table offsets compare **identical, hash-identified real-desktop working clips** exported by both builds. All reported pairs are equal. Independent live A/B captures have scheduling-dependent absolute offsets; those original medians, per-flash offsets, source hashes and pause/export steps are retained in `parity*.json` and each marker run's `results.json`. This is not a claim that independently captured clips have identical offsets or that the physical desktops measured 0 ms. GIF and WebP have no audio.

² Ubuntu MP4/WebM moving exports passed after the crop/cover correction. GIF stopped early on its budget before Resume; baseline GIF and both WebP attempts refused with `disk_space_insufficient`. Later controls also refused, requiring 417–430 MB more free space. This resource failure affects baseline too; the row remains unaccepted. Guest root expansion requires administrator authentication (`sudo -n` was refused). Earlier attempts hit missing `gtksink`, startup notification/edge gates, and duplicated extraction disk use; these were retained and corrected with the existing `ximagesink`, wider cover margins, cached exact extracts, and disposable-guest notification settings. No missing package was installed and no disk guard was relaxed.

**Mint 22.3 Cinnamon X11 — m74: PASS**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 18.848 / 18.801 | 16.000 / 16.000 | PASS |
| WEBM | 18.812 / 18.803 | -0.500 / -0.500 | PASS |
| GIF | 18.651 / 18.684 | N/A — silent | PASS |
| WEBP | 18.708 / 18.674 | N/A — silent | PASS |

**Kubuntu Plasma Wayland — k72: PASS**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 20.003 / 20.107 | 28.700 / -4.000 | PASS |
| WEBM | 20.107 / 19.897 | 19.500 / 19.500 | PASS |
| GIF | 19.712 / 19.660 | N/A — silent | PASS |
| WEBP | 19.790 / 19.724 | N/A — silent | PASS |

**Aurora KDE Wayland — aurora-amd: FAIL (HEVC VA-API)**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 20.126 / 19.982 | 29.300 / 29.300 | PASS |
| WEBM | 19.988 / 19.994 | 35.500 / 35.500 | PASS |
| GIF | 19.723 / 19.749 | N/A — silent | PASS |
| WEBP | 19.889 / 19.991 | N/A — silent | PASS |

**Ubuntu GNOME Wayland VM on d69: BLOCKED / partial**

| Format | Motion candidate / baseline | A/V ms candidate / baseline¹ | Pause/resume |
|---|---:|---:|---|
| MP4 | 25.813 / 25.809 | 46.000 / 46.000 | PASS² |
| WEBM | 26.029 / 25.919 | 55.500 / 55.500 | PASS² |
| GIF | — / — | N/A — silent | BLOCKED (disk reserve)² |
| WEBP | — / — | N/A — silent | BLOCKED (disk reserve)² |

**Fedora GNOME — f44: NOT RUN**

| Format | Motion C / B | A/V C / B | Pause/resume |
|---|---|---|---|
| MP4 | NOT RUN | NOT RUN | NOT RUN |
| WebM | NOT RUN | NOT RUN | NOT RUN |
| GIF | NOT RUN | NOT RUN | NOT RUN |
| WebP | NOT RUN | NOT RUN | NOT RUN |

The live `codex-pr1247-ab` desktop lock refused acquisition; it was never broken. Digests were verified read-only. NVENC is **NOT RUN — no lab NVIDIA hardware**.

**Aurora hardware failure — candidate HEVC is corrupt; baseline is clean**

Forced `PUTGD_RECORD_EXPORT_ENCODERS=h264_vaapi` and `hevc_vaapi` logs prove actual hardware encoders, not a software fallback. Both produced about 200 frames at 1920×1080. H.264 is visually correct for both builds, decoded motion 25.448 / 25.462. HEVC's initial candidate export decoded as mostly black damaged pixels, versus correct scrolling bars for baseline (motion 7.315 / 25.468).

The re-check interleaved candidate → baseline → candidate → baseline **from exactly the same live recorded working clip**. Both candidate exports reproduced the corruption (motion 7.314832); both baseline exports remained correct (25.454271). Decoder exit status was zero with no warnings, so exit code and nonzero motion alone would have missed the failure. Debian's independent FFmpeg 7.1.5 decoder also shows the candidate corruption (9.019022) and a correct baseline (25.454138). Source hash, encoder logs, output hashes and all seven decoded frames per export are retained. This establishes a candidate-only observed failure; no code fix or attribution beyond these measurements is claimed.

**Posters and History:** both builds returned `history.preview state:ready` and displayed the selected local recording in History on Mint (`history9`), Kubuntu (`history7`), Aurora (`history6`) and the Ubuntu VM (`history7`). The explicit recording Upload action was routed solely to an isolated local archive (`local_only`, remote `not_requested`); no remote destination or credentials were used. The returned synthetic poster PNGs are retained. Full History screenshots rejected by the cover gate were discarded, not counted as saved visual proof.

**Failure and cleanup context:** initial cover/edge failures, cancelled KWin portal fallbacks, insufficient-marker runs and disk-reserve failures are preserved in their original run JSON. Rejected clip/frame files were destroyed by the privacy gate. Final Mint/Kubuntu/Aurora ordinary format rows use only retained copies with passing frame gates. The GTK player on Aurora/Ubuntu used the existing X11 image sink embedded in the cover; the recorder itself remained native Wayland (`kde-screencast`/`mutter-screencast`). Earlier separate-ffplay attempts failed the frame gate and are excluded. No lock was broken, no Patrick application was killed, no golden was modified, and no pattern kill or recursive directory deletion was used. Actual session/kernel, build digests, acquisition, host load, timing, IDs and parameters are recorded in the run JSON. Socket `/run/user/1000/putgd/session.sock` is 33 UTF-8 bytes; the VM QMP socket was 44 and its UI-harness check was 62, all below 107.

Only curated synthetic fixture/poster frames are published. Redundant controls, startup UI and bulk frames remain in the private archive indexed by `private-visual-index.json`; raw clips remain on their physical hosts, with the Ubuntu exported results also retained on d69 before overlay retirement. Original per-host export checksums describe the full private export, including the indexed frames; `public-SHA256SUMS.json` describes the published subset.
