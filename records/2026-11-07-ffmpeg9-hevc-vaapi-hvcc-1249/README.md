# FFmpeg 9 hevc_vaapi corrupt MP4 on AMD: root cause and fix (#1249)

The same hash-identified working clip (`src.mkv`, sha256
`10f7096d474f20748cbff8ad5b5c2bbc6bfecdfd2703c9c1293256969951a78a`, 200 frames of
moving colour bars) was exported with `putgd-record --export` and
`PUTGD_RECORD_EXPORT_ENCODERS=hevc_vaapi` or `h264_vaapi` (no software fallback)
on every build below. Each export was decoded and scored against the source
(PSNR average after `fps=30` alignment), and its `hvcC`/`avcC` and first packet
were traced with `trace_headers`. The contact sheets show every 30th frame.

## Root cause

- `hevc_vaapi`'s extradata is libavcodec's own VPS/SPS/PPS. AMD radeonsi (Mesa
  26.2.6, Radeon 740M) rewrites the parameter sets it emits in-band to what it
  actually coded. The extradata SPS says `max_transform_hierarchy_depth_inter/intra
  = 0` (and, built against libva < 2.21 as the AppImage is, height 1080 with no
  conformance window). The in-band SPS says depth 4, height 1088 with a 4-row
  bottom conformance window. See `sps-diff.txt`.
- FFmpeg ≤ 7.1 kept those in-band sets in `hvc1` MP4 samples, so decoders used
  the right ones. FFmpeg 8.0's movenc commit `f0051604c7` ("avformat/movenc:
  don't write PS NALUs in hvcC for codec tag hvc1") strips in-band parameter sets
  from `hvc1` tracks. Only the wrong `hvcC` remained, and every slice was parsed
  with the wrong transform tree. The result: green/magenta garbage and no decoder
  warning.
- Fedora's own `ffmpeg` 9.0.2 CLI (`-c:v hevc_vaapi -tag:v hvc1`) produces the
  same broken file on aurora-amd. Neither release/9.0 nor master has a fix.
- `h264_vaapi` has the same mismatch in its `avcC` PPS (`transform_8x8_mode_flag`
  1 vs 0, `pic_init_qp_minus26` −2 vs 0). It decodes only because movenc still
  keeps in-band sets for `avc1`.

## Fix

In `src/record/ClipExporter.cpp`, VA-API encoders no longer get
`AV_CODEC_FLAG_GLOBAL_HEADER`. With no extradata, movenc copies the first packet
and builds `hvcC`/`avcC` from its in-band parameter sets, which are the ones the
driver coded. Every FFmpeg from 6.1 to 9.0 has that first-packet path.

## Results (PASS = PSNR > 35 dB, no decoder warning, non-empty hvcC/avcC)

| Host / GPU | FFmpeg | Build | hevc_vaapi | h264_vaapi |
| --- | --- | --- | --- | --- |
| aurora-amd Radeon 740M | 7.1.5 | nightly AppImage | PASS 49.18 | PASS 48.70 |
| aurora-amd | 9.0.2 | #1249 AppImage before fix | **FAIL 6.37** | PASS 48.70 |
| aurora-amd | 9.0.2 | #1249 AppImage with fix (CI 42403829742) | PASS 49.18 | PASS 48.70 |
| aurora-amd | 6.1.1 | dev build, unfixed / fixed | PASS / PASS | PASS / PASS |
| aurora-amd | 7.1.5 | dev build, unfixed / fixed | PASS / PASS | PASS / PASS |
| aurora-amd | 8.0.1 | dev build, unfixed / fixed | **FAIL 5.77** / PASS 49.18 | PASS / PASS |
| aurora-amd | 8.1.3 | dev build, unfixed / fixed | **FAIL 5.86** / PASS 49.18 | PASS / PASS |
| aurora-amd | 9.0.2 | dev build, unfixed / fixed | **FAIL 5.78** / PASS 49.18 | PASS / PASS |
| d69 Intel HD 530 iHD 25.2.3 | 7.1.5 Debian distro | dev build, unfixed / fixed | no HEVC encode entry point | PASS / PASS 48.21 (byte-identical) |
| d69 | 9.0.2 | #1249 AppImage with fix | no HEVC encode entry point | PASS 48.21 |
| k72 Intel HD 530 iHD 26.1.2 | 8.0.1 Kubuntu distro | dev build, unfixed / fixed | no HEVC encode entry point | PASS / PASS 48.21 (byte-identical) |
| k72 | 9.0.2 | #1249 AppImage with fix | no HEVC encode entry point | PASS 48.21 |

- `grid-aurora-hevc.png` and `grid-h264.png` hold all rows. Per-export sheets
  are under `frames/`. `matrix-*.json` has every field: sizes, hashes, the traced
  `hvcC`/`avcC` and first-packet fields, decoder warnings and PSNR.
- d69's own PSNR graph (Debian ffmpeg 7.1.5) misaligns frames and reports 22.47 dB
  for every build, including the unfixed one. The same files score 48.21 on
  aurora's 9.0.2 and are byte-identical across fixed and unfixed builds. The
  table uses the 9.0.2 score.
- `frames/d69-debian-7.1.5-decode-of-aurora/` holds aurora's fixed exports
  decoded by the independent Debian 7.1.5. All show the bars with no warnings,
  and the unfixed 9.0.2 HEVC is garbage there too.
- On Intel the fixed and unfixed exports are byte-identical, because iHD emits
  libavcodec's packed headers unchanged. No lab Intel GPU (HD 530) has HEVC
  encode. f44's Fedora iHD exposes no encode entry points, and m74 has no VA
  encode, so their distro FFmpeg versions (8.1.3, 6.1.1) are covered by the
  aurora dev builds.

## Builds

- AppImages: nightly `putgd-26.1107.4036-dev+g369f001b66a9` (sha256 31761f85…82ed),
  candidate `26.1107.4044-dev+g33af4071b5fa` (d59c2e68…a83b), fixed
  `26.1107.4046-dev+g8ed31be16488` (c55b1591…4a67, CI run 42403829742, merge of
  #1249 head 508970b5e76c).
- aurora-amd dev builds: FFmpeg tags n6.1.1, n7.1.5, n8.0.1, n8.1.3 and n9.0.2,
  built in the `putgd-build` Fedora 45 Toolbx with `media.json`'s configure flags
  (`scripts/ffbuild.sh`). Three deviations: no libx264/libx265 (not in Fedora),
  `--disable-nvenc` for 6.1.1 and 8.0.1 (Fedora's nv-codec-headers 13.1 is too new
  for them), and libva 2.24 headers. `putgd-record` was built from #1249 head
  508970b5e76c, and from the same tree with the one-line fix reverted
  (`scripts/recbuild.sh`). The run used the host's negativo17 Mesa 26.2.6.
- d69/k72 dev builds: `putgd-record` from the same two trees against the distro
  FFmpeg (`scripts/distro-build.sh`).
- Scratch-only change for these dev builds: the AWS SDK pin was relaxed to the
  builders' prepared 1.11.907. `putgd-record` does not use the SDK.
