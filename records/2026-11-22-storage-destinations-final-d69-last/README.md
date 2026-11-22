# Final redaction labels and idle tray quit on d69

These checks ran on the physical Debian 13 desktop with KDE Plasma 6.3.6 and
KWin Wayland 6.3.6. The native Debian 13 CI job supplied the DEB
`26.1122.6476~dev+g0d2fe70ddf38`. The resident reported commit
`0d2fe70ddf38e16f4769d0f09135e72cec095fdf` and tree
`134ada1e96d020b55fbf5001b66ef1fc805d9188`, both matching the artifact manifest.
The DEB checksum matched on d69 and the isolated socket path was 38 UTF-8 bytes.
[CI run 45037852454](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45037852454),
[manifest](receipts/build-info-0d2fe70d.json),
[resident](receipts/native-resident-0d2fe70d.txt),
[DEB receipt](receipts/debian13-staging-0d2fe70d.txt)

| Row | Result | Observed |
| --- | --- | --- |
| F1 | PASS | SFTP was the default and its Link address was blank. After a live region capture and **Redact and upload**, the editor displayed **Upload only** beside its Upload button. [Route](receipts/F1-route.json), [prompt](screenshots/F1prompt.png), [editor](screenshots/F1editor.png), [receipt](receipts/F1-editor.json) |
| F2 | PASS | After setting SFTP's HTTPS Link address, the editor and the Review window for a 5.3-second screen recording displayed **Shared link**. [Link address](receipts/F2-route.json), [editor](screenshots/F2editor.png), [Review](screenshots/ReviewSharedLink.png), [Review receipt](receipts/ReviewSharedLink.json) |
| F3 | PASS | With the signed-in Nextcloud destination as the default, **Redact and upload** opened the editor and displayed **Shared link**. [Signed in](receipts/F3-signed-in.json), [route](receipts/F3-route.json), [editor](screenshots/F3editor.png), [receipt](receipts/F3-editor.json) |
| F4 | PASS | After a successful SFTP connection and upload test and with zero active operations, choosing **Quit put.gd** in the KDE tray exited the resident in 0.176 seconds. Its session socket was removed. [SFTP test](receipts/sftp-pre-quit-test.json), [idle state](receipts/F4-idle.json), [tray menu](screenshots/F4tray.png), [exit timing](receipts/F4-quit.json) |

The SFTP and Nextcloud captures used a synthetic redaction-list entry set to
Warn. Each capture found the entry, opened the Redact editor from the visible
prompt, and showed one suggested cover. The sessions were discarded after
checking their labels, and History reported zero items. [F1 prompt result](receipts/F1-prompt.json),
[F2 prompt result](receipts/F2-prompt.json), [F3 prompt result](receipts/F3-prompt.json),
[empty History](receipts/history-empty.json)

The SFTP password control was checked visually with a dummy character after
AT-SPI could not verify focus. The character was cleared before the protected
input was sent. One CI status poll ran about 20 seconds ahead of the
three-minute interval.

## Restoration

The nightly controller released d69 before testing. The Nextcloud destination
signed out and the isolated profile was cleared of test destinations. The SFTP
listing showed no d69 test files. Setup used a private DEB extraction, and
verification confirmed the original system package state of absent. The lab CA
was removed from system and Firefox trust, the temporary Firefox profile and
KWin entries were removed, and the URI handler file was restored byte for byte.
The lease passed cleanup and was released at 15:37:01 UTC. The lock status
showed d69 free. [Controller gate](receipts/nightly-controller-gate.txt),
[Nextcloud sign-out](receipts/nextcloud-signout.json), [destinations](receipts/removed-destinations.json),
[restoration](receipts/restoration.txt), [release](receipts/release.txt),
[lock status](receipts/lock-after.txt)
