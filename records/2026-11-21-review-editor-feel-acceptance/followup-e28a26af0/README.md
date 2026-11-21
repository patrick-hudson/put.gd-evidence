# PR #1791 acceptance recheck on e28a26af0

[Manual CI run 44956148888](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44956148888) succeeded. Both live residents reported 26.1121.6132-dev+ge28a26af087c, commit e28a26af087cadfddf419ac1f8d5c0eb681d054f and tree 20b6d20807872c4f3435f15b2f709cfd3facf1d0. [Plasma AppImage](measurements/plasma-identity.json) · [Cinnamon DEB](measurements/cinnamon-identity.json).

## Campaign results through e28a26af0

The final candidate passed the requested rechecks. Each row cites the build on which the corresponding checks ran.

| Row | Aurora Plasma Wayland | Mint Cinnamon X11 |
| --- | --- | --- |
| A · Hit targets | Pass on 799e392e2, late-grip and cover-slide checks on 5f2f799ac | Pass on 799e392e2, late-grip and cover-slide checks on 5f2f799ac |
| B · Hover and skim | Pass on 799e392e2 and 5f2f799ac | Pass on 799e392e2 and 5f2f799ac |
| C · Drag, snap and cancel | Pass on 799e392e2, final-frame selection and rapid cover drags pass on e28a26af0 | Pass on 799e392e2, final-frame selection and rapid cover drags pass on e28a26af0 |
| D · Covers and typed fields | Typed edits pass on 5f2f799ac. Refused Save passes on e28a26af0. | Typed edits pass on 5f2f799ac. Refused Save passes on e28a26af0. |
| E · Keys | Requested J/K/L and Enter focus checks pass on e28a26af0. The remaining Plasma focus permutations are unverified. | Pass on 799e392e2 |
| F · Export | Pass on 5f2f799ac, including the small blur | Pass on 5f2f799ac, including the small blur |
| G · 1100 × 700 overlay | Pass on 799e392e2 | Pass on 799e392e2 |
| H · Agent parity | CLI and MCP actions pass on 5f2f799ac. Native wheel-lanes and timeline-zoom recipe passes on e28a26af0. | CLI and MCP actions pass on 5f2f799ac. Native wheel-lanes and timeline-zoom recipe passes on e28a26af0. |

| Row S desktop | Latest smoke | Result |
| --- | --- | --- |
| Fedora GNOME Wayland | 5f2f799ac RPM | Pass |
| Budgie labwc Wayland | 5f2f799ac AppImage | Pass |
| Omarchy Hyprland Wayland | e28a26af0 AppImage | [Pass](../omarchy-final-e28a26af0/README.md) |

## Exact final desktop recheck

| Recheck | Aurora Plasma Wayland | Mint Cinnamon X11 |
| --- | --- | --- |
| Build identity | Verified | Verified |
| C · Final-frame selection and quick cover-edge drags | Pass | Pass |
| D · Save after a refused typed cut | Pass | Pass |
| E · J/K/L speed and focused Upload Enter | Pass | Earlier key pass |
| H · Review wheel-lanes and timeline-zoom recipe | Pass | Pass |

- **C.** The native pointer selected each clip's final frame. Two rapid drags adjusted one cover's start and then its end. An additional handoff held a genuine edit acknowledgement on the private lab control pipe so a drag on another cover could take over the pending preview. The frame shown matched the second target. [Plasma final selection](measurements/plasma-end-selection.json) · [Cinnamon final selection](measurements/cinnamon-end-selection.json) · [Plasma handoff](measurements/plasma-consecutive-edge-drags.json) · [Cinnamon handoff](measurements/cinnamon-consecutive-edge-drags.json).
- **D.** Set a cut from 4–6 s, trim to 3.9–4.1 s, and type 0:03.8 into Cut Starts. Hold the real Save a copy press until the resident refuses the edit, then release. On both desktops the refusal arrived before release, the revision and cut stayed unchanged, and the app reported “No copy was saved”. The chooser stayed closed and the file stayed absent. [Plasma receipt](measurements/plasma-refused-save.json) · [Cinnamon receipt](measurements/cinnamon-refused-save.json).
- **E.** On Plasma, L increased playback speed, J reduced it during playback, K paused and reset it to 1×, and J stepped back one second while paused. Enter on the ruler kept the review open. Tab focused Upload and Enter then wrote a valid MP4 in the private local archive. The test profile contained no remote destinations. [Transport](measurements/plasma-keyboard-k.json) · [Enter](measurements/plasma-local-focused-enter.json).
- **H.** The exact-head registered wheel-lanes and timeline-zoom recipe ran through the native desktop adapter with a real keyboard and private moving and frozen clips. Five overlapping covers used two lanes and a +3 chip. The timeline zoomed to 4× and Fit preserved the covers. [Plasma assertions](measurements/plasma-surface-recipe.json) · [Cinnamon assertions](measurements/cinnamon-surface-recipe.json).

The [original comparison](../README.md) and [5f2f799ac retest](../fixed-5f2f799ac/README.md) score B as pass under the confirmed post-click dwell rule. The [matched Omarchy comparison on e28a26af0](../omarchy-final-e28a26af0/README.md) records the final candidate and nightly smoke on the same fresh overlay. The [earlier matched comparison](../omarchy-comparison/README.md) records readiness and export on both the original candidate and nightly, plus their different top-left resize outcomes.

The version captions and outlines were drawn with the packaged put.gd image editor. [Plasma selection](pictures/plasma-final-selection.png) · [Plasma cover preview](pictures/plasma-second-cover-drag.png) · [Plasma refused Save](pictures/plasma-refused-save.png) · [Cinnamon selection](pictures/cinnamon-final-selection.png) · [Cinnamon cover preview](pictures/cinnamon-second-cover-drag.png) · [Cinnamon refused Save](pictures/cinnamon-refused-save.png).

The Aurora and m74 leases were released after their cleanup checks. [Cleanup receipts](measurements/lab-cleanup.json).
