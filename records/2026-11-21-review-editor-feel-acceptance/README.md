# Recording review acceptance for PR 1791

See the [campaign results through final candidate e28a26af0](followup-e28a26af0/README.md) for the retests and the matched final Omarchy smoke. This page records the original package run.

The candidate was built by manual CI run [44948858752](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44948858752). The source commit was `799e392e24ee807bc0c7ec8f3fc8814676cdc105` and the source tree was `ad40905e88405725ebee0697a418cebc124b47af`. The candidate AppImage identified itself as `26.1121.6117-dev+g799e392e24ee`. All fixtures were synthetic and used a private local destination. System audio and microphone were disabled.

The offset matrix used seed `2611216060` and the baseline driver's trajectories. The nightly comparison uses `26.1121.6060-nightly`. Images were annotated with the candidate's offscreen image editor.

## Results

PR 1791 did not meet acceptance. A blocked row is missing a required observation. Fail identifies an assertion that did not match the observed state.

| Row | Aurora Plasma 6.8.2 Wayland, AppImage | Mint 22.3 Cinnamon 6.6.9 X11, DEB |
| --- | --- | --- |
| A · Grip and edge offsets | Pass | Pass |
| B · Hover and skim | Pass | Pass |
| C · Drag, snap and cancel | Pass | Pass |
| D · Covers and typed Save | Blocked | Pass |
| E · Keyboard and focus | Blocked | Pass |
| F · Export | Pass | Pass |
| G · 1100×700 overlay | Pass | Pass |
| H · CLI, MCP and review recipe | Blocked | Fail |

| Smoke desktop | Exact package | S |
| --- | --- | --- |
| Fedora 44 GNOME Shell 50.6 Wayland, physical `f44` | RPM | Pass |
| Fedora 44 Budgie 10.10.2 on labwc 0.9.6, guest `b1` | AppImage | Pass |
| Omarchy 4.5.0 Hyprland Wayland, guest `o5` | AppImage | Pass after readiness retest |

## Before and after on Plasma

All ten images show Aurora’s physical Plasma 6.8.2 Wayland session. Before images show nightly `26.1121.6060-nightly`. After images show candidate `26.1121.6117-dev+g799e392e24ee`. The cyan outlines and build captions were added through the packaged image editor’s `editor.open`, `editor.apply`, and `editor.saveCopy` calls.

| Review state | Nightly v26.1121.6060 | PR 1791 build |
| --- | --- | --- |
| Selected redaction grips and side hit bands | [Before](pictures/before-01-selected-cover.png) | [After](pictures/after-01-selected-cover.png) |
| Covers lanes, transport toggles, drag readout, and snap guide | [Before](pictures/before-02-timeline.png) | [After](pictures/after-02-timeline.png) |
| Placement prompt | [Before](pictures/before-03-placement-prompt.png) | [After](pictures/after-03-placement-prompt.png) |
| Edits list and selected cut details, including Starts and Ends | [Before](pictures/before-04-edits-details.png) | [After](pictures/after-04-edits-details.png) |
| Transport with clip and recording times | [Before](pictures/before-05-clip-recording-time.png) | [After](pictures/after-05-clip-recording-time.png) |

Candidate `26.1121.6117-dev+g799e392e24ee` on the [full Aurora desktop](pictures/aurora-full-desktop.png) and in the [1100×700 overlay after scrolling](pictures/aurora-compact-scrolled.png) and [reopening another cover’s details](pictures/aurora-compact-details.png).

## Plasma observations

