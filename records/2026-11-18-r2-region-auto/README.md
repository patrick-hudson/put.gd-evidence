# Cloudflare R2 uses the region auto in Settings (#1678)

**Builds.** Round 1 (frames 1–4): put.gd-desktop `94240e1e3`, before: nightly `faf34a8c6`. Round 2 (after the Sol
review): #1684 rebased onto #1688 (`fix/s3-region-name-1675` at `5e7906655`): frame 5 at `ea1a557c2`, frames 6–7
at `df35b37e1`, and the "before" of frame 7 at `ea1a557c2`, which doesn't have the Bucket routing fix. All were
built with the `dev` preset on aurora-amd in the Fedora 45 `putgd-build` Toolbx (GCC 16.2.1, Qt 6.11.2, AWS SDK
1.11.924). The status bar reads `0.0.0-dev.unknown` because the trees were shipped without `.git`.

**Session.** A private Xvfb display (1300×1300) on aurora-amd and a private resident (`dbus-run-session`, its own
`XDG_*` folders) with one synthetic destination ("Screenshots", bucket `my-screenshots`, no credentials). The page
was driven with xdotool, and each frame was cropped from Xvfb's framebuffer to the put.gd window. Red boxes mark the
rows that changed. The R2 endpoint uses a synthetic account `0123456789abcdef0123456789abcdef`.

| Frame | What it shows |
| --- | --- |
| `1-amazon-s3.png` | The starting point: Amazon S3 with region `us-east-1` (same in both builds). |
| `2-before-r2-chosen.png` / `2-after-…` | Cloudflare R2 chosen. Before: Region still offers AWS regions, and the AWS endpoint stays. After: Region is a note that R2 has no regions, the AWS endpoint is cleared so the field asks for the account endpoint, and Bucket says where uploads go in words. |
| `3-before-r2-endpoint-entered.png` / `3-after-…` | The account endpoint entered. Saved region: before `us-east-1`, after `auto`. |
| `4-before-back-to-amazon-s3.png` / `4-after-…` | Amazon S3 chosen again. Before: the R2 endpoint stays saved under "Amazon S3". After: `us-east-1` and `https://s3.us-east-1.amazonaws.com` are saved. |
| `5-before-saved-r2-wnam-opened.png` / `5-after-…` | A saved R2 destination with a jurisdiction endpoint (`….eu.r2.cloudflarestorage.com`) and a dashboard location as its region. Before: an AWS-style Region field shows the location. After (round 2): the note shows, and the saved region is left unchanged. Opening Settings writes nothing; requests to an R2 host sign with `auto` (#1688). |
| `6-after-region-tab-existing-destination-empty-bucket.png` | Bucket emptied on a saved destination, then Tab into and out of Region. The problem shows only under Bucket; nothing under Region. |
| `7-before-region-tab-new-destination.png` / `7-after-…` | A new destination with no bucket yet; Tab into and out of Region. Before: the generic "Invalid S3 settings; use a supported endpoint…" appears under Region. After: the problem shows only under Bucket. |
| `8-after-other-service-with-region-auto.png` | Round 3 (`3a31096b4`): an Other S3-compatible destination saved with region `auto` says at Region that auto is Cloudflare R2's region, instead of keeping it quietly. |
| `9-after-refused-endpoint-error-under-endpoint.png` | Round 3 (`74dde223b`): after a refused one-letter Bucket, a refused Other endpoint (with a query string) shows its error under Endpoint, not under Bucket. Nothing was saved. |
| `10-after-refused-r2-endpoint-nothing-saved.png` | Round 3 (`74dde223b`): AWS destination, Cloudflare R2 chosen, an R2 endpoint with a query string entered and refused. Region and Endpoint are retried as one unit, so the saved destination stays `us-east-1` + `https://s3.us-east-1.amazonaws.com`. Before, `auto` was saved against the AWS endpoint. |

Saved settings read back with `settings.get` (round 2 build, synthetic destinations):

| Step | Saved afterwards |
| --- | --- |
| Amazon S3 picked again on `https://s3.dualstack.us-east-1.amazonaws.com` | endpoint unchanged (round 1 replaced it) |
| Other (`https://minio.example.test`, `us-west-1`) → R2 with endpoint → Other | R2: `auto` + R2 endpoint; back to Other: `us-west-1` + `https://minio.example.test` |
| Bucket typed as `x` (refused), then the R2 endpoint entered | region `auto` + R2 endpoint saved; bucket stays `my-screenshots` |
| R2 destination with region "Western North America (WNAM)" opened | region unchanged; nothing saved |
| Endpoints `https://acct.r2.cloudflarestorage.com.example` and `https://storage.example/cloudflarestorage.com` | shown as Other S3-compatible with an editable Region; nothing saved |

**Live Cloudflare R2 Test upload and link** (isolated offscreen resident on aurora-amd, session credentials,
account endpoint `https://<acct>.r2.cloudflarestorage.com`, bucket `<bucket>`, prefix `i1678-test/`, Link domain
`https://<r2.dev>` where listed). Each run left 0 objects under the prefix, and no output file holds a key, the
account id, the bucket name or the r2.dev host.

| Case | Nightly `faf34a8c6` | Round 2 with R2 signing (`8e2258964`, the change now moving to #1688) | #1688 `5e7906655` + #1684 `df35b37e1` |
| --- | --- | --- | --- |
| Saved region "Western North America (WNAM)", expiring links | `s3_transport_unknown` ("S3 could not be reached reliably", the #1675 report) | passed | `s3_settings_invalid` (not sent): needs #1688's R2 signing |
| Saved region WNAM, public links, `<r2.dev>` Link domain | `s3_transport_unknown` | passed | `s3_settings_invalid` (not sent): needs #1688's R2 signing |
| Region `auto`, expiring links | passed | passed | passed |
| Region `auto`, public links, empty Link domain | `public_url_unreachable` | `public_url_unreachable` | `public_url_unreachable` |
| Region `auto`, public links, `<r2.dev>` Link domain | passed | passed | passed |
