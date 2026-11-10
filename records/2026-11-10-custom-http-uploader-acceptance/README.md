# Custom HTTP uploader: final package acceptance and PR pictures

Issue [#1361](https://github.com/patrick-hudson/put.gd-desktop/issues/1361), code [PR #1371](https://github.com/patrick-hudson/put.gd-desktop/pull/1371), docs [PR #1375](https://github.com/patrick-hudson/put.gd-desktop/pull/1375). Acceptance worker: Sol. Observed 2026-11-10 UTC. All five required desktops passed the feature campaign below. No product changes were made by the acceptance worker.

## Build identity

Final packages are from green [CI run 42755553182](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42755553182). PR head is `2d19d7181ac231a3004abab69c453e20d44635c7`; the packages actually build merge `d23382b99c030f96120de10803fc5936eb0ac346`, tree `7a5cc3062c3a4a3461341c0adcb8af84c2d6a4da`, merging that head with nightly `7fc609dc4`. Version: `26.1110.4465~dev+gd23382b99c03` (AppImage uses `4465-dev`). The additional nightly changes include #1378, #1380 and #1382; they do not change this feature's files. Both identities matter: these pictures show the accepted combined package tree, not a development build of the PR head alone.

Earlier provisional checks used head `72d41fd6fcc744078593316754ef791c90ca0ac7`, CI `42739906940`, merge `98e7ed9190e28a93c8fcfd9b5183c9b548fee979`, tree `be8cbd029b410c98dac04ac917e1387796f73696`, version `26.1110.4433~dev+g98e7ed9190e2`. Mint, Fedora and Kubuntu packages were extracted to private roots on their physical desktops; Budgie and Hyprland used fresh guests. These provisional runs exercised all three receiver files through native file choosers. Fedora's provisional physical run inherited extension 21; the final fresh Fedora guest instead loaded the tested RPM's extension 19 after login. Final packages supersede those provisional results. Package hashes for both builds and final embedded build-info are in [builds](builds/).

## Results

All final guests were fresh disposable KVM overlays on builders, visible throughout on the workstation display wall. Mint, Fedora and Kubuntu had their distribution package genuinely installed. Budgie and Hyprland used the published AppImage with its bundled Qt runtime. No workstation VM or C++ application build was used.

| Desktop | Final host/run, session | Package, loaded Qt | Result and scope |
|---|---|---|---|
| Cinnamon | m74/c1, Mint 22.3 Cinnamon 6.6.4, X11 | Ubuntu 24.04 DEB 4465, Qt 6.4.2 | PASS: common campaign, gnome-keyring restart/explicit unlock, native shortcut refusal; 10 installed-resident MCP cases; full PR pictures. [Results](results/c1/) |
| GNOME | f44/g1, Fedora 44 GNOME 50, Wayland; packaged extension 19 active after login | Fedora RPM 4465, Qt 6.11.2 | PASS: common campaign, gnome-keyring restart/explicit unlock and shortcut refusal; final security checks below. [Results](results/g1/) |
| KDE Plasma | k72/k1, Kubuntu 26.04 Plasma 6.6.6, Wayland | Ubuntu 26.04 DEB 4465, Qt 6.10.2 | PASS: common campaign, KWallet/ksecretd restart/explicit unlock, native shortcut refusal. [Results](results/k1/) |
| Budgie | d69/b2, Fedora 45 Budgie 10.10.3 on labwc 0.20.2, Wayland | AppImage 4465, Qt 6.12.0 | PASS: common campaign and session credentials unavailable after restart. Keychain mode and MCP suite were not run on this desktop. [Results](results/b2/) |
| Hyprland | d69/h2, Omarchy 4.5 / Hyprland 0.56.2, Wayland | AppImage 4465, Qt 6.12.0 | PASS: common campaign and session credentials unavailable after restart. Keychain mode and MCP suite were not run on this desktop. [Results](results/h2/) |

The common final campaign imported each of Zipline, Chibisafe and XBackBone's own web-generated SXCU files into session storage, checked ready/stored hints, ran Test connection for each, captured and uploaded a real desktop screenshot to each, and compared each copied link to History. One actual capture per desktop was opened from History in a real default browser using an isolated browser profile. XBackBone deletion was prepared and confirmed through History and checked remotely as HTTP 404. Zipline and Chibisafe provide no deletion URL; their unavailable deletion state is expected. All receiver objects were ultimately purged with the disposable receiver pods.

Per coordinator, final Settings regression coverage repeated the destination form and at least one native chooser import on every desktop (Chibisafe; GNOME also XBackBone); all three native chooser imports had already been exercised on each desktop with provisional build 4433. Other final receiver imports used the production CLI/session API. The published token-search reports show actual receiver values absent from config/data/history, state/logs, Settings snapshots and every decompressed diagnostics member, including checks after the final native chooser imports. The receiver-suite search is after its three imports, rather than a separate persisted report after each individual API import. No raw SXCU, diagnostic archive or credential-bearing fixture record is published.

Every final desktop also passed plain-HTTP import refusal until explicit opt-in, URLShortener rejection, concurrent-import busy, stored-but-lost reply / cut reply / server-500 unknown outcomes, explicit-resend duplicate notice and an additional stored copy only after retry, credential echo rejection without recording/copying its URL, cross-host secret-bearing deletion URL discarded with an explanation, and an ordinary stored word (`screenshots`) legitimately appearing in a recorded/copied link. See each `refusals-and-last-fixes.json`.

On Cinnamon/GNOME/KDE, all three receiver values were stored in the guest's own real system keychain. After disabling startup unlock, quitting and restarting, credentials were unavailable and an actual configured capture/upload shortcut refused with `credential_setup_required`; credential generation stayed zero. Explicit `setup.unlockCredentials` then enabled uploads/captures. Upload did not implicitly unlock the keychain. All nine exact receiver references were removed by attributes; the cleanup reports show none remaining. These were guest session buses, not the builders' desktop keyrings.

Additional GNOME checks: a remote request returning `http://fedora:...`, where `fedora` resolved to this guest's own IPv6 addresses, had its returned-address fetch refused with “it points at this computer”; returned plain HTTP was also refused when its opt-in was off. These demonstrate fetch refusal, not a claim that the DNS-local URL was never present in Test connection's result. A keychain reference already owned by another destination was rejected. An unanswered native keychain prompt timed out after 119.8 seconds and a later session import succeeded while that prompt was still pending; the temporary owned collection was removed. [Reports](results/g1/).

The official SDK 2.3.0 MCP helper forwarded to the installed Mint resident for ten custom-uploader cases, including import/schema, stored hints, Settings form, Test connection, upload/prepared deletion, unknown outcome/no automatic resend, explicit retry and diagnostics in both naming modes. [MCP report](results/mcp-native-cinnamon.json). MCP was not repeated on the other final desktops; provisional Plasma had nine MCP cases. Parser/body/template/encoded-value coverage comes from green CI and the separately labelled implementer test report, not five desktop walkthroughs of every parser branch.

## Pictures and captions

All 21 images contain callouts made in put.gd's own native image editor through its MCP helper. The editor was the installed Mint final DEB, with MCP output schemas validated; see [annotation report](results/annotation-results.json). Images are cropped to the owned application, browser or log surface. No token, deletion key or keyring password is visible. Final GUI functional checks ran at 100%; 150% pictures check form layout only.

Except the explicit baseline and mixed test panel, each caption below refers to **installed Ubuntu 24.04 DEB `26.1110.4465~dev+gd23382b99c03`, PR head `2d19d7181`, package merge `d23382b99`, Mint/Cinnamon X11, loaded Qt 6.4.2**. The baseline is **Ubuntu 24.04 DEB `26.1109.4404~dev+g32a9a763e350`, nightly `32a9a763e3502e0bf26db88def6140a7e250bbb4`, same Mint guest, Qt 6.4.2**. The test panel labels its two distinct sources inside the image.

- [00-before-add-destination.png](pictures/00-before-add-destination.png): Before: the round-start nightly Add destination menu has the three existing destination types. Baseline DEB 4404 / nightly 32a9a763e350 / Qt 6.4.2.
- [01-add-destination-menu.png](pictures/01-add-destination-menu.png): After: Custom HTTP uploader is available in Add destination. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [02-new-custom-uploader.png](pictures/02-new-custom-uploader.png): The new custom uploader form and its explicit plain HTTP control. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [03-import-dialog.png](pictures/03-import-dialog.png): Import a ShareX .sxcu file or paste its contents. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [04-imported-plain-http-refused.png](pictures/04-imported-plain-http-refused.png): An imported lab HTTP destination is refused until its own plain HTTP switch is enabled. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [04b-imported-plain-http-allowed.png](pictures/04b-imported-plain-http-allowed.png): The per-destination plain HTTP opt-in enables this lab destination. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [05-imported-fields-masked.png](pictures/05-imported-fields-masked.png): Imported values are masked, with the form showing the parsed request and response fields. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [06-stored-masked.png](pictures/06-stored-masked.png): Stored credentials appear as references and masked values. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [07-test-connection-result.png](pictures/07-test-connection-result.png): Test connection against the real XBackBone receiver succeeds and removes its test object. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [08-history-uploaded.png](pictures/08-history-uploaded.png): History records an upload to the real receiver. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [09-browser-shows-upload.png](pictures/09-browser-shows-upload.png): The real default Firefox browser displays the uploaded synthetic image opened from History. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [10-prepared-deletion.png](pictures/10-prepared-deletion.png): History prepares deletion with the exact upload and receiver. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [11-history-deleted.png](pictures/11-history-deleted.png): Deletion completes and the receiver no longer serves the object. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [12-retry-may-duplicate.png](pictures/12-retry-may-duplicate.png): A lost reply is unknown and the explicit resend notice warns about duplicates. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [13-after-retry.png](pictures/13-after-retry.png): Explicit retry is a separate attempt; an earlier unknown outcome remains visible. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [14-no-deletion-url.png](pictures/14-no-deletion-url.png): When the receiver returns no deletion URL, deletion is unavailable with an explanation. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [15-test-suites.png](pictures/15-test-suites.png): Installed Mint DEB receiver results plus the implementer's separately identified m74 development-build CTest report (221 rows, 76 cases). The CTest portion is not package desktop evidence. Mint CI DEB 4465 / merge d23382b99 / Qt 6.4.2 receiver report; m74 DEV head 2d19d7181 CTest.
- [16-link-holds-stored-value.png](pictures/16-link-holds-stored-value.png): A response link containing the upload token is refused; no link is recorded or copied, and History explains why. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [17-deletion-url-not-kept.png](pictures/17-deletion-url-not-kept.png): A deletion URL carrying a stored value to another host is discarded; History explains why and offers no Delete action. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 100%.
- [18-form-150.png](pictures/18-form-150.png): The new destination form at 150% scale. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 150%.
- [19-import-150.png](pictures/19-import-150.png): The filled imported form and plain HTTP refusal at 150% scale. Mint DEB 4465 / PR 2d19d7181 / merge d23382b99 / Qt 6.4.2; 150%.

Supplemental real-browser and prepared-deletion screenshots for the other desktops are under their results folders. The Cinnamon `browser-captured-object.png` is the retained, already-loaded real captured object; it was focused for the saved visual after receiver teardown, without claiming a new network fetch then. The pictured browser in 09 was captured during the live receiver run.

## Corrections and limits

No product defect requiring an acceptance-worker patch was found. Failed harness attempts were preserved privately before correction: startup `initializing`, native chooser location versus file-row selection, a stale guest SSH pin, a missing guest clipboard utility, a History refresh selection race, SDK-version mismatch, and the inherited GNOME extension. Full private logs, raw visuals, diagnostics and source are retained outside the public record.

One procedural error: the worker initially ran `uv sync --locked` for the editable Python MCP helper on the workstation, contrary to the round's no-packaging rule. That environment and its generated caches were removed; all remaining helper setup ran on m74. This was a Python helper setup, not a C++ build, CTest run or workstation VM. The failed attempt and removal receipt are retained.

Budgie/Hyprland keychain mode was not required and was not run. The final MCP suite ran on Cinnamon only. The Debian DEB and Arch package were produced by CI but not selected for these five desktop runs. This campaign does not assert hardware-specific release gates or general recording/editor acceptance.

## Cleanup

Every guest's evidence was exported and checksum-verified before guarded overlay retirement; all five final retirement receipts are in [cleanup](cleanup/). Earlier provisional Budgie/Hyprland overlays were also retired. Owned VNC tunnels and wall entries are gone; no owned app, fixture, VM or tunnel remains. Physical desktop leases were released after their provisional cleanup; final runs needed no physical lease. Other sessions' processes and leases were preserved.

On aurora-amd, `receivers.py down --purge` removed all three receiver pods and managed scratch; the clean `i1361-git` source checkout and existing `putgd-build` Toolbx were preserved. Actual receiver SXCU copies and full environment snapshots were removed by exact path from builders. Remaining private evidence/source was moved out of active scratch roots into `~/work/putgd-acceptance-1361-archive/{pre-final,final}` on each builder. Immutable goldens were untouched. See per-builder sweeps and receiver teardown receipt.

The final runtime inventory found an unattributed, empty uv lock under `/tmp/m1361a` on f44. It has no app/socket/VM and was preserved rather than deleting another worker's possible scratch. No owned runtime scratch remained.
