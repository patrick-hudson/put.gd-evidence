# Final storage destination acceptance on Fedora 44

The Fedora 44 GNOME 50.6 Wayland desktop used the Fedora 44 RPM from CI run 45020516913. Resident diagnostics matched commit `3db098a3b5a3443764fa30d58243d5445f8bfa96` and tree `e2e00447ed24ae8655f67281bb8acee431228870`. The installed-package baseline was no system put.gd RPM. The native session ran with AppIndicator active and the RPM's put.gd capture extension version 25 loaded.

[CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45020516913) · [RPM inspection](rpm-inspection.txt) · [Artifact manifest](ci-build-info.json) · [Resident build](resident-build-info.json) · [Desktop readiness](desktop-ready.json) · [Restoration](restoration.txt)

The lead authorized starting after confirming that the controller skipped f44. The acceptance desktop lease ran from 12:58:34 to 13:33:22 UTC. The resident socket was 39 bytes and the SFTP askpass socket path was 40 bytes. Each offscreen editor resident used a 36-byte socket.

| Row | Result | Observation |
| --- | --- | --- |
| S1 | PASS | The exact RPM requires `openssh-clients`. |
| S2 | PASS | Pasting the SFTP URL filled Server, User and Folder and showed the resolved OpenSSH connection line. [Form](screenshots/s2-url-paste.png) |
| S3 | PASS | The ED25519 fingerprint matched the Aurora service status. Trust saved that fingerprint. [Banner](screenshots/s3-trust.png) |
| S4 | PASS | The first test pointed to Password. The session password passed the upload test, which reported connected and signed in. [Failure](screenshots/s4-failed-test.png) · [Pass](screenshots/s4-connected.png) |
| S5 | PASS | The HTTPS base changed the button to Test upload and link. Upload, link and deletion passed. [Test](screenshots/s5-link-test.png) |
| S6 | PASS | A region upload copied its HTTPS URL, showed Uploaded, appeared in History and opened its image in Firefox. A banner obscured the filename suffix in the full-desktop address bar. The annotation transcribes the verified clipboard URL. [Firefox](annotated/s6-firefox-clear.png) · [History](screenshots/s6-history.png) · [Notice](screenshots/s6-notifications.png) |
| S7 | PASS | Clearing Link address left the clipboard canary intact. Capture output said Upload only, the notice gave the remote path and History offered Copy path. [Notice](screenshots/s7-saved-exact-path.png) · [History](screenshots/s7-copy-path.png) · [Output](screenshots/s7-output-mode.png) |
| S8 | PASS | Deleting the linked capture from History made its HTTPS URL return 404. [Confirmation](screenshots/s8-history-delete.png) |
| S9 | BLOCKED | The 13.2-second moving clip was 171,122 bytes. The upload advanced from encoding through preflight to completed before the harness observed uploading, so cancellation during transfer remains unverified. The completed clip was deleted and its exact name was absent from the SFTP listing. [Review](screenshots/s9-review.png) · [Cleanup](history-cleanup.json) |
| S10 | PASS | The read-only folder returned permission denied. Create folder made the nested path, the retest passed and both empty directories were removed. [Read-only](screenshots/s10-readonly.png) · [Create](screenshots/s10-create-offer.png) · [Retest](screenshots/s10-retest-success.png) |
| S11 | PASS | The MCP helper added a second SFTP destination, trusted the exact verified fingerprint, tested and uploaded a synthetic PNG. CLI and MCP verified its remote path and completed deletion. [Cleanup](history-cleanup.json) |
| N1 | PASS | A pasted Nextcloud Files URL normalized to the HTTPS server base. [Form](screenshots/n1-normalized.png) |
| N2 | PASS | Default Firefox opened Connect to your account. Logging in and granting access showed Signed in as put.gd lab. [Browser](screenshots/n2-firefox-connect.png) · [Settings](screenshots/n2-signed-in.png) |
| N3 | PASS | Cancel sign-in returned Sign-in cancelled and retained the earlier grant. [Notice](screenshots/n3-cancelled.png) |
| N4 | PASS | The Nextcloud test reported successful upload, link and cleanup. [Test](screenshots/n4-test-passed.png) |
| N5 | PASS | The copied HTTPS share opened the region in a private Firefox window without an account prompt. History showed Shared link. The browser address is masked in evidence. [Browser](screenshots/n5-private-preview.png) · [History](screenshots/n5-shared-history.png) |
| N6 | PASS | History warned that Nextcloud keeps the file in its trash bin. After confirmation, the anonymous share returned HTTP 404. [Confirmation](screenshots/n6-trash-confirmation.png) |
| N7 | PASS | Test upload and link against the untrusted listener showed the issuer, SHA-256 and Fedora trust commands. A synthetic session credential for that address let Test reach TLS. [TLS error](screenshots/n7-untrusted-test.png) |
| N8 | PASS | Nextcloud's Security page issued a manual app password. Storing it through the masked app form showed Signed in as put.gd lab. [Form](screenshots/n8-manual-signed-in.png) |
| N9 | PASS | Sign out showed Signed out. The Fedora device disappeared from Nextcloud's Devices & sessions. [Before](screenshots/n9-device-listed.png) · [After](screenshots/n9-devices-after.png) |
| N10 | PASS | The bare WebDAV address normalized to HTTPS, the test passed and Firefox displayed the region. History deletion returned HTTP 404. [Test](screenshots/n10-test-success.png) · [Firefox](screenshots/n10-pattern-in-browser.png) · [Confirmation](screenshots/n10-delete-confirmation.png) |
| N11 | PASS | Test offered Create folder. The retest passed using the matching nested public base. WebDAV DELETE returned 204 and a follow-up GET returned 404. [Create](screenshots/n11-create-folder-offer.png) · [Retest](screenshots/n11-test-success.png) |
| N12 | PASS | An HTTP link address was refused until Allow plain HTTP was checked. The HTTPS base and unchecked toggle were restored. [Refused](screenshots/n12-http-refused.png) · [Allowed](screenshots/n12-http-enabled.png) |
| N13 | PASS | CLI and MCP added a destination and started Login Flow. Firefox granted access. MCP tested, uploaded, shared, deleted and revoked the app password. The anonymous share returned 200 before deletion. [Receipt](nextcloud-agent.txt) |
| G1–G4 | Covered on k72 | The k72 worker owns the shared policy and host-key changes. |

