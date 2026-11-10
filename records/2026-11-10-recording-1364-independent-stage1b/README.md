# Recording #1364 independent timing diagnosis — stage 1b

Code PR https://github.com/patrick-hudson/put.gd-desktop/pull/1372, docs PR #1374. Tested the remote head at stage-1b start: 598648cc7ec5ca52240bc9535890a014f136d608 (verified with git ls-remote; detached worktree). Its CI run is 42760908969; package build 26.1110.4480-dev+g20f4c6911013, synthetic merge 20f4c6911013. Baseline is the still-latest published v26.1109.4346-nightly, source 68c59afe53c1ec6b0e68fdca746f878e41afd2b2. Package jobs passed; CI test jobs encountered dependency-download failures. This is a diagnostic pass, not final-head acceptance. No product source changes, PR body edits, merges or watches. Stage 2 has not started.

## Method and validity

Audio minus video, in milliseconds: positive = sound later, negative = picture later. Bound ±33.333 ms at 30 fps; **bold** means outside. Tables contain each recording's exported median (wf-recorder has no export step). Every requested run is shown; no averaging or discarding of alignment failures. Working values, every marker pair and spreads are in raw JSON. The working/export median shift is at most 0.8 ms across the system-only comparisons; timing failures already exist before export.

62 primary recordings: Hyprland20, physical desktops36, and Budgie three wf-recorder plus three paired nightly. All primary put.gd captures have saved exports, motion >1, at least 15 marker pairs in system-only comparisons, and saved frames passing unchanged coverage checks. wf-recorder has 17–18 pairs, motion >1 and passing saved-frame checks. All inputs are the same moving white-flash/1kHz-burst marker method, shown by the GTK cover. System sound is always a private null output made default for the run; both old defaults restored by name. Microphone is off and not requested. No real microphone, physical speaker playback or external upload destination. No workstation builds, ctest, encoding or VMs.

Builds alternate nightly/PR for each format in every round. Hyprland: five rounds, two formats, two builds, one fresh Omarchy4.5/Hyprland0.56.2 guest on f44, 2 vCPU/6144MiB/virtio-vga software rendering, SSH22567/VNC5957/wall6067. The harness applies its existing Hyprland on_focus_under_fullscreen guard to region targets too; all frames pass and the flag returns to its prior value. Region0,0,960,540, marker640x360; 6s lead, 16s recording without pause. Native Cinnamon/m74, Plasma6.3/d69 and GNOME/f44 each use three rounds with their distro packages extracted into private roots, distro Qt, the same lead/duration/region and full-screen cover on the host's visible native VNC tile. Host version files identify exact sessions/packages. Native marker is1280x720 on1920x1080. No offscreen/mock evidence.

## 1. Hyprland repeat

| Run | Nightly MP4 | PR MP4 | Nightly WebM | PR WebM |
|---|---:|---:|---:|---:|
| 1 | +17.3 | +4.7 | +14.5 | +1.5 |
| 2 | +8.7 | +14.7 | +7.5 | +1.5 |
| 3 | -11.3 | +18 | +23.5 | +1.5 |
| 4 | +33.3 | +12.7 | +21.5 | +9.5 |
| 5 | -14 | +16 | +17.5 | +5.5 |

