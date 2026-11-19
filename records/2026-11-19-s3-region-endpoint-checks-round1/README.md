# S3 Region and Endpoint checks, review round 1 (#1675, #1676)

Pictures and live results for the review fixes on #1688 and #1689. This record
continues `2026-11-19-s3-region-endpoint-checks-r2-exempt`. Since that record, requests
to a Cloudflare R2 endpoint are signed with `auto` whatever Region holds, so an R2
destination saved with the dashboard location now works.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `4437bec51d9eb0dcbf2d8f33734371f4515978cd`, stacked on `fix/s3-region-name-1675` at
  `4d32c0531e1ab761e65840e510fb79957fcbe94f` (on nightly `53c29eaad`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the
  footer reads `0.0.0-dev.unknown`. Pictures 01 and 02 come from the same Region code one
  commit earlier (`dd6213faa`); its only later change is in how the Endpoint section opens.
- Before: the published `26.1118.5367-nightly` AppImage.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident on the real display; hosts, account and bucket are synthetic. Red
boxes mark the change.

1. `01-aws-region-typed-region-message.png`: an Amazon S3 destination with its generated
   endpoint. Typing `Western North America (WNAM)` into Region is refused with the
   Region message. Before this round it showed the generic "Invalid S3 settings…" text,
   because the typed Region had gone into the generated endpoint host.
2. `02-endpoint-to-r2-clears-region-message.png`: the same destination switched to
   Cloudflare R2 with an R2 Endpoint. The Region message under the field clears, because
   R2 ignores Region. The status line still shows the earlier refusal because the typed
   Region is an unsaved draft. Committing it again saved it with no error.
3. `03-short-window-opens-at-endpoint.png`: a 700 px tall window. Choosing a saved R2
   destination that has the bucket on Endpoint opens the advanced section and scrolls
   the Endpoint row and its message into view.
4. `04-r2-bucket-on-endpoint-before.png` and `05-r2-bucket-moved-saved.png`: with Bucket
   empty, committing the Endpoint moves the bucket name into Bucket. Endpoint and Bucket
   save together, and the destination keeps Region `Western North America (WNAM)` with
   no error.
5. `06-r2-endpoint-path-refused.png`: a path that is not the Bucket name stays and is
   refused at the Endpoint field.

## Live runs (f44, Fedora 44)

`tools/live1675.py`, isolated resident, session credentials read in memory. R2 with
expiring links under `i1675-test/`; AWS S3 key set 2, bucket put.gd, prefix
`acceptance/i1675-test/`. Everything under those prefixes and under the doubled
`<bucket>/i1675-test/` was deleted after each run and checked gone.

| Case | 26.1118.5367-nightly | This build |
|---|---|---|
| R2 endpoint, Region `Western North America (WNAM)` | Test: `s3_transport_unknown`, "could not be reached reliably" | Saves; Test upload and link passes |
| That R2 destination saved by the nightly, opened by this build | n/a | Test upload and link passes |
| AWS endpoint, same Region | Test: "could not be reached reliably" | Save refused, field `region` |
| R2, Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>` | Test: `public_url_unreachable`; one object left under `<bucket>/i1675-test/` (removed by the harness) | Save refused, field `endpoint` |
| That Endpoint saved by the nightly, opened by this build | n/a | Test: `s3_settings_invalid`, Endpoint message |
| R2 correct, AWS S3 correct | Pass | Pass |

Nothing was left in either bucket after this build's runs.
