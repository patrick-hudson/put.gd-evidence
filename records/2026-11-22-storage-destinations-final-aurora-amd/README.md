# Final SFTP and Nextcloud storage acceptance on Aurora

The physical `aurora-amd` desktop ran Aurora Fedora 45 Atomic `testing-45.20261101.2`, Plasma and KWin 6.8.2, and a native KDE Wayland session. [Host inventory](host-before.txt)

The AppImage came from [CI run 45020516913](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45020516913). Resident diagnostics reported version `26.1122.6466-dev+g3db098a3b5a3`, commit `3db098a3b5a3443764fa30d58243d5445f8bfa96`, and tree `e2e00447ed24ae8655f67281bb8acee431228870`, matching the CI manifest. The download and staged AppImage had the same SHA-256. The desktop, SFTP askpass and editor session socket paths were 38, 39 and 40 UTF-8 bytes. [Manifest](build-info.json) · [Checksum](AppImage.sha256) · [Resident identity](resident-identity.txt)

Nightly held the host from 12:32:25 to 12:57:37 UTC. The lead approved the controller's exact release receipt plus current free status after the status display selected an unrelated history file. The acceptance lease began at 13:01:12 UTC. [Controller release](controller-release.json)

The AppImage inherited a private `SSL_CERT_FILE` containing the system bundle and the lab CA. Firefox, the host's default browser, used a disposable profile with the lab CA imported in its certificate database. System trust rejected the lab listener. [Host inventory](host-before.txt)

## Results

| Row | Result | Observed behavior |
|---|---|---|
| S1 | PASS | The host had OpenSSH clients 10.5p1. The installed executable used during an AppImage upload was `/usr/bin/ssh`. [Process receipt](S1-running-ssh.txt) |
| S2 | PASS | Pasting the SFTP URL populated Server, User and Folder and showed the resolved connection as `putgd-pw`. [Settings](screenshots/S2Clean.png) |
| S3 | PASS | The ED25519 SHA-256 fingerprint matched the lab server status. Trust accepted the exact key. [Trust banner](screenshots/S3Trust.png) |
| S4 | PASS | The first signed connection directed the user to Password. Using it for this session made Test upload pass and the destination show Connected. [Password prompt](screenshots/S4Password.png) · [Test result](screenshots/S4Passed.png) · [Connected](screenshots/MakeDefaultDialog.png) |
| S5 | PASS | Test upload and link checked the HTTPS public link and cleaned up the test object. [Result](screenshots/S5Verified.png) |
| S6 | PASS | Region capture copied the public PNG link. Plasma recorded Uploaded, History showed Shared link and Open in browser opened the image in Firefox. [Notice](screenshots/S6S7Notifications.png) · [History](screenshots/S6HistoryProof.png) · [Full desktop](screenshots/S6BrowserClean.png) |
| S7 | PASS | Without a Link address, capture output showed Upload only, the clipboard sentinel hash stayed identical, History offered Copy path and the notice named the saved server path. [Routing](screenshots/S7Routing.png) · [History](screenshots/S7NoticePanel.png) · [Notice](screenshots/S7SavedNotice.png) |
| S8 | PASS | History confirmed the exact linked capture. Its public link returned HTTP 404 after deletion. [Confirmation](screenshots/S8Confirm.png) |
| S9 | FAIL | A 20.0 s recording reached Cancelled after a History click, but an independently listed partial file remained on the paced SFTP connection. [Review](screenshots/S9ReviewPacedFinal.png) · [Operation](S9-settled.json) · [SFTP listing](S9-late-partial.json) |
| S10 | PASS | The test reported permission denied for `/ro`. Create folder made the nested path and the retest passed. Both empty folders were removed. [Denied](screenshots/S10Denied.png) · [Create offered](screenshots/S10Missing.png) · [Retest](screenshots/S10Final.png) |
| S11 | PASS | MCP added the second destination and independently pinned the fingerprint using the host's DNS name. The CLI uploaded a synthetic PNG, MCP read its location receipt and exact History deletion removed it. [Test](screenshots/S11Passed.png) |
| N1 | PASS | Pasting the Nextcloud Files URL saved the base server address. [Settings](screenshots/N1Normalized.png) |
| N2 | PASS | Firefox opened Connect to your account. I logged in and granted access. Settings showed Signed in as put.gd lab. [Browser](screenshots/N2FirefoxConnect.png) · [Signed in](screenshots/N2SignedInActual.png) |
| N3 | PASS | Cancel sign-in showed Sign-in cancelled and the original session stayed signed in. [Notice](screenshots/N3Cancelled.png) |
| N4 | PASS | Test upload and link reported upload, link and cleanup passed. [Result](screenshots/N4Passed.png) |
| N5 | PASS | Capture copied a public share URL. Firefox's private window showed the image without a login. History offered Copy link and Open in browser. [Full desktop](screenshots/N5Private.png) · [History](screenshots/N5History.png) |
| N6 | PASS | History confirmation named the Nextcloud trash bin. The deleted share returned 404 and Firefox showed Page not found. [Confirmation](screenshots/N6Trash.png) · [Browser](screenshots/N6Missing.png) |
| N7 | PASS | Test at :18373 named the issuer, certificate SHA-256 fingerprint and Fedora CA command. A synthetic placeholder reached TLS validation without sending a real credential. [Test diagnostic](screenshots/N7TestExact.png) |
| N8 | PASS | I created a lab app password in Nextcloud Security and entered it into the app's masked field. Use for this session stored it and the account was signed in. [Stored state](screenshots/N8Stored.png) |
| N9 | PASS | Both test destinations reached Signed out. Firefox found no manual test device, and the server inventory showed only the pre-existing 08:38 UTC flow device with the same label. [Settings](screenshots/N9FlowSignedOut.png) · [Firefox](screenshots/N9ManualCountAfter.png) · [Server inventory](N9-device-inventory.json) |
| N10 | PASS | WebDAV's connection test passed. A capture's returned link opened in Firefox and returned 404 after exact History deletion. [Test](screenshots/N10Connected.png) · [Firefox](screenshots/N10Firefox.png) · [Deletion](screenshots/N10Delete.png) |
| N11 | PASS | Create folder made the missing collection. Test passed with its matching public subpath and WebDAV DELETE removed the empty collection. [Create offered](screenshots/N11Missing.png) · [Retest](screenshots/N11Verified.png) |
| N12 | PASS | Plain HTTP appeared and the address was refused with the checkbox off. Enabling it saved the address. I restored HTTPS and turned the checkbox off. [Refused](screenshots/N12Refused.png) · [Allowed](screenshots/N12Allowed.png) |
| N13 | PASS | MCP drove destination creation and Login Flow v2 in Firefox, then the upload-and-link test and synthetic upload. The public share returned 200 and then 404 after exact CLI deletion. MCP sign-out returned Signed out. [Grant](screenshots/N13LoginForm.png) · [Test](screenshots/N13Test.png) · [Signed out](screenshots/N13SignedOut.png) |
| G1–G4 | k72 | Covered on k72. Aurora made no shared quota, sharing policy or host-key changes. |

