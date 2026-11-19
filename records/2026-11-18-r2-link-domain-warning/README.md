# Settings warns about Cloudflare R2 public links with no Link domain (#1679)

**Builds.** After: put.gd-desktop `9964f0168` (branch `fix/r2-link-domain-warning-1679`). Before: `94240e1e3`
(the #1678 branch it is stacked on, which has no warning). Both were built with the `dev` preset on aurora-amd in the
Fedora 45 `putgd-build` Toolbx (GCC 16.2.1, Qt 6.11.2, AWS SDK 1.11.924). The status bar reads `0.0.0-dev.unknown`
because the trees were shipped without `.git`.

**Session.** A private Xvfb display (1300×1300) on aurora-amd and a private resident (`dbus-run-session`, its own
`XDG_*` folders) with one synthetic destination. Each run chose Cloudflare R2, entered a synthetic account endpoint
and kept "Public bucket: links that never expire". The page was driven with xdotool, and each frame was cropped from
Xvfb's framebuffer to the put.gd window. Red boxes mark the Link domain row and the warning.

| Frame | What it shows |
| --- | --- |
| `1-before-r2-public-empty-link-domain.png` | Before: R2, public links and an empty Link domain, with nothing said until Test upload and link fails. |
| `1-after-r2-public-empty-link-domain.png` | After: the same setup shows a warning below Link domain: R2 doesn't serve public links from its S3 endpoint; enter the bucket's r2.dev address or a custom domain, or choose Private bucket: links that expire. |
| `2-after-link-domain-set.png` | A Link domain entered (`https://pub-0123456789abcdef.r2.dev`, synthetic): the warning is gone. |
| `3-after-link-domain-cleared.png` | Link domain emptied again: the warning is back. |
| `4-after-expiring-links.png` | Private bucket: links that expire chosen: the warning is gone. |

Saved settings after each step (from `settings.get`): Link domain set → `linkMode public`, `publicUrlBase` set;
cleared → `publicUrlBase null`; expiring links → `linkMode presigned`. The region was `auto` throughout.

**Why the warning is needed** (live, build `94240e1e3`, see record `2026-11-18-r2-region-auto`): Test upload and link
on R2 with public links and an empty Link domain fails with `public_url_unreachable`, while the same destination
with expiring links passes. The lab bucket has no r2.dev address in the lab notes, so the public-link pass with an
r2.dev Link domain was not run, and none was enabled.