The [original stage-1 record](https://github.com/patrick-hudson/put.gd-evidence/tree/2c0325bbc7dc4a08622c4a6adeb1ea03e5963468/records/2026-11-10-recording-1364-independent-stage1) retains the ec0d5ad22 -73.5 ms PR WebM result, which is real in its retained stage-1 clip (working -74.3), but did not repeat here. Neither format shows a consistently early PR path. This does not disprove an intermittent failure, and is not proof of a product fix: RecordingPipeline.cpp is unchanged between ec0d5ad22 and598648cc7. The current harness's system-only setup uses --no-microphone (one private null output) rather than creating unused microphone/holding nodes as the older harness did; both builds in this comparison get identical setup. Raw: h/r/results.json, working/, out/, frames/.

## 2. Physical desktops

Each cell is MP4 / WebM.

| Physical desktop / build | Run 1 MP4 / WebM | Run 2 MP4 / WebM | Run 3 MP4 / WebM |
|---|---:|---:|---:|
| Cinnamon / nightly | -17.3 / -0.5 | -11.3 / -19.5 | -10.7 / +17.5 |
| Cinnamon / pr | -21.3 / -15.5 | +4 / -14.5 | -8 / +1.5 |
| Plasma / nightly | +7.3 / +13.5 | -4.7 / +25.5 | +6.7 / -16.5 |
| Plasma / pr | -10 / +16.5 | -12 / -2.5 | -2.7 / +17.5 |
| GNOME / nightly | +8.7 / +29.5 | **+36** / +7.5 | +28.7 / **+35.5** |
| GNOME / pr | **+40** / +23.5 | +14.7 / +13.5 | +21.3 / +28.5 |

Cinnamon and Plasma have all cells inside. GNOME has three out-of-bound cells: PR MP4+40.0, nightly MP4+36.0 and nightly WebM+35.5. Therefore GNOME is not an all-cell alignment pass. The three-round samples do not show a consistent PR regression in either format. A progress update prematurely said every PR cell was inside after reading only the latest log lines; full raw review caught PR+40.0 and corrected the commentary and STATUS.md before this report.

Native binaries were never rebuilt. Cinnamon used separate private roots. Plasma initially fell back to a portal picker after switching private executable paths: that attempt was saved under d69/changing-paths/ and excluded. The corrected harness copies unchanged package bytes into one private active root before each build, with a stable KWin permission entry, restoring the original desktop-entry state after the run. Every primary Plasma recording reports kde-screencast. GNOME reports mutter-screencast and Cinnamon x11.

f44 had no putgd package or extension before testing and no owner applications open (process audit and visible desktop). Installed the matching PR RPM, re-logged in, verified extension21 ACTIVE, then compared both private package roots against that backward-compatible extension. Cleanup removed only putgd with --noautoremove, restored enabled/disabled extension settings exactly, re-logged in after another owner-app check, and verified package/extension absent again. Audio defaults returned by name; actual analog input stayed SUSPENDED. First GNOME attempt refused to record while Activities Overview was up (cover fraction0.615); saved failure context, exited Overview via visible VNC console, retried with unchanged gate. Raw primary: m74/r, d69/r, f44/r. Native package states on m74/d69 were not modified.

DNF emitted an invalid/pending offline-update transaction warning during the authorized RPM install. Its pre-install validity was not recorded, so it would be wrong to claim this was a newly valid plan before the test or to reschedule it speculatively. The original transaction file remains unchanged (SHA256 bdfea34f2342c957794f7a972ba13d29f6c157c87ed6ad00534cb6b0da09fc82), with its cached RPMs and a private backup retained on f44. No offline OS upgrade, cleanup or replan was performed. This caveat is separate from the verified restored putgd package/extension/audio state.

## 3. Independent Budgie recorder

Fresh Fedora45 Budgie10.10.3/labwc0.20.2 guest on d69, 2 vCPU/6144MiB/virtio-vga, SSH22568/VNC5958/wall6068. Paired wf-recorder first, then put.gd nightly, for three rounds on that same guest with the same marker player and private output monitor. No put.gd resident or recording helper captures while wf-recorder runs; put.gd is used only to generate/analyze the fixture, then for the paired nightly recording. Independent capture is distro wf-recorder0.6.0-5.fc45 (commit587a357), wlr-screencopy, PulseAudio source named explicitly in each wf-N.json; --no-dmabuf, 30fps, region0,0 960x540, libvpx-vp9 realtime/cpu-used8 and AAC in Matroska. No wf-recorder code was modified. [Upstream recorder](https://github.com/ammen99/wf-recorder).

| Run | wf-recorder VP9/AAC Matroska | Nightly MP4 | Marker pairs wf / nightly |
|---|---:|---:|---:|
| 1 | **-56** | **+43.3** | 17 / 16 |
| 2 | +26 | +12.7 | 18 / 16 |
| 3 | **+43.3** | **+38** | 18 / 16 |

Both recorders breach the one-frame bound in two of three runs. They do not reproduce one stable, identical +35–50 ms offset. The independent recorder is not a clean passing control, so these data cannot uniquely blame put.gd's nightly Budgie path. Equally, this is not sufficient proof to waive the precise standing offset as a fixed compositor/guest outside limit. It establishes substantial timing variation without put.gd capture code; that narrower finding is what should be carried forward. Budgie remains unaccepted against the strict one-frame bound. Raw: b/results.json, b/wf-1.json through wf-3.json, b/out/wf-*.mkv and paired nightly exports/working clips and frames.

Preserved setup attempts: FFV1/PCM was not decodable by the packaged analyzer and wf-recorder's PCM capture emitted a PulseAudio read error (failure frames extracted with distro FFmpeg); OpenH264/AAC failed because the guest's distro OpenH264 encoder could not initialize. Those attempts and their paired nightly runs are under b/r-ffv1-pcm and b/r-openh264, excluded from the primary comparison. VP9/AAC passed an independent encode/decode smoke check and all three actual captures then passed marker/audio/motion/visual checks. The guest stayed in active use through correction and was retired as soon as collection completed.

## Evidence and cleanup

summary.json retains all primary raw rows and tables.md the three tables. The original raw results, logs, surviving working/export clips and saved visuals are present. Repeated generated marker inputs are retained privately on the builders and workstation collection; retained-marker-index.json gives SHA256, size, host and exact restore path. Completion manifests describe the full original exported trees including those retained inputs; their hashes were checked before publishing. Test sources and package build-info/CI identities are included. No credentials or protected login values were used or published.

Both VM overlays were exported/verified and retired through guarded cleanup; state, completion manifests and completed overlay-cleanup receipts are in h/ and b/. All owned guests, tunnels and tiles are gone; immutable goldens preserved. m74 released05:57:58UTC, d69 06:00:53UTC, f44 06:19:11UTC, well before the coordinator's10:15UTC deadline. All desktop-lock cleanup checks passed; no owned processes or desktop lease remain. Private extracted inputs, source and full evidence remain on the builders for reproduction. Stage2 waits for the coordinator's final head and new CI packages.
