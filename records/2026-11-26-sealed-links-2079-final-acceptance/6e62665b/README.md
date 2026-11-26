# Follow-up native acceptance — 6e62665b

CI run 45814758171, PR head 6e62665bc132e4456e8607adbb853419429d68a8.
AppImage 26.1126.7212-dev+gcca4b55d901b, SHA-256
3c3ac857aba3163b703420de4746fd768c3c80b8373ad67026cf079fec074136.
CI merge commit cca4b55d901b00c5c46af4677d20c6df58d702a2, gitTree
9da4c0ddf317790c8c0a9b872f1706b395ee01d1. The PR head tree is
c05d94698d7c2ba54bedd796e841bf5a8f3c60b3; the CI merge has both
the exact PR head and new nightly parent cb8fccf670dd40040d2d100a1c92adfbc624f72b.
Every native resident reports the CI merge manifest above. No local builds
or product code changes.

Aurora Fedora 45, native KDE Plasma Wayland, mounted production CLI from
the exact AppImage, Firefox Flatpak 161.0. The previous Chrome viewer
results stand by coordinator direction: the viewer hash was unchanged.
All desktop and quiet leases were free before the 12:15 UTC cutoff.
The nightly Aurora lease was released at 12:56:36 UTC; the manual round
started at 12:58:19 UTC, after it had finished on this host.

## Rows

- **Test + cancel: PASS.** S3 public Test sealed check passed. Second
  Test observed event step=seal/status=running and requested Cancel.
  Setup terminal state failed with error code cancelled, connectionPassed
  true, result seal.state cancelled. The previous connection and seal
  checks both remained passed; independent prefix empty.
- **Tray and editor: PASS.** Actual native tray Capture region (sealed)
  selected and region drawn. Correct key suffix, Copy link clipboard
  exact, real Firefox portal viewer opened/decrypted and displayed capture.
  Editor helper Seal off/on and inspect stayed open, submitted and uploaded
  inline, Copy link exact, Firefox displayed synthetic PNG. Both History
  deletes terminal and removed.
- **Cancel while sealing: PASS.** Same 1,061,463,118-byte test video,
  observed item.phase=sealing, requested Cancel; state cancelled with
  message "Upload cancelled before it started. Select Retry upload to
  try again." Operation artifact folder contained only original artifact
  UUID and _manifest.json; no stray sealed page/data files. Prefix empty.
- **Private S3: PASS expected refusal.** Coordinator replaced unreachable
  seal_needs_link row with actual supported capability refusal. Set
  captureDefaults.publicationMode=private, requested sealed upload;
  terminal failed with unsupported_capability in resident log and plain
  notification "this destination doesn't support private uploads. Change
  Sharing or Destination in Settings → Capture." Retry same failure and
  isolated prefix empty both times. The harness originally selected empty
  item-level error rather than the operation-level error; exact refusal
  code is proven by private-refusal-resident-log.json.
- **Passphrase: PASS on fresh resident.** First mixed-control sequence
  had prior external Capture settings patches (private then share); mode
  selection acknowledged but profile seal wasn't persisted, setup job
  returned seal_passphrase_unset. On a fresh resident, same UI mode action
  persisted mode=passphrase and session reference; setup store completed,
  inline upload and clipboard succeeded. Actual Firefox wrong passphrase
  gave "That passphrase doesn't open this link."; right passphrase showed
  exact plaintext. History delete completed. No direct settings fallback
  needed. The original sequence-specific refusal was not reproduced on
  the fresh path.
- **Additional bounded external revision check: PASS.** With Settings
  Destinations open, an external settings.patch changed the selected S3
  label. Revision ca8d4030... -> 7c049f5c...; UI mode Passphrase saved
  over the changed profile, revision 1c752b7e..., preserved external label,
  persisted seal mode/reference. Typed synthetic passphrase into visible
  masked field and clicked Save. Actual green "Seal links passphrase saved."
  message, typed value cleared, passphraseLoaded true, persisted mode/reference
  and external label unchanged. The success matches real stored session
  passphrase state. No silent lost save in this bounded scenario.
  Request IDs and full revisions in conflict-results.json.
- **1 GB split: PASS for upload, CLI, Delete.** Same original SHA-256
  baade7cf41e68b458c6c904a2208286663677c8774e2755ad806182069b2d3d3,
  1,061,463,118 bytes. Fresh seal upload completed/copied; two same-stem
  origin objects, mounted CLI open from stdin restored exact SHA. Terminal
  History Delete completed, remoteStatus removed, sealDataStatus removed,
  zero objects/versions/unfinished multipart. Firefox portal opened and
  reached 66% decrypt in first attempt before tester's 80-second controller
  window timed out; subsequent extended-window retest recorded separately.

## Pictures

All pictures in this folder show the native 26.1126.7212-dev+gcca4b55d901b
build (no link fragments, passphrases, or credentials shown).
Actual screenshots, not mocks.

- tray-menu-sealed-row.png: native tray row; Action failed heading is
  the deliberately tested Private refusal, not failure of tray upload.
- tray-inline-final.png: actual captured image decrypted in Firefox.
- editor-inline-final.png: actual edited synthetic PNG decrypted in Firefox.
- private-refusal-notification.png: expected capability refusal.
- passphrase-wrong-clean.png, passphrase-right-check.png: exact wrong
  refusal and correct opened text.
- conflict-after-save.png: real Settings Save confirmation after external
  profile revision change.

Fresh Firefox profiles showed their first-run modal; test opted out of
diagnostic/interaction data before continuing on disposable profiles.
Only the exact test profiles were retired, MIME handlers restored.

## Extended Firefox witness and closure

PASS: a fresh second 1 GB split upload on the exact same package, with
a 240-second visual-controller window, opened via the real default
browser portal and decrypted fully in Firefox. Native playback was
witnessed at 0:04 and 0:09, distinct frames, screenshots large-play1.png
and large-play2.png. Terminal History Delete removed both objects,
sealDataStatus removed, prefix empty. The first shorter window's timeout
was a tester scheduling limitation, not a product failure.

Independent cleanup inventory: four exact synthetic S3 prefixes,
current objects 0, versions 0, unfinished multipart 0. No manual
removal necessary in final sweep. No other objects, bucket policies or
versioning settings changed. All test private browser profiles and
desktop handlers absent, original browser associations restored,
resident and helper exited, no installed putgd package (AppImage only).
Aurora verified desktop release 2026-11-26T13:19:18Z and quiet lease release
13:19:19Z. Other concurrent nightly work was left untouched.
