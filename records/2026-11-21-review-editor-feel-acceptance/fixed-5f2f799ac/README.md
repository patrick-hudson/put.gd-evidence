# PR #1791 retest on 5f2f799ac

[Manual CI run 44952020879](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44952020879) succeeded at commit 5f2f799acf9464af978a742365fd004bd41479fc, tree 46131d860bcc784a214baaed4f05ce3590dd7545, version 26.1121.6125-dev+g5f2f799acf94. Each desktop's receipt pairs the live resident's diagnostics.build with the verified SHA-256 of the CI package. [Original acceptance record](../README.md).

| Desktop | CI asset | Build proof |
| --- | --- | --- |
| Aurora Plasma 6.8 Wayland | AppImage | [Identity](measurements/plasma-build.json) |
| Mint 22.3 Cinnamon X11 | Ubuntu 24.04 DEB | [Identity](measurements/cinnamon-build.json) |
| Fedora 44 GNOME Wayland | Fedora 44 RPM | [Identity](measurements/gnome-build.json) |
| Fedora 44 Budgie labwc Wayland guest | AppImage | [Identity](measurements/budgie-build.json) |
| Omarchy Hyprland Wayland guest | AppImage | [Identity](measurements/omarchy-build.json) |

| Row | Plasma | Cinnamon | GNOME | Budgie | Omarchy |
| --- | --- | --- | --- | --- | --- |
| A · Late grip and cover slide spot checks | Pass | Pass | — | — | — |
| B · Skim spot checks | Fail · post-click travel | Fail · post-click travel | — | — | — |
| C · Snap spot checks | Pass | Pass | — | — | — |
| D · Placement, typed fields, refused Save | Fail · copy saved after refusal | Fail · copy saved after refusal | — | — | — |
| E · Keys | Blocked at original head | Pass at original head | — | — | — |
| F · Cut-spanning redaction and narrow blur | Pass | Pass | — | — | — |
| G · Compact window | Pass at original head | Pass at original head | — | — | — |
| H · CLI, MCP and surface recipe | Fail · surface recipe | Fail · surface recipe | — | — | — |
| S · Desktop smoke | — | — | Pass | Pass | Pass |

A–D, F and H were retested with the fixed build. The original record retains the full hit-offset tables and annotated before/after pictures. The retest used an owned synthetic fullscreen source, real pointer input and local Save a copy. The uinput pointer had middle-button emulation disabled. The private resident had no service profiles. System and microphone audio were off. The full desktop exports used the Save a copy button after local fixture setup. The smoke exports used recording.saveCopy.

## Plasma

