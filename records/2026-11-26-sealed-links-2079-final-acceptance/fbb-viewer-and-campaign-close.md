# Final viewer retest and campaign closure

CI run 45798745702, PR head fbb648aa1e66de2a7be21430a2cb86497acf18e2.
Downloaded Debian package 26.1126.7194~dev+gc4a09e043e41, reported resident
26.1126.7194-dev+gc4a09e043e41, CI merge commit
c4a09e043e416d18209608df5596a8ad03250b0b, gitTree
3324764b9dcface79778bdf8b02e8f4ea26ef905 matches the exact PR head.
Viewer pin at this head:
1074b3e648dd82fda2f186e8ac61e1d4bfcc2b993b1766e88eba1503e4680f82.
No local product builds or product changes. Native Debian Plasma Wayland,
official Google Chrome 158.0.8127.88 and Firefox ESR 153.5.0esr.

## Four viewer rows and fallback

| Row | Result | Observed |
|---|---|---|
| Chrome normal, 1 GB | PASS | Fresh fbb split page, actual History portal, video plays at 0:03 and 0:09 of 1:40; different frames. Previous exact e910 page on the same Chrome was blank at 0:00 even after Play. |
| Chrome fallback, same link | PASS | Fresh incognito profile through actual History portal. Exact message about too large for browser, Save to file button, no video player or Download link. Click opened native KDE save dialog, chose isolated file, viewer said Saved. Exact file size and original SHA. |
| Chrome headless fallback | PASS (supplemental) | Fresh official Chrome headless profile, screenshot after 60 seconds real time using local browser diagnostics; exact message and button. The initial CLI screenshot command completed in 0.9 seconds using virtual time, so the delayed capture is the decisive witness. |
| Firefox, same 1 GB link | PASS | Actual History portal, native profile player 0:04 of 1:40 and subsequent distinct frame. |
| Chrome small | PASS | Fresh inline 2400×1600 PNG displays correctly, decrypted message. |
| Firefox small / zoom | PASS | Same inline PNG, clicked image toggled display from fit to full-size; distinct screenshots show doubled band heights and zoom-out pointer. |
| CLI integrity | PASS | Fresh fbb inline and split pages accepted by the pinned CLI; original SHA matched in both. |

The same moving H.264 fixture was used for e910 and fbb: 1,061,463,118 bytes,
100 seconds, SHA-256 baade7cf41e68b458c6c904a2208286663677c8774e2755ad806182069b2d3d3.
The Chrome incognito Save file had exactly the same size and hash. The
normal-profile result is a positive improvement, not failure to trigger the
conditional fallback; the incognito result independently exercises the real
fallback workflow.

First fbb small-image run completed both browser witnesses and terminal
History deletion. Its SSH transport then exited 143 during the next large
operation; the tester canceled only that exact operation, the resident
exited, independent origin listing verified zero current objects and
versions. Fresh large-only run redirected its harness results to a durable
remote log; transport also later exited 143, but the native resident and
script completed all requested browser checks and terminal History deletion.
That prefix's two objects were gone, with sealDataStatus removed. These were
harness transport interruptions, not demonstrated application failures.

## New picture captions

All annotated pictures below were marked with the installed fbb put.gd
editor's actual editor.apply rectangles/arrows and editor.saveCopy.
The initial and earlier UI pictures retain the build captions in README.md
and native-desktop-witnesses.md; no claim that those pictures were taken
on fbb. Screenshots exclude address bars, key fragments and credentials.

| Picture | Build shown | Caption |
|---|---|---|
| annotated/chrome-large-before.png | e910 26.1126.7192-dev+gf977a6911c14 | Fresh same-size S3 sealed page, black 0:00 player after Play |
| annotated/chrome-large-after.png | fbb 26.1126.7194-dev+gc4a09e043e41 | Same original 1 GB newly uploaded, Chrome normal profile playing at 0:09 / 1:40 |
| annotated/chrome-large-fallback.png | fbb | Chrome fresh incognito, message and Save to file button |
| annotated/chrome-large-saved.png | fbb | Same incognito page reports Saved after native file chooser; exact SHA proven |
| fbb-chrome-split-play1.png and fbb-chrome-split-play2.png | fbb | Normal-profile Chrome actual distinct playback frames |
| fbb-firefox-split-play1.png and fbb-firefox-split-play2.png | fbb | Firefox actual distinct playback frames |
| fbb-chrome-small-inline.png | fbb | Chrome inline PNG regression check |
| fbb-firefox-image-fit.png and fbb-firefox-image-zoom.png | fbb | Firefox fit and native full-size zoom |
| fbb-save-dialog-safe-crop.png | fbb | Native Save dialog's filename and save controls; safe footer crop only |
| fbb-headless-fallback-final.png | fbb | Official Chrome headless, actual 60-second delayed screenshot of same fallback |

## Final acceptance matrix (campaign, not a blanket claim on untested revisions)

