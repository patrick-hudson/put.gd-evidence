# S3 Region and Endpoint checks, review round 5 (#1675, #1676)

Pictures and live results for the last review round on #1688 and #1689. This record
continues `2026-11-19-s3-region-endpoint-checks-round4`.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `20e33c47cd62802a7e4bd2b26af729de2cb9be91`, stacked on `fix/s3-region-name-1675` at
  `42ac6c30466f259dfdcd95525e8441732e427565` (on nightly `f3f67d5df`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the footer
  reads `0.0.0-dev.unknown`.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident on the real display. Hosts, account and bucket are synthetic.

1. `01-endpoint-message-quotes-typed-path.png`: a saved R2 destination whose Endpoint ends
   in `/my-screenshots%2Ffolder/`. The message quotes that text exactly as it appears in the
   field, not a decoded form of it.
2. `02-refused-file-own-line-destinations.png` and `03-refused-file-own-line-settings.png`:
   while put.gd was open, the configuration file was edited outside it to blank the
   Region of the other (non-R2) destination. The resident refused the reload. Both
   footers show "The configuration file wasn't loaded: …" on a line of its own, below
   the form's own feedback. The form's values don't change that line. Only a
   successful reload or save clears it.

## Live runs (f44, Fedora 44)

`tools/live1675.py` against Cloudflare R2 (isolated resident, credentials read in memory)
with #1689 at `6e61ebfe3`, whose `src/storage` is identical to the head above (the later change is only the Settings footer line).

| Case | Result |
|---|---|
| Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>%2Ffolder/` | Save refused, field `endpoint`: Remove "/<bucket>%2Ffolder/" from the end of Endpoint… |
| Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>` | Save refused, field `endpoint`: Remove "/<bucket>"… |
| R2 correct | Test upload and link passes |

Nothing was left in the bucket.
