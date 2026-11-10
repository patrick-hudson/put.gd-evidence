# A cut-off reply is judged by its own length (#1393): the picture and the stress runs

Implementer's record for put.gd-desktop PR #1394 at `432acc072` (issue #1393: the scripted-receiver
suite `http_uploader_integration` failed twice in CI in `aReplyCutOffAfterItsStatusLineIsUnknown`
and passed its retry).

## The picture

`pictures/cut-reply-history.png`: what a user sees when a server's reply ends before it is
complete. The scripted receiver stored the file and answered with a whole link in a reply that
was 64 bytes short of its `Content-Length`. History shows the upload as an unknown outcome, "The
server's reply was cut off before it was complete (HTTP 200; it ended after 254 of 318 bytes)",
records no link, and offers Retry with its warning. `raw/` has the capture untouched and
`raw/cut-reply-result.json` what the session methods returned for it.

- Build: a dev build of the PR head `432acc072` on k72 (Kubuntu 26.04, Qt 6.10.2). The tree has
  no git metadata, so the window's version reads `0.0.0-dev.unknown`.
- Taken without a physical desktop: a private resident on a private X display (Xvfb), driven
  through `putgd-cli` (`tools/picture1393.py`).
- The marks were drawn with put.gd's own image editor (`editor.open`, `editor.apply`,
  `editor.saveCopy`) in a headless resident of the same build: `tools/annotate.py` with
  `tools/annotations.json`.
- The receiver's token is its synthetic one and is not in the frame or in the record.

## The stress runs

`results.json` has every count. Each run: 8 busy loops on a 4-CPU builder (load about 9),
`PUTGD_TEST_TIME_SCALE=3`. "Case" is `aReplyCutOffAfterItsStatusLineIsUnknown` alone in a loop
(`tools/repro1393.sh`); "suite" is the whole `http_uploader_integration` through the repository's
`tools/ci/stress_suite.py`, whose ledger and summary are in each folder under `stress/`.

| Builder | Qt | Commit | Case runs | Case failed | Suite iterations | Suite failed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| m74 | 6.4.2 | nightly `e870ba5c4` (before) | 300 | **7** | not run | |
| m74 | 6.4.2 | `432acc072` (head) | 300 | 0 | 20 | 0 |
| k72 | 6.10.2 | `432acc072` (head) | 400 | 0 | 54 of 100, stopped by hand | 0 |
| f44 | 6.11.2 | `432acc072` (head) | 300 | 0 | not run | |
| m74 | 6.4.2 | `09348ade7` (first commit) | 1000 | 0 | 101 of 120, stopped by hand | 0 |
| f44 | 6.11.2 | `09348ade7` (first commit) | 600 | 0 | 120 | 0 |
| k72 | 6.10.2 | `2b0867338` (third commit) | 400 | 0 | 1, stopped by hand | 0 |

The seven failures on nightly are in `stress/before-nightly-m74.txt`, each with what Qt
reported for every exchange of that run: all seven are a 200 reply with fewer bytes than its
`Content-Length` and `QNetworkReply` error 205 (`ContentReSendError`) where the other rows show
error 2 (`RemoteHostClosedError`). Three of them recorded a truncated link as an upload. The same
loop on nightly on f44 (Qt 6.11.2) did not fail in 300 runs.

Runs marked "stopped by hand" were stopped by their recorded PID when the work was cut down to
the head; the counts are what they had reached.
