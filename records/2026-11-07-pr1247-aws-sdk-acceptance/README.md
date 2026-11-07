# PR #1247 AWS SDK acceptance

Candidate head: `e84d5b08b5107b238002bfb8316d6116a3c3003c`.
CI run **42393591166**, attempt 2, required CI summary PASS.
Exact CI packages identify test-merge `6c1d282960010c87388ae2d2ea11b6ee45f98893`, tree `0f913c13169f78ac60f6c95f2318a0e739b77d2f`; this tree matches the PR head.
Frozen driver: `191f2f41f5ba649e4f471ec100dd7a4ffed1c358` in each builder's existing `~/nd` checkout. No compilation, harness edits, shared-checkout branch changes or commits, PR code edits or merge.

## Candidate Tier 1 and clipboard

| Desktop / builder | Result | Cells | Evidence |
| --- | --- | --- | --- |
| Cinnamon (Mint) / m74 | PASS | 13/13 | [result.json](m74/out/cinnamon-(mint)/result.json) |
| Ubuntu GNOME / d69 | PASS | 13/13 | [result.json](d69/out/ubuntu-gnome/result.json) |
| Kubuntu KDE / k72 | PASS | 13/13 | [result.json](k72/out/kubuntu-kde/result.json) |
| Fedora GNOME / f44 | FAIL | 12/13 | [verified-result.json](f44/out/fedora-gnome/verified-result.json) |
| Aurora / aurora-amd | PASS | 13/13 | [result.json](aurora-amd/out/aurora/result.json) |

Total: **64/65** versus published nightly `v26.1105.3986-nightly`'s **65/65** on issue #1003 ([preserved table](nightly-comparison.md)). Four candidate rows passed all cells; Fedora Edit & upload failed twice at “arrow tool selected by real input”. Its saved failure frame shows Settings in front of the expected editor. Baseline comparison is recorded separately below. This result does not claim 65/65 acceptance.

All five rows use the exact configured Tier 1 goldens in d69's private nightly configuration, fresh guarded overlays on their designated builders, CI native packages on Mint/Ubuntu/Kubuntu/Fedora and the exact AppImage on Aurora. Displays remained available on workstation wall ports 6100–6104 through SSH tunnels to each builder's loopback VNC. The unchanged worker acquires and heartbeats desktop leases and manages Proton lending. Host, guest, compositor, Qt platform, source and package identities, saved synthetic frames, terminal audited receipts and retirement manifests accompany each row.

## Live providers

All standalone transfers used the exact CI Debian 13 package, production resident/CLI/provider workers, private sockets checked below the Linux limit, fresh private XDG directories including data home, and synthetic files under unique isolated prefixes. They are offscreen provider tests, not desktop proof. Credentials came from the owned private builder input, in memory, through temporary credential references. The independent Python SDK performed only reads; it did not upload or delete the objects. Every successful upload was downloaded independently and checked for exact length and SHA-256, then deleted with the exact History ID through delete.prepare/delete.confirm. No bucket policy, versioning or pre-existing user objects were modified.

| Provider / path | 65 MiB multipart | 1 MiB single-part | ETag |
| --- | --- | --- | --- |
| AWS S3 / C++ S3 worker | PASS | PASS | multipart `dc90a685fe5db6091c0725ac8abf3e24-5`; single `4f78af707a8e56b11e9ab942e54a3664` |
| R2 / C++ S3 worker | PASS | PASS | multipart `dc90a685fe5db6091c0725ac8abf3e24-5`; single `4f78af707a8e56b11e9ab942e54a3664` |
| B2 / C++ S3 worker | FAIL, pre-existing conditional-write limitation | FAIL, same limitation | No successful S3 ETag; completion/PUT refused |
| B2 / native B2 worker, supplementary | PASS, large-file parts | PASS | Native receipts use file IDs, not multipart S3 ETags |
| Proton / lab lease | PASS on all five candidate desktop rows | n/a | Region upload, independent recipient verification and revocation; session baton returned |

[Provider summaries](provider-results.json) retain operation/History/deletion IDs, ETags, bytes, hashes and error stages. Multipart payload SHA-256: `28047d8ebd7cbf68154a9bb426fb117d351820f879c50a866e6652016db13786`; single-part SHA-256: `4f94c27d4cdc1a2f90e40de9bcc93fd562060e7120b24b2e45e0e77dde0dbe28`.

