# PR #1791 final desktop spot checks on 321627d99

[Manual CI run 44954083198](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44954083198) succeeded. Both desktops reported version 26.1121.6131-dev+g321627d99141, commit 321627d991414e7693cb323ebaf13f9d706fc6c0 and source tree 3d53f2f736e418e40d494d1cd43a3e0f94f299a3 from the live resident. Each package hash matched the exact CI download.

| Desktop | Package identity | Last-frame selection | Two drags on one cover | Pending preview handoff |
| --- | --- | --- | --- | --- |
| Aurora Plasma Wayland | [Verified AppImage](measurements/plasma-identity.json) | [Pass](measurements/plasma-end-selection.json) | [Pass](measurements/plasma-same-cover-drags.json) | [Pass](measurements/plasma-consecutive-edge-drags.json) |
| Mint Cinnamon X11 | [Verified Ubuntu 24.04 DEB](measurements/cinnamon-identity.json) | [Pass](measurements/cinnamon-end-selection.json) | [Pass](measurements/cinnamon-same-cover-drags.json) | [Pass](measurements/cinnamon-consecutive-edge-drags.json) |

| Desktop | Clip duration | Selected source span | Selection length | Same-cover gap | Pending handoff gap | Handoff target | Handoff frame shown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Plasma | 12,599,999 µs | 12,566,667–12,599,999 µs | 33,332 µs | 213 ms | 168 ms | 9,366,667 µs | 9,366,667 µs |
| Cinnamon | 12,166,666 µs | 12,133,333–12,166,666 µs | 33,333 µs | 193 ms | 153 ms | 9,400,000 µs | 9,400,000 µs |

A real pointer dragged across the final frame at the closest timeline zoom. The selected interval ended at the clip duration and the trim stayed unchanged. The live durations and selection lengths are recorded above. In CI, the exact-head timeline test also retained the 30,000 µs partial frame of its 10,030,000 µs fixture.

The same-cover check dragged the start and then the end as soon as the first edit settled. The second frame matched its target and both edits committed. For the additional handoff check the lab held one genuine resident edit reply on the private control pipe. The first release held its edge frame, then a drag on a different cover took over before the reply was delivered. The second target stayed active as the first reply arrived, its decoded frame appeared, and both cover edits committed. The exact-head CI review test exercises the late frame callback from the first drag. [CI regression receipts](measurements/ci-regression-tests.json).

The annotation boxes and version captions were applied with the packaged put.gd image editor. [Plasma final selection](pictures/plasma-last-frame-selection.png) · [Plasma second drag on the same cover](pictures/plasma-same-cover-preview.png) · [Plasma pending preview handoff](pictures/plasma-pending-preview-handoff.png) · [Cinnamon final selection](pictures/cinnamon-last-frame-selection.png) · [Cinnamon second drag on the same cover](pictures/cinnamon-same-cover-preview.png) · [Cinnamon pending preview handoff](pictures/cinnamon-pending-preview-handoff.png).

The broader findings belong to the [799e392e2 campaign](../README.md), [5f2f799ac retest](../fixed-5f2f799ac/README.md), and [994d699de spot checks](../spot-994d699de/README.md). These two final desktop checks used Aurora and m74. Both leases were verified clean and released. The first Plasma fixture used the trim bracket’s hit area and retried a cover during a pending edit. The next selection was kept but the harness compared the response’s extra lengthUs field. The final fixture aimed outside the bracket, checked the two selection endpoints directly, and honored the same-cover pending guard. [Lab cleanup](measurements/lab-cleanup.json).
