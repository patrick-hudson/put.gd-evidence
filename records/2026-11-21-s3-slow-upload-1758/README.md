# S3 24 MiB upload hang and publication_unknown (#1758)

Live S3 runs for put.gd-desktop #1758, fixed by PR #1783 (docs #1784). Each upload used one
24 MiB file of random bytes made for it, sent through a private put.gd resident on the
builder's real desktop session (`upload.files` through `putgd-cli`). Every upload went to an
isolated `acceptance/tier1-live/<random>/` prefix in the `put.gd` bucket (us-east-2) with
AWS key set 2. Each outcome was checked in the bucket by HEAD: ETag equals the local MD5,
size matches, and the `putgd-sha256` metadata matches. The first six natural nightly rows on k72
and the 100 MiB multipart object were checked by an authenticated GET and SHA-256 instead.
Every test prefix was emptied afterwards.

"Shaped" rows limit only the builder's HTTPS uploads to AWS S3 address blocks
(3.5/16, 52.219/16, 16.12/16, 16.15/16) to 2.4 Mbit/s with `tc` HTB. That is about 300 KB/s,
the slow-link condition behind the original failure. Natural rows ran on the lab uplink as it
was (about 3.4 MiB/s that afternoon).

## Root cause, from the original failing run

The resident log of the failing published-nightly run on k72 (2026-11-21 01:25 UTC,
`v26.1120.5875-nightly`) is in `k72/resident-log-s3-records.json` (file
`putgd-20261121T012509728Z-154084-1.jsonl`). Each of the three PutObject attempts ended
`curlCode: 28 … Operation timed out after 60000 milliseconds with 0 bytes received`, with
HTTP 100 (S3's `100 Continue`), each on a fresh connection, with a 404 HEAD between them.
The upload then ended `publication_unknown` after 181 s. The default request timeout
(60 s) was curl's whole-request limit, so a PUT that needs more than 60 s to send its bytes
could never finish, and each attempt started over. curl's 30 s low-speed rule never fired,
so bytes were moving the whole time.

## Results

| Host | Build | Rows | Result |
|---|---|---|---|
| k72 | published nightly 26.1121.6060 (DEB, SHA-256 matched the release) | 10 natural | 10 completed, 7.1–11.9 s, all in the bucket |
| k72 | nightly | 2 shaped | both `partial`, upload `unknown`, `publication_unknown`, 182.6 s and 183.0 s; object absent. TCP samples: three connections, each sent about 17 MB of 25 MB in about 59 s, then cut |
| k72 | nightly | Retry of the first unknown item, still shaped | reconciled (`reconciling`, key missing), uploaded again, hung again: 183.3 s, `publication_unknown`, absent |
| k72 | nightly | Retry of the same item, shaping removed | reconciled, uploaded, completed in 8.2 s; in the bucket |
| d69 | published nightly 26.1121.6060 (DEB, Debian 13 Plasma) | 5 natural / 1 shaped | 5 completed in 7.5–8.3 s / shaped `publication_unknown` after 183.2 s, absent |
| k72 | candidate `84867e810` | 10 natural serial | 10 completed, 7.2–7.9 s, all in the bucket |
| k72 | candidate `84867e810` | 3 shaped | 3 completed in 90.7–92.8 s, each on one connection; in the bucket |
| k72 | candidate `84867e810` | Cancel at 20.5 s, shaped | `cancelled` 0.85 s later, item `failed`; object absent |
| k72 | candidate `84867e810` | 100 MiB multipart | completed in 26.4 s; authenticated GET SHA-256 matches |
| d69 | candidate `84867e810` | 5 natural / 2 shaped | 5 completed in 7.1–8.0 s / 2 completed in 90.5 s and 91.2 s; in the bucket |
| k72 | candidate `277c12284` (reviewed code head before the help-text-only commits) | 10 natural serial | 10 completed, 6.9–8.4 s, all in the bucket |
| k72 | candidate `277c12284` | 2 shaped | 2 completed in 90.9 s and 91.2 s; in the bucket |
| k72 | candidate `277c12284` | Cancel at 20.3 s, shaped | `cancelled` 0.17 s later, item `failed`; object absent |
| d69 | **final head** `c9a894d0a` (tree `fcd95f0e`, Debian 13 DEB) | 10 natural serial | 10 completed, 7.1–7.2 s, all in the bucket |

The commits after `277c12284` change only the Request timeout help text in Settings. The
picture listed below was taken on k72 from the final-head package (`c9a894d0a`, version
26.1121.6084), with the pointer on the help button.

The d69 nightly rows show the hang doesn't depend on k72 or its desktop. The same link
rate causes it on Debian 13 Plasma too.

## Pictures

- `pictures/settings-request-timeout-help.png`: the Request timeout help on the final head,
  annotated.
- `pictures/upload-time-before-after.png`: seconds to a final state, nightly against the fix.

## Files

- `k72/*.jsonl`, `d69/*.jsonl`: one line per upload or Retry. Each line gives the operation
  ID, time to the terminal state, state, upload status, error code and message, bucket check,
  and a per-connection TCP summary (`ss -tin`: bytes sent and acked, retransmits, RTT).
- `k72/tcp-samples/`, `d69/tcp-samples/`: the raw twice-a-second `ss` samples for each upload.
- `*/resident-log-s3-records.json`: the S3 and operation records from the resident logs of these runs.
- `k72/nightly-7-bucket-check.json`: natural nightly row 7, whose record the harness lost in a
  download timeout, checked by HEAD afterwards.
- `k72/candidatemultipart-get-verify.json`: the GET check of the multipart object.

Superseded rows aren't included: a shaped and a Cancel candidate row on k72 that a leftover
shaping watchdog unshaped mid-run, and d69 candidate rows refused with `initializing` before
the resident was ready.
