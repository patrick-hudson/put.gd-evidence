# S3 expiring links and History renewal — issue #1365

Feature acceptance passed for code PR [#1366](https://github.com/patrick-hudson/put.gd-desktop/pull/1366), head `d0893278229dad138f55521b9ae6bf59dc2886d8`, version `26.1109.4410-dev+gd0893278229d`. Documentation is separate in [#1367](https://github.com/patrick-hudson/put.gd-desktop/pull/1367). No merge was performed.

Required [PR CI](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42722893045) and the [complete package workflow](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42722899262) passed at that exact code head. The local S3 SigV4 oracle, S3 worker/protocol, B2 identity/renewal, History persistence, configuration, CLI/MCP, GUI and redaction tests run in CI. Selected job results are retained in `data/ci-*.json`. Development also passed the production MCP helper's seven integration tests, ten configuration tests, the 199-state catalog/control map and 28-state secret inventory on Debian builder d69. Those development checks are distinguished from native package acceptance below.

## Exact packages and desktops

All after pictures and final functional checks use those CI packages. Before pictures use round-start nightly `32a9a763e3502e0bf26db88def6140a7e250bbb4`, version `26.1109.4404-dev+g32a9a763e350`, Debian package from CI `42706400392` on d69's physical Plasma/Wayland desktop.

| Target | Package | Native session / run | Final AWS checks |
| --- | --- | --- | --- |
| m74, Linux Mint 22.3, Cinnamon 6.6.9, X11 | Ubuntu 24.04 DEB | c89; shell 625683; boot `4ba460ee-1af9-4ae8-b832-d1c54cdb642f` | Test connection, upload, expiry, explicit saved-keychain unlock and MCP refresh, real clipboard, deletion |
| f44, Fedora 44, GNOME Shell 50.6, Wayland | Fedora RPM, installed for native acceptance | 8926; shell 3035140; boot `06940f74-cbcc-4acf-8214-6d7fc5146ec6` | Test connection, upload, expiry, MCP refresh after changing current destination, deletion |
| k72, Kubuntu 26.04.1, Plasma 6.6.6, Wayland | Ubuntu 26.04 DEB | 509; shell 3440893; boot `a4df139d-cadf-4e3e-845a-151648c295c3` | Same AWS cycle, including real clipboard copy |
| d69 guest b365, Fedora 45 Budgie on labwc, Wayland | AppImage | `fa3f40a8-33e8-42f9-bbd9-60b20e55f2a2` | Same AWS cycle, native Settings/History and real MCP copy |
| d69 guest h365, Omarchy 4.5.0 / Hyprland, Wayland | AppImage | `5ed380bc-2195-46eb-af43-e3fe07213b23` | Same AWS cycle, native Settings/History and real MCP copy |

The five Settings/History sets are in `pictures/`; `data/*-public-facts.json` records actual source, resident and session identities. Native desktops and both VM displays stayed on the visible wall throughout testing. The VMs used fresh overlays of these immutable goldens:

- Budgie SHA-256 `a6749512438d507ef2b2c47fe675955627464d9a5a85341002f91cd54fb401ad`.
- Omarchy SHA-256 `bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256`.

Package SHA-256:

| Package | SHA-256 |
| --- | --- |
| Ubuntu 24.04 DEB | `17abc3b65cf375ee13af6d51a096d1ebe514c9381f949ce3f9a44479c90bd9d0` |
| Ubuntu 26.04 DEB | `b11e961a7140036e55d19b71757b8d526b6779617604b78e7a1d7c448a1ec39d` |
| Debian DEB | `af5cf366d7acc34d93f7c7652d3872ff290f5028fddb2d9aa184e0633e281a46` |
| Fedora RPM | `feb0e3175215573b18f34aff2a892814ccb22ed2b4f675b36f905246ef295e81` |
| AppImage | `af752743688b3df9cc4737e359b03c94fac606a6346805d9f87d428ca9e612df` |

## Live service results

Synthetic PNGs and unique `acceptance/i1365-…` object prefixes were used. No bucket policy, versioning or existing user object was changed. Credentials stayed on the builders in protected inputs and memory.

| Service | Signed GET | Unsigned GET | Actual short link after expiry | History renewal | After guarded deletion |
| --- | --- | --- | --- | --- | --- |
| AWS S3 | 200, exact uploaded PNG | 403 | 403 | 200, new URL/expiry | 404 |
| Cloudflare R2 | 200, exact uploaded PNG | 400, structured InvalidArgument naming Authorization | 403 | 200, new URL/expiry | 404 |
| Backblaze B2 | 200 | 200: existing test bucket is public | 401 | 200, new authorized URL/expiry | 404 |

AWS ran on all five desktops. R2 and B2 ran on Cinnamon with the same CI head; see `data/cinnamon-{aws,r2,b2}-result.json`. The normal Test connection passed in presigned mode on each desktop and on R2; B2's authorized-mode connection test passed too. The Cinnamon picture shows the real **Test upload and link** button's result.

Three-second credentials were created only by the external live driver, then verified as working and subsequently refused. Only the disposable History row's URL and expiry were set to that actual expired test link; its object identity, publication, destination and credential reference were preserved. No short validity is reachable through product settings, the schema, CLI or MCP.

Cinnamon exercised AWS, R2 and B2 with saved keychain credentials, removed the current profile, restarted with startup unlock disabled, and proved copy refused with `credential_setup_required` while showing **Unlock saved credentials**. The real MCP `unlock_history_link_credentials` followed by a separate `copy_history_link` succeeded using the receipt's original reference. It neither used the current profile nor uploaded again. The actual desktop clipboard equalled the renewed link. All other receipt fields remained equal. B2 also passed a direct **Refresh and copy link** button run. CI verifies B2 refuses renewal if the filename now serves a replacement version and issues no token in that case.

The AWS run compared its working URL, expired URL, renewed URL and signing query values against every member of a diagnostics ZIP and the resident logs: none were present. Raw History and operation/destination-test journals remain private because they can contain bearer receipts.

## Browser and pictures

Cinnamon's real configured default Firefox loaded the AWS and R2 objects visibly at their original 900×540 size. `browser-aws.png` and `browser-r2.png` retain browser chrome; a labelled privacy cover concealed the address row before frame capture. No default handler was changed in that run.

A further GNOME run exercised the production MCP `open_history_link` for both services: both returned `opened:true`, `route:portal`; the guarded real Firefox received the exact receipt URL and loaded the PNG. `data/product-browser-results.json` retains the safe results. The existing lab browser fixture temporarily directs both native and isolated MIME profiles to the same real Firefox with a disposable private profile and restores the original files byte for byte. It reported zero foreign browsers. `history-open-aws.png` shows the actual native kiosk browser after the AWS handoff; the hidden address bar never entered a saved frame. R2's attempted handoff picture was rejected because put.gd remained in the foreground; the accepted R2 visual is the Cinnamon Firefox capture. No personal Firefox profile received a test link. Both additional objects were removed and returned 404.

Annotations and crops were drawn through put.gd's production image editor via its MCP helper. The final small crop of the already-recorded browser frame used the same CI editor offscreen on a builder; it is an edit of native evidence, not an offscreen desktop claim. Cinnamon History/150% crops exclude a stale desktop notification from their top chrome; GNOME window crops remove wallpaper. Originals are retained privately. Each embedded PR picture has a change called out inside it. `s3-form-100.png` and `s3-form-150.png` show the mode, validity and endpoint/temporary-credential notes. No working bearer query is visible in any published picture.

Before: the S3 form offered public URL/ACL controls; on the live private bucket its unsigned History URL returned 403. B2's expired authorized URL still copied and returned 401. After: History shows expiry, offers refresh and stores a fresh working URL for both providers.

## Post-use memory observation

Each desktop was observed with the unchanged `bench_ui_process.py` for 180 seconds / 37 samples after functional use and closing its windows. Every run passed, ended with one resident and zero UI/escaped processes, and was checked for absence of resident Qt Network, SSL, AWS, GTK and KDE library maps.

| Desktop | Final RSS MB | Final PSS MB | Peak sampled RSS MB |
| --- | ---: | ---: | ---: |
| Cinnamon | 9.51 | 6.25 | 20.27 |
| GNOME | 12.36 | 8.37 | 17.75 |
| KDE | 13.24 | 7.44 | 13.24 |
| Budgie | 10.92 | 8.37 | 15.95 |
| Hyprland | 12.31 | 10.33 | 17.82 |

MB uses 1024×1024 bytes. Full reports are `data/*-memory-results.json`. These are sampled post-use diagnostics, not a cold-idle release-budget, leak, CPU-budget or rendered-tray claim. A complete release campaign was not run for this feature PR.

## Failures, corrections and cleanup

An earlier green head `1b309c25447a` clipped a long expiry date on Cinnamon. Its failed image and package identities were retained; the label now wraps, and all final desktop checks and pictures were retaken at d089. An expired-link summary found during catalog review was also corrected before final acceptance. B2's filename/version guard was added and tested before this head.

GNOME initially had no installed put.gd extension. The exact CI RPM was installed normally; an inspected, empty desktop was restarted through GDM to load extension 19. Its first AWS connection tests encountered real TLS failures (a bounded status-only probe observed curl code35). A later uninstrumented run passed. The failed cleanup journal's exact synthetic targets were checked: three objects were already absent, one matching publication/ETag was conditionally deleted, and three multipart uploads were aborted or already absent. A journal inspection accidentally included URL fields in tool output; output was stopped and all recorded targets were removed, making those links unusable. No such URLs are in this record.

GNOME's first memory attempt correctly refused a missing tray. Its existing AppIndicator extension was enabled for the successful observation and restored to its original disabled state afterwards. The temporary RPM was removed with `--noautoremove` before lease release. DNF noted a pre-existing downloaded offline-update transaction; read-only status still reported download-complete. No offline update, reboot for updates or rescheduling was performed. The later extracted-RPM browser attempt required the package's bundled SDK directory on its library search path; the first failed preflight had no upload journal, object reference or direct URL, and no remote mutation. That driver correction required no rebuild.

All synthetic History objects were removed with guarded deletion, all three fresh Cinnamon keychain references were removed, test clipboard content was cleared, and owned app/browser/helper processes stopped. Both VM evidence archives were exported and checksum-verified before guarded overlay retirement. Only their disposable disks were removed; goldens were preserved. Cleanup receipts are `data/*-overlay-cleanup.json`. The two wall entries and tunnel units were removed. Desktop leases were released: KDE 00:18:25, GNOME 00:28:58, Cinnamon 00:29:55, final GNOME browser slot 00:35:57 UTC on November 10. Other lanes' leases/processes were left alone; no new issue was filed.

Scratch source, test drivers, failed attempts, package assets and private evidence are archived on d69/f44/k72/m74 under `~/work/putgd-archives/2026-11-09-1365/`. Each `RESTORE.json` maps historical source paths and verifies its private temporary-evidence archive; copies are in `data/*-archive-index.json`. Original temporary directories remain private until normal host cleanup. Process sweeps across all five builders found no remaining owned candidates. No workstation build, test, image encoding or VM was run.
