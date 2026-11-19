# Round 4: live pass with the scoped token

round-4-queue.md says the live pass couldn't run. The cause was found: the lab's Cloudflare API
token, from which its broad R2 key is derived, expired on 2026-11-19 at 17:59:43 UTC after its
30-day life. The harness now uses only the bucket-scoped R2 token, for put.gd and for its own
listing and cleanup, in the bucket named on the credentials file. It doesn't use the broad key
or the API token.

The pass was built from `bdbb2a7c1` (on nightly with the save queue and #1682) on aurora-amd. Every
step passed:
- Test upload and link with expiring links completed.
- With public links and an empty Link domain it failed with `public_url_unreachable`.
- With the r2.dev Link domain it completed.
- An upload with an expiring link and one with a public r2.dev link both returned GET 200 with
  matching bytes, and the receipt provider was `cloudflare-r2`.
- Copy link after a backdated expiry renewed it: new link, expiry in the future, GET 200.
- History deletion was `removed` twice, and 0 objects were left.
- 3 destination-test journals were kept, none holding a signed query.
- The output files hold no key, account or bucket value (count 0).
