# PR #1245 dependency candidate acceptance

Tier 1 final result: 65/65 cells after recorded cleanup recovery. The supplemental LayerShellQt findings below are reported separately and do not change the Tier 1 count.

Candidate PR head: ec3b48c777d116a0fe41d9cf4bd44b54cbf91ca9.
CI run: 42363534641. Package/catalog commit: 05b61eec291e510ae6b7e67855345dd9e3816963
(GitHub test merge). Both commits have tree 9cc27397b972a00cbfde3b39b3564c7874551838.
Frozen acceptance driver: 191f2f41f5ba649e4f471ec100dd7a4ffed1c358 on each builder's ~/nd.
No candidate compilation or harness source edits. The shared workstation checkout was not switched or committed.

The five rows are copied from d69's private nightly configuration: Mint/Cinnamon X11 on m74 (Ubuntu 24.04 DEB), Ubuntu/GNOME Wayland on d69 (Ubuntu 26.04 DEB), Kubuntu/Plasma Wayland on k72 (Ubuntu 26.04 DEB), Fedora/GNOME Wayland on f44 (Fedora 44 RPM), Aurora/Plasma Wayland on aurora-amd (AppImage). Each uses the configured immutable golden and a new guarded overlay. The normal worker acquires/heartbeats the desktop and guest-slot leases and cleans up on exit. Guest displays were forwarded on workstation ports 6100–6104 to each builder's loopback 5946 and added to the existing wall.

Additional provider tests use the extracted candidate Debian 13 package on d69, a new private runtime, and production resident + CLI + upload workers. These are offscreen upload tests, not desktop acceptance. AWS S3 uses a 65 MiB synthetic file (production threshold 64 MiB, 16 MiB parts); B2 and R2 each use 1 MiB. Credentials are read only in memory from the owned private input and imported through the existing lab broker into fresh references. Every successful upload is independently downloaded and hashed, then removed through exact History IDs using delete.prepare and delete.confirm. The result records retain operation, History and deletion identities. Public URLs are omitted from published summaries; original receipts remain privately on d69.

The initial S3 attempt was rejected before operation creation while the app initialized. The corrected attempt waits on that explicit pre-operation refusal. The upload and public download passed; the controller then used the wrong deletion response field. Recovery inspected the existing deletion, confirmed remoteStatus=removed, and removed the temporary credential; it did not send another delete. The first R2 attempt used unsupported aclMode=none and was rejected during settings validation before an upload. The corrected command uses aclMode=omit. All original failed attempts are retained and do not constitute application regressions.

Only synthetic local editor screenshots are included for desktop examples. Live account and share-link frames stay private on the builders. Terminal surface-driver receipts and their scans establish the functional checks; screenshots alone do not establish acceptance.

## Tier 1 result

| Desktop / host | Result | Cells | Summary |
| --- | --- | --- | --- |
| Cinnamon (Mint) / m74 | PASS | 13/13 | [result.json](m74/out/cinnamon-(mint)/result.json) |
| Ubuntu GNOME / d69 | PASS | 13/13 | [verified-result.json](d69/out/ubuntu-gnome/verified-result.json) |
| Kubuntu KDE / k72 | PASS | 13/13 | [verified-result.json](k72/out/kubuntu-kde/verified-result.json) |
| Fedora GNOME / f44 | PASS | 13/13 | [result.json](f44/out/fedora-gnome/result.json) |
| Aurora / aurora-amd | PASS | 13/13 | [verified-result.json](aurora-amd/out/aurora/verified-result.json) |

The latest published nightly is v26.1105.3986-nightly. Its issue #1003 table also has 65/65 cells; the exact table is preserved in nightly-comparison.md. Counts are one cell per flow, not per interaction assertion. Some recipes emit several interaction assertions.

## Additional uploads

- PASS: 65 MiB AWS S3 upload through the candidate Debian 13 resident/C++ SDK, five-part ETag, exact unsigned download length and SHA-256 match, History deletion confirmed removed. See live2-result.json.
- PASS: 1 MiB Backblaze B2 upload, independent public download length/SHA-256 match, exact History deletion. See b2-result.json.
- PASS: 1 MiB Cloudflare R2 upload through the candidate C++ S3 worker, independent authenticated read length/SHA-256 match, exact History deletion. See r2b-result.json.
- PASS: Proton region upload, recipient download/byte or pixel verification and revocation on every Tier 1 row; borrowed session returned on every builder.

