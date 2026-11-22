# Final storage destination desktop acceptance on d69

Checks for SFTP #1881 and Nextcloud/WebDAV #1879 ran on the physical Debian 13
desktop with KDE Plasma 6.3.6, KWin Wayland 6.3.6, and Firefox ESR. All regional
captures used a synthetic pattern. The recording used moving synthetic noise.
The baseline system had no installed put.gd package. Both test builds used
private Debian 13 DEB extractions, and resident diagnostics matched their CI
manifests. The isolated desktop socket paths were 38 UTF-8 bytes.

| Scope | CI run | Running commit | Running tree | Package version |
| --- | --- | --- | --- | --- |
| Original checklist and notifications | [45020516913](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45020516913) | `3db098a3b5a3443764fa30d58243d5445f8bfa96` | `e2e00447ed24ae8655f67281bb8acee431228870` | `26.1122.6466~dev+g3db098a3b5a3` |
| Review labels and S6/S8 retest | [45034946415](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45034946415) | `a3656f6ab6bc1cde649e5cab7864097c7fef001c` | `2c12ad7825deb57a81e4e62a571d72a25b7bf09f` | `26.1122.6474~dev+ga3656f6ab6bc` |

The nightly controller released d69 at 13:35:57 UTC before the first acceptance
lease. [Controller gate](receipts/nightly-controller-gate.txt)

## Observations


Resident diagnostic receipts are available for [the original build](receipts/native-resident-3db098a3.txt) and [the replacement](receipts/native-resident-a3656f6a.txt).

