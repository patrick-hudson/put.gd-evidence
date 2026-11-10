# Final CI, review and cleanup receipt

PR1378 head1194b9e788908d8315a5ff04f03c7618b0c51d4a: CI42748211102 attempt2 SUCCESS, Ubuntu24.04/26.04 and contracts passed, required CI summary passed. Attempt1 lost only Ubuntu26 Install distro dependencies after20 minutes; raw failure log retained. No product build/test failure in that attempt. Packages/pipewire/sanitizers were path-selected out, not asserted passing.

PR1380 head0125ada526addfa868503d26add510f9393bb4c1: CI42745579753 attempt2 SUCCESS, Ubuntu24.04/26.04 and required CI summary passed. The prior runner-only Ubuntu24 dependency failure is recorded in README. No new package run.

Current-head CodeRabbit reviews remain5836285177 and5836120462; complete bodies previously read, including checking for Outside diff range comments. No outside-diff or inline code findings, zero review threads, generic docstring coverage warning answered with the existing focused C++ contract comments. No review approvals are implied. Current full CI receipts and final thread query are included.

Latest nightly2c8d864baa0a26d04da4c0065b40c2d1b3478fc9 includes the unrelated CI mirror change and S3 links work, touching none of these branches' source files or tests. Both source PRs are mergeable; no update required under round coordination's shared-file rule. Source heads unchanged.

The final current-head Fit image with a left-edge arrow is a-patches-head-final.png; PICTURE-EDGE.md documents its annotation. Original screenshot is preserved byte-for-byte. Both PR bodies will embed current-head images and cite final CI. CLEANUP-FINAL.md identifies retained isolated build caches and original private-run artifacts. No own desktop locks, app/build/test/package processes, VMs, or tunnels remain. No merge or PR watch. No docs PR: no new persistent cache, so the source Memory table remains accurate.
