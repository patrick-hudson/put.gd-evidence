# S3 Region and Endpoint checks (#1675, #1676)

Settings refuses a Region the AWS SDK can't use and an Endpoint with a path, with a
message at that field. A destination saved earlier with either value still loads and
shows the message when it opens.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `d014b92253b921e2e34eb5087ab5cb0ca8804d32`, which sits on `fix/s3-region-name-1675` at
  `8d4e0b2317e2ece9083b669618c194aacce31289` (branched from nightly `faf34a8c6`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the
  window footer reads `0.0.0-dev.unknown`. The `src/` tree on both hosts hashes the same
  as the commit above.
- Before: the published `26.1118.5367-nightly` AppImage.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident (own XDG folders and runtime folder, no keyring) on the real
display. The account ID and bucket are synthetic. Red boxes mark the change.

1. `01-saved-earlier-region-and-endpoint.png`: a configuration saved with Region
   `Western North America (WNAM)` and the bucket on the end of Endpoint. It loads,
   and the destination opens with both messages. The advanced section opens by
   itself so the Endpoint row is in view.
2. `02-region-typed-refused.png`: typing the dashboard location into Region is refused
   at the Region field. The saved Region stays `auto`.
3. `03-endpoint-with-bucket-pasted.png` and `04-bucket-moved-out-of-endpoint.png`:
   with Bucket empty, the bucket's full URL is pasted into Endpoint, then Tab. The
   bucket name moves into Bucket and Endpoint keeps only the address. The save then
   stops at Region, which was still wrong at that point.
4. `05-endpoint-path-refused.png`: an Endpoint path that is not the Bucket name stays
   where it is and is refused at the Endpoint field.

## Live runs (f44, Fedora 44)

`tools/live1675.py`: isolated resident under `dbus-run-session`, offscreen, private XDG
folders, session credentials read from the builder's credentials file in memory.
Cloudflare R2 with expiring links (`presigned`, 1 day) under `i1675-test/`. AWS S3 with
key set 2, bucket put.gd, prefix `acceptance/i1675-test/`, expiring links. After every
run the harness listed and deleted everything under each prefix, and under
`<bucket>/i1675-test/` (the doubled path), then checked that it was gone.

| Case | 26.1118.5367-nightly | This build |
|---|---|---|
| R2, Region `Western North America (WNAM)` | Saves. Test fails `s3_transport_unknown`, "S3 could not be reached reliably…" (SDK error type 103, no request sent) | Save refused, `s3_settings_invalid`, field `region`, Region message |
| R2, Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>` | Saves. Test fails `public_url_unreachable`; one object left under `<bucket>/i1675-test/` (removed by the harness) | Save refused, `s3_settings_invalid`, field `endpoint`, Endpoint message |
| Region value saved by the nightly, opened by this build | n/a | Loads (`validation.ok`). Test fails `s3_settings_invalid`, field `region`, Region message |
| Endpoint value saved by the nightly, opened by this build | n/a | Loads. Test fails `s3_settings_invalid`, field `endpoint`, Endpoint message |
| R2 correct (host-only Endpoint, Region `auto`) | Test upload and link passes | Passes |
| AWS S3 correct | Passes (a first attempt timed out on the network; the rerun passed) | Passes (twice) |

Leftovers after this build's runs: none, on either service.

An extra fixture check (not kept as a test): a recorded upload whose Region the SDK
refuses, checked and deleted through History's path. No request reached the server;
the error was `s3_settings_invalid`, "put.gd's S3 library refused these settings before
sending anything: Region is not a region code…", `requestSent: false`.