Earlier native desktop results (1ba3aa6b) and provider/large results
(e910ab33) were accepted by the coordinator as still applicable; the four
viewer rows above were repeated on final fbb. Initial defects and exact
nightly comparisons are in the pinned initial record and preceding
supplements. All five desktop build diagnostics record the same 1ba
gitTree f8d601a3523b16c64cb5a1cfebf3bb41fb9c54f5, version
26.1126.7190-dev+g164e8a3af24c (verified CI packages; that run subsequently
cancelled by a newer push). e910 gitTree 58f251154db252458bb8d6ff804de1ed5bf19a23.

| Row | State | Witness |
|---|---|---|
| S3 public HTTPS / presigned; R2 r2.dev; B2 public | PASS | Test seal passed, CLI text/PNG, correct fragments and random HTML names; native tray uploads; split public S3/R2/B2 1 GB and terminal deletion successful. |
| B2 authorized | PASS with coverage limit | Authorization query and actual inline CLI SHA; large refusal. Lab scoped bucket is public-only; true private-bucket enforcement not tested. |
| SFTP HTTPS / WebDAV HTTPS | PASS | Test, inline CLI text/PNG, native tray; WebDAV large split passed; kept-data safe-delete limitation below. |
| HTTPS custom uploader | PASS (controlled actual TLS receiver) | Test, inline text/PNG and native tray; 500 after half POST, retry exact stored page/key and exact origin SHA; cleanup. Named XBackBone ordinary test failed on candidate and nightly before sealing, so named receiver row blocked. |
| HTTP / Nextcloud / Proton | PASS expected refusal | Plain reasons for lack of HTTPS, HTML download and existing E2EE respectively; no sealed upload. |
| Split unsupported / >2 GB / retry / Seal Off | PASS | S3 presigned and B2 authorized same 1 GB refused seal_split_unavailable; oversized 2,147,483,649-byte file seal_too_large; retries same and empty prefixes; disabled Seal produced ordinary link. |
| Passphrase | PASS | Saved mode, separate-passphrase notification, wrong case refused and correct opened in Chrome and Firefox. |
| History | PASS | Lock glyph list/gallery, copy and independent QR key match, Forget removes link availability, delete ordinary inline and both public split files. WebDAV large-data retained intentionally with explicit confirmation (identity limitation; manually removed own file). |
| Browser | PASS desktop, BLOCKED phone | Images with zoom, videos, text, other files download, HTML downloads not render; missing key explanation; final detailed viewer rows above. No phone device tooling enabled or emulator/adb on five hosts. |
| CLI | PASS | Inline and split hashes, harmless altered one-byte viewer rejected seal_page_changed/no output; final pin retested. |
| Native UI, agent | PASS with visibility note | All five native desktops: Test, card/mode, editor and review toggle, tray row, actual capture upload; agent ui.sealLinks/operation.seal/editor.seal/recording.review controls. Notification emitted on Mint, but stale prior notification interfered visually; GNOME/KDE notification screenshots. Optional MCP helper absent. |
| Pictures | PASS | Before nightly, candidate card/editor/review/tray/history/notification and viewer, final annotated e910/fbb playback pair and fallback. |

WebDAV large file safe delete: old candidate returned seal_data_left with
dataStatus unknown and dataError unsupported_capability (identity_unconfirmed),
retry same. Nightly 26.1125.7045 ordinary 1 GB file lacked concurrencyToken
and delete.prepare refused; this is the server's lack of strong ETag for
large files, not introduced by sealing. The accepted e910 behavior explicitly
names the retained encrypted data in confirmation and ends remoteStatus
removed/sealDataStatus kept. The tester manually removed the exact
SHA-verified BIN and isolated directory. Current fbb includes subsequent
passphrase wording refinement; the pictured confirmation is specifically
e910, not a claim that this later wording was graphically exercised.

## Cleanup

Independent final origin inventory checked every recorded temporary prefix:
19 S3 (current objects, versions and unfinished multipart uploads all 0),
4 R2 (objects and unfinished multipart uploads 0; version API NotImplemented),
9 B2 (versions and unfinished large files 0). No residual objects needed
manual removal on this final sweep. The exact 9 WebDAV, 5 SFTP, and 1
Nextcloud temporary folders were independently checked directly in their
lab containers and all absent, including the initial failing cleanup cases.
The controlled HTTPS receiver reported empty and was stopped; named
receiver files were zero before and after, and test receiver pods stopped
without removing volumes. No bucket policy, versioning or other objects
were changed. Private browser profiles and temporary WebDAV password copy
were retired, test CA absent, original browser MIME restored, temporary
Chrome/wget and putgd removed from d69. d69 prior installed-package state
was no putgd (residual config before and after, now latest package version);
Mint, Fedora and Kubuntu restored published 26.1125.7045 nightly, Aurora
AppImage no installed package. Fedora DNF invalidated a pre-existing
pending offline transaction when the package was changed; no desktop
package changed and no distro update run. All five desktop and quiet
leases free, d69 release 10:36:05 UTC and quiet 10:36:13 UTC, ahead
of the 12:15 UTC cutoff.

Exact counts and rows: final-cloud-inventory.json,
final-lab-folders-inventory.json. Sanitized viewer/annotation logs and file
SHA proof are in d69-fbb-*-results.json and annotate-fbb-results.json.