| Row | Build | Status | Observation |
| --- | --- | --- | --- |
| S1 | `3db098a3` | PASS | The Debian 13 DEB declares `openssh-client`. [Package fields](receipts/debian13-package-fields-3db098a3.txt) |
| S2 | `3db098a3` | PASS | Pasting the SFTP URL filled Server, User, and Folder and showed where OpenSSH connects as `putgd-pw`. [Form](screenshots/S2.png) |
| S3 | `3db098a3` | PASS | The ED25519 SHA-256 fingerprint matched the Aurora server and Trust key persisted the pin. [Trust offer](screenshots/S3.png) |
| S4 | `3db098a3` | PASS | First connection pointed to Password. Use for this session enabled a successful connection, test upload, and cleanup. [Session test](screenshots/S4.png) |
| S5 | `3db098a3` | PASS | The HTTPS Link address changed the button to Test upload and link. The test connected, opened its link, and deleted the test file. [Test](screenshots/S5.png) |
| S6 | `3db098a3` | PASS | Region upload copied the direct HTTPS link, appeared in History and opened the image from History in Firefox. The notice said Uploaded and Link copied. [Full desktop](screenshots/S6image.png), [notice](screenshots/S6notification.png) |
| S7 | `3db098a3` | PASS | The unlinked upload left the clipboard sentinel unchanged. History offered Copy path and the capture summary read Upload only. The notice named the saved SFTP path. [Notice](screenshots/S7notification.png), [History](screenshots/S7context.png), [capture summary](screenshots/S7output.png) |
| S8 | `3db098a3` | PASS | History deleted the exact S6 file. The public endpoint answered HTTP 404. [Confirmation](screenshots/S8confirm.png) |
| S9 | `3db098a3` | PASS | A moving 81.2 s clip reached 4,128,768 of 2,420,656,823 transfer bytes before History cancelled it. SFTP listing confirmed the partial was gone. Review reproduced #1887. [Cancellation](receipts/sftp-recording-result.json), [Review](screenshots/S9review.png) |
| S10 | `3db098a3` | PASS | `/ro` returned Permission denied. Create folder made both levels of `/upload/acc-d69/sub`; Test passed and both empty folders were removed. [Read-only](screenshots/S10readonly.png), [folder test](screenshots/S10pass.png) |
| S11 | `3db098a3` | PASS | CLI and MCP added a second profile, trusted the exact offered key, tested, uploaded the PNG, read its SFTP location and deleted the exact History item. [Location](receipts/sftp-agent-location.txt), [History](screenshots/S11history.png) |
| N1 | `3db098a3` | PASS | A pasted Nextcloud Files URL normalized to the base HTTPS origin. [Form](screenshots/N1.png) |
| N2 | `3db098a3` | PASS | Default Firefox opened Connect to your account. The lab user granted access and Settings showed Signed in as put.gd lab. [Browser grant](screenshots/N2grant.png), [Settings](screenshots/N2signed.png) |
| N3 | `3db098a3` | PASS | Cancelling a second browser sign-in displayed “Sign-in cancelled.” The prior session stayed signed in. [Settings](screenshots/N3.png) |
| N4 | `3db098a3` | PASS | Test upload, link and cleanup passed. [Connection test](screenshots/N4.png) |
| N5 | `3db098a3` | PASS | A region capture copied an HTTPS share link and History showed Shared link. Firefox Private Browsing displayed the synthetic image without authentication. [Full desktop](screenshots/N5image.png) |
| N6 | `3db098a3` | PASS | Delete from destination explained Nextcloud's trash bin. The deleted share returned HTTP 404. [Confirmation](screenshots/N6confirm.png), [HTTP result](receipts/nextcloud-delete.txt) |
| N7 | `3db098a3` | FAIL | After switching to port 18373, Test refused the app password bound to port 18374. Sign in against 18373 displayed the issuer, certificate SHA-256, and Debian CA commands. [Test result](screenshots/N7test.png), [TLS details](screenshots/N7tls.png) |
| N8 | `3db098a3` | PASS | A manually generated password from Nextcloud Security worked in Login name and App password. The destination showed Signed in as put.gd lab. [Manual form](screenshots/N8form.png), [Signed in](screenshots/N8signed.png) |
| N9 | `3db098a3` | PASS | Settings showed Signed out. The uniquely named put.gd d69 manual device disappeared from Devices & sessions after reloading Firefox. [Before](screenshots/N9manualbefore.png), [after](screenshots/N9manualafter.png) |
| N10 | `3db098a3` | PASS | WebDAV test passed, History opened the capture in Firefox, and deletion returned HTTP 404. [Browser](screenshots/N10image.png), [HTTP result](receipts/webdav-delete.txt) |
| N11 | `3db098a3` | PASS | Test offered Create folder for the missing collection. With its matching public Link address, the retest passed and WebDAV DELETE returned 204 for the test folder. [Offer](screenshots/N11offer.png), [retest](screenshots/N11pass.png) |
| N12 | `3db098a3` | PASS | The plain HTTP checkbox appeared and configuration rejected the HTTP address while unchecked. The checkbox was cleared again. [Off](screenshots/N12off.png), [on](screenshots/N12on.png) |
| N13 | `3db098a3` | PASS | CLI and MCP added the destination, the returned Login Flow URL opened in Firefox and the lab granted access. Test, PNG upload and share, exact History deletion and sign-out succeeded. [Grant](screenshots/N13grant.png), [deleted](receipts/nextcloud-agent-delete.json), [signed out](screenshots/N13signedout.png) |
| G1–G4 | k72 | Covered on k72 | The k72 worker owns the shared policy and host key changes. |

## Replacement build retests

| Row | Build | Status | Observation |
| --- | --- | --- | --- |
| #1887, SFTP without a Link address | `a3656f6a` | PASS | Review recording displayed Upload only after recording and stopping. [Review](screenshots/ReviewUploadOnly.png), [receipt](receipts/ReviewUploadOnly.json) |
| #1887, SFTP with a Link address | `a3656f6a` | PASS | Review recording displayed Shared link. [Review](screenshots/ReviewSharedLink.png), [receipt](receipts/ReviewSharedLink.json) |
| #1887, local-only recording | `a3656f6a` | PASS | Review recording displayed Local only. [Review](screenshots/ReviewLocalOnly.png), [receipt](receipts/ReviewLocalOnly.json) |
| S6 sanity | `a3656f6a` | PASS | A native region capture copied the exact History HTTPS link. History opened the image in Firefox and the endpoint returned HTTP 200. [Full desktop](screenshots/RetestS6browser.png), [clipboard](receipts/S6-a3656f6a-clipboard.txt), [HTTP result](receipts/S6-a3656f6a-http.txt) |
| S8 sanity | `a3656f6a` | PASS | History deleted the exact S6 capture. Its HTTPS link returned HTTP 404. [Confirmation](screenshots/RetestS8confirm.png), [History after deletion](screenshots/RetestS8result.png), [HTTP result](receipts/S8-a3656f6a-http.txt) |

