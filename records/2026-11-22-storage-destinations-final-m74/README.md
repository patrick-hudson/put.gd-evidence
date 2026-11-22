# Final storage destination acceptance on m74

Physical Linux Mint 22.3, Cinnamon 6.6.9 on native X11, display `:0`, 1920 × 1080. The nightly controller released m74 at 13:32:11 UTC on November 22, 2026. The acceptance lease started at 13:32:37 UTC. [Nightly gate receipt](nightly-gate.json)

The installed Ubuntu 24.04 DEB was `putgd 26.1122.6466~dev+g3db098a3b5a3`. Its SHA-256 was `6f3e00d5fa61050dbc94f01e7cc9ae4a0adbaf148f0be1369a0133100273b1be`. Resident diagnostics on Cinnamon matched the artifact manifest and the candidate source. The desktop socket was 39 UTF-8 bytes. The offscreen editor socket was 36 bytes. [CI run 45020516913](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45020516913)

| Identity | Value |
|---|---|
| Branch | `candidate/storage-destinations` |
| Running commit | `3db098a3b5a3443764fa30d58243d5445f8bfa96` |
| Running tree | `e2e00447ed24ae8655f67281bb8acee431228870` |
| Original installed DEB | `26.1122.6373~dev+gaa202c7a634c` |

## Results

| Row | Result | Observation |
|---|---|---|
| S1 | PASS | The exact DEB control record lists `openssh-client` in Depends. |
| S2 | PASS | Pasting the SFTP URL populated Server, User and Folder. The connection line named the host, port and user. [Screen](screenshots/s2.png) |
| S3 | PASS | Trust key showed the same ED25519 SHA-256 fingerprint as the lab server. Trust saved that fingerprint. [Screen](screenshots/s3.png) |
| S4 | PASS | Test directed the sign-in failure to Password. Entering it in the masked field and choosing Use for this session let the test pass. [Screen](screenshots/s4.png) |
| S5 | PASS | The trusted HTTPS base changed the label to Test upload and link. The test uploaded, opened the link and cleaned up. [Screen](screenshots/s5.png) |
| S6 | PASS | The region upload copied its URL, showed Uploaded, and appeared in History. Open in browser displayed the image and URL in Firefox. [Notice](screenshots/s6notice2.png) · [Firefox](screenshots/s6finalBrowser.png) |
| S7 | PASS | Clearing the link kept the clipboard marker intact. The notice identified the saved server path, History offered Copy path, and the capture footer said Upload only. [Notice](screenshots/s7notice2.png) · [History menu](screenshots/s7context.png) |
| S8 | PASS | Exact History deletion removed the S6 PNG. Its public HTTPS URL returned 404. [Confirmation](screenshots/s8finalConfirm.png) |
| S9 | PASS | Cancelled the 82.5-second recording after 4,063,232 of 1,800,532,583 bytes had transferred. The worker reported removal of the partial file and independent SFTP listing confirmed absence. [Result](screenshots/s9final.png) |
| S10 | PASS | `/ro` refused creation with permission denied. Create folder made the nested `/upload/acc-m74/sub`, then Test passed. Both empty directories were removed over SFTP. [Permission](screenshots/s10ro.png) · [Create offer](screenshots/s10offer.png) |
| S11 | PASS | CLI and MCP added the second destination, trusted the exact fingerprint, tested, uploaded the PNG, read `/upload/acc-m74-agent-sftp.png` from History and deleted it. The public endpoint returned 404. [Test screen](screenshots/s11test.png) |
| N1 | PASS | Pasting the Files page URL saved the Nextcloud server base. [Screen](screenshots/n1.png) |
| N2 | PASS | Firefox opened Connect to your account. After login and Grant access, Settings showed Signed in as put.gd lab. [Browser](screenshots/n2connect.png) · [Settings](screenshots/n2signed.png) |
| N3 | PASS | Sign in again followed by Cancel sign-in displayed Sign-in cancelled and preserved the existing account. [Screen](screenshots/n3.png) |
| N4 | PASS | Test upload, link and cleanup all passed. [Screen](screenshots/n4.png) |
| N5 | PASS | The region capture copied an HTTPS `/s/` URL and History showed Shared link. Firefox Private Browsing loaded the image anonymously. [Browser](screenshots/n5privateFinal.png) |
| N6 | PASS | History’s confirmation named Nextcloud’s trash bin. After deletion, reloading the same private browser URL displayed Page not found. [Confirmation](screenshots/n6confirm.png) · [Browser](screenshots/n6missing.png) |
| N7 | PASS | Test on the untrusted listener with a dedicated synthetic password fixture named Caddy’s issuer, the certificate SHA-256 and the Mint CA import command. [Screen](screenshots/n7tls.png) |
| N8 | PASS | Created a named app password in Firefox Security, copied it through the browser control and stored it in the masked put.gd form. Settings showed Signed in as put.gd lab. [Screen](screenshots/n8signed.png) |
| N9 | PASS | Sign out displayed Signed out. Firefox’s Devices & sessions search went from one match for the test device to Phrase not found after a reload. [Before](screenshots/n9witness.png) · [After](screenshots/n9manualAfter.png) |
| N10 | PASS | WebDAV Test passed with the trusted base. The actual capture opened in Firefox. History deletion made the URL return 404. [Browser](screenshots/n10browser.png) · [History](screenshots/n10deleted.png) |
| N11 | PASS | A missing WebDAV collection offered Create folder. The new collection passed Test. An independent WebDAV check verified it was empty and removed it. [Offer](screenshots/n11offer.png) · [Retest](screenshots/n11pass.png) |
| N12 | PASS | An HTTP address revealed Allow plain HTTP. The draft was refused while unchecked and accepted when checked. Restored unchecked and HTTPS. [Refused](screenshots/n12refused.png) · [Opt-in](screenshots/n12enabled.png) |
| N13 | PASS | CLI and MCP created the destination and returned the Login Flow URL. Granted access in Firefox, then tested, uploaded and shared a PNG, deleted it with the exact History acknowledgement, and confirmed sign-out revoked the app password. [Browser](screenshots/n13connect.png) · [History](screenshots/n13done.png) |
| G1–G4 | Covered on k72 | Shared server policy and rotation rows belong to k72. |

