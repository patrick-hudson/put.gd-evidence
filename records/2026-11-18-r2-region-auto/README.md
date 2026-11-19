# Cloudflare R2 uses the region auto in Settings (#1678)

**Builds.** After: put.gd-desktop `94240e1e3` (branch `fix/r2-auto-region-1678`). Before: nightly `faf34a8c6`.
Both were built with the `dev` preset on aurora-amd in the Fedora 45 `putgd-build` Toolbx (GCC 16.2.1, Qt 6.11.2,
AWS SDK 1.11.924). The status bar reads `0.0.0-dev.unknown` because the trees were shipped without `.git`.

**Session.** A private Xvfb display (1300×1300) on aurora-amd and a private resident (`dbus-run-session`, its own
`XDG_*` folders) with one synthetic destination ("Screenshots", bucket `my-screenshots`, no credentials). The page
was driven with xdotool, and each frame was cropped from Xvfb's framebuffer to the put.gd window. Red boxes mark the
rows that changed. The R2 endpoint is a synthetic account `0123456789abcdef0123456789abcdef`.

| Frame | What it shows |
| --- | --- |
| `1-amazon-s3.png` | The starting point: Amazon S3 with region `us-east-1` (same in both builds). |
| `2-before-r2-chosen.png` / `2-after-r2-chosen.png` | Cloudflare R2 chosen. Before: Region still offers AWS regions at `us-east-1`, and Endpoint keeps the AWS address. After: Region is a note that R2 has no regions and put.gd uses `auto`, the AWS endpoint is cleared so the field asks for the account endpoint, and Bucket says where uploads go in words rather than `s3://`. |
| `3-before-r2-endpoint-entered.png` / `3-after-…` | The account endpoint entered. Saved region: before `us-east-1`, after `auto`. |
| `4-before-back-to-amazon-s3.png` / `4-after-…` | Amazon S3 chosen again. Before: nothing changes, so the picker says Amazon S3 while the R2 endpoint stays saved. After: region `us-east-1` and endpoint `https://s3.us-east-1.amazonaws.com` are saved. |
| `5-before-saved-r2-wnam-opened.png` / `5-after-…` | A saved R2 destination with a jurisdiction endpoint (`….eu.r2.cloudflarestorage.com`) and the dashboard location `WNAM` as region, opened in Settings. Before: `WNAM` stays. After: the note shows and `auto` is saved as the destination is shown. |

Saved settings after each step (from `settings.get`):

| Step | Before (`faf34a8c6`) | After (`94240e1e3`) |
| --- | --- | --- |
| R2 endpoint entered | region `us-east-1` | region `auto` |
| Amazon S3 chosen again | endpoint `https://<synthetic>.r2.cloudflarestorage.com`, region `us-east-1` | endpoint `https://s3.us-east-1.amazonaws.com`, region `us-east-1` |
| Saved R2 profile with `WNAM` opened | region `WNAM` | region `auto` |

**Live Cloudflare R2 test** (build `94240e1e3`, isolated offscreen resident on aurora-amd, session credentials,
destination as the new form saves it: region `auto`, account endpoint `https://<acct>.r2.cloudflarestorage.com`,
bucket `<bucket>`, prefix `i1678-test/`):

| Case | Test upload and link | Objects left under the prefix |
| --- | --- | --- |
| Private bucket: links that expire | completed | 0 |
| Public links, empty Link domain | failed: `public_url_unreachable` (the case #1679 warns about) | 0 |
| Public links with the bucket's r2.dev address | not run: the lab notes have no r2.dev address for the lab bucket, and none was enabled | n/a |

No output file of the live run contains a key, the account id or the bucket name (checked by count).