- **A.** The pointer rested 4 px outside the east grip center, slipped another 6 px, then pressed about 18–19 ms later. On redaction and blur, an ensuing drag moved only the east edge and a still press left it unchanged. Eight cover-bar drags retained all 63 frames, including slides against both clip ends. [Grip](measurements/plasma-late-press.json) · [Slide](measurements/plasma-cover-slide.json).
- **B.** The 2.25 s sweep displayed 29.0 distinct 1080p frame updates/s and restored the playhead frame on exit. A 1198 × 718 recording also showed an exact skim and returned to the starting playhead. For the post-click check, click the filmstrip, wait 240 ms, nudge 1 px, move to (+14,+8) px from the anchor, then wait 240 ms. This quiet leg showed an exact skim. A straight (+11,0) leg stayed quiet and further deliberate travel engaged skim. The seeded assertion follows the round-5 post-click travel rule and the documentation draft. The shipped implementation allows dwell again at a 12 px radial distance, which accounts for this observation. [Sweep](measurements/plasma-skim-visual.json) · [Post-click](measurements/plasma-post-click-skim.json) · [Unaligned skim](measurements/plasma-unaligned-skim.json).
- **C.** The snap guide appeared, Ctrl bypassed snap, the Snap switch disabled snap, and at 2× the pointer scrubbed to a frame beside a cut edge. [Snap](measurements/plasma-snap-ctrl-n.json) · [Adjacent frame](measurements/plasma-snap-to-cut-and-adjacent.json).
- **D.** Click and 5 × 6 px wobble made the default box. Drags of 8 × 3 and 42 × 4 px kept their thin shapes. Typing applied a 3–7 s cover interval, verified by four luma samples in the MP4, and the Cut Starts and Ends fields applied 3.5 and 6.5 s in separate saves. At 24 fps, typing 3.1 and 6.1 s rounded outward to 3.083333 and 6.125000 s. Each saved duration matched within one frame. [Cover](measurements/plasma-typed-save-copy.json) · [Cut](measurements/plasma-cut-fields-save.json) · [24 fps cut](measurements/plasma-cut-fields-24fps.json).
- **D failure.** Add a cut at 4–6 s, trim to 3.9–4.1 s, then select the cut. Type 0:03.8 in Starts and click **Save a copy** while the field is focused. Choose a fresh filename. The resident returned recording_cut_empty and retained the previous cut and revision. The app still wrote refused.mp4 and reported “Saved refused.mp4.” [Refusal and save state](measurements/plasma-refused-save.json) · [Desktop screenshot](pictures/plasma-refused-save.png).
- **F.** The 15.366667 s MP4 matched the displayed 15.366668 s length. All 157 unique cut-marker frames were excluded. Luma samples confirmed redaction on each side of the cut and preserved source content before and after the cover. Mean luma motion was 34.27 in the export versus 0.0021 in the frozen control. A 4 × 64 px blur on a 1920 × 1080 source reduced the sampled preview luma range from 132 to 25 and the export range from 202 to 156. [Export](measurements/plasma-export-metrics.json) · [Blur](measurements/plasma-small-blur.json).
- **H.** All 23 CLI and 24 MCP action/inspect checks passed. These include both setCutEdge edges, scrollTimeline, both placeMask argument forms, and rejection of both arguments or neither argument with the edit unchanged. Each wire used its displayed zoom ladder. In the unchanged wheel-lanes recipe, the native adapter placed all five overlapping covers. The test then failed the two-lane and +n chip assertion. The full surface driver was outside this adapter run. [Agent parity](measurements/plasma-agent-parity.json) · [Surface checks](measurements/plasma-surface-recipe.json).

## Cinnamon

- **A and C.** Late east-grip drags resized both cover kinds and still presses left them unchanged. Eight cover slides kept 63 frames, including at the clip boundaries. Snap guide, Ctrl bypass, toggle and the neighboring-frame check passed. [Grip](measurements/cinnamon-late-press.json) · [Slide](measurements/cinnamon-cover-slide.json) · [Snap](measurements/cinnamon-snap-to-cut-and-adjacent.json).
- **B.** The 1080p sweep displayed 19.7 updates/s and restored the playhead. The same (+14,+8) px post-click sequence as Plasma engaged exact skim during the dwell. [Sweep](measurements/cinnamon-skim-visual.json) · [Post-click](measurements/cinnamon-post-click-skim.json).
- **D.** Click, wobble and thin-drags behaved as on Plasma. The typed cover used 3–7 s in the saved MP4, and Cut Starts and Ends applied 3.5 s and 6.5 s. At 24 fps the proposed 3.1 and 6.1 s cut edges became 3.083333 and 6.125000 s. The refusal sequence also returned recording_cut_empty, preserved the old cut and revision, and saved refused.mp4. [Cover](measurements/cinnamon-typed-save-copy.json) · [Cut](measurements/cinnamon-cut-fields-save.json) · [24 fps cut](measurements/cinnamon-cut-fields-24fps.json) · [Refused Save](measurements/cinnamon-refused-save.json).
- **F.** The 15.133333 s export matched the displayed 15.133334 s. It excluded all 151 cut markers and kept redaction on both sides of the cut. Motion was 34.12 versus 0.0072 in the frozen control. The 4 × 64 px blur reduced the sampled preview luma range from 133 to 26 and the export range from 198 to 153. [Export](measurements/cinnamon-export-metrics.json) · [Blur](measurements/cinnamon-small-blur.json).
- **H.** All 23 CLI and 24 MCP checks passed. The unchanged lane recipe placed five full-span covers. It observed one occupied lane and four hidden covers, then failed its two-lane assertion. The five bars reach the area reserved for the chip on lane 2 under T17, which accounts for the recipe mismatch. [Agent parity](measurements/cinnamon-agent-parity.json) · [Surface assertion](measurements/cinnamon-surface-recipe.json) · [Screenshot](pictures/cinnamon-surface-failed.png).


