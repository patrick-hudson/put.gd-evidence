# B2 large files send parts on idle upload slots (#1792, PR #1798)

Live Backblaze B2 acceptance for [#1792](https://github.com/patrick-hudson/put.gd-desktop/issues/1792): a B2 large file sends up to four parts at once on upload slots the resident lends, as S3 does (#174). Code PR [#1798](https://github.com/patrick-hudson/put.gd-desktop/pull/1798), docs PR [#1800](https://github.com/patrick-hudson/put.gd-desktop/pull/1800). Built on #1788 (#1782, no request timeout while file data moves).

## Setup

- Host: d69 (Debian 13), a private headless resident (`QT_QPA_PLATFORM=offscreen`, private XDG directories, session-only credentials). No desktop and no keychain.
- Destination: a bucket-scoped B2 key, a public bucket, and the isolated prefix `acceptance/i1792-b4b93fa2e37a/`. The key was read in-process from the builder's credential file and handed to the resident over its socket. It was never printed or stored.
- `limits.concurrentUploads` 4, so a large file may borrow 3 slots (4 parts in flight). Large files use 16 MiB parts above 64 MiB.
- Builds (each identified by the resident's `ui.snapshot` build identity):
  - **nightly**: published `26.1121.6060-nightly` (`4a7730e4a`), Debian 13 package.
  - **cand1**: early candidate `26.1121.6101-dev+ge24862462d7a`, a manual `ci.yml` run on `candidate/b2-parallel-1792` (run 44934327143), before Sol's fixes.
  - **final**: `26.1121.6113-dev+gd816e1c447c5`, gitTree `4a8d9a87661a53ba92f477017623efc057c10017`. That is PR #1798's head, from `ci.yml` run 44943717007.
- Harness in `harness/`: `run.py` runs the resident and serial uploads, and samples `ss` once a second. It counts the worker's TCP connections to port 443 that sent more than 64 KiB since the last sample. `b2acc.py` checks the bucket: version list, size, `contentSha1` for single uploads, a downloaded SHA-1 for large files, and unfinished large files. `shape.sh` limits HTTPS to Backblaze's networks with `tc`. `stall.sh` drops every packet to those networks except the API address.

## Results

| Row | Build | Time | Connections sending | Result | Bucket |
|---|---|---|---|---|---|
| 200 MiB | nightly | 109.5 s, 118.6 s | 1 | uploaded | size and downloaded SHA-1 match |
| 200 MiB | cand1 | 58.7 s, 56.7 s | 4 | uploaded | size and downloaded SHA-1 match |
| 200 MiB | final | 54.4 s, 53.6 s, 59.6 s | 4 | uploaded | size matches (see the download cap below) |
| 80 MiB through a 4 Mbit/s limit, request timeout 60 s | cand1 / final | 184.2 s / 185.5 s | 4 | uploaded; every 16 MiB part took over 2 minutes and none was cut | cand1: downloaded SHA-1 matches; final: size matches |
| 80 MiB, every upload connection stalled 45 s in | cand1 / final | 135.0 s / 135.3 s | 4, then 0 | `failed`, `b2_transport_unknown` "the transfer timed out" (operation `partial`, as on nightly) | no version, 0 unfinished large files |
| 80 MiB, Cancel at 45 s, shaped | cand1 / final | 46.5 s / 46.2 s | 4 | `cancelled` | no version, 0 unfinished large files |
| 10 MiB single upload | cand1 / final | 6.3 s / 15.7 s | 1 | uploaded, one request | size and B2 `contentSha1` match |

Parallel parts made a 200 MiB upload about 2× faster on this uplink: 3.4–3.7 MiB/s against 1.7–1.8 MiB/s. Raw rows are in `results/*.jsonl`.

## Download cap gap

After the cand1 rows and the nightly baselines, B2 refused further downloads with `403 download_cap_exceeded`: the account's daily download cap ran out. So the final head's large files (`final-large200` ×2, `final-shaped`) were checked for exact size in `b2_list_file_versions` (`results/final-bucket-listing.json`), but not by a downloaded SHA-1. B2 still checked every part's SHA-1 when it arrived, and `b2_finish_large_file` checked the part SHA-1 list, so a wrong part is refused rather than stored. cand1 uses the same part-assembly code, and all three of its large files matched by downloaded SHA-1. The final head adds Sol's fixes on top: the part-URL abort path, the loan check per part, the lane start check, and the progress lock.

One more final-head 200 MiB upload (`final-keep200`) and its local copy were kept for a downloaded SHA-1 check after the cap resets at 00:00Z. Its result is added below as a follow-up.

## Cleanup

Every other test object in the prefix was deleted, and no unfinished large file remains. The shaping was removed. The test residents were stopped.