## Findings

- **Product.** Configure SFTP with `/upload` and clear Link address. Select it as the default, record a short region and stop to open Review recording. Expected the output label to say Upload only. The review footer said **SFTP · Shared link**. Completion saved a path, and History showed the file without a share. This reproduction uses the candidate's new SFTP destination. [Review footer](screenshots/s9-review.png)
- **Test limitation.** The compact moving test clip uploaded before an in-flight cancellation could be issued. One upload attempt was made, as requested for the shared lab. The completed clip was removed.
- **Lab setup.** Private RPM extraction left the GNOME capture helper undiscovered. A reviewed DNF preview would have invalidated a pending offline transaction. I temporarily staged the matching RPM extension files in their system location and re-logged into GNOME to load version 25. The package inventory and offline update were preserved.
- **Test recovery.** The first WebDAV capture picked up the lab browser underneath the selector. I removed it, verified 404, and repeated the capture with only the synthetic pattern exposed. The evidence uses the second capture. The first attempt is in the local private artifacts.
- **Test recovery.** The first MCP result reader used the wrong SDK attribute name and failed after adding the destination. I corrected the reader, verified the existing profile and continued with that exact destination. The sequential annotation run returned `editor_active` after its first image. Fresh offscreen residents exported the remaining copies.

## Restoration

All eight owned uploads report removed in History. The nested SFTP directories and the WebDAV test folder were removed. Nextcloud's deleted synthetic uploads follow the tested trash-bin behavior. Nextcloud no longer listed the Fedora or manually generated f44 app credentials. The five test destinations were removed from the private put.gd configuration.

The exact system package baseline was verified. The lab CA was removed from the system store and Firefox NSS. The temporary browser association and Firefox profile were removed and the original Firefox association verified. The staged put.gd GNOME extension was removed and the original extension preferences were restored. The re-logged physical Wayland desktop reported AppIndicator active and the wall's VNC service active. The cleanup check passed and f44 was free at 13:33:22 UTC. [Restoration receipt](restoration.txt) · [Owned upload cleanup](history-cleanup.json)

The PR images were marked with the candidate's own offscreen editor using rectangle, arrow and text marks in `#D7263D`, with width 4 for strokes. [Annotated images](annotated)