## Smoke exports

| Desktop | MP4 duration | Displayed length | Export motion | Frozen motion | Unique cut markers excluded |
| --- | ---: | ---: | ---: | ---: | ---: |
| [GNOME](measurements/gnome-export.json) | 10.166667 s | 10.166666 s | 30.66 | 0.0104 | 78 |
| [Budgie](measurements/budgie-export.json) | 10.733333 s | 10.733333 s | 29.25 | 0.0003 | 84 |
| [Omarchy](measurements/omarchy-export.json) | 9.866667 s | 9.866666 s | 31.67 | 0.0011 | 47 |

Budgie generated its MP4 in the guest. Its verified files were decoded on d69 after the guest's FFmpeg could not initialize H.264. Omarchy's first attempt timed out at the portal, and the next attempts stalled reopening the fullscreen source after the frozen review. The passing attempt clicked the visible synthetic output in the portal and restarted the owned fullscreen source for the moving clip.

## Desktop pictures

All pictures below show the 5f2f799ac run. The [original annotated before/after set](../README.md) captions the earlier builds separately.

- Plasma [full desktop](pictures/plasma-desktop.png) · [placement wobble](pictures/plasma-wobble-preview.png) · [annotated Cut Starts and Ends](pictures/plasma-cut-fields-annotated.png) · [cut-spanning redaction](pictures/plasma-cut-spanning-redaction.png) · [narrow blur](pictures/plasma-small-blur.png) · [refused Save](pictures/plasma-refused-save.png) · [unaligned skim](pictures/plasma-unaligned-skim.png).
- Cinnamon [full desktop](pictures/cinnamon-desktop.png) · [late grip](pictures/cinnamon-late-grip.png) · [placement wobble](pictures/cinnamon-wobble-preview.png) · [cut fields](pictures/cinnamon-cut-start-typed.png) · [cut-spanning redaction](pictures/cinnamon-cut-spanning-redaction.png) · [narrow blur](pictures/cinnamon-small-blur.png) · [refused Save](pictures/cinnamon-refused-save.png) · [surface assertion](pictures/cinnamon-surface-failed.png).
- Smoke [GNOME review](pictures/gnome-review.png) · [Budgie review](pictures/budgie-review.png) · [Omarchy portal](pictures/omarchy-portal.png) · [Omarchy review](pictures/omarchy-review.png).

## Lab cleanup

| Resource | Acquired or boot verified UTC | Released or retired UTC |
| --- | --- | --- |
| Aurora codex-1791-fixed-plasma | 22:01:22 | 22:10:13 |
| f44 codex-1791-fixed-gnome | 22:10:28 | 22:12:53 |
| m74 codex-1791-fixed-mint | 22:13:12 | 22:20:20 |
| f44 Budgie b2, e2070fba-293a-4d64-8633-cce30ff5785f | 22:03:55 | 22:07:43 |
| f44 Omarchy o3, 686a4667-a092-4da5-a699-329e3960bf0e | 22:08:33 | 22:14:22 |

Desktop sessions were released after their cleanup checks. The app packages were removed from f44 and m74. DNF invalidated a queued dnf5daemon-server offline transaction during the scoped package transactions. Both disposable guest overlays were retired with guarded cleanup after transfer and checksum verification. Their VNC wall tiles and tunnels were removed. [Cleanup receipts](measurements/lab-cleanup.json).
