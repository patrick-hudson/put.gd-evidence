# B2 upload on a slow connection finishes instead of being cut at the request timeout (#1782)

Live acceptance for put.gd-desktop PR #1788 (issue #1782). These are real Backblaze B2 native-API
uploads through put.gd's own resident and `putgd-b2-worker`, each checked afterwards against the
bucket.

## Setup

- **Host:** k72, Kubuntu 26.04 (Qt 6.10.2), wired uplink of about 1 MiB/s.
- **Builds.** Each was unpacked privately with `dpkg -x`. Nothing was installed.
  - Published nightly `26.1121.6060~nightly`: git `4a7730e4a844582745b9cc3b7686826943c903b1`.
  - Intermediate candidate `26.1121.6100~dev+g58c57d34540b`: git `58c57d34540bb5bd9c236a6f8215237960b6337e`, from manual ci.yml run 44932943794. Its files are `results/candidate-*`.
  - **Final head** `26.1121.6103~dev+g45fdf6bb83ee`: git `45fdf6bb83eea8964966af67ff076b7182fe85a0`, tree `b665ebb4b5e2c6ac6f6d27a80025e7910f830d30`, Ubuntu 26.04 DEB from manual ci.yml run 44939435134, SHA-256 `2367095ccb60aeb7d84d9f2beb5c2f8da781aebad5b91b9f4b2cce58affc1e49`. Its files are `results/candidate2-*`.
- **Resident.** A headless private resident (`QT_QPA_PLATFORM=offscreen`) with its own
  `XDG_*` directories. Its B2 profile used session-only credentials: the key was handed to the
  resident's socket by `harness/b2acc.py` in memory and was never printed or written. The
  profile used the default 600 s request timeout and 10 s connect timeout.
- **Destination.** The B2 test bucket (allPublic), isolated prefix `acceptance/i1782-b1eab2e71c99/`,
  with synthetic random payloads. Every test version was deleted afterwards and the prefix was
  verified empty. No unfinished large files were left.
- **Shaping.** `harness/shape.sh` used `tc` HTB on `eno1`, 640 kbit/s (about 80 KB/s). It limited
  only HTTPS to the three Backblaze upload networks (104.153.0.0/16, 149.137.0.0/16,
  206.190.0.0/16) and had a self-removing watchdog. It was removed after each run, and k72's
  qdisc was verified back to the default `fq_codel`.
- **Stall.** `harness/stall.sh` was applied 60 s into a shaped upload. It dropped every packet to
  the upload networks except the API host 104.153.233.180, so the upload connection stalled
  while put.gd could still list versions.
- **Per-upload check.** `harness/b2acc.py check` compared each upload against the bucket: the
  name's versions, size, SHA-1 (single uploads), `putgd-sha256` file info, and unfinished large
  files.

## Results

| Build | Row | Time to end | Outcome | Bucket |
|---|---|---|---|---|
| nightly 6060 | 60 MiB, shaped | 1805.6 s | `partial`, upload `failed`, `b2_transport_unknown` "(deadline)" | nothing stored |
| **45fdf6bb8** | 60 MiB, shaped, #1 | 830.0 s | completed, `uploaded` | one version; size, SHA-1 and SHA-256 match |
| **45fdf6bb8** | 60 MiB, shaped, #2 | 829.0 s | completed, `uploaded` | one version; size, SHA-1 and SHA-256 match |
| **45fdf6bb8** | 20 MiB, shaped, stall after 60 s | 150.9 s | `partial`, upload `failed`, "the transfer timed out" | nothing stored |
| **45fdf6bb8** | 60 MiB, shaped, Cancel at 120 s | 121.2 s | `cancelled`, upload `failed`, "Cancelled before Backblaze B2 received the whole file; nothing was uploaded" | nothing stored |
| **45fdf6bb8** | 60 MiB, unshaped | 17.8 s | completed, `uploaded` | size, SHA-1 and SHA-256 match |
| **45fdf6bb8** | 100 MiB large file, unshaped | 37.4 s | completed, `uploaded` | size and SHA-256 match, large file finished |
| 58c57d345 | the same rows | 830.2 / 829.1 / 151.0 / 121.3 / 17.6 / 34.0 s | as above, except Cancel ended upload `unknown` | nothing stored for stall and cancel |

- **The bug.** The nightly made three attempts. Each was cut at the 600 s request timeout and
  started again from byte 0. 60 MiB at 80 KB/s needs about 786 s.
- **The fix.** Both shaped final-head uploads took about the time their bytes need, in one request.
- **The Cancel row on 58c57d345.** The version listing that settles a cut upload was itself cut by
  the cancel flag, so the upload stayed `unknown`. That led to the final rule: an attempt cut
  before the transport read the whole file can't have stored it, so Cancel ends it `failed` with
  no lookup. A cut after the whole file went out stays `unknown` unless the lookup finds the file.
- **Progress gaps.** The largest gap between two changes in reported upload progress (1 s polling)
  was 4.2 s and 3.1 s on the shaped final-head rows, far below the 30 s stall limit. The 29.7 s
  gap in the stall row is the stall itself. A review concern was that Qt's transfer timer counts
  bytes queued to the socket, not bytes delivered. It did not show at this rate.

## Files

- `results/*.jsonl`: one line per upload, with the operation ID, timing, outcome, error code,
  message, details and bucket check. `nightly-*` is the published nightly, `candidate-*` is
  58c57d345 and `candidate2-*` is the final head 45fdf6bb8.
- `harness/`: the scripts used. `run.py` drives the resident, `b2acc.py` does the bucket checks
  and cleanup and loads the key in-process, `shape.sh` and `stall.sh` do the `tc` work, and the
  `chain-*.sh` files are the run orders. The first final-head chain lost its two shaped rows to a
  harness race: it uploaded while the resident still answered `initializing`. `chain-candidate3.sh`
  reran them after a retry was added to `run.py`.
