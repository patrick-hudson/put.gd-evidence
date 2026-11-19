# S3 Region and Endpoint checks, review rounds 3 and 4 (#1675, #1676)

Pictures and live results after #1689 dropped the bucket move and #1688 made the Region
feedback come only from the shown destination's current values. This record continues
`2026-11-19-s3-region-endpoint-checks-round2`.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `0b8634110c41f60d6b98b2e265f2b9b9bc52a765`, stacked on `fix/s3-region-name-1675` at
  `673f269771eeb83f006763b77023f3bc175f032f` (on nightly `f3f67d5df`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the footer
  reads `0.0.0-dev.unknown`. Before: the published `26.1118.5367-nightly` AppImage.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident on the real display. Hosts, account and bucket are synthetic.

1. `01-saved-region-message-field-and-footer.png`: an "Other S3-compatible" destination
   saved with Region `Western North America (WNAM)` opens with the Region message under the
   field and in the footer. Both come from the form's current values.
2. `02-r2-saved-endpoint-message.png`: switching to a Cloudflare R2 destination saved with
   the same Region and `/my-screenshots` on the end of Endpoint. Region shows nothing (R2
   ignores it), and the previous destination's footer message is gone. The advanced
   section opens, and Endpoint shows the new message, which names the part to remove.

## Live runs (f44, Fedora 44)

`tools/live1675.py`, isolated resident, session credentials read in memory, R2 with
expiring links under `i1675-test/`. These runs used #1689 at `fbad71353`, whose provider
code is the same as the head above. The only later change to `src/storage` is the
case-sensitive FIPS check.

| Case | 26.1118.5367-nightly | This build |
|---|---|---|
| R2, Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>` | Saves; Test: `public_url_unreachable`, one object left at the doubled path (removed by the harness) | Save refused, field `endpoint`: "Remove "/<bucket>" from the end of Endpoint and put the bucket name in Bucket…" |
| That Endpoint saved by the nightly, opened by this build | n/a | Loads; Test: `s3_settings_invalid`, same message |
| R2 correct | Pass | Pass |

Nothing was left in the bucket after this build's runs.