## Findings

- **Product bug #1887.** Configure SFTP without a Link address and make it the recording destination. Record a region and stop to open Review. The recording destination should say Upload only. Review showed “SFTP m74 final · Shared link.” Capture’s footer correctly showed Upload only, and the recording exercise used the linkless SFTP route. This is in the new provider flow. [Issue #1887](https://github.com/patrick-hudson/put.gd-desktop/issues/1887) · [Review screen](screenshots/s9review.png)
- **Capture fixture and focus.** The first synthetic fixture painted a blank image. A draw callback on a dedicated GTK drawing area fixed the fixture. In the first upload-only attempt, Firefox retained focus after the harness requested Destinations and the address was never cleared. The corrected test explicitly raised put.gd and checked that Link address had saved empty before capturing. The extra synthetic uploads were deleted from History.
- **Browser authentication and TLS preflight.** The manual creation flow asked for browser password confirmation before showing the newly generated app password. After completing that step, the browser’s Copy app password action and a separate HTTPS authentication check verified the input before Store. The initial untrusted-address attempt correctly refused the existing app password because it belonged to the trusted address. The TLS repeat used a separate profile and a synthetic password at the untrusted address.
- **Superseded artifact.** The first CI attempt failed to compile the SFTP worker on Ubuntu 24.04 because `QStringDecoder` lacked its header. The correction was present in the final candidate. [Initial CI job](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45017272816/job/137192254563)

The Firefox screenshots hide login and share addresses where they contain tokens. The Nextcloud deletion dialog was cropped in the put.gd editor. The four annotated PR images use the candidate editor’s rectangle, arrow and text tools. [Annotated images](annotated/)

## Restoration

The acceptance worker stopped responding after the last row passed. Its final evidence command was waiting for an approval it never received, and the lease expired at 14:48 UTC. The campaign lead ran the worker's own restore steps on m74 at 14:50–14:53 UTC:

- **Test destinations:** the remaining Nextcloud and WebDAV sign-ins were signed out and all six test destinations were removed from the private resident. Capture went back to local.
- **Processes:** the private resident and the clipboard helper were stopped. No `putgd-ui`, `/tmp/pgda.*` or private-Firefox processes remain.
- **Browser and trust:** the Firefox handler was restored, leaving `firefox.desktop` as the HTTPS default. The temporary system CA and the NSS profile entry were removed, and curl again refuses the lab listener as untrusted.
- **Package:** the reviewed restore plan downgraded only `putgd`, removing nothing, back to the original `26.1122.6373~dev+gaa202c7a634c`.
- **Accessibility bus:** `IsEnabled` was set back to `false`, its original value.
- **Lock:** the desktop lock was released with the cleanup check at 14:53:19 UTC (receipt `history/2026-11-22T14-53-19Z-release.json`). The only processes it noted were an older lab watchdog (313646, 313651) that predates the lease.
