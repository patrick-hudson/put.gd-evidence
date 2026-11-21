# PR #1811 Upload click and double-click after a refused edit on Plasma

The AppImage from [manual CI run 44962802408](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44962802408) ran on Aurora Plasma Wayland. The package manifest, launcher and live resident agree on `26.1121.6189-dev+ga7a973dd5912`, commit `a7a973dd5912181a37c6ad97ff60b9f5a66cbf28` and tree `23765b962bc363fde7e8fef5883fbc0f3906fd3d`. The run succeeded. The resident used a private profile and a local-only archive. [Build identity](measurements/plasma-identity.json) · [CI run receipt](measurements/ci-run.json).

| Check | Result |
| --- | --- |
| Single Upload click after refused typed Until | Pass. Review remained open. The archive, history and operations stayed unchanged. |
| Upload double-click after refused typed Until | Pass. Both releases left review open with no new archive file, history entry or operation. |
| Right-click while left Upload press was held after refusal | Pass. Review stayed open, with no new archive file, history entry or operation. |
| Outside release, then Enter on focused Upload | Pass. The outside release did nothing. Enter created one local item. |
| Upload after valid typed Until | Pass. One completed operation, one history entry and one MP4. |
| Save a copy after valid typed Until | Pass. One valid MP4, with review still open. |

Select a redaction that spans 2–8 s. For the single click, type 0:01.0 into Until, press Upload and release after the resident refuses the edit. For the double-click, type 0:01.2 and deliver two native pointer presses at the same coordinates. The second press followed the first by 108 ms. The refusal arrived 17 ms after the initial press, before release. For the third gesture, type 0:01.4, hold the left press until refusal, press and release the right button, then release the left button. All three gestures kept the original cover and revision. The visible status read “Nothing was uploaded: a change wasn't applied. Check the edits, then upload again.” [Single click](measurements/single-click-refusal.json) · [Double-click](measurements/double-click-refusal.json) · [Right-click during left press](measurements/right-click-refusal.json) · [Annotated status line](pictures/plasma-upload-double-click-refusal.png).

Type 0:06.0 into Until and click Save a copy. The chooser saved one 12.567 s local MP4, applied the new endpoint and kept review open. [Save receipt](measurements/normal-save.json).

Type 0:05.0 into Until and click Upload with the native pointer. The completed operation produced one 12.567 s MP4 in the private archive. Decoded frames kept redaction at 4 s and restored the source at 6.5 s, confirming the typed endpoint was applied. [Completed upload and decoded samples](measurements/valid-upload.json) · [Archive and history observation](measurements/after-valid-upload.json).

For the outside-release check, use a fresh recording and a 2–8 s redaction. Type 0:01.8 into Until and press Upload until the edit is refused. Drag the pointer onto the picture and release. The original edit and archive stayed unchanged. Tab to Upload and press Enter. The unchanged edit produced one additional local recording under the existing recording operation ID. The read-only database check and MP4 probe confirmed the final result. [Outside release and Enter receipt](measurements/outside-release-enter.json) · [Durable archive verification](measurements/outside-durable.json).

Two fixture assertions needed correction. The raw outcomes and the reason for each correction are recorded. [Fixture attempts](measurements/harness-attempts.json).

The Aurora lease ran from 2026-11-21T23:52:32Z to 2026-11-21T23:56:07Z and passed its cleanup check. [Lab receipt](measurements/lab.json).
