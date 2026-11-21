# Omarchy smoke on final candidate e28a26af0

The final candidate from [CI run 44956148888](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44956148888) and nightly v26.1121.6060 used separate private profiles on the same fresh Omarchy Hyprland Wayland overlay. Both used the same moving and frozen synthetic fixtures, native pointer and a 210 s recording-readiness limit. Build identities came from the two live residents and package hashes. [Candidate identity](measurements/candidate-identity.json) · [Nightly identity](measurements/nightly-identity.json).

| Build | Record and review | Top-left resize | Export and cut | MP4 length | Export motion | Frozen motion |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 26.1121.6132-dev+ge28a26af087c | Pass | Pass | Pass | 9.866667 s | 31.45 | 0.0011 |
| 26.1121.6060-nightly | Pass | Fail | Pass | 9.866667 s | 32.08 | 0.0011 |

- Candidate reached readiness in frozen 2.81 s, moving 0.48 s. [Readiness](measurements/candidate-readiness.json).
- Nightly reached readiness in frozen 2.49 s, moving 0.47 s. [Readiness](measurements/nightly-readiness.json).

The nightly top-left drag left the redaction rectangle unchanged. That nightly supports the bottom-right resize grip. [Candidate drag](measurements/candidate-nw-resize.json) · [Nightly drag](measurements/nightly-nw-resize.json).

The export checks measure duration, visual motion, the frames removed by the cut and redaction samples. [Candidate export](measurements/candidate-export-metrics.json) · [Nightly export](measurements/nightly-export-metrics.json).

[Candidate review at 26.1121.6132-dev+ge28a26af087c](pictures/candidate-review.png) · [Nightly review at 26.1121.6060-nightly](pictures/nightly-review.png).

Overlay o6 (96c514e8-5557-4e5c-b9e6-084288178c10) was retired at 2026-11-21T23:11:28.512306+00:00 after export and checksum verification. Its display-wall entry and tunnel were removed. [Cleanup receipt](measurements/lab.json).
