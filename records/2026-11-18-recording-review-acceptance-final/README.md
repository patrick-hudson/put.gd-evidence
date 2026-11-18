# Recording review final desktop acceptance

PR #1635, source `9500ca0994772a6ec33e9494767e55965bc283bb`. CI run `44287865139` built merge snapshot `652b83781a9021ff7a9c6bc25687cffcf2958e9f` with the same tree, `ebb93c833833c9edc2a4c8236e06002e743264a2`. Native build version `26.1118.5424-dev+g652b83781a90`. Each acceptance lane checks the running resident's `diagnostics.build.gitTree` against the source tree before using desktop evidence.

## Desktop matrix

| Desktop | A | B | C | D | E | F / AC2 | G | H | I | New 1 | New 2 | New 3 | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d69 Plasma Wayland | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Direct pass, recipe blocked | — | Pass | Pass | Pass | — |
| m74 Cinnamon X11 | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Direct pass, recipe failures | Pass | Pass | Pass | Pass | — |
| f44 GNOME Wayland | — | — | — | — | — | — | — | — | — | — | — | — | Pass |
| Omarchy Hyprland guest | — | — | — | — | — | — | — | — | — | — | — | — | Pass |
| Fedora 45 Budgie guest | — | — | — | — | — | — | — | — | — | — | — | — | Pass |

Every final lane's running tree is in its build receipt. Row H records direct checks and the outcomes of the catalog-backed recipes.

| Desktop and CI artifact | Running gitTree | Capture encoder | Decoded MP4 / clock | Motion compared with frozen | Seam counters | Flash/beep offsets | Filmstrip worker p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| d69 Debian 13 DEB | [ebb93c83…](d69/build.json) | `vah264lpenc`, `avenc_aac` in the diagnostic capture | 10.400000 / 10.400000 s, H.264/AAC | 25.137 / 30.093, frozen 0.022 | 136 → 163 | +20.0, −12.7 ms | — |
| m74 Ubuntu 24.04 DEB | [ebb93c83…](m74/build.json) | `vah264lpenc`, `avenc_aac` | 10.133333 / 10.133334 s, H.264/AAC | 25.546 / 29.682, frozen 0.016 | 136 → 163 | −30.0, +4.0 ms | 401.7 / 713.1 ms |
| f44 Fedora 44 RPM | [ebb93c83…](f44/build.json) | `openh264enc`, `avenc_aac` | 13.766667 / 13.766667 s, H.264/AAC | 23.048 / 25.109, frozen 0.010 | 136 → 163 | −12.0, −11.3, −11.3 ms | — |
| Omarchy CI AppImage | [ebb93c83…](hyprland/build.json) | `x264enc` | 14.766667 / 14.766666 s, H.264 | 37.977 whole clip, frozen 0.000 | 136 → 162 | — | — |
| Budgie Fedora 45 RPM | [ebb93c83…](budgie/build.json) | `openh264enc` | 14.300000 / 14.299999 s, H.264 | 15.790 / 42.877, frozen 0.006 | 136 → 163 | — | — |

Every lane ran `26.1118.5424-dev+g652b83781a90`. Motion on two sides is listed in pre-cut then post-cut order. The Omarchy and Budgie smoke recordings used video only.


## Debian 13 Plasma Wayland

Plasma 6.3.6, Qt 6.8.2 and Debian 13 kernel 6.12.107. The Debian CI package SHA-256 was `17e308b3a00fd49a469fa411bed92ebc6bf170c40315fe5e6c2a0c84ca16ffec`. The working capture used KDE screencast, with system audio and a synthetic PipeWire microphone. The exported MP4 contained H.264 and AAC. A diagnostic capture selected `vah264lpenc` with `avenc_aac`. The installed export helper used `h264_vaapi` and AAC when replaying the E trim and cut. [Build](d69/build.json), [platform](d69/platform.txt), [encoder diagnostic](d69/live-encoders.txt), [CLI trace](d69/steps.jsonl).

