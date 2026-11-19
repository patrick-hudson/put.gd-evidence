# S3 Region and Endpoint checks, review round 2 (#1675, #1676)

Live results and pictures for the second review round on #1688 and #1689. This record
continues `2026-11-19-s3-region-endpoint-checks-round1`.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `0c5a16b4a695046d9bbe3da059828f6cf5010163`, stacked on `fix/s3-region-name-1675` at
  `f62c21d472e062393a13d70545562ada8b060cc5` (on nightly `f3f67d5df`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the footer
  reads `0.0.0-dev.unknown`. Before: the published `26.1118.5367-nightly` AppImage.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident on the real display; hosts, account and bucket are synthetic.

1. `01-aws-region-refused-field-and-footer.png`: an Amazon S3 destination refuses
   `Western North America (WNAM)` in Region, with the message under the field and in the
   footer.
2. `02-r2-endpoint-clears-field-and-footer.png`: after switching the same destination to
   Cloudflare R2 and entering an R2 Endpoint, both the message under Region and the one in
   the footer are gone. In round 1 the footer kept it.

## Live runs (f44, Fedora 44)

`tools/live1675.py`, isolated resident, session credentials read in memory. R2 with
expiring links under `i1675-test/`; AWS S3 key set 2, bucket put.gd, prefix
`acceptance/i1675-test/`. Everything under those prefixes and under the doubled
`<bucket>/i1675-test/` was deleted after each run and checked gone.

| Case | 26.1118.5367-nightly | This build |
|---|---|---|
| R2, Region left blank | Save refused | Saves; Test upload and link passes |
| R2, Region `Western North America (WNAM)` | Test: "could not be reached reliably" | Saves; Test upload and link passes |
| R2, Endpoint typed as `HTTPS://<ACCT>.R2.CLOUDFLARESTORAGE.COM` | Saves; Test: "The S3 endpoint hostname could not be resolved" | Saves; Test upload and link passes |
| AWS endpoint, Region `Western North America (WNAM)` | Test: "could not be reached reliably" | Save refused, field `region` |
| R2, bucket on the end of Endpoint | Test: `public_url_unreachable`, object left at the doubled path | Save refused, field `endpoint` |
| R2 correct, AWS S3 correct | Pass | Pass |

Nothing was left in either bucket after this build's runs.

The new Settings test `refusedBucketMoveNeverLeavesAnUnsavedBucketShowing` was also run
against this build with the undo call removed. It failed there (the form showed
`new-bucket` while `saved-bucket` was saved) and passes with the fix.