B2's supplied account key authenticates the native API but the S3 endpoint rejects its name HEAD (403) on both candidate and published nightly. Temporary derived B2 application keys scoped to each unique synthetic prefix passed authentication and reached the actual SDK multipart completion. B2 rejected CompleteMultipartUpload (501 NotImplemented, `upload_complete`) and PutObject (`upload_put`) because the endpoint does not support put.gd's required conditional writes. Both failures reproduce on checksum-verified published nightly Debian 13 package `v26.1105.3986-nightly`. Each temporary key was deleted. Independent native B2 listing confirmed no remaining files or unfinished large files in every tested prefix. The requested three-provider S3 multipart gate therefore remains unmet; native B2 success does not replace it.

## Preserved failures and cleanup

Kubuntu Proton attempt 1 failed with keychain_unavailable during setup; the unchanged worker's attempt 2 passed. Fedora live S3 attempt 1 failed with TLS curlCode 35 at name_head, before an upload; retry passed. Its first attempt left guest-local fixture state and prevented automatic cleanup. The original worker result remains blocked. Explicit recovery read the exact failed History row: uploadStatus=failed, remoteStatus=not_requested, empty receipt/object reference. The private History DB was copied to the builder, the exact bridge credential was removed, the Proton baton was confirmed returned, and guarded retirement and checked lease release completed. The separately named verified-result.json derives 12 passing cells and the editor failure from unchanged terminal receipts; it preserves the original worker summary. No evidence was rewritten into a pass.

The first Fedora baseline launcher stopped at preflight while a just-released guest port was unavailable; no app started, and its lock release passed. The fresh retry is under focused-baseline2. All original attempts are retained.

NOT RUN by requested scope: supplemental Aurora bar.handle (#1246), recording-selector and bar-options input blocks. Their known prior findings are not counted as passing tests.

## Package SHA-256

| Artifact / use | SHA-256 |
| --- | --- |
| release-native-ubuntu24.04 / Mint | `e51d812132af8b879f7e4eb1029239438fab13f00b6b08ac86ba2295af9905a5` |
| release-native-ubuntu26.04 / Ubuntu and Kubuntu | `a3f57f33bcf792ca7486603b6eff0854d7c8070f9646ccbd9d24801f033212eb` |
| release-native-debian13 / live providers | `d1ee3eb94bfbb294eb0675ad5ba333caf40f20b6e6bb8a6875a27e0cbefb6cda` |
| release-native-fedora44 / Fedora | `843707167f28708c65c63ec82e3e54d5caacdd0c65e21b85c865205476733851` |
| release-appimage / Aurora | `b48a1cab908dad37878b60ce9bee47fd0ff4795c263f0720f5fdf7c9924a1861` |
| published nightly Debian 13 / B2 comparison | `eabbc08cc6ded7669f4de88dc8eeee505b276bf36be4bc52af9bdf1850d4eaf7` |

Full filenames and identities: [package-digests.json](package-digests.json). Downloads occurred on builders; Aurora package/catalog were downloaded on d69 and streamed directly to Aurora because it lacks gh. No host tools were installed. Live account/share-link frames remain private on builders.

## Published-nightly Fedora comparison

The checksum-verified published Fedora RPM and its exact-build catalog (CI run 42035780388) identify `191f2f41f5ba649e4f471ec100dd7a4ffed1c358`. A fresh overlay of the same Fedora golden ran region, window/desktop, recording, Edit & upload, then live S3. **All five passed**. [Focused baseline result](f44/focused-baseline2/result.json).

The candidate editor failure **did not reproduce on this published-nightly replay**. Its cause remains unresolved; this report does not declare it pre-existing or establish an SDK cause. Fedora's first-attempt TLS failure also did not reproduce on the baseline; the candidate's own retry had passed. B2 S3's 501 completion/PUT failures **did reproduce** on the published Debian nightly.

## Final lab state

All five candidate overlays and the focused Fedora baseline overlay were retired through guarded evidence manifests. The aborted preflight baseline created no guest. All five desktop and five Proton leases are free ([final leases](final-leases.json)). Only this campaign's five tunnels and five VM wall tiles were removed; physical tiles and unrelated desktop work were preserved ([wall cleanup](wall-cleanup.json)). No golden was modified or deleted. Private test source, original failed receipts, live frames and the failed S3 History copy remain on their builders. Standalone summaries omit account URLs. Shared workstation checkout pre-existing untracked files were preserved.

**Result: acceptance incomplete.** Candidate Tier 1 is 64/65, compared with baseline 65/65; Fedora Edit & upload remains a candidate-only observed failure. AWS/R2 multipart and single-part, native B2 large/small and Proton pass; B2 S3 multipart and single-part fail on candidate and nightly. No merge or PR code edit was performed.

Published Fedora baseline RPM SHA-256: `119b158eeb7b75d886636ab60026ba92ce69101e5bd88052f6bccb42e5ff19b8`.