- **A.** Review opened paused at zero and 1440×900 with 12 thumbnails and the five onboarding gestures. The exact skim reported 3.228214 s. The visible counter was 71, the decoded non-keyframe at 3.233000 s, 4.786 ms from the reported cursor time. [Opening and panel](d69/A-initial.json), [skim evidence](d69/A-skim-counter.json).
- **B–D.** Both bracket drags updated the edge preview and output clock. The real C key cut the chosen range, moved the playhead one second before the seam and shortened the clock. Play across jumped the seam, Restore removed it and Undo/Redo traversed the edit history. The cover panel showed the kept start/end frames and Blur displayed its warning. In the focused follow-up, a real drag placed the box and clicks on Save and Upload left placement active. [Trim](d69/B-trim.json), [cover bounds](d69/D-initial-bounds.json), [disabled controls](d69/D-placement-disabled.json), [recheck](d69/D-G-recheck.jsonl).
- **E.** The native Save a copy chooser saved 312 video frames at 30 fps. Zero cut-marker frames or removed counters decoded. Both kept source neighbours match the exported seam, with the test area covered on both pictures. The presentation-slack rule covered the picture at the 7.600 s cover edge as well. [Chooser and save result](d69/E-save-result.json), [decoded frame, motion and audio evidence](d69/E-decoded.json).
- **F / AC2.** A fresh still capture exercised adaptive capture. The deterministic replay used the same first-pass sparse working clip with 12 source frames one second apart. Trim start 0.200 s brackets at packet PTS 0/1 s, cut start 4.800 s at 4/5 s, cut end 7.800 s at 7/8 s and trim end 10.700 s at 10/11 s. Cover edges 8.200 and 8.600 s both fell in the 8/9 s packet gap, which is 7.890/8.890 s after the 110 ms stream origin is applied. Its held picture occupied output 4.700–5.700 s. All 30 decoded frames were opaque in the tested area. The two kept tone runs lasted 2.010 s each at 500 and 1300 Hz. The export contained no 900 Hz cut tone. The decoded duration and clock were both 7.500 s. [Live capture packets](d69/F-live-packets.json), [sparse timestamps, tones and pixels](d69/F-gap-analysis.json).
- **G.** At 1100×700, Edits opened beside the fitted picture. Escape closed it and Space reopened it from the focused button. [Folded Edits](d69/G-overlay.png), [after Escape](d69/G-escape.png), [keyboard focus](d69/G-focus.png).
- **New 1.** At 1000 Hz and 440 Hz, the working file had the two lab audio inputs. Clicking the Format menu checkbox and saving MP4 produced zero audio tracks. [Format menu](d69/N1-format-menu.png), [input tones](d69/N1-working-tones.json), [MP4 stream list](d69/N1-muted-media.json).
- **New 2.** Set Out and cover Set to playhead left the paused 4.633 s picture in place. The last exported frame was counter 113, the same picture, with the test area covered. [Paused-frame trace](d69/N2-frame.json), [decoded output](d69/N2-last-media.json).
- **New 3.** The lab delayed the isolated resident's acknowledgement for 1.55 s. With a trim acknowledgement pending, Ctrl+Enter queued Upload. Changing Format's audio checkbox surfaced “Upload cancelled: you changed the clip. Press Upload again.” with no archive write. The next queued Upload with no further change completed one file via the local destination. [Cancellation state](d69/N3-cancelled.json), [operation](d69/N3-committed.json), [payload inventory](d69/N3-local-payloads.json).

### Debian live recipe

The five selected checked-in recipes ran against the installed package and exact CI UI catalog. Playback, cut flow, trim, covers and Save a copy captured their native fixtures, then the stock profile refused window geometry. Its stated reason refers to Qt 6.4. The installed Qt is 6.8.2. A retry of cut flow with the checked-in read-only KWin witness in a scratch profile reached the live review and failed to connect to `/run/user/1000/at-spi/bus`. Direct `recording.review` actions against the real window, including `setCoverEdge` and `resize`, completed. [Default profile receipt](d69/live-default-profile.json), [KWin witness receipt](d69/live-kwin-witness.json), [setCoverEdge result](d69/H-set-cover-edge.json).

