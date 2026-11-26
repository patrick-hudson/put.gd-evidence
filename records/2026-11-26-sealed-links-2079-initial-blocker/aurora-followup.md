# Aurora native KDE Wayland — WebDAV results

The CI AppImage from run 45778610390 was launched on the native Aurora KDE Wayland desktop, with isolated XDG runtime paths (64 and 65 bytes) and the same build tree and version as the Debian trial: 26.1126.7184-dev+g088b612dfe44 / f3552a236750367d09c2ad27fefe29eab9cb8852. The lab CA was supplied to the test process; no system trust change. All files and credentials were synthetic or read in-process from protected lab inputs.

| Row | Result |
| --- | --- |
| HTTPS WebDAV Test + seal | Pass twice, probe cleanup removed |
| Seal links Off → On | Pass via ui.sealLinks, native card visible |
| Text and PNG sealed | Pass twice each through upload.files and live WebDAV, copyStatus copied, History fragment pattern correct |
| Actual notifications | Pass — native 'Sealed link copied' visible twice |
| Passphrase mode and field | Visible; immediate direct store after agent mode change raced auto-save and was refused; entering a generated passphrase through focused masked Settings field and Save passphrase succeeded, subsequent upload completed with passphrase required |
| History Copy link, QR save, Forget key | API calls passed; Forget key made link unavailable; QR contents and clipboard were not independently decoded |
| Delete from destination | All five uploaded artifact records reached remoteStatus removed and progress done |
| Plain HTTP link | Pass (expected refusal): clear HTTPS explanation, probe cleanup removed |
| Native editor toggle | Blocked by editor_exit after opening the editor on a synthetic PNG; exact nightly comparison pending |

The first HTTP row attempt failed in the harness because replacing a profile ID left action routes referring to the old ID. Retest with the same profile ID succeeded. This is not a product failure. Both created DAV collections were independently listed as empty after application deletions; HTTP DELETE of each empty collection returned failure, so the tester used exact `rmdir` inside the disposable lab WebDAV container and verified each path absent. Both desktop locks released verified-clean (08:23:58 and 08:26:36 UTC).

## Visual witnesses

These are unannotated crops from the native display at the candidate build stated above. The requested editor annotations and before/after comparison are not complete.

- [Sealed links card, On](aurora-seal-card.png)
- [Passphrase mode and row](aurora-passphrase-row.png)
- [Sealed link copied notification](aurora-sealed-link-copied.png)
- [Editor failure notification](aurora-editor-error.png)

See the two JSON files for sanitized IDs, outcomes and cleanup states. No live link keys, passphrases or upload tokens are included.
