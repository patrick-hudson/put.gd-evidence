# Round 2 (Sol round 2 on #1699)

Frame 10 is `settings-r2` from `putgd-ui-catalog`, built with the `dev` preset on aurora-amd
(Fedora 45 Toolbx, Qt 6.11.2) from commit 5e0dcbdd6 of `feat/cloudflare-r2-destination`. A new Cloudflare R2
destination whose Account ID and Bucket aren't valid yet is not sent: the form says so under
Bucket ("Not saved yet: this destination saves once every field is valid."), next to the field
messages. The box and label were added afterwards to call out the new line.

The live scoped-token pass for this round (the code plus #1682's driver commits on nightly, a
local test tree) passed every step: Test upload and link with expiring links, with public links
and no Link domain (`public_url_unreachable`), and with the r2.dev Link domain; uploads with an
expiring and a public link, GET 200 with matching bytes; Copy link renewed a backdated expiry;
History deletion `removed` twice; 0 objects left; 3 destination-test journals kept, none
holding a signed query.