## Linux Mint 22.3 Cinnamon X11

Cinnamon 6.6.9, Muffin 6.6.3, Qt 6.4.2. The Ubuntu 24.04 CI DEB SHA-256 was `78a6a540df7237ec757d89e7e63efcc0b2af7685e75946d18e69cb5caf738744`. The live encoder was `vah264lpenc` with `avenc_aac` for the mixed system audio and lab microphone. [Build](m74/build.json), [platform](m74/platform.txt), [live encoder](m74/live-encoders.txt).

- **A–D.** The review opened at 1440×900, paused at zero. The exact skim at cursor time 3.228809 s displayed counter 76, the independently decoded non-keyframe at 3.233000 s. Both bracket drags previewed their edge frames, and the clock followed the brackets. The real C shortcut cut the selection. Play across, Restore, Undo and Redo behaved as requested. X armed a cover, the placement banner named the span and Save or Upload could not activate. Escape cancelled. The second attempt used a real box drag. The cover links and Blur warning were visible. [Skim comparison](m74/A-skim-counter.json), [edge drags](m74/B-trim.json), [placement state](m74/D-placement-disabled.json), [cover bounds](m74/D-boundaries.json).
- **E.** The native chooser saved 304 video frames at 30 fps, with a one-microsecond difference between the file duration and the clock. Both kept source neighbours were adjacent and covered in the MP4. Zero cut-marker frames or removed counters decoded. The exporter conservatively covered one more picture at each cover boundary. [MP4 decode](m74/E-decoded.json).
- **GIF and WebP.** Pillow decoded 152 moving frames in each regular animation, with zero cut markers, zero removed counters and no uncovered interior cover frames. The durations were 10.130 s (GIF) and 10.132 s (WebP). A leading cut to the final packet left counter 360. Both the GIF and WebP decoded as one 640×320 image of counter 360. The single-image WebP has no animation delay. [Animation and pixel decode](m74/animations-decoded.json), [single-frame source](m74/single-input.json).
- **G.** At 1100×700, Edits opened as an overlay beside the picture. Escape closed it and Space reopened it from the focused button. [Overlay](m74/G-overlay.png), [keyboard focus](m74/G-focus.png).
- **I.** Quiet-host CPU busy fraction was 0.01 at baseline. The 3840×2160, 60 fps, approximately three-minute fixture used a warm-up and five measured warm runs for each count. The nearest-rank p95 for five runs is the largest measured time.

  | Tiles | Worker times (ms) | Worker p95 | Process p95 | Worker budget |
  | --- | --- | ---: | ---: | ---: |
  | 12 | 401.5, 400.2, 400.7, 401.7, 400.3 | 401.7 ms | 553.3 ms | ~450 ms |
  | 24 | 707.2, 706.7, 710.9, 713.1, 709.8 | 713.1 ms | 861.5 ms | ~750 ms |

  [Raw timing, helper build and fixture hash](m74/filmstrip.json).
- **New 1.** The real Format menu disabled sound. The saved MP4 had no audio stream. The source contained both the system and synthetic microphone tones. [Menu](m74/N1-format-menu.png), [input tones](m74/N1-working-tones.json), [decoded MP4](m74/N1-muted-media.json).
- **New 2.** Set Out and cover Set to playhead both preserved the 4.500 s paused picture. The MP4 ended on the same counter 114 with its area covered. [Paused-frame trace](m74/N2-frame.json), [decoded last frame](m74/N2-last-media.json).

- **New 3.** The delayed acknowledgement test showed “Upload cancelled: you changed the clip. Press Upload again.” after the user changed Format. The isolated archive held no output for that attempt. The next waiting Upload, with no further change, completed once and added one file. [Cancelled state](m74/N3-cancelled.json), [completed operation](m74/N3-committed.json), [archive inventory](m74/N3-local-payloads.json).

