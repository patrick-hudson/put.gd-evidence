# Encrypted link rename and recording follow-up

PASS, native Aurora Fedora 45 KDE Plasma Wayland, Firefox Flatpak 161.0.
CI run 45841878505, requested head a85f5ad4e4d1f1b2573353d894d61e19e78e7689.
AppImage 26.1126.7219-dev+g22e336024933, artifact SHA-256
850184c21aaa052cf2153c5dc0e649d353091f2a4d355233fd5fa890ec01576e.
Resident gitCommit 22e336024933a7841ee5c756ac671d1b6880025b,
gitTree 62207350f359318ab637e1ca70b17882af6877da. CI merge parents were
cb8fccf670dd40040d2d100a1c92adfbc624f72b and the requested PR head.
PR head tree 0c846e45e684459f20f6283370b9ed5420b553f9; CI merge
tree differs due to advanced nightly parent, exact requested run's package.
No local product builds or source changes.

| Row | Result | Witness |
|---|---|---|
| S3 public connection and encrypted check | PASS | setup.inspect encrypt.state passed, cleanup removed; ui.encryptedLinks inspect and mode on succeeded. |
| Real renamed tray | PASS | Capture region (encrypted) selected, drawn region, actual notification Encrypted link copied, History encrypted=true and correct v1 fragment, clipboard exact, Firefox via portal displayed image with Encrypted with put.gd footer. |
| Native recording review | PASS | Real 11.7-second region recording, recording.start and stop, state reviewing; recording.review encrypt off/on and operation.encrypt succeeded. Visible review Encrypt toggle; real Upload button clicked. History encrypted=true, inline, correct key fragment. Firefox real player advanced 0:03 to 0:08 of 0:12. The captured settings region was largely static; time advancing and pause control establish playback, not changing-frame proof. Captured credential fields were empty or masked, no revealed values. |
| CLI open | PASS | Mounted production CLI open from stdin restored exact finalized recording SHA: 159a902156d44cbbad58bcc5441730ba7ea2af242f159b2d886040bc85e4c208, 189064 bytes. |
| History label and Delete | PASS | Native tooltip on selected recording shows Encrypted. Uploaded · Shared link. Terminal History Delete remoteStatus removed, progress done, journal completed, origin empty. |
| Renamed CLI upload switch | PASS | Additional synthetic text uploaded using putgd-cli upload --encrypt, completed/copied encrypted inline, correct key fragment; terminal History Delete removed it. |

All images in this folder were captured on 26.1126.7219-dev+g22e336024933.
The three annotated screenshots used the exact installed candidate's
actual editor.apply rectangle and arrow and editor.saveCopy (see
annotation-results.json). The card shows name Encrypted links, mode On,
passed connection check. The tray row shows Capture region (encrypted).
The recording review controls show Encrypt beside Upload. Other pictures
show native notification, actual Firefox inline image, two distinct
playback times, and the actual History tooltip. No key fragments or
revealed credentials in pictures or logs.

Initial short attempt: the quiet lease was already held by another
session, but the test shell erroneously continued into a short desktop
Test. Stopped the resident promptly before capture/recording, prefix
zero, released desktop at 14:59:04 UTC. A wheel scroll over the mode
control had changed its visible selection; that screenshot is not the
accepted witness. Once the other quiet lease was released, acquired
both leases and restarted on a fresh isolated profile. Final test passed.
The first attempt is retained in initial-short-test.json.

Independent final inventory of both exact S3 prefixes: zero current
objects, versions, and unfinished multipart uploads; final sweep removed
nothing. No bucket policy/versioning or other objects changed. Private
Firefox profiles and temporary desktop handler absent; original MIME
restored, no resident/UI helper, no installed putgd package. Desktop and
quiet leases both released 15:03:45 UTC.
