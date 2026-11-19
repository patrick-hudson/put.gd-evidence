# S3 Region and Endpoint checks, R2 exempt from the Region rule (#1675, #1676)

Settings refuses a Region the AWS SDK can't use (on any host but Cloudflare R2) and
an Endpoint with a path (on every host, R2 included), with a message at that field. A
destination saved earlier with either value still loads and shows the message when it
opens. This record replaces `2026-11-19-s3-region-endpoint-checks`, made before R2
hosts were exempted from the Region rule. Its pictures show a Region message on an R2
destination, which no longer happens.

## Build

- Code: put.gd-desktop `fix/s3-endpoint-path-1676` at
  `63884af955446d1796090db29798b52a9d25e902`, which sits on `fix/s3-region-name-1675` at
  `5e79066554b86aae9ac7eacd8315a32ca6910be2` (branched from nightly `faf34a8c6`).
- Dev builds (`cmake --preset dev`, AWS SDK 1.11.924) synced without `.git`, so the
  window footer reads `0.0.0-dev.unknown`. The `src/` tree on m74 and f44 hashes the same
  as the commit above.
- Before: the published `26.1118.5367-nightly` AppImage.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident (own XDG folders and runtime folder, no keyring) on the real
display. The hosts, account ID and bucket are synthetic. Red boxes mark the change.

1. `01-other-service-saved-region-message.png`: an "Other S3-compatible" destination
   saved with Region `Western North America (WNAM)` loads and opens with the Region
   message.
2. `02-other-service-region-typed-refused.png`: after Region was fixed to `us-east-1`,
   typing the dashboard location again is refused at the Region field. The saved Region
   stays `us-east-1`.
3. `03-r2-saved-endpoint-message-no-region-message.png`: a Cloudflare R2 destination
   saved with that Region and the bucket on the end of Endpoint. Region shows no
   message, because R2 ignores it (#1678). Endpoint shows its message, and the advanced
   section opens by itself so the row is in view.
4. `04-r2-bucket-on-endpoint-before.png` and `05-r2-bucket-moved-saved.png`: with Bucket
   empty and the bucket on Endpoint, committing Endpoint (Return) moves the name into
   Bucket and leaves only the address in Endpoint. The destination then saves.
5. `06-r2-endpoint-path-refused.png`: an Endpoint path that is not the Bucket name stays
   and is refused at the Endpoint field. The saved Endpoint is unchanged.

## Live runs (f44, Fedora 44)

`tools/live1675.py`: isolated resident under `dbus-run-session`, offscreen, private XDG
folders, session credentials read from the builder's credentials file in memory.
Cloudflare R2 with expiring links (`presigned`, 1 day) under `i1675-test/`. AWS S3 with
key set 2, bucket put.gd, prefix `acceptance/i1675-test/`, expiring links. After every
run the harness listed and deleted everything under each prefix, and under
`<bucket>/i1675-test/` (the doubled path), then checked that it was gone.

| Case | 26.1118.5367-nightly | This build |
|---|---|---|
| AWS endpoint, Region `Western North America (WNAM)` | Saves. Test fails `s3_transport_unknown`, "S3 could not be reached reliably…" | Save refused, `s3_settings_invalid`, field `region` |
| The same, saved by the nightly and opened by this build | n/a | Loads. Test fails `s3_settings_invalid`, field `region`, Region message |
| R2 endpoint, Region `Western North America (WNAM)` | Saves. Test fails `s3_transport_unknown`, "could not be reached reliably" (SDK error type 103, nothing sent) | Saves. Until #1678 signs R2 requests with auto, Test fails `s3_settings_invalid`, "put.gd's S3 library refused these settings before sending anything: Region is not a region code…", `requestSent: false` |
| R2, Endpoint `https://<acct>.r2.cloudflarestorage.com/<bucket>` | Saves. Test fails `public_url_unreachable`; one object left under `<bucket>/i1675-test/` (removed by the harness) | Save refused, `s3_settings_invalid`, field `endpoint` |
| That Endpoint saved by the nightly, opened by this build | n/a | Loads. Test fails `s3_settings_invalid`, field `endpoint`, Endpoint message |
| R2 correct (host-only Endpoint, Region `auto`) | Passes | Passes |
| AWS S3 correct | Passes (a first attempt timed out on the network; the rerun passed) | Passes |

Leftovers after this build's runs: none, on either service.