- **F / AC2.** Replayed the same 12-packet sparse capture with the 0.200–10.800 s trim, 4.800–7.800 s cut and 8.200–8.600 s cover. The trim and cut edges fell strictly inside the 0/1, 4/5, 7/8 and 10/11 s packet brackets. The two cover edges fell between the 8 s and 9 s packets. The export clock and file were 7.600 s. All 30 decoded output pictures at 4.700–5.700 s were opaque throughout the cover interior, with maximum 8-bit RGB channel value 2. The kept tones at 500 Hz and 1300 Hz each lasted 2.010 s. The cut's 900 Hz tone was absent. [Live adaptive capture packets](m74/F-live-packets.json), [deterministic replay timestamps, tones and pixels](m74/F-gap-analysis.json).

The fresh still captures had maximum adjacent video packet gaps of 34 ms on both desktops. The AC2 replay used the same SHA-verified sparse fixture on each private recording's working path while exporting through the real window. The harness restored each original working file after that check. The fixture's raw video packet PTS runs from 0 through 11 s in one-second steps. [Sparse fixture SHA-256](sparse-fixture.sha256).

### Cinnamon live recipe

The exact-catalog run selected Playback, Cut flow, Trim, Covers, Format, Save a copy, Status actions and Advice. All fixtures recorded natively on X11. The Playback, Cut flow, Trim and Covers scenarios hit their 120 s recipe deadlines. Format and the failed-save Status actions scenario each found zero matching owned live controls. Save a copy found zero matching windows for geometry. Advice used a regular file as the parent of the requested MP4 path, waited for the resident to report the failed save, then removed the blocker. The recipe expected the review's Details control. The live window showed no error band or Details control at the assertion. The fixture submits RPC `recording.saveCopy`, whose failure is returned through `lastExport`. The native chooser submits a review event with a separate completion handler for the error band. This fixture exercises the RPC path. The direct Format click, native Save a copy chooser, cut, playback, trim, real cover placement, `setCoverEdge` and `resize` all passed separately. [Full recipe receipt](m74/live-recipe.json), [failed-save witness](m74/H-advice-fixture.png), [live direct-action trace](m74/steps.jsonl).

## Fedora 44 GNOME Wayland smoke

Final RPM SHA-256 `89debd737fefc139153314bd8ddfebc77f1125e9b5d2ae2d175b325699bb42e4`. GNOME Shell and Mutter 50.6, Qt 6.11.2. The final review opened at 1440×900 on the normal workspace without Escape, both on the first review and on the subsequent moving capture. Published nightly `26.1117.5114` opened in Activities on this same desktop and needed Escape to show its normal workspace window. Both builds displayed the existing setup notification. [Final initial view](f44/av-review.png), [published nightly initial view](f44/S-nightly-initial.png), [nightly after Escape](f44/S-nightly-workspace.png), [final build](f44/build.json), [nightly build](f44/nightly-build.json).

A cut and a redaction exported to a 413-frame MP4. The export excluded all 19 marked frames and kept both source neighbours adjacent. [Review](f44/S-review.png), [export decode](f44/S-decoded.json), [encoders](f44/live-encoders.txt).

## Omarchy Hyprland guest smoke

Omarchy 4.5.0, Hyprland 0.56.2. The CI AppImage matched SHA-256 `8e0955f52ed044dbd57880bfe6b06933c628bf1d1bf6ca52e35e09ba1e01dc8a` and the running resident reported the pinned tree. The app captured on native `wlr-capture` with `x264enc` and opened a full 1280×800 review on the guest display. The first fixture-player attempt aborted in its default graphics output. The run switched that synthetic fixture to mpv's native Wayland SHM video output. [Build](hyprland/build.json), [fixture-player log](hyprland/player-diagnosis.log), [guest and encoder](hyprland/platform.txt), [opening](hyprland/av-review.png).

The H.264 MP4 had 443 video frames. The cut removed all 18 marked frames and the retained counters matched the source neighbours. The cover applied in the selected retained interval. The exported and source clips were copied off the guest and hashed before retirement. [Cut and cover](hyprland/S-review.png), [decoded export](hyprland/S-decoded.json), [compare motion](hyprland/S-motion.txt), [wall](hyprland/wall-connected.json), [retirement](hyprland/retire.json).