- The intended resize occurred at the centre of all 16 picture handles. Selected cut-edge trials improved from 17/21 to 19/21 on both edges versus the previous Cinnamon nightly run. The [offset table](measurements/hit-targets.md) distinguishes the two compositors and measurement windows. All eight off-midpoint side bands produced the intended resize in 16/21 trials each on both desktops.
- The 1920×1080 skim sweep produced 26.24 observed viewer updates per second at a 31.16 Hz sample rate, then restored the same decoded frame. Clicking the live skim kept that frame, and a trim drag displayed the edge. The (+14,+8) px move re-engaged skim after a 240 ms dwell in step `B-hover-0938`. That follows the confirmed design rule. After a click, moving at least 12 px from the click allows a 150 ms dwell to count as skim intent. [Visual skim trace](measurements/plasma-skim-visual.json) · [Assertion receipts](measurements/plasma-assertion-findings.json)
- With the trim grip aimed five pixels past the playhead, snapping put the trim on the playhead frame. Holding Ctrl and turning Snap off each allowed the adjacent frame. Two early attempts to put the endpoints in view fell short. The corrected test used the furthest valid seek and scrolled the viewport to the edge, then verified the exact 0 and duration trim limits at 2×. A separate drag snapped the cover to the 6 s cut boundary, and the ruler scrub reached the adjacent 6.033333 s frame. [Snap receipt](measurements/plasma-snap.json) · [Endpoints](measurements/plasma-zoomed-trim-endpoints.json) · [Other edge and adjacent frame](measurements/plasma-snap-to-cut-and-adjacent.json)
- The typed-field Save test did not complete its first field commit with the VNC keyboard. The follow-up input fixture also failed to arm the cover or establish the K speed setup. Real Skim and Snap button presses switched the controls off. The follow-up keyboard presses did not switch them back. Plain Enter and the other exercised shortcuts were checked in the main run. Focused Upload activation and a full set of focus contexts remain unverified on Plasma.
- The 1100×700 overlay scrolled to a different cover. Clicking the row selected it and closed the overlay. Reopening Edits displayed that cover’s details. A click through to the ruler while Edits was open closed the overlay and moved the playhead. [Selected cover details](pictures/aurora-compact-details.png)
- Each of the 20 action/inspect pairs passed through the CLI and through the official SDK’s MCP session. The unchanged lane/zoom recipe, executed against the native session with a scratch context adapter, timed out waiting for the centred Enter placement to change the edit revision. [Parity measurements](measurements/plasma-parity.json)

## Guest observations

Budgie’s native labwc session on AppImage `26.1121.6117-dev+g799e392e24ee` recorded the moving test pattern, opened review, cut a middle span, and resized the redaction from its top-left handle. Its saved MP4 matched the 10.733333 s shown duration. The guest’s FFmpeg could not initialize OpenH264, so the existing capture and export were checksum-verified and decoded on Aurora. Across the cut and cover checks, all 83 identifiable cut-interior frame codes were absent and all four redaction samples matched. [Budgie review](pictures/budgie-smoke-review.png) · [Decoded export](measurements/budgie-export.json)

Omarchy’s native Hyprland session on AppImage `26.1121.6117-dev+g799e392e24ee` showed the output picker with the synthetic capture surface. The first overlay timed out at the 45 s recording-ready gate. The fresh overlay also timed out with a 105 s gate. Neither attempt reached an editable recording. On fresh overlay o5, the same candidate and nightly both reached review with the corrected picker control and 210 s readiness gate. [Picker witness](pictures/omarchy-screen-share-picker.png) · [Matched comparison](omarchy-comparison/README.md)

## Measured exports

Motion scores are mean absolute luma differences between sampled frames. The motion fixture displayed scrolling bars, a moving ball and a 16-bit time-code strip. The frozen control used the same scene at one timestamp. The scan decoded the time strip in each exported frame and checked the redaction’s interior before, on both sides of the cut and after the cover.

| Desktop | Editor duration (s) | MP4 duration (s) | Moving | Frozen | MP4 motion | Cut-interior codes found |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Plasma | 22.366666 | 22.366667 | 18.54 | 0.0021 | 36.84 | 0 of 222 |
| Cinnamon | 22.099999 | 22.100000 | 17.38 | 0.0067 | 36.65 | 0 of 219 |
| GNOME | 10.033333 | 10.033333 | 36.00 | 0.0110 | 30.78 | 0 of 79 |
| Budgie | 10.733333 | 10.733333 | 33.99 | 0.0010 | 29.23 | 0 of 83 |

Detailed [Plasma](measurements/plasma-export.json), [Cinnamon](measurements/cinnamon-export.json) [GNOME](measurements/gnome-export.json) and [Budgie](measurements/budgie-export.json) export measurements include the luma results.

## Cinnamon observations

