# Sealed links acceptance: native desktops and inline destinations

CI run 45787632813, head 1ba3aa6b89d254462d56db938ff81f12df54664a.
Downloaded release packages: version 26.1126.7190-dev+g164e8a3af24c,
CI merge commit 164e8a3af24c46648b360be29cdfae30c1c48bad, gitTree
f8d601a3523b16c64cb5a1cfebf3bb41fb9c54f5 (matches PR head).
No local product build. All five native desktops reported this build.

- Cinnamon X11 Mint m74, GNOME Wayland Fedora f44 (AppIndicator active),
  KDE Wayland Kubuntu k72, KDE Wayland Debian d69, KDE Wayland Aurora
  (AppImage): Test S3 public passed, Seal mode On, editor and review kept
  open with agent-driven Seal toggle, actual native tray Capture region
  (sealed) uploaded with a v1 key fragment and History Delete removed it.
  Each prefix initially and finally empty. History list and gallery lock
  visible; independent QR decode matched on m74 and d69.
- Aurora actual Capture region & edit with SFTP HTTPS (not a file opened
  into the editor): selector drag, toggled Seal off/on, editor stayed open,
  uploaded sealed; menu Forget key visible, link removed after forget;
  destination deletion and folder absent.
- S3 public/presigned and R2 public small CLI --seal PNG/text, origin random
  HTML name, page SHA matches stored seal, clipboard exact, CLI open SHA
  matches, deletion verified. B2 public small CLI --seal and CLI-open
  SHA match; B2 file-version listing empty. SFTP HTTPS Test after pinned host
  key trust passed, production upload.files text/PNG both exact page SHA
  and random HTML; folder absent. AppImage resident's executable did not
  expose a CLI sibling for this route.
- f44 first harness run omitted the actual Wayland socket from gnome-shell's
  environment, Qt aborted before resident initialized; corrected invocation
  confirmed the native Wayland socket and every row then passed. Another
  optional f44 region retest's S3 connection timed out during the d69 GB
  upload, after earlier success; prefix verified empty; Aurora actual
  region-editor test passed independently.
- Public split video first passed CLI and Firefox actual playback. Chrome
  showed a blank control at 0:00 even after play clicked; investigation
  and independent destination deletion results follow in a later record.

## Picture captions

All annotated pictures are native framebuffer crops annotated with the
candidate put.gd editor's editor.apply rectangles/arrows and editor.saveCopy.
No link fragments, credentials or passwords included.

| Picture | Build shown | Caption |
|---|---|---|
| annotated/card-before.png | 26.1125.7045~nightly | Debian, Connection test with no Sealed links card |
| annotated/card-after.png | 26.1126.7190-dev+g164e8a3af24c | Debian, Sealed links mode On after HTTPS Test passed |
| annotated/passphrase-row.png | same candidate | Aurora, On with a passphrase, passphrase input and Save |
| annotated/editor-seal.png | same candidate | Kubuntu, editor Seal beside Upload |
| annotated/capture-region-editor.png | same candidate | Aurora, actual Capture region & edit, SFTP destination, Seal toggle stays open |
| annotated/review-seal.png | same candidate | Kubuntu, recording review Seal beside Upload |
| annotated/tray-row.png | same candidate | Kubuntu, actual desktop tray Capture region (sealed) |
| annotated/history-list-lock.png | same candidate | Kubuntu, lock on list row |
| annotated/history-gallery-lock.png | same candidate | Kubuntu, lock on gallery tile |
| annotated/history-forget-key.png | same candidate | Aurora, Forget key in actual item menu |
| annotated/notification.png | same candidate | GNOME, Sealed link copied after tray capture |
| annotated/firefox-split-viewer.png | same candidate | Debian Firefox, decrypted 1 GB moving clip playing at 0:07 |
| firefox-split-play1.png and firefox-split-play2.png | same candidate | Distinct actual playback frames 0:03 and 0:07, 100-second clip |
| chrome-split-play1.png and chrome-split-play2.png | same candidate | Chrome, same decrypted split link, black player 0:00 with no duration |
