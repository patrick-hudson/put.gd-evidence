# Cloudflare R2 as its own destination type (#1678, #1679, #1691)

**Code.** put.gd-desktop `b5ecbe286` (branch `feat/cloudflare-r2-destination`, stacked on #1688
`fix/s3-region-name-1675` at `8356b1f15`). The pictures and live runs used a local test tree with the same Settings
and R2 code, plus #1682's S3 driver commits and #1686/#1697 merged in. They were never pushed and are not part of the
PR. All builds used the `dev` preset on aurora-amd in the Fedora 45 `putgd-build` Toolbx (GCC 16.2.1, Qt 6.11.2,
AWS SDK 1.11.924). The status bar reads `0.0.0-dev.unknown` because the trees were shipped without `.git`.

**Pictures.** A private Xvfb display (1300×1300) on aurora-amd and a private resident (`dbus-run-session`, its own
`XDG_*` folders). The page was driven with xdotool, and each frame was cropped from Xvfb's framebuffer to the put.gd
window. Red boxes mark what changed. Accounts, buckets and the r2.dev address are synthetic
(`0123456789abcdef0123456789abcdef`, `lab-bucket`, `pub-0123456789abcdef.r2.dev`).

| Frame | What it shows |
| --- | --- |
| `1-add-destination-cloudflare-r2.png` | Add destination offers Cloudflare R2 beside Amazon S3, Proton Drive, Backblaze B2 and Custom uploader. |
| `2-new-cloudflare-r2-destination.png` | A new Cloudflare R2 destination asks for the Account ID (with where to find it) and Jurisdiction, with no Region, Endpoint, upload access request or storage class. |
| `3-s3-api-address-pasted.png` | The dashboard's S3 API address `https://ACCOUNT.eu.r2.cloudflarestorage.com/lab-bucket`, typed into Account ID and finished with Return, filled Account ID, Jurisdiction EU and Bucket, saved as one edit ("Ready to test"). |
| `4-public-links-no-link-domain-warning.png` | Public links with no Link domain: the warning says R2 doesn't serve public links from its S3 endpoint and what to do (#1679). |
| `5-r2-dev-link-domain-set.png` | The bucket's r2.dev address as Link domain: the warning is gone and the example link uses it. |
| `6-s3-destination-on-r2-move-offered.png` | An existing S3 destination on R2 (EU endpoint, Region "Western North America (WNAM)" as in #1675) offers Move to Cloudflare R2 and says what it keeps. Showing it saved nothing. |
| `7-after-move-to-cloudflare-r2.png` | After Move: the same destination (ID `screenshots`, same credential reference) as Cloudflare R2, with the account and jurisdiction read from its endpoint. |

**Live Cloudflare R2** (lab bucket `<bucket>`, account `<acct>`, put.gd running with the **scoped** R2 token; the harness used the
broader lab key only to list and clean the prefix `i1678-r2dest/`). Isolated resident on a private Xvfb display (for the
clipboard), session credentials, destination `cloudflare-r2` with region `auto` derived and path addressing. Each value
below was read back by the script; the r2.dev address is written `<r2.dev>`.

| Step | Result |
| --- | --- |
| Test upload and link, expiring links | passed; 0 objects left |
| Test upload and link, public links, empty Link domain | `public_url_unreachable` (the #1679 case); 0 objects left |
| Test upload and link, public links, `<r2.dev>` Link domain | passed; 0 objects left |
| Destination-test journals after each test | 0 kept, 0 holding a signed query (with R2 on the S3 path in `DestinationTestJournal.cpp`, see below) |
| Upload with expiring links | completed; receipt provider `cloudflare-r2`; the link (R2 endpoint, signed) GET 200 with the uploaded bytes |
| Copy link after the recorded expiry was moved into the past (in the run's own History database) | renewed: the recorded expiry is in the future again; the copied link GET 200 with the bytes |
| Upload with public links and `<r2.dev>` | completed; the link (`<r2.dev>`) GET 200 with the bytes; Copy link copied it |
| History deletion of both uploads | `removed` and `removed`; 0 objects left under the prefix |

Without #1682's driver commits, the scoped token can't read bucket versioning: the expiring link returned 501 and
History deletion ended `unknown`. With #1686/#1697 as they stand, R2 test journals were kept (1, 2, 3 after three
tests; none held a signed query). With `cloudflare-r2` taking the S3 path in `linkedProvider` and
`destinationTestSettled`, all three were settled and removed. No output file of the live runs holds a key, the
account id, the bucket name or the r2.dev host (checked by count).

## Round 1 after the Sol review (`e080f2b1b`)

| Frame | What it shows |
| --- | --- |
| `6-s3-destination-on-r2-move-offered.png` (retaken) | Move to Cloudflare R2 now sits at the left of its row, like the other row actions. |
| `8-other-service-to-amazon-s3.png` | Other S3-compatible (`https://minio.example.test`, `us-west-1`) → Amazon S3: saved `us-west-1` and `https://s3.us-west-1.amazonaws.com`, and the picker stays on Amazon S3. |
| `9-back-to-other-s3-compatible.png` | Back to Other S3-compatible: the MinIO endpoint and region are restored and saved. |

Live again on the scoped token, built from this head with nightly (#1686) and #1682's driver commits merged in a
local test tree: Test upload and link with expiring links and with the r2.dev Link domain passed; public links with
no Link domain gave `public_url_unreachable`; uploads in both modes loaded with the right bytes; Copy link renewed a
backdated expiry; History deletion ended `removed` for both; 0 objects left. Three test journals were kept (#1697 no
longer removes them) and none held a signed query.
