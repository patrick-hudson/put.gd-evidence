# Independent #1364 stage 2: GNOME on physical f44

Product: PR1372 at cccf91a501247dce525217271b78b4665b0fbd0d, Git tree93ae895ea84a5a19a2b3de877573aa9f3189e480. Exact published GitHubActions run42774290115, nativeFedora44RPM26.1110.4538-dev+g1d19e1e8ac50 (package synthetic merge1d19e1e8ac506ddb12a80904749536dafdc9117a; identical source tree). Installed nativeRPM, distroQt6.11, Shell50.6/Wayland on physicalGPU. Extension21 verified ACTIVE after an owner-app audit and new login. No other lane VM or application build ran on f44 during timing.

Final PR head6f23ce41616f1a26ad445d76672c025d45d5c704 changes only tools/lab/record_run.py (24added/7removed lines total) from package headcccf91a50. Commit87a795f98 has the identical SHA256 used here; the next lab-only commit repairs reuse of a destructively removed fixture and rejects multi-recording output-removal invocations. This row retained the coordination driver and used separate fresh invocations instead. The product build is unchanged. The superseded87aCI42777375685 is not counted as a pass; final-head CI is reported in the combined record. This row uses the coordinator's corrected record_run.py, SHA256e5f1764ff963e974c3755267abb932ecc9aaccf0b23446b89767026fbe68398e, copied byte-for-byte under lab/. The corrected step had not been desktop-tested by the implementer. We retain its exact output, both countdown captures and operation results. The only additional test fixtures are: client-visible flash in cover_player.py at[40,220,100,40], and a physical-host safety guard in virtual_mic.py that restores the saved private monitor default before removing a simulated source only when that source is itself the current default. The leak-test's already-private output monitor remains the default. recording_bar_shots.py selects Capture settings, chooses only the simulated input in its private picture profile, and accepts an explicitly recorded QT_SCALE_FACTOR for picture-only150% coverage. No product binary or source was patched.

All sound goes to private null sinks. Every microphone stream is the checked simulated remap source. A private monitor is the outer default input for the campaign: monitor refusal and hotplug never open the physical analog input. Inner defaults return to that guard; the outer fixture finally restores the original source/output by name and unloads modules by exact ids. Output-loss checks use an explicitly private fallback; the no-fallback/sound-cards-off variant is not run on f44 because network outputs also exist. The physical analog input is checked SUSPENDED.

Every recording contains the moving marker's sweeping bar. Audio-minus-picture medians are positive when audio is late. Required bound: -45 through+125ms, with no regression against same-desktop nightly outside observed run spread. One frame±33.3ms remains the target, reported separately. Nightlyv26.1109.4346 and the PR alternate for three runs performat. Paused microphone and mixed runs check captureStepMs and working/export offsets; raw marker pair timings and tones are retained.

Click timing is the ring's first visible frame minus the cover's flash on the actual button-press event. Pointer-based delayMs is retained as a historical diagnostic and is not the acceptance reference. The flash centre[90,240] sits inside monitor, region and window captures and outside every ring search box. Position errors remain measured against the scripted press. Test and measurement scripts are included.

Raw working clips and exported files are published. Full desktop source frames and generated marker inputs are retained privately with checksums and restore paths in retained-file-index.json; only inspected and app-cropped pictures are published. No recording or test source was deleted. Final cleanup/state/lease receipts and the combined results are added when complete.

## Observed results

**GNOME row PASS.** 29 retained exported clips and their 29 working clips decode/probe successfully. Export motion scores 4.863–40.864; every clip has a cover-checked visual. All 25 signal-bearing alignment medians meet −45/+125 ms; 24 of 25 meet the ±33.3 ms target. The Ready-follow clip is +34.0 ms, the one target miss. Muted-input runs contain no usable 1 kHz bursts: their noise-derived offsets are not alignment measurements.

| Check | MP4 | WebM | Result |
|---|---|---|---|
| Microphone alone, 3 s pause | +5.3 ms, 17 pairs; step +0.9 ms | +28.5 ms, 17 pairs; step 0.0 ms | PASS; tone and motion; export shifts −1.0/−0.2 ms |
| Microphone + system, 3 s pause | −6.7 ms, 17 pairs; step −0.2 ms | +17.5 ms, 17 pairs; step +0.5 ms | PASS; both tones; export shifts +0.7/−0.2 ms |
| Toggle off, input still fed | 1 kHz peak 0.000356 | 1 kHz peak 0.000309 | PASS; 440 Hz system tone remains |
| Microphone pulled at 6 s | 14.867 s kept / 14.202 s recorded | 14.866 s / 14.196 s | PASS; inspect reports loss; 7 initial marker pairs each; unrecorded 440 Hz peaks 0.00377 / 0.000079 |
| Output removed, private fallback | 14.933 s / 14.258 s | 14.906 s / 14.251 s | PASS; remains recording; inspect names fallback.monitor |
| Output removed, muted simulated default microphone | 15.033 s / 14.352 s | 14.933 s / 14.261 s | PASS; fallback.monitor; 1 kHz peaks 0.000317 / 0.000298 |
| Ready hotplug, MP4 | none → plugged/off → on → pulled/requested → back/on | — | PASS; waits 0.26/0.04/0.72/0.49 s; 10 pairs, +34.0 ms; captured five bar states |
| Private default input is a monitor | prepare refuses recording_unsupported with monitor reason | — | PASS; other real input remains unopened |
| Same resident, desktop:3 capture → monitor recording → desktop:3 capture | captures completed/saved in 3.46/3.50 s, cover OK, 6216 changed countdown pixels each | — | PASS; recording 3/3 rings; no click error; motion 8.465 |

