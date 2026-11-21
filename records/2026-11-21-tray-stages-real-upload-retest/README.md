# Physical tray activity and live S3 re-test

PR #1755 candidate `c2f1d8655df206ca6a1ae54a0b163b435b9c4b61`, tree `28599b18f9be27ca9bdcac5a1cc04f181f2584c9`.
The manual workflow supplied the native packages. The resident's build identity comes from the production `putgd-cli ui.snapshot` diagnostics on each physical seat.
[Candidate PR](https://github.com/patrick-hudson/put.gd-desktop/pull/1755) · [Manual CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44853167996) · [Previous test on a6e5399f2](https://github.com/patrick-hudson/put.gd-evidence/blob/60a473b181703bdd4c868224515e7220b8b44514/records/2026-11-20-tray-stages-real-upload/README.md)

| Host | Physical seat session | Running diagnostics | Package SHA-256 |
| --- | --- | --- | --- |
| k72 | plasmashell 6.6.6, wayland, seat0 session 509 | [`c2f1d8655df206ca6a1ae54a0b163b435b9c4b61`](k72/build.json) | `5ff481f495e89a842ec442e4e597e87aef9e05926ae54c43178d2651017fa439` |
| m74 | Cinnamon 6.6.9, x11, seat0 session c89 | [`c2f1d8655df206ca6a1ae54a0b163b435b9c4b61`](m74/build.json) | `b7c3c851716cd83127fcb1d9d2c8bfc50e10f265fd9e4ce0d25f2c561f3ee642` |
| f44 | GNOME Shell 50.6, wayland, seat0 session 21444 | [`c2f1d8655df206ca6a1ae54a0b163b435b9c4b61`](f44/build.json) | `6a34ead3a7c4c3b6820c082ec6d1dfb1837478a6d394d41a9096884b14a0a0fc` |

## Results

| Scenario | k72 | m74 | f44 |
| --- | --- | --- | --- |
| 1. Native hotkey region to S3 | **PASS** · capturing → processing → uploading → complete → idle. Upload complete with a checked turkey, authenticated S3 GET matched. | **PASS** · capturing → processing → uploading → complete → idle. Upload complete with a checked turkey, authenticated S3 GET matched. | **PASS** · capturing → processing → uploading → complete → idle. Upload complete with a checked turkey, authenticated S3 GET matched. |
| 2. Refused endpoint, expiry, attention row and recovery | **PASS** · Failed badge returned to idle in 8.001 s. Menu row persisted and recovery uploaded. | **PASS** · Failed badge returned to idle in 8.001 s. Menu row persisted and recovery uploaded. | **PASS** · Failed badge returned to idle in 8.001 s. Menu row persisted and recovery uploaded. |
| 3. Local-only hotkey save | **PASS** · capturing → processing → complete → idle. Saved with a checked turkey. | **PASS** · capturing → processing → complete → idle. Saved with a checked turkey. | **PASS** · capturing → processing → complete → idle. Saved with a checked turkey. |
| 4. Multi-file live S3 upload | **PASS** · 3 S3 objects verified. Green fill rose from 233 to 2076 pixels, with 11 samples after a file finished and none full early. | **PASS** · 3 S3 objects verified. Green fill rose from 233 to 2076 pixels, with 12 samples after a file finished and none full early. | **PASS** · 3 S3 objects verified. Green fill rose from 233 to 2076 pixels, with 9 samples after a file finished and none full early. |
| 5. Resident continuity and journal | **PASS** · PID 221023 with the same start time throughout. Journal had no resident crash. | **PASS** · PID 2729344 with the same start time throughout. Journal had no resident crash. | **PASS** · PID 2127069 with the same start time throughout. Journal had no resident crash. |

## Method and evidence

Ctrl+Shift+1 was sent through the native RFB session. The region was dragged over a maximized, synthetic GTK pattern. Tray stage timestamps are UTC. The success and recovery captures each had an independent authenticated S3 GET compared with the local artifact.

The refused-endpoint run used a second S3 profile configured for a loopback port that rejected a connection. The two snapshots bracket the wait with menu counters and the attention row. Recovery used another normal region hotkey and live destination.

The multi-file operation sent three synthetic files (3, 4 and 5 MiB) in one `upload.files` call, the same resident endpoint the file-manager integration uses, and used one upload slot. Trace rows bracket each real StatusNotifier pixmap read with per-file upload states. Samples of unfinished batches were compared with the prior dark-panel full-green fingerprint. The last upload transitioned to the checked Complete icon between samples, so the trace has no separate full-green Uploading frame after confirmation. Each reported S3 object match came from an authenticated GET.

- k72 diagnostics. [region-history](k72/region-history.json) · [failure-history](k72/failure-history.json) · [recovery-history](k72/recovery-history.json) · [local-save-history](k72/local-save-history.json) · [batch-1-result](k72/batch-1-result.json) · [resident-liveness](k72/resident-liveness.json)
- k72 inspected panel frames. [failure-failed](k72/failure-failed.png) · [region-processing](k72/region-processing.png) · [region-complete](k72/region-complete.png) · [local-save-complete](k72/local-save-complete.png) · [batch-1-panel-early](k72/batch-1-panel-early.png) · [batch-1-panel-late](k72/batch-1-panel-late.png)
- m74 diagnostics. [region-history](m74/region-history.json) · [failure-history](m74/failure-history.json) · [recovery-history](m74/recovery-history.json) · [local-save-history](m74/local-save-history.json) · [batch-1-result](m74/batch-1-result.json) · [resident-liveness](m74/resident-liveness.json)
- m74 inspected panel frames. [failure-failed](m74/failure-failed.png) · [region-processing](m74/region-processing.png) · [region-complete](m74/region-complete.png) · [local-save-complete](m74/local-save-complete.png) · [batch-1-panel-early](m74/batch-1-panel-early.png) · [batch-1-panel-late](m74/batch-1-panel-late.png)
- f44 diagnostics. [region-history](f44/region-history.json) · [failure-history](f44/failure-history.json) · [recovery-history](f44/recovery-history.json) · [local-save-history](f44/local-save-history.json) · [batch-1-result](f44/batch-1-result.json) · [resident-liveness](f44/resident-liveness.json)
- f44 inspected panel frames. [failure-failed](f44/failure-failed.png) · [region-processing](f44/region-processing.png) · [region-complete](f44/region-complete.png) · [local-save-complete](f44/local-save-complete.png) · [batch-1-panel-early](f44/batch-1-panel-early.png) · [batch-1-panel-late](f44/batch-1-panel-late.png)

## Setup adjustments

The DEB hosts used dpkg after APT simulation and a local-archive path error. Fedora used RPM after reviewing the DNF preview and its pending offline update notice. Mint resumed with the same resident after the fixture finished drawing.
[Kubuntu package setup](k72/setup-result.json) · [Mint package and fixture setup](m74/setup-result.json) · [Fedora package setup](f44/setup-result.json)

## Cleanup

- k72. Removed five test objects, verified empty prefix and multipart listing, removed the temporary credential reference, profiles, runtime and package, and released the desktop lock. [Receipt](k72/cleanup.json)
- m74. Removed five test objects, verified empty prefix and multipart listing, removed the temporary credential reference, profiles, runtime and package, and released the desktop lock. [Receipt](m74/cleanup.json)
- f44. Removed five test objects, verified empty prefix and multipart listing, removed the temporary credential reference, profiles, runtime and package, and released the desktop lock. Restored GNOME AppIndicator settings. [Receipt](f44/cleanup.json)
