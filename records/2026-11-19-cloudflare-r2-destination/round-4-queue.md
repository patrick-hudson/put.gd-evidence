# Round 4: on the Settings save queue

#1699 rebased onto nightly with the Settings save queue (#1710, `c31e7403f`) and pushed as
`bdbb2a7c1`. Frame 11 is `settings-r2` from `putgd-ui-catalog` at that commit (aurora-amd, Fedora 45
Toolbx, Qt 6.11.2). A new Cloudflare R2 destination whose Account ID and Bucket aren't valid yet
keeps them out of the queue as one group, and the line under Bucket says "Account ID,
Jurisdiction and Bucket save together once all three are valid." The box and label were added
afterwards.

The scoped-token live pass could not run for this round: the lab's broad R2 key now gets 403 on
ListBuckets, and the Cloudflare API token gets 401, on every builder's credential file. The
round-2 live pass (frame 10's round) is the latest one.
