# PR 1541: failed uploads with unknown outcomes — KDE acceptance

**PASS on all five requested scenarios**, on k72's real native Plasma Wayland desktop. No failure requiring a nightly comparator was observed. The list uses destination-specific wording, **“Upload to PR1541 lab HTTP receiver failed · …”**; the selected item's details say **“Upload failed”**. This records the actual wording rather than claiming the list literally starts with the shorter generic phrase in the brief.

## Build and host proof

- Requested and checked-out head: **27c977f351961a4c4db40ba7b418e46a72008c34**, branch `fix/failed-uploads-unknown-outcome`, PR #1541 / issue #1539.
- `git fetch origin` preceded checkout. Expected tree from `git rev-parse 27c977f351961a4c4db40ba7b418e46a72008c34^{tree}`: **3de3ae46f4d3287e197a2b62121c9f3c953fa105**.
- CI **43662052474** succeeded. Waited in the foreground using `gh run watch 43662052474 -R patrick-hudson/put.gd-desktop --interval 60 --exit-status`, then downloaded its artifacts with `gh run download`; [watch log](ci-watch.log). No compilation was performed on any builder or workstation.
- Installed only the run's Ubuntu 26.04 native DEB: version **26.1115.5036-dev+g27c977f35196**. [Package checksum](package.json), [reviewed install plan](install-plan.txt).
- Production resident diagnostics reported the exact expected tree before testing and after the crash/restart: [initial diagnostics](diagnostics.json), [restarted diagnostics](restart-diagnostics.json).
- Host: **k72 / 192.168.68.72; Ubuntu 26.04.1; Plasma 6.6.6; native Wayland; distro Qt 6.10.2**. [Host receipt](host.txt).

## Results and frames

Every linked image is a complete real desktop RFB frame, unmasked and uncropped. No offscreen catalog or storage fixture establishes a result. Production operation IDs, UI queries and real pointer clicks are in [the trace](trace.jsonl), with [operation identities](operations.json).

| Step | Result | Observation and decisive evidence |
|---|---|---|
| 1. HTTP 503 unknown outcome | PASS | [Tray Failed uploads (1)](01-503-tray.png) opened [Failed uploads with the actual file, count 1 and Retry upload](01-failed-history.png). The file also appears in [All items](01-all-items.png). Details show [Upload failed and Retry upload](01-details-notice.png). |
| 2. Retry succeeds | PASS | Changed the receiver to normal responses and clicked Retry upload in the details pane. The same operation completed with `uploadStatus: uploaded`; [Failed uploads becomes empty, count 0](02-retry-cleared.png), and [All items shows the uploaded result](02-retry-uploaded.png). The sidebar suppresses its zero badge; production category totals explicitly report `failed: 0`. |
| 3. Crash-interrupted upload | PASS | Started a second upload with its HTTP response held open; [frame while uploading](03-held-before-crash.png). Ended only the started resident PID **1961700** with SIGKILL during production phase `uploading` ([crash receipt](crash.json)). After restart, the operation was `interrupted`, its upload status `unknown`, and [Failed uploads listed crash-held with Retry upload and count 1](03-recovered-failed.png). The [post-restart tray has no Failed uploads attention row](03-restart-tray-no-attention.png), as designed. Released the receiver, clicked Retry upload, and the same operation completed: [Failed uploads cleared](03-retry-cleared.png), [both files uploaded in All items](03-retry-uploaded.png). |
| 4. Exact unknown filter | PASS | Before the first retry, All items → Upload state: Outcome unknown found the unknown file: [filter frame](04-exact-unknown-filter.png). Production UI query remained exactly `uploadStatus: unknown`, with one row, and the record's upload status was `unknown`. After both retries, `history.list` with that exact filter returned zero records. |
| 5. Merged tray sanity | PASS | [Idle tray](05-idle-tray.png) keeps T1's action order, separators and groups; no retired History/Destinations/About rows or attention block. This profile's delay is None and output Local only. |

Exact retry notice observed in the selected item's UI:

> This upload may already be on the server: its outcome is unknown, and this destination cannot be asked. Retry upload sends the file again and may leave a second copy there.

The notice is visible in [this frame](01-details-notice.png). The HTTP-503 row additionally explains that the server failed after the upload was sent and that the uploader cannot check whether the server stored it. The crash-recovered row has the failure label and saved-local status without that HTTP-503 explanation.

## Real mechanisms and procedure

Used the documented rootless lab receivers, including real **Zipline 4.8.3** on k72, and the same small slow-response proxy mechanism as the tray campaign. The proxy answered 503 for the first synthetic 96 × 64 PNG. Normal responses forward the actual multipart upload to Zipline and return its result. For the crash test, Zipline had accepted the second request and the proxy held its HTTP response while the resident was killed. [Receiver events](receiver-events.jsonl) retain status, request byte count and held-response flags, never headers or credentials.

The private proxy supplied Zipline's authorization header from its protected lab `.sxcu`; the product's derived custom-uploader configuration had no secret headers. This avoids losing session-only credentials during the intentional crash and avoids writing the real desktop keyring. Import explicitly selected `credentialMode: session`. No user objects, bucket policies or production destinations were touched.

Started a new private XDG profile at `/tmp/t541`; the resolved session socket `/tmp/t541/runtime/putgd/session.sock` was **36 UTF-8 bytes**, checked before each resident launch (limit 107). The lab cover passed its full-frame precheck at **100% cover** before app frames were captured. Real VNC pointer input opened the tray attention row and clicked both Retry upload buttons. The supported production `ui.history` methods selected details and set the exact filter; they drove the visible application, not mock data.

One scripting attempt looked for a nonexistent `historyId` field in an operation item and stopped before driving the UI. It was corrected to use the real `history.list.records[].id`; accepted frames and operations follow that correction. No product code changed and no subagent was started.

## Restoration and publication boundaries

k72 had **no installed putgd binary, resident or receiver pod** at acquire ([baseline](baseline.txt)). The candidate was removed after testing; final dpkg state is residual configuration only, `rc 26.1115.5036~dev+g27c977f35196`, with no installed binary and no resident/helper processes. Exact owned cover, input-holder and proxy PIDs were stopped. The documented receiver `down` removed the owned pods while preserving their private volumes/state. All receiver ports are absent from the final listener inventory: [restoration log](restoration.txt).

The desktop lock was held from **01:30:48 to 01:36:24 UTC**, under its 30-minute lease, and released **verified-clean**, with empty `check.left`: [acquire](acquire.json), [release](release.json). No guest was used and no guest/tunnel/wall tile was created. No general upgrade or compositor/desktop package change occurred. All remote transport used the lab's pinned SSH form. No PR comment, issue or merge action was made.

Published logs omit nonempty, non-secret `concurrencyToken` UUID values (JSON null) to avoid the generic-api-key false positives encountered in the prior campaign. [Omission count and raw-source hash](publication-log-omissions.json). Original logs and private receiver credentials remain outside this record. Operation IDs, build identities, all frames and other evidence are unchanged. Actual private authorization values were checked against the proposed publication and were absent.
