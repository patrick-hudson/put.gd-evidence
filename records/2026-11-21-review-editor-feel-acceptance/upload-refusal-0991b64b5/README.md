# PR #1811 Upload after a refused edit on Plasma

The AppImage from [manual CI run 44961028162](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44961028162) ran on Aurora Plasma Wayland. The package manifest, launcher and live resident agree on `26.1121.6186-dev+g0991b64b5dff`, commit `0991b64b5dffeeda2e2692968d27736b1f0e3b4b` and tree `a4ca3fa02d9935dd95c7a1730c04395e0d76ef66`. The run published this AppImage before it ended cancelled. The resident used a private profile and a local-only archive. [Build identity](measurements/plasma-identity.json) · [CI run receipt](measurements/ci-run.json).

| Check | Result |
| --- | --- |
| Upload after refused typed Until | Pass. Review remained open. The archive, history and operations stayed unchanged. |
| Upload after valid typed Until | Pass. One completed operation, one history entry and one MP4. |

Select a redaction that spans 2–8 s and type 0:01.0 into Until. Press Upload with the native pointer, hold until the resident refuses the edit and release. The refusal arrived 37 ms into the press. The revision and the cover stayed unchanged and the visible status read “Nothing was uploaded: a change wasn't applied. Check the edits, then upload again.” [Refusal and storage observations](measurements/refusal.json) · [Annotated status line](pictures/plasma-upload-refusal.png).

Type 0:05.0 into Until and click Upload with the native pointer. The completed operation produced one 12.667 s MP4 in the private archive. Decoded frames kept redaction at 4 s and restored the source at 6.5 s, confirming the typed endpoint was applied. [Completed upload and decoded samples](measurements/valid-upload.json) · [Archive and history observation](measurements/after-valid-upload.json).

The Aurora lease ran from 2026-11-21T23:29:56Z to 2026-11-21T23:30:57Z and passed its cleanup check. [Lab receipt](measurements/lab.json).