## Findings

- **SFTP cancellation left a partial file.** Record the moving pattern for 20.0 s, then upload it to the password-backed SFTP lab folder through the temporary `acc-aurora-paced` OpenSSH alias. Its ProxyCommand paced outgoing traffic to 880 bytes/s after the first 5120 bytes. Once an independent SFTP listing shows the target exists and History shows an active upload, click Cancel this upload. The expected result is Cancelled and no remote file. The operation settled Cancelled, and its item reported that put.gd could not confirm removal. The target remained zero bytes at settlement and later measured 65,536 bytes. The exact synthetic object was manually removed and SFTP confirmed it absent. This is a product cleanup failure under controlled network backpressure. Two follow-up attempts with roughly one-minute clips and faster pacing finished uploading before the harness clicked Cancel. The first watcher did not track the current recording, and the second found a partial file before History's active-upload banner appeared. The two full files were removed. [Operation](S9-settled.json) · [Partial file](S9-late-partial.json) · [Cleanup](S9-manual-cleanup.json)
- **Recording Review mislabels SFTP uploads.** Clear Link address and make the SFTP destination the default. Record a region and stop into Review. The capture toolbar says Upload only, while Review says Shared link. SFTP is new in this candidate and the lead already filed the mismatch. [Review](screenshots/S9ReviewPacedFinal.png) · [Issue #1887](https://github.com/patrick-hudson/put.gd-desktop/issues/1887)
- **The lease status display selected the wrong receipt.** On Aurora, `desktop_lock.py status` displayed `last: None` after a verified nightly release. Its lexical sort selected the unrelated `plasma1364-scratch-retired.json` instead of the timestamped release receipt. The lead owns this lab issue. [Actual receipt](controller-release.json)

## Restoration

The host had no put.gd RPM before or after the test. The system trust bundle SHA-256 matched the baseline and system curl still rejected the lab certificate. I removed both the private CA bundle and the disposable Firefox profile after deleting the imported CA from its certificate database. The original Firefox handler and the SSH client configuration were restored byte for byte. [Host verification](host-after.txt) · [Browser restoration](restore-browser.txt) · [SSH restoration](restore-ssh.txt)

All six destinations were removed and capture output returned to local save. I deleted the synthetic uploads, the empty SFTP, WebDAV and Nextcloud folders, and the one leftover partial file. Nextcloud retained the deleted synthetic items in its trash as designed. The checkout remained clean. The desktop cleanup check passed and the acceptance lock was released at 13:45:06 UTC. [Destination restoration](restore-destinations.json) · [SFTP partial removal](S9-manual-cleanup.json) · [Lease release](restore-desktop.txt)

The PR pictures were marked in the candidate's own editor from an offscreen resident. [Annotated screenshots](annotated/) · [Editor receipt](editor-annotations.txt)