The template description in the B2/R2 raw summaries says multipart; their actual `bytes` fields are 1 MiB and those two tests were single-part. Only the S3 65 MiB test claims multipart coverage.

## Lab recovery and preserved failures

Kubuntu History attempt 1 recorded its deletion but retained guest-local fixture resources during cleanup; attempt 2 passed. After all 13 flows passed, the live recipe cleanup receipts and returned Proton baton were checked, the owned VM was retired through the guarded cleanup manifest, and the same lease was released with an empty cleanup check. The original result.json remains unchanged; verified-result.json derives final cells from audited terminal receipts and references the recovery.

Aurora file-manager upload attempt 1 timed out waiting for the Upload complete popup; the built-in retry passed. A focused published-nightly comparison is recorded separately. The first supplemental launcher passed recipes as separate arguments instead of a comma-separated list. Aurora cleanup then rejected the launcher’s /home alias in its evidence path; canonical /var/home paths fixed that. The original worker stopped the guest in its finally block. A retry against that stopped endpoint was blocked before input; the retained owned overlay was restarted with the existing lab qemu_command primitive, with socket checks and saved visible preflight. The temporary /usr probe overlay disappeared on reboot, so standard preparation reinstalled the probe tools; its RAM step refused the already prepared Downloads symlink. Subsequent selector tests used the existing valid profiles and restored probes. All these attempts are preserved; the frozen harness source was not changed.

Ubuntu cleanup found the new data directory created by the separate provider controllers. Its only artifact directories matched the exact three synthetic operation IDs; the entire directory was moved into c1245b/live-private-data on d69, preserving History and payloads outside the publishable evidence, and cleanup then passed.

The manual recording-selector controller first had no output route enabled. The corrected run enabled a local route and restored the exact original settings. Escape visibly dismissed the selector and its durable operation reported cancelled. A later drag attempt lost its recording session before readback; it is not claimed as a passing drag test. The frozen selector automation reports known #942 untitled-layer-surface identification blocks.

## LayerShellQt findings and published-nightly comparison

- PASS: candidate AppImage on the Aurora 45 / Plasma 6.8.2 Wayland golden: region overlay opens, captures, Escape/right-click cancel, live and screenshot-first modes. The recording bar, bounds ring, start/pause/resume/stop lifecycle and moving captured video pass in `layers5/receipt.json` (13 passing interaction assertions).
- PASS: the manual recording selector visibly opens and Escape cancels its durable operation; before/after screenshots and `manual3-selector.json` retain that specific result. This does not claim the later manual drag passed.
- FAIL: `selectors.bar_handle` asserts “full-screen target requires handle” before recording starts. It fails identically on candidate and published `v26.1105.3986-nightly`, using the same Aurora golden, native Wayland session, frozen driver and AppImage format. The baseline AppImage is verified against release SHA256SUMS: `ecf34e4ffcfc0dcb00dc8e1e30920840ca00a03f48c97db7e5d906cc3de43a9f`. This predates the dependency candidate; the test does not establish a new dependency regression or a passing compact-handle check.
- NOT RUN: automated recording-selector input is blocked by identification of the anonymous KWin layer window, the same mapping class described in closed issue #942. Automated bar options are blocked by missing/ambiguous input controls. Both reproduce on the published nightly. The candidate's additional bar Escape recipe is likewise blocked; it is not counted as a pass.
- PASS on retry: candidate file-manager upload; its first failure screenshot visibly contains the Upload complete popup despite the detection timeout. Published-nightly focused replay passes on its first attempt.

The baseline lives under `baseline/`; it has its own exact identity, clean terminal receipts, retirement manifest and verified lease release. The LayerShellQt PR checklist remains unchecked because of the reported failure and coverage blocks. Tier 1 is still 65/65: its flows are distinct from these extra selector/control recipes. No merge, retarget or ready-for-review action was taken.

## Cleanup and evidence scope

All five candidate overlays and the additional baseline overlay were retired through guarded cleanup, preserving host-side evidence and receipts. Desktop/Proton leases were released; only the five owned VM tunnel units and their five wall entries were removed. Physical desktop tiles and unrelated entries were preserved. See `wall-cleanup.json` and the per-row lock-release/retirement records. Synthetic raw bulk artifacts and live frames remain on their builders; no golden was altered or deleted.

The setup notes record GitHub CLI provisioning and Fedora's reported offline-transaction invalidation. Checksums of every candidate package used are in `package-digests.json`. The original blocked worker summaries remain alongside the separately named verified summaries, which derive their cells from the unchanged audited terminal recipes after cleanup succeeds.
