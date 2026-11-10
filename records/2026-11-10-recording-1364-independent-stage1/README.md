# Independent recording timing diagnostics for #1364, stage 1

Code PR https://github.com/patrick-hudson/put.gd-desktop/pull/1372; docs PR #1374. Stage 2 has not started. No product changes, merge, or PR watch.

## Identities and method

Workstation worktree detached at requested head ec0d5ad22d8b415e152e3c9bb2084352ebaa90ab because the feature branch is owned by the implementer's worktree. PR CI run 42755920629, AppImage 26.1110.4474-dev+g68af31fcdc9f, built merge 68af31fcdc9f4455938cecf6ef4589ab33df44e6 (see ci-run.json and pr-build-info.json). Baseline published v26.1109.4346-nightly, source 68c59afe53c1ec6b0e68fdca746f878e41afd2b2. SHA-256 of each running AppImage is in every results.json.

All VMs and media work ran on f44 (192.168.68.70), QEMU/KVM, 2 vCPUs, 6144 MiB, virtio-vga without 3D acceleration, 1280x800. No workstation build, VM, ctest, packaging or encoding. Budgie 10.10.3 / labwc 0.20.2 / Fedora 45, run b, golden a6749512438d507ef2b2c47fe675955627464d9a5a85341002f91cd54fb401ad. Hyprland 0.56.2 / Omarchy 4.5, final control h3, golden bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256. State and bootstrap visuals identify each session. Each guest was on the display wall and retired immediately after collection.

The PR's marker/analyzer was used for both builds. 640x360 moving marker on a full-screen synthetic cover; region 0,0,960,540; 30 fps, 6 s lead, 16 s recording without pause, MP4 and WebM. Audio minus picture in milliseconds: positive means sound appears later in the clip; bound ±33.3 ms. Every primary audio export has at least 14 marker pairs, motion >1, a saved frame passing coverage checks, and saved export. Budgie build order: nightly/PR, PR/nightly, nightly/PR; microphone and mixed after each pair. Mixed records 1 kHz marker bursts from simulated microphone plus 440 Hz from private output. No real microphone or physical speaker output. Exact module IDs unloaded; results' microphoneRemoved.left is empty. System-only uses --mic off --system tone, routing marker and tone to the private null output.

## Audio results

All numbers below are each exported recording's median, not a median pooled across recordings.

| Input / build | Budgie MP4 (runs 1, 2, 3) | Budgie WebM (runs 1, 2, 3) | Hyprland MP4 | Hyprland WebM |
| --- | --- | --- | --- | --- |
| System / nightly | +19.3, +10.7, +54 | +40.5, +36.5, +36.5 | -14.7 | +1.5 |
| System / PR | +40, +38, +38 | +37.5, +32.5, +43.5 | +5.3 | -73.5 |
| Microphone / PR | +6.7, +50, +50 | +70.5, +11.5, +65.5 | -2.7 | +9.5 |
| Mixed / PR | +19.3, +36.7, +29.3 | +11.5, +54.5, +11.5 | -15.3 | +5.5 |

The same out-of-bound positive offset exists on pre-PR nightly on Budgie, in both formats. Therefore it predates this change in this Budgie capture/playback/guest chain; these tests do not isolate compositor from guest playback/scheduling. System-run median-of-medians: nightly +19.3/+36.5 versus PR +38/+37.5 ms (MP4/WebM). This is not evidence of a stable new Budgie system-audio shift greater than one frame. Presence of the baseline offset does not prove the PR has no additional timing issues: the retained Hyprland PR system WebM control is -73.5 ms while its nightly control is within the bound; that is an unresolved timing failure in this diagnostic pass. It is also not a blanket alignment pass: Budgie microphone/mixed exports still exceed the bound in multiple recordings.

Audio-only runs do not request click highlights, so the PR's recorder-drawn cursor path is not active in these comparisons. A positive offset means sound is late relative to picture, not late picture. Product-versus-guest inference is bounded to the baseline result, not a claim about physical Budgie hardware.

## Rings against client-visible effect

Corrected fixture flashes a white 100x40 patch at (40,700) for 500 ms when its GTK client receives the press. Clicks at 4/8/12 s, (200,100)/(640,100)/(1100,100), left/right/middle. Patch and ring first change use the same analyzer in the same exported clip. Patch is outside all ring search boxes. Negative below means ring before client effect; the early bound is -70 ms.

| Recording | First click | Second click | Third click |
| --- | --- | --- | --- |
| 1 | +0 | +34 | +34 |
| 2 | -34 | +0 | +0 |
| 3 | +0 | +0 | -33 |
| 4 | -33 | +0 | +0 |
| 5 | -33 | +0 | +0 |

All 15 rings are between -34 and +34 ms of the visible client effect. The first ring's old pointer-arrival metric on these same clips is -66/-67/-67/-100/-100 ms. Thus the large first-ring early value is a pointer-reference artifact, reproduced within the same recordings. Small one-frame early observations are not exclusive to the first ring (third click in recording 3 is -33 ms). Raw event/effect timing: b/s1/ring-effect2.json; ring detection and positions: b/s1/clicks2/results.json. Clips and ring frames remain beside those results.

## Preserved failed attempts and harness corrections

- Budgie block 2 had native GNOME host activity (host load up to 5.69, motion reduced). Both system runs are under interference-*, excluded and repeated PR/nightly under lower host load.
- First Budgie click fixture patch overlapped the first ring's search box. Its five recordings are diagnostic only under clicks/. The generic --frames check deleted their clips because the test recording bar reduced bottom-edge cover fraction to 0.8915 (<0.9); JSON/logs/ring frames remain. Corrected clicks2 keeps clips and analyzer ring frames; it does not apply the physical-desktop edge check to this disposable guest.
- Omarchy launch h used the wrong existing bootstrap key. No tests started. Retired; corrected fresh h2 used the documented Omarchy key.
- h2 initially lacked distro pulsesink. Three setup failures under dependency-* produced no recordings. Installed gst-plugin-gtk and gst-plugins-good in the overlay; no broad package upgrade.
- h2 WebM captures failed unchanged top/left coverage gates and were deleted by the harness. Their numbers are excluded from the primary table. Fresh h3 uses the same coverage gates and an isolated harness copy whose existing Hyprland fullscreen guard covers region targets too. h3 reports onFocusUnderFullscreen before=1/during=0 and restores it at cover close; all eight primary control frames pass. Original and corrected driver are included. This fixes measurement setup only, with no product source edit.

## Files and retirement

summary.json is the primary structured result; tables.md has the exact tables. b/s1 and h3/s1 contain primary raw JSON, logs, working clips, exports, frames and simulated-device receipts. h and h2 retain failed/provisional attempts. Every run has its state, completion manifest and overlay-cleanup.json; local verification checked every manifest hash and completed retirement status before publication. Immutable goldens preserved. All owned guests stopped, overlays deleted by guarded cleanup, tunnels/tiles removed; no physical desktop lease was taken. Source/scripts and host evidence remain private on f44. Stage 2 awaits the coordinator's final head and will use that head's CI packages.

The repeated 60-second generated marker inputs (about 501 MiB) remain byte-for-byte in the private f44 evidence tree and workstation collection. retained-marker-index.json gives exact SHA-256, size and f44 restore path for every input; they are omitted from this public record. Test source, every raw result JSON and log, surviving working/export clips and saved visuals are published here. Completion manifests describe the full original exported trees, including these retained marker files.
