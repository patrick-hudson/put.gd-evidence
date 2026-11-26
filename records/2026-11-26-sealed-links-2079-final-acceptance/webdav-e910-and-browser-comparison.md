# e910 WebDAV confirmation and Chrome comparison

The follow-up Debian CI package was run 45789606403, head e910ab333f91f710e818ba5d69a638d57403e5af, CI completed successful. Resident reported version 26.1126.7192-dev+gf977a6911c14, gitTree 58f251154db252458bb8d6ff804de1ed5bf19a23, exact PR head tree. No local build.

## WebDAV deletion

1,061,463,118-byte moving H.264 file uploaded in split form with two same-stem random objects. CLI open - restored the original SHA. History deletion terminal remoteStatus removed, progress done; delete.inspect reported sealDataStatus kept. Only the BIN was left. Compared its SHA-256 to operation.inspect's stored data artifact: identical. Explicit DELETE of that isolated test object returned 204, independent PROPFIND empty; folder DELETE succeeded and final PROPFIND 404. This intentionally differs from S3/R2/B2: server does not supply strong ETag for large WebDAV files; nightly had the same identity limitation on ordinary files.

A separate 338,946,758-byte moving segment reproduced the third-party server ETag limitation and the same outcome. Native actual History item menu → Delete from destination opened the confirmation. **annotated/webdav-kept-data-confirmation.png shows e910 build 26.1126.7192-dev+gf977a6911c14**, with the final text about the retained file, its encrypted content, and a saved page plus full link remaining usable until the file is removed. Screenshot crop annotated in the put.gd editor. The second isolated test data file and folder also SHA-verified and deleted.

## Chrome large split comparison on 1ba3aa6b

Original file: H.264 Constrained Baseline level 5.0, 1920×1080 yuv420p, 30fps, 100s, 1,061,463,118 bytes. Faststart: moov offset 32, mdat offset 18,914. In Chrome 158.0.8127.88 directly opened via file://, it played (0:22 to 0:25) with visibly different frames in chrome-original-play1.png and chrome-original-play2.png. Same Chrome's sealed page remained at blank 0:00 even after play was clicked. The viewer said the file was decrypted. In chrome://media-internals selected its sole blob player; only created/origin/frame/title/blob URL events, no pipeline error or initialized decoder/track/resolution status. See sanitized chrome-media-internals-summary.json. Firefox on the same sealed link played the full-size file. Nightly has no sealed viewer, so cannot reproduce this sealed-viewer symptom; the original local video demonstrates the codec is supported.

The first S3 split's cleanup poll returned on page progress done while remoteStatus was still deleting. One isolated object remained and the test cleanup removed it; final prefix empty. This was a premature test poll, not proof of product deletion failure. Recheck waits for terminal delete.inspect.

## Additional native tray/provider results

The 1ba3aa6b AppImage's mounted production putgd-cli was discovered under the actual resident process. SFTP HTTPS and WebDAV HTTPS CLI --seal PNG/text both passed, random names and origin page SHA matched; WebDAV actual clipboard matched. Native tray Capture region (sealed) on SFTP, WebDAV, R2 public, S3 presigned and B2 public completed with sealed History and correct key fragment; all isolated prefixes/folders verified empty or absent. These supplement the all-five-desktop S3 public tray results.

Phone: T3 device access disabled; adb and emulator absent on all five physical systems. Optional putgd-mcp helper not installed or configured on these desktops.