- The native recording fixture captured at 1920×1080 and the seeded offset matrix used the maximized 1920×1040 review client. The full-desktop witness used the same running DEB first put into fullscreen. [Cinnamon desktop, 26.1121.6117-dev+g799e392e24ee](pictures/mint-full-desktop.png)
- The 1080p skim sweep showed 22.26 viewer updates per second at a 27.00 Hz sample rate and restored the same decoded frame. Clicking the skim kept its time. A trim drag showed the edge frame. The Skim and Snap controls toggled both ways. The same (+14,+8) px move and dwell engaged skim as designed. Six vertical or diagonal crossings per desktop produced no sampled skim frames. [Skim trace](measurements/cinnamon-skim-visual.json) · [Crossings](measurements/vertical-crossings.json)
- Both trim brackets reached their exact endpoint at 2× zoom, and the cancel gestures preserved the edits. The initial snap check used a microsecond distance threshold. Frame-index scoring of the same gestures proved that Snap chose the playhead frame and Ctrl and N chose the adjacent frame. One additional Ctrl-wheel probe reported no zoom change. A separate real-pointer drag snapped the cover to the 6 s cut boundary, and the ruler scrub reached the 6.033333 s adjacent frame. [Other edge and adjacent frame](measurements/cinnamon-snap-to-cut-and-adjacent.json) · [Endpoints](measurements/cinnamon-zoomed-trim-endpoints.json) · [Snap receipt](measurements/cinnamon-snap.json) · [Assertion receipts](measurements/cinnamon-assertion-findings.json)
- Both cover types showed four distinct resize cursor images with matching opposite pairs. The typed cover moved from 2–8 s to 3–7 s. The Until field still read 8 s in the committed edit immediately before the Save button press, and the saved MP4 samples verified the 3–7 s result. [Cover cursors](measurements/cinnamon-cover-cursors.json) · [Typed Save and decoded samples](measurements/cinnamon-typed-save-copy.json)
- K reset 4× playback to paused 1×. Space did not start playback from the focused cover time field. Enter left the review open until the local-only Upload button had keyboard focus, at which point Enter wrote the private copy. [K](measurements/cinnamon-keyboard-k.json) · [Enter focus](measurements/cinnamon-local-focused-enter.json)
- The compact Edits overlay scrolled, reopened on the chosen cover’s details, and dismissed on a ruler click that also moved the playhead. [Scrolled list](pictures/mint-compact-scrolled.png) · [Selected details](pictures/mint-compact-details.png)
- The CLI and official SDK MCP runs both passed all 20 action/inspect pairs. The unchanged lane/zoom recipe successfully placed all five overlapping covers and then rejected the state against its expectation of two shown lanes and a hidden-covers chip. This recipe was executed through the same scratch native context adapter as Plasma. [Parity](measurements/cinnamon-parity.json) · [Recipe assertions](measurements/cinnamon-surface-recipe.json)

## GNOME observations

Fedora 44 GNOME Shell 50.6 ran RPM `26.1121.6117~dev+g799e392e24ee-1.fc44` and completed the moving capture, cut, top-left handle resize and Save a copy smoke. The export matched the 10.033333 s shown duration, carried motion and omitted all 79 cut-interior frame codes. Both the installation and removal were scoped to put.gd. DNF reported that the lab’s pending offline update transaction was invalidated. [Review](pictures/gnome-smoke-review.png) · [Decoded export](measurements/gnome-export.json)

## Package identity

| CI package | SHA-256 |
| --- | --- |
| AppImage x86_64 | `d5b147a980ca23fab13a551d9fbb02f2711fa0bbe551328e90f45da450fd9231` |
| Ubuntu 24.04 DEB | `dd8e16205c423cd705515a1af07cf0c8da65f7225ca4aecd3d53f190e799d6cd` |
| Fedora 44 RPM | `7b41857dcb933be3512434ff8410d51cf6fcbbfa282e0f97c4551aafa7e000f8` |

Each resident checked against the expected source tree via `diagnostics.build.gitTree`. AppImage executions also checked the embedded `--version-json` identity.

## Lab cleanup

All times are UTC on 2026-11-21. Each physical lease ended after the verified cleanup check. The test DEB and RPM were removed using scoped transactions.

| Physical lease | Acquired | Released |
| --- | --- | --- |
| `aurora-amd` full run | 21:01:52 | 21:25:27 |
| `m74` full run | 21:25:32 | 21:47:55 |
| `f44` GNOME smoke | 21:48:00 | 21:49:54 |
| `aurora-amd` side bands and timeline follow-up | 21:49:59 | 21:54:38 |
| `m74` timeline follow-up | 21:54:44 | 21:56:21 |

| Guest on f44 | Run identity | Final state |
| --- | --- | --- |
| Omarchy `o1` | `e83b48f8-7674-4fca-9dc9-f9717654ec70` | Stopped. Overlay retired after evidence verification. Wall entry and forward removed. |
| Budgie `b1` | `f01b746f-df18-4018-982b-c47223724896` | Stopped. Overlay retired after evidence verification. Wall entry and forward removed. |
| Omarchy `o2` | `563c79d5-d514-4c95-aab4-22a276251a62` | Stopped. Overlay retired after evidence verification. Wall entry and forward removed. |

Full step traces, failed harness attempts, build identities and cleanup receipts are preserved in the private lab campaign.
