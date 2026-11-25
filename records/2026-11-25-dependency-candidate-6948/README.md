# Dependency candidate 6948: physical-desktop checks

Tested 2026-11-25 UTC on the four physical lab desktops. Candidate commit `f1330c473081be5de0c7836a328d7a8521fd3672`, tree `57165306fe9c0191793e800dba07fedf3ea66d5f`, GitHub Actions run 45533080342. Every candidate resident reported this exact tree through `diagnostics`. No product source changed. This is a scoped dependency acceptance, not the complete release matrix.

| Row | Physical host / package | Result | Evidence |
| --- | --- | --- | --- |
| 1 | aurora-amd, Aurora Fedora 45 Plasma Wayland / AppImage | PASS | `aurora-overlay.png`, `aurora-amd-retry.log`, `aurora-amd.log`, `aurora-amd-region-pixels.jsonl` |
| 2 | m74, Mint 22.3 Cinnamon X11 / AppImage | PASS | `mint-overlay.png`, `m74-region3.log`, `m74-retry2.log`, `m74-region-pixels.jsonl` |
| 3 | k72, Kubuntu 26.04 Plasma Wayland / DEB | PASS (presigned R2) | `k72-retry.log`, `k72-r2-presigned.log`, `k72-history.png`, `k72-nightly.log` |
| 4 | f44, Fedora 44 GNOME Wayland / RPM | PASS on retry | `f44-candidate.log`, `f44-retry.log`, `f44-overlay.png`, `f44-region-pixels.jsonl`, `f44-nightly.log` |

## Observations

* Aurora: live overlay dragged a 200 × 140 region from the lab-only magenta cover. The resulting PNG was 100% magenta. The S3 destination's real keypair was saved through the Settings credential transport, the resident quit and restarted, and `setup.unlockCredentials` completed. The earlier independent session-mode S3 upload's link served byte-identical PNG data (HTTP 200). The attempted immediate post-restart upload was refused as `initializing`; the upload requirement is separately proven, not asserted on that restarted process. The unique keychain entry was deleted via the lab bridge (`ok: true`).
* Mint: initial test cover lacked sufficient visible coverage; a new run waited for the dashboard to settle, established 96.5% coverage and dragged the live region. The resulting 200 × 140 PNG was entirely magenta. Settings credential save, restart, unlock and S3 upload succeeded in the retry-two run; link HTTP 200, exact bytes. The keychain entry was deleted. The old notification banner in the overlay frame is not from the scored region capture; the operation completed and its output pixels independently matched.
* Kubuntu: AWS S3 and bucket-scoped B2 gave HTTP 200 and byte-identical PNGs. R2 upload completed in public mode but the link served 403, exactly reproduced on published nightly `v26.1124.6905-nightly` (tree `eadbbdc70f2ba5410d1778282305a7dccaf332f4`). In presigned mode the candidate's R2 link returned 200 with the exact uploaded bytes, and returned 404 after the History deletion. B2 likewise returned 404 after History deletion; the wall frame shows the R2 History item marked Deleted from destination. Public R2 reachability remains a pre-existing lab-destination failure; it is not counted as passing public-link behavior. The requested working-link check passes using the supported presigned mode. The first native attempt was a test-configuration error (omitted mandatory R2 low-speed fields), not a product outcome.
* Fedora: package-installed `putgd@put.gd` and AppIndicator were both Enabled and ACTIVE, and the lock admission verified the StatusNotifierWatcher host. First S3 upload ended `partial` (`s3_transport_unknown`, `name_head`, `Unclassified`); retry succeeded with HTTP 200 and identical PNG bytes. Published nightly 6905 also passed a single S3 upload and delete. Thus the initial transport error was not persistent, but its cause is unproven. The retry's region capture produced a 200 × 140 entirely magenta image. The initial cover was obscured, so no first-attempt region claim was made.

All uploads used newly generated synthetic PNGs and unique isolated acceptance prefixes. Every successful upload was deleted using the prepared exact History ID, destination receipt, effect and acknowledgement. S3 CDN links remained temporarily available after delete; the independent S3 list checks show all run prefixes empty, rather than treating the cached GET as a failed deletion. All exported images were inspected; evidence exact-value scans performed on the builders reported zero matching secret values. The diagnostic logs contain build identities, states, receipt IDs and HTTP results, not links or secret values.