## Fedora 45 Budgie guest smoke

Budgie 10.10.3, labwc 0.20.2, Qt 6.11.2. The Fedora 45 CI RPM SHA-256 was `c54431851427e7c72705ba69824378763ca6d5fbb4893876d437c7d8055ad0ea`. The disposable overlay used the distro's Cisco OpenH264 2.6.0 package in place of the golden's `noopenh264` placeholder, and the app captured with `openh264enc`. The window opened at 1256×752 with the desktop panel clear. [Running build](budgie/build.json), [platform and encoders](budgie/platform.txt), [opening](budgie/av-review.png).

The 429-frame MP4 contained zero of the 20 marked frames in the source and kept both source seam neighbours. The first check's single-pixel marker probe included three later frames from a similar colour in the moving fixture, so its cut extended to the last source frame. The rerun identified the actual marker at three points inside its rectangle and re-exported the same working clip. The first and final exports were retained and hashed on the builder. [Corrected export decode](budgie/S-decoded.json), [first attempt decode](budgie/S-first-attempt-decoded.json), [cut and cover](budgie/S-review.png), [wall](budgie/wall-connected.json), [retirement](budgie/retire.json).

## CI gate

The native builds, AppImage and exact UI catalog completed. The required CI check is red. WaitLint reported raw `qWait` calls at lines 625, 652 and 955 of `tests/gui/test_review_window_actions.cpp` and lines 400 and 416 of `tests/integration/test_recording_service.cpp`. [Contracts job](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44287865139/job/134745931306), [failure excerpt](ci-contract-failure.txt).

## Annotated full-desktop pictures

The installed production editor added the boxes and arrows. The source and annotated PNGs are full 1920×1080 captures. The opening pictures came from fresh recordings with the moving fixture already on screen at the first frame.

| Desktop | Opens | Cut | Cover and panel | Folded Edits |
| --- | --- | --- | --- | --- |
| d69 | [Open](d69/A-presentation-annotated.png) | [Cut](d69/C-cut-annotated.png) | [Cover](d69/D-cover-annotated.png) | [Edits](d69/G-overlay-annotated.png) |
| m74 | [Open](m74/A-presentation-annotated.png) | [Cut](m74/C-cut-annotated.png) | [Cover](m74/D-cover-annotated.png) | [Edits](m74/G-overlay-annotated.png) |

## Lab leases and retirement

All times are UTC. Each native run had one verified desktop lease. The guest launches each had an independent f44 lease and wall tile. The two guest overlays and tiles were retired after smoke. Media hashes matched the files exported to the builder.

| Lock used | Scope | Acquired | Released |
| --- | --- | --- | --- |
| f44 `rrfinal-gn0` | Published nightly control | 10:45:58 | [10:48:37](f44/nightly-release.txt) |
| d69 `rrfinal-d69` | Plasma full rows and recipes | 10:52:42 | [11:12:02](d69/release.txt) |
| m74 `rrfinal-m74` | Cinnamon full rows, timing and recipes | 11:12:06 | [11:38:40](m74/release.txt) |
| f44 `rrfinal-f44` | GNOME CI RPM smoke | 11:38:44 | [11:41:42](f44/release.txt) |
| f44 `rrfinal-omarchy` | Omarchy CI AppImage smoke | 11:41:45 | [11:46:13](hyprland/release.txt) |
| f44 `rrfinal-budgie` | Budgie CI RPM smoke | 11:46:17 | [11:51:55](budgie/release.txt) |
| d69 `rrfinal-d69-focus` | Plasma real cover drag, Edits focus and encoder check | 11:51:59 | [11:54:56](d69/focus-release.txt) |

Omarchy overlay `ca76dce2-d131-4b28-843a-40b32e114acc` retired at 11:45:57 UTC. Budgie overlay `7f6bae24-2b84-4b3b-a0ef-ae3be778563f` retired at 11:51:44 UTC. The scoped native f44 DNF transactions invalidated pending daemon offline transactions. [Omarchy retirement](hyprland/retire.json), [Budgie retirement](budgie/retire.json).

