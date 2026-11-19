# Destination connection status on k72

All eight checks passed on the physical k72 desktop on 2026-11-19. The machine ran Kubuntu 26.04, Plasma and KWin 6.6.6 on Wayland, and Qt 6.10.2. The active session was unlocked and the resident reported the `kde-wayland` adapter. The window actions used the existing wall VNC server over its host loopback, and the screenshots show the actual Destinations row cropped on k72 before export.

## Build identity

- PR head tested was `a86fbe882f94f8eb271b4b2b8b9e3a0f8824e6d5` from [CI run 44477653690](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44477653690) for [PR #1695](https://github.com/patrick-hudson/put.gd-desktop/pull/1695) and [issue #1692](https://github.com/patrick-hudson/put.gd-desktop/issues/1692).
- The `release-native-ubuntu26.04` artifact contained package `26.1119.5622~dev+g860a6b5b9458`. The DEB SHA-256 was `63f4b1ad8e38b27bd8215f59b8a12788418268d395440b93c8f30ae5631f7b9b`.
- Diagnostics before and after restart reported CI build commit `860a6b5b9458746990780bc8d5fef08b51c5675c` and Git tree `d9a194de6ac3243306fd4f2bb8fdf6cc4f29413b`. The tree exactly matched the requested PR head. [Running build diagnostics](build-diagnostics.json)
- The resident changed from PID 2489825 at 06:55:00 UTC to PID 2492330 at 06:57:06 UTC. The resident SHA-256 was `7ddca2c192973f9d64e1696bdd6d6004d1c7c238851e194439923b7c8837d76f`. Both launches used the extracted native package and a private XDG profile. The resolved app socket was 46 UTF-8 bytes and the native Wayland socket path was 24 bytes.

## Results

| Step | Expected | Observed | Result |
| --- | --- | --- | --- |
| 1. Add S3 destination and click Test upload and link | Connected. Status passed from test. | Connected. `passed` from `test`. [Screenshot](01-test-passed.png) | PASS |
| 2. Close all put.gd windows and reopen Settings | Connected. | The UI helper exited and the resident stayed up. The reopened row showed Connected with the same record. [Screenshot](02-reopen-settings.png) | PASS |
| 3. Rename destination | Connected. | The saved label changed to K72 renamed. The row still showed Connected with the same record. [Screenshot](03-rename.png) | PASS |
| 4. Quit and restart the resident | Connected with the same status record. | A new resident showed Connected and returned the identical state, source and fingerprint. [Screenshot](04-restart.png) | PASS |
| 5. Upload a real screenshot | Upload succeeds and the row stays Connected. | The screenshot of step 4 uploaded through the production file-upload path. Independent S3 HEAD matched its length, and the row stayed Connected. [Screenshot](05-real-upload.png) [Operation](screenshot-upload.json) | PASS |
| 6. Change the bucket and restore it | Ready to test, then Connected. | The saved alternate bucket showed Ready to test and `untested`. Restoring the original bucket brought back Connected and the original passing record. [Changed](06a-bucket-changed.png) [Restored](06b-bucket-restored.png) | PASS |
| 7. Store a wrong secret, test and upload | Ready to test, then Test failed, then the file upload fails. | The row showed Ready to test on key storage, Test failed after clicking Test upload and link, and Needs testing after the upload refusal. The file had `uploadStatus: failed` with `s3_permission_denied` and HTTP 403. [Stored](07a-wrong-key-stored.png) [Test](07b-wrong-key-test.png) [Upload](07c-wrong-key-upload.png) [Operation](wrong-key-upload.json) | PASS |
| 8. Restore the correct keys and click Test | Connected. | Connected with `passed` from `test`. [Screenshot](08-correct-key-retest.png) | PASS |

[Per-step destinationStatus readings from settings.get](destination-status.jsonl)

The destination was configured through the revision-checked session API. Credential changes went through the local Settings transport in keychain mode. Test, closing the window, the rename and bucket changes were driven in the real window. Step 5 used the actual cropped desktop screenshot as a synthetic upload payload. Step 7's aggregate operation was `partial`. Its one file's upload failed with the expected refusal.

## Cleanup

The screenshot upload was removed through the exact History ID and acknowledgement. The deletion item reported `removed` with provider phase `done`. S3 independently confirmed the object was absent, the isolated prefix was empty, and no incomplete multipart uploads remained. [Deletion receipt](deletion.json) [S3 verification](s3-cleanup.json)

The test destination and keychain entry were removed. The two test residents and their helpers exited, the extracted package and private test directories were removed, and the active test URL was cleared from the clipboard. The previous clipboard value was not recorded. The initial package-manager state was `rc` for putgd `26.1118.5396~dev+g31de163ea8cf` with no resident. Both conditions were verified again after cleanup. The verified-clean desktop lock was released at 08:00:27 UTC.

## Recovered setup and tooling attempts

An initial package check raced the transfer. The completed copy matched the local SHA-256 before extraction. A settings patch using two unrecognized preference names was rejected. The corrected patch used `launchAtLogin` and `notifications`. A preliminary bucket-edit click landed on the preview text and changed nothing. The field edit was then verified through the saved configuration.

The wrong-key operation assertion initially looked at the aggregate state. The saved item state and HTTP refusal were verified from the same operation. The first upload-cleanup script stopped before confirmation because it looked for an ETag under the object reference. The corrected script checked the receipt's concurrency token against S3's HEAD ETag before confirming deletion.