| System-only control | MP4 run 1 / 2 / 3 | WebM run 1 / 2 / 3 |
|---|---|---|
| PR installed RPM 4538 | +8.7 / +16.7 / +32.0 ms | +24.5 / +9.5 / +19.5 ms |
| Published nightly 4346 | +30.0 / +23.3 / +5.3 ms | +23.5 / +27.5 / +11.5 ms |

Builds alternate for every format/run. All 12 controls meet the one-frame target, with 16–17 pairs each and real motion. PR maximum is 2 ms later than nightly maximum, below the observed nightly run ranges (24.7 ms MP4, 16 ms WebM). Microphone/mixed medians show no worse absolute alignment beyond that spread. These are observational controls, not proof of identical timing distributions.

| Click target | Export rings | Ring minus client-visible flash, left/right/middle | Largest measured centre error |
|---|---:|---|---:|
| Monitor / same-session | 3/3 | −33 / 0 / 0 ms | 0.78 px |
| Region | 3/3 | −33 / −33 / −33 ms | 2.31 px |
| Window | 3/3 | 0 / 0 / −33 ms | 0.78 px |
| Monitor, setting off | 0/3 | not applicable | not applicable |

Working clips agree: all 9 rings; timing −34..0 ms, centres ≤2.18 px. All are within the 70 ms click bound. Region's original pointer-based analyzer skipped the first ring because its pointer was already at that position; the ring is visibly present in the retained clip. `click_measure.py` finds each actual client flash first and independently queries the ring around it, without requiring pointer arrival. Original pointer/ring diagnostics and the initial pointer-gated postprocessing log are retained.

## Excluded setup attempts, retained

- My first campaign grouped destructive fixture formats: microphone/output removal in MP4 consumed the fixture, so subsequent WebM requests correctly refused the missing microphone/output. Three WebM cells were rerun in fresh independent driver invocations (`fresh_removed.py`); originals remain, explicitly excluded.
- My shared default region rectangle remained in monitor/window/off requests. Product correctly refused `invalid_request Only region targets take a rect`. Corrected commands omit it; same-session uses the supplied `both_run.sh` unchanged. The first countdown of the invalid monitor attempt succeeded, but that attempt is not counted as case13.
- Picture-only helper first requested internal-only `captureSettings` through public ui.show. Its off/on/no-microphone photos had already succeeded; Settings was refused. Retried with documented ui.show settings and visible VNC Capture-tab navigation, at 100% and 150%. The first timed Settings frame expired before navigation; it is excluded. Final picture helper uses an explicit take-settings handshake.
- Annotation harness first used the SDK's old structuredContent attribute, then stopped on the normal editor_starting state. Corrected to structured_content and bounded editor_starting polling; successful official-SDK MCP receipts and all annotated outputs retained. No product or same-session workaround.

## Pictures and retention

All GNOME after-images depict the installed build 4538, whose product tree is unchanged at final head 6f23ce416. `pictures/gnome-nightly-bar.png` is the separately captioned before image from the published nightly4346. Boxes/arrows/labels/crops were applied by this build's own editor through the official-SDK MCP helper in an isolated offscreen resident; that annotation session is not desktop acceptance evidence. The alignment chart is generated directly from the real recording measurements with Cairo. Settings is pictured at actual Qt scale 1.0 and 1.5.

`pictures/cinnamon-bar-off.png` is an assembly supplement only: source is Cinnamon worker's retained `f/frames/pr-mp4-1-ready-plugged.png`, build4538 on physical m74; source record72c8486d3073caafafa2e39e3014e7232a4006de/records/2026-11-10-recording-1364-cinnamon-4538. The actual off control was cropped/boxed through the same editor. It does not claim a new Cinnamon run.

Physical f44 lease released **08:01:52 UTC** after two-step cleanup. The original absent package/extension state, exact GNOME extension arrays, and named audio defaults were restored after a second owner-app check and login; no lab modules or physical-input activation. Own process sweep is empty. Pre-existing pending offline plan's original transaction SHA remains bdfea34f2342c957794f7a972ba13d29f6c157c87ed6ad00534cb6b0da09fc82; no OS upgrade or speculative replan. `cleanup.json`, `after.json`, `lease-release.txt`, audio observer, container probes and retained-file index supply receipts. Raw source frames/marker inputs remain directly usable privately; no test source was deleted. Generated private authentication artifacts are not published.

The native package audit is published as a lossless derived source-hash entry list plus its canonical reference/hash. Five scanner false positives arose when dependency filenames such as sentry.ts were dictionary keys directly preceding file SHA256 values. Every filename/digest is preserved, decoded original JSON equality verified, and canonical CI bytes retained; no scanner rule is suppressed. The failed redacted scan report is included.
