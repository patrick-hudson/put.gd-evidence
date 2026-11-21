# Omarchy comparison on fresh overlay o5

Both AppImages used the same Omarchy Hyprland Wayland guest, synthetic source, 210 s recording-readiness timeout, and output selection guard. The candidate reruns the original 799e392e2 readiness gate. Nightly uses v26.1121.6060. Build identities came from each live resident.

| Build | Recording and review | Top-left resize | Export and cut | MP4 length | Export motion | Frozen motion |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 26.1121.6117-dev+g799e392e24ee | Pass | Pass | Pass | 9.800000 s | 31.44 | 0.0011 |
| 26.1121.6060-nightly | Pass | Fail | Pass | 9.866667 s | 32.05 | 0.0011 |

The candidate reached recording readiness and performed the cut and northwest resize. Its raw verifier found a reused synthetic time code at output frame 134. The 4.466667 s output timestamp maps to the first kept timestamp, 7.100 s. The adjacent 7.067 s interior frame and the 7.100 s kept frame shared the code and differed by at most one luma level in the decoded 160 × 96 comparison. The raw and source-timestamp results are preserved. [Candidate export](measurements/candidate-export-metrics.json) · [Candidate seam verification](measurements/candidate-seam-analysis.json).

Nightly also reached readiness. The first nightly attempt used a review field introduced after nightly, so the adapter was adjusted to read its older geometry. The later attempts used the displayed box coordinates. On nightly the top-left drag left the box unchanged, and the rest of the smoke proceeded to export. The nightly implements resizing at the bottom-right grip. [Nightly resize](measurements/nightly-resize.json) · [Nightly export](measurements/nightly-export-metrics.json) · [Nightly seam verification](measurements/nightly-seam-analysis.json).

[Candidate identity](measurements/candidate-identity.json) · [Candidate review](pictures/candidate-review.png) · [Nightly identity](measurements/nightly-identity.json) · [Nightly review](pictures/nightly-review.png).

Overlay o5 (2b17eafc-1a31-4397-926a-ccd01ad7aca9) was retired at 2026-11-21T22:55:05.644247+00:00 after transfer and checksum verification. Its VNC entry and tunnel were removed. [Lab receipt](measurements/lab.json).
