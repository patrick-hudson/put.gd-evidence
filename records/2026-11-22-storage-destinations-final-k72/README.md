# Final storage destination acceptance on k72

The Ubuntu 26.04 DEB from [CI run 45020516913](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45020516913) ran on k72, Kubuntu 26.04 with Plasma 6.6.6 on native Wayland. Resident diagnostics matched candidate commit `3db098a3b5a3443764fa30d58243d5445f8bfa96` and tree `e2e00447ed24ae8655f67281bb8acee431228870`. Package version `26.1122.6466~dev+g3db098a3b5a3` and local and remote DEB SHA-256 `0a9e83002d76a093bf2c8937a2884412163a2ae9f27fcb01ab1cf4c950f19fc9`. The isolated resident session socket was 39 UTF-8 bytes. The lead cleared k72 at 12:58 UTC while the controller held other builders.

| Row | Result | Observed |
| --- | --- | --- |
| S1 | PASS | The exact DEB depends on `openssh-client`. k72 had OpenSSH client `1:10.2p1-2ubuntu3.8`. |
| S2 | PASS | Pasting the SFTP URL filled Server, User and Folder and showed the resolved connection as putgd-pw. [Frame](screenshots/S2.png) |
| S3 | PASS | The unknown-key banner showed the same ED25519 SHA-256 fingerprint as the lab server. Trust stored that exact pin. [Frame](screenshots/S3.png) |
| S4 | PASS | Test without the password pointed to Password. After Use for this session, Test passed and the destination showed Connected. [Prompt](screenshots/S4auth.png) · [Connected](screenshots/S4.png) |
| S5 | PASS | The HTTPS Link address enabled Test upload and link. The upload, link check and cleanup passed. [Frame](screenshots/S5.png) |
| S6 | PASS | The region arrived in History and its HTTPS URL was on the clipboard. The notice said Uploaded. Open in browser showed the image and URL in Firefox. [History](screenshots/hist.png) · [Notice](screenshots/notices.png) · [Browser](screenshots/S6browser.png) |
| S7 | PASS | The clipboard marker stayed in place. The notice named the saved SFTP path, History offered Copy path, and the capture footer said Upload only. [Notice](screenshots/notices.png) · [History](screenshots/S7path.png) |
| S8 | PASS | The exact linked capture was deleted from History. Firefox and a fresh HTTPS request returned 404. [Confirmation](screenshots/S8confirm.png) · [404](screenshots/S8notFound.png) |
| S9 | PASS | A 65.87 s moving recording was cancelled after 4,194,304 of 164,415,194 bytes. The operation became cancelled. An authenticated SFTP listing found neither its original name nor a partial file. [Review](screenshots/S9finalReview.png) |
| S10 | PASS | The read-only folder returned permission denied. Create folder created the nested path, Test passed and both empty folders were removed. [Denied](screenshots/S10denied.png) · [Create folder](screenshots/S10offer.png) · [Retest](screenshots/S10retest.png) |
| S11 | PASS | MCP added the second destination and trusted the exact fingerprint on the IPv4-mapped address. A synthetic PNG uploaded, CLI History returned its location and exact MCP deletion removed it. [History](screenshots/historyRaised.png) |
| N1 | PASS | The pasted Nextcloud Files URL became the HTTPS server base. [Frame](screenshots/N1session.png) |
| N2 | PASS | Firefox opened Connect to your account, accepted the lab login and granted access. Settings showed Signed in as put.gd lab. [Connect](screenshots/N2page.png) · [Grant](screenshots/N2grant.png) · [Signed in](screenshots/N2signed.png) |
| N3 | PASS | Cancel sign-in during a second flow showed Sign-in cancelled and retained the earlier signed-in account. [Frame](screenshots/N3.png) |
| N4 | PASS | Test upload and link passed with cleanup. [Frame](screenshots/N4.png) |
| N5 | PASS | The public share URL was copied and History showed Shared link. Firefox Private Browsing previewed the image without login. [History](screenshots/historyRaised.png) · [Full desktop with share token covered](screenshots/N5full.png) |
| N6 | PASS | The exact History confirmation named the Nextcloud trash bin. The private browser then showed Page not found. [Confirmation](screenshots/N6trash.png) · [Browser](screenshots/N6notFound.png) |
| N7 | FAIL | Test refused the app password bound to :18374 after the server was changed to :18373. Sign in again against :18373 showed the issuer, SHA-256 fingerprint and Ubuntu CA command. [Test](screenshots/N7.png) · [TLS diagnostic](screenshots/N7tls.png) |
| N8 | PASS | A named app password was made in native Firefox Security and typed into put.gd's masked field. Use for this session showed Signed in as put.gd lab. [Form](screenshots/N8manual.png) · [Signed in](screenshots/N8stored.png) |
| N9 | PASS | Sign out returned Signed out and put.gd (kubuntu) disappeared from the browser's Devices & sessions list on reload. [Before](screenshots/N9rows.png) · [Signed out](screenshots/N9signout.png) · [After](screenshots/N9afterList.png) |
| N10 | PASS | The WebDAV address became HTTPS, Test passed, Firefox opened the captured image and History deletion made its URL return 404. [Addresses](screenshots/N10ready.png) · [Test](screenshots/N10result.png) · [Browser](screenshots/N10check.png) · [Confirmation](screenshots/N10delete.png) |
| N11 | PASS | Create folder made the missing collection. Test passed when Link address pointed to that same subfolder. WebDAV DELETE returned 204 and follow-up PROPFIND returned 404. [Offer](screenshots/N11offer.png) · [Retest](screenshots/N11retest.png) |
| N12 | PASS | The plain HTTP address was refused with the checkbox clear, saved with it ticked, and the checkbox was unticked again before returning to HTTPS. [Refused](screenshots/N12off.png) · [Opted in](screenshots/N12on.png) |
| N13 | PASS | MCP added the destination and opened Login Flow v2 in Firefox. Grant, Test, PNG upload, shared receipt, exact deletion and sign-out all completed. [Grant](screenshots/N13grantStep.png) · [Signed out](screenshots/N13signedout.png) |
| G1 | PASS | Test reported that the server requires a password on every public link. The server setting was restored to off. [Frame](screenshots/G1.png) |
| G2 | PASS | A native region capture reported that public links were turned off and saved a local copy. The server folder stayed empty. Sharing was restored to on. [Notice](screenshots/G2.png) |
| G3 | PASS | The 6 MiB clipboard file was rejected. The notice said the account had used 184.0 MB of its 5.0 MB quota. The folder stayed empty and quota was restored to none. [Notice](screenshots/G3.png) |
| G4 | PASS | Test showed a red Was/Now ED25519 fingerprint banner with Trust new key. After trusting the verified new key, Test uploaded and deleted its probe. The lab pin was refreshed and a strict authenticated SFTP connection succeeded. [Old pin](screenshots/G4baseline.png) · [Change and Trust](screenshots/G4.png) · [Retest](screenshots/G4connected.png) |

