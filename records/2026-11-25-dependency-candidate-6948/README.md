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
* Kubuntu: AWS S3 and bucket-scoped B2 gave HTTP 200 and byte-identical PNGs. R2 upload completed in public mode but the link served 403, exactly reproduced on published nightly `v26.1124.6905-nightly` (tree `eadbbdc70f2ba5410d1778282305a7dccaf332f4`). In presigned mode the candidate's R2 link returned 200 with the exact uploaded bytes, and returned 404 after the History deletion. B2 likewise returned 404 after History deletion; the wall frame shows the R2 History item marked Deleted from destination. The 403 was reproduced with the original probe on nightly, but the follow-up below establishes that it was caused by the probe’s default Python-urllib User-Agent, not public R2 reachability or put.gd. Candidate public-link behavior passed the browser-UA retest on m74. The k72 presigned-mode check was also successful. The first native attempt was a test-configuration error (omitted mandatory R2 low-speed fields), not a product outcome.
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

## Follow-up: alternating AppImage S3 transport check

Ran both exact AppImages on f44 headlessly, using two private HOME/XDG roots, separate non-activating session buses, and offscreen Qt. No desktop lock or desktop interaction, no keychain access, and no changes to the installed RPM. Both resolved session socket paths were 58 UTF-8 bytes. Candidate AppImage SHA-256: `998e7d0a77625366e34c1be0249cc970f1b0d44cc081cc864f9f0db7a7dfe164`; published nightly AppImage SHA-256: `42bc3c872a473fba31d2caf73b6c1f45a07a093decec448ca7fd2b4be3eb931a` (verified against the release checksum). Both residents' running `diagnostics.build.gitTree` identities were checked before uploads.

| Build | Attempts | Upload completed | HTTP 200, exact PNG bytes | History delete removed | S3 transport failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Candidate 26.1125.6948 | 20 | 20 | 20 | 20 | 0 |
| Nightly 26.1124.6905 | 20 | 20 | 20 | 20 | 0 |

The exact order in `f44-s3-repeat.log` is candidate, nightly, repeated twenty times with new synthetic payloads. Each attempt waited for its upload, fetched the direct link, and completed the History deletion before the next attempt. Each line has an attempt/build/order, operation and history IDs, terminal state, error code and phase, restricted diagnostic fields, link byte check, and deletion state. All upload failure codes were null and phases `completed`. On both builds, the History record also carried the nonfatal `source_unsupported` diagnostic from the unavailable headless desktop adapter (the link-copy path; `UnavailableSource::copy` in `OperationService.cpp`); this did not prevent successful upload, HTTP GET or deletion. No SDK/CRT/curl transport errors were emitted for any scored upload. The test did not trigger the requested conditional 10+10 S3 run on k72 because the candidate had no recurrence of `s3_transport_unknown`.

Judgment: no observed evidence of an AWS SDK regression in this alternating sample. The earlier single Fedora RPM `name_head` transport error is not reproduced in either AppImage and its cause is not established; this sample cannot prove that a low-frequency transport fault is absent or that it occurs on both builds. Both S3 prefixes were independently listed empty. The residents exited 0, their sockets disappeared, and the exact-value evidence audit found zero matches. The quiet lease released at 03:14:03 UTC; installed RPM remained `26.1122.6439~nightly-1.fc44`.

## Follow-up: R2 public link User-Agent correction

The k72 quiet lease was held by a separate full-suite stress campaign, so its acquire was refused and no test command or package installation ran there (`k72-r2-public-ua.log`). The coordinator directed the same one-shot test to m74 using the exact candidate AppImage, headlessly under a quiet lease. Both HTTP requests used the very same public link produced by put.gd, with only the User-Agent changed.

| Request | Result |
| --- | --- |
| Upload in public mode | completed |
| Default Python-urllib User-Agent | HTTP 403 |
| Firefox User-Agent | HTTP 200, exact uploaded PNG bytes |
| History delete | removed |
| Firefox User-Agent after delete | HTTP 404 |
| Independent scoped R2 prefix listing | empty |

**Correction to the initial record:** the previous R2 public-link 403 was the probe’s User-Agent, not a candidate regression, not disabled public access, and not a put.gd upload error. The m74 result directly demonstrates the probe difference on the same newly uploaded object. `m74-r2-public-ua.log` contains the diagnostic build identity, exact item and operation IDs, and HTTP witnesses, without any link or credential. Resident exit was 0, socket disappeared, zero credential-value matches, quiet lease released 03:14:09 UTC, pre-existing Mint DEB unchanged.

Significant follow-up commands:

* `gh release download v26.1124.6905-nightly -R patrick-hudson/put.gd-desktop -p '*x86_64.AppImage'`; `sha256sum -c --ignore-missing SHA256SUMS` — downloaded and verified comparison AppImage.
* Pinned BatchMode SSH/SCP — staged candidate/nightly AppImages and private-session test driver on f44, and candidate AppImage and R2 driver on m74; candidate hash checked on each builder.
* `python3 tools/lab/desktop_lock.py run f44 --resource quiet --owner codex --session deps6948-repeat-f44 --minutes 15 --release -- ... python3 repeat.py ... f44 20` — alternating upload/delete campaign, independent prefix check, exact secret-value audit.
* `python3 tools/lab/desktop_lock.py run k72 --resource quiet ...` — refused because another session held the lease, no test executed.
* `python3 tools/lab/desktop_lock.py run m74 --resource quiet --owner codex --session deps6948-r2ua-m74 --minutes 10 --release -- ... python3 r2-public.py ... m74 1` — public R2 upload, two-UA check, History delete and second browser-UA GET.
* `python3 tools/lab/desktop_lock.py status f44 m74 --resource quiet` — both free.