## Package hashes (SHA-256)

* Candidate AppImage: `998e7d0a77625366e34c1be0249cc970f1b0d44cc081cc864f9f0db7a7dfe164`
* Candidate Ubuntu 26.04 DEB: `d44f43c8e974d46227e40d0aabe76d9680b2208c88ff7e0c1c87bd79e130a7f4`
* Candidate Fedora 44 RPM: `6ed1f2f94d08573001cdca50f8c70c54a03687ffbdf4d9885e7a0c933b49d545`
* Nightly comparison DEB and RPM: both checked OK against that release's SHA256SUMS.

## Cleanup

All four lab desktop release checks passed, and all leases were released before 03:08 UTC. Aurora had no native package installed before or after. Mint's existing DEB was left untouched. Kubuntu and Fedora were restored to the acquire-time `26.1122.6439~nightly` and `26.1122.6439~nightly-1.fc44`, respectively. No compositor packages were changed. Fedora's package transaction reported that it invalidated an existing pending dnf5daemon-server offline transaction; the previous put.gd package was restored but that pending system transaction was not rescheduled. Private per-run profile and failed-attempt evidence remain in the dedicated host work directories, not the default profiles. Uploads necessarily use the normal automatic clipboard behavior.

## Significant commands

* `git fetch origin && git switch --detach origin/candidate/deps-20261125 && git rev-parse HEAD HEAD^{tree}` — verified pinned source.
* `gh run download 45533080342 -R patrick-hudson/put.gd-desktop -n release-appimage -n release-native-ubuntu26.04 -n release-native-fedora44` — downloaded candidate artifacts.
* `gh release download v26.1122.6439-nightly ...` — downloaded exact rollback DEB/RPM.
* `gh release download v26.1124.6905-nightly ...`; `sha256sum --ignore-missing -c SHA256SUMS` — downloaded and verified comparison release packages.
* Pinned SSH and SCP to the dedicated `~/work/tmp/dp6948` directories — staged only candidate, rollback, comparison packages and lab drivers.
* `python3 tools/lab/desktop_lock.py status ... --check` — preflight and final cleanup inventory.
* `desktop_lock.py run aurora-amd ... --release -- bash .../row.sh` then `retry.sh` — native AppImage overlay, Settings save/unlock, S3 checks.
* `desktop_lock.py run m74 ... --release -- bash .../row.sh`, `retry.sh`, `retry2.sh`, `region-only.sh` — native X11 retries and S3/keychain checks.
* `sudo -n apt-get -s --no-install-recommends ... install ./candidate.deb`; `sudo -n apt-get -y --no-install-recommends ...` — inspected and applied scoped package transactions; ran native probes.
* `desktop_lock.py run k72 ... native2.sh`, `native3.sh`, `nightly-r2.sh` — S3/B2/R2 public and presigned checks; comparison public link; restored baseline DEB.
* `desktop_lock.py run f44 ...` — initial lock refused while #2000 owned it; successfully acquired after that session released.
* `sudo -n dnf --assumeno --setopt=install_weak_deps=False install ./candidate.rpm`; `sudo -n dnf -y --setopt=install_weak_deps=False install ...` — inspected and applied scoped RPM transaction.
* `gnome-extensions info putgd@put.gd`; `gnome-extensions info appindicatorsupport@rgcjonas.gmail.com` — both ACTIVE.
* `desktop_lock.py run f44 ... row.sh`, `f44-retry.sh`, `nightly-f44.sh` — candidate and published-nightly native tests; inspected downgrade transaction and restored original RPM.
* Session socket calls: `capabilities`, `diagnostics`, `settings.get`, `settings.patch`, `action.invoke`, `operation.inspect`, `setup.storeCredentials`, `setup.unlockCredentials`, `upload.files`, `history.list`, `history.detail`, `delete.prepare`, `delete.confirm`, `delete.inspect`, `ui.show`, `ui.quit`.
* RFB frame captures and independent image pixel reads; independent unauthenticated HTTP GET byte hashes; boto3 `list_objects_v2` restricted to unique run prefixes; exact credential-value scan of export files in memory on each builder.
* `python3 tools/lab/desktop_lock.py status aurora-amd m74 k72 f44 --check` — final inventory and package restoration verification.