## Findings

- **Product #1887.** Clear the SFTP Link address, make it the capture default, record a region and Stop. Review showed `SFTP · Shared link` while the destination could only upload. The expected label was `Upload only`. [Review frame](screenshots/S9review.png) · [Issue](https://github.com/patrick-hudson/put.gd-desktop/issues/1887)
- **N7 checklist mismatch.** Sign in at :18374, change the Nextcloud address to :18373 and press Test upload and link. The checklist expected the TLS diagnostic. put.gd protected the credential on the original address and asked for a new sign-in. The same untrusted listener produced the expected certificate diagnostic on Sign in again. [Test](screenshots/N7.png) · [Sign-in result](screenshots/N7tls.png)
- **N11 test setup.** The old public Link address returned 404 for a test upload in the newly created subfolder. Once the public address matched the upload folder, Test passed and cleaned up. [Initial retest](screenshots/N11wrongBase.png)
- **Test harness recovery.** The first recording progress reader treated a missing progress value as an object, and that short upload finished. The file was deleted. A corrected poller cancelled the longer clip during transfer. The first manual app-password reader also stopped before using the new value. That exact named test password was revoked, and the retry used the visible Security dialog's password field in memory and succeeded. The editor needed a fresh headless resident for each of the remaining annotation files after the first save. During final cleanup, the scoped Firefox process scan raced with an exiting process. Cleanup retried with a scan that handled disappearing PIDs and verified removal of the browser profile.

## Restoration

The main-leg package rollback installed the exact original DEB `26.1122.6374~dev+gffeead0fc1f3`. The temporary Firefox profile and CA were removed and the original MIME settings restored byte-for-byte. The system CA bundle matched its original checksum and the trusted lab listener was refused again by system curl with certificate error 60. The isolated application configuration and test destinations were removed. The named k72 Nextcloud app passwords were absent. All successful uploads made by the main leg were removed, and SFTP confirmed the cancelled recording left no partial.

The quiet leases were released at 13:30:24 and 13:40:13 UTC. The main desktop lease was released at 13:42:39 UTC. The global test lease began at 15:14:45 UTC after all four peer desktops, including Aurora’s rerun, were free. The running build matched the same commit and tree. Each Nextcloud global setting was restored after its row. Final server readback was quota none, sharing on, and link passwords off. The lab SFTP pin now matches the rotated ED25519 key and strict authenticated listing passed.

After the global rows, the original package and system trust checksum were verified again. System curl returned certificate error 60. Scoped Firefox, its CA and the isolated application profile were removed, and the original default browser and MIME settings were restored. The Nextcloud app password was revoked and the empty k72 test collection was removed. Cleanup inventory matched the original package. The final k72 lease was released at 15:23:59 UTC and status showed it free. [Restoration checks](global-restoration.txt)

[Annotated pictures](annotated/)