The S9 mid-transfer cancellation evidence is from `3db098a3`.

## Findings

- **Known product bug #1887 on `3db098a3`.** Configure SFTP with an empty Link
  address, select it for capture, record and stop. Review should say Upload
  only. Review displayed Shared link. The actual region route and clipboard
  followed upload-only behavior. The replacement displayed all three expected labels. [Review before the fix](screenshots/S9review.png), [Review after the fix](screenshots/ReviewUploadOnly.png)
- **N7 checklist mismatch.** Sign in on port 18374, edit the same Nextcloud
  destination to port 18373, and choose Test upload and link. The checklist
  expects the certificate error at that control. Test refused to reuse the app
  password on a different origin. Choosing Sign in on 18373 reports the
  untrusted Caddy issuer, the certificate SHA-256 fingerprint, and
  `sudo cp server-ca.crt /usr/local/share/ca-certificates/` followed by
  `sudo update-ca-certificates`. This matches the credential-origin guard in
  the candidate. N7 is a test checklist mismatch for the new destination. [Test refusal](screenshots/N7test.png), [Sign in TLS result](screenshots/N7tls.png)
- **Lab setup corrected.** The first region attempt from the extracted DEB
  reported that its restricted desktop entry did not match the executable.
  Registering the packaged capture and recording entries against the extracted
  executables and restarting the resident enabled native KWin capture. The
  receipt confirms ScreenShot2 version 4 and an exact executable match.
  [Initial refusal](screenshots/selector.png)
- **Test harness corrected.** The first monitoring pass hit an absent upload
  progress object during recording export. The corrected watcher observed
  partial byte progress before History confirmed cancellation. The SFTP
  listing then showed no recording object. [Recorder result](receipts/sftp-recording-result.json),
  [SFTP listing](receipts/sftp-recording-listing.txt)

The SFTP agent profile used the same service through its IPv4-mapped IPv6
address, so the second profile received an independent host key offer. The
WebDAV folder test used the public link base corresponding to the new
collection. The manual Nextcloud app password had a d69-specific device label,
which let the browser show its exact removal in the shared lab account.

## Restoration

The system put.gd package inventory still had no installed package. The
temporary CA was removed from the system trust and test browser profiles.
The original URI handler file was restored byte for byte, the temporary
Firefox and KWin entries were removed, and the test resident profiles had zero
destinations before shutdown. Test uploads and the empty folders created for
the checks were removed. Nextcloud History deletion used the server's trash
semantics. Signed-in put.gd devices created for these checks were revoked.

The 3db098a3 leases were released at 14:03:48 and 14:15:54 UTC after their
cleanup checks. [First restoration](receipts/restoration-3db098a3.txt),
[first lease](receipts/release-3db098a3.txt),
[second restoration](receipts/restoration-3db098a3-second.txt),
[second lease](receipts/release-3db098a3-second.txt)

The replacement lease passed its cleanup check and was released at 15:10:33 UTC. [Replacement restoration](receipts/restoration-a3656f6a.txt), [replacement lease](receipts/release-a3656f6a.txt)

## Annotated screenshots

The production put.gd editor generated these copies using a separate headless
resident. [SFTP key](annotated/S3.png), [SFTP browser image](annotated/S6image.png),
[Nextcloud private share](annotated/N5image.png), [Corrected Review label](annotated/ReviewUploadOnly.png)
