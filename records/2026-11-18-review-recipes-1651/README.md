# Recording review recipes on Cinnamon and Plasma

Lab-only fix for #1651 at `ee14bf560e6f6ccd6cd6df559d2ab483eb835051`. The tests ran the #1635 Debian 13 and Ubuntu 24.04 packages from CI run `44287865139`. On both physical desktops, the running app reported version `26.1118.5424-dev+g652b83781a90`, commit `652b83781a9021ff7a9c6bc25687cffcf2958e9f`, and tree `ebb93c833833c9edc2a4c8236e06002e743264a2`. The catalog came from that same CI run.

| Recipe | m74 · Cinnamon X11 | d69 · Plasma Wayland |
| --- | --- | --- |
| Playback and speed | [Pass](m74/live2-receipt.json) | [Pass](d69/live2-receipt.json) |
| Cut flow | [Pass](m74/live2-receipt.json) | [Pass](d69/live2-receipt.json) |
| Trim | [Pass](m74/live2-receipt.json) | [Pass](d69/live5-receipt.json) |
| Covers and setCoverEdge | [Pass](m74/live3-receipt.json) | [Pass](d69/live5-receipt.json) |
| Format | [Pass](m74/live2-receipt.json) | [Pass](d69/live5-receipt.json) |
| Status actions | [Pass](m74/live1-receipt.json) | [Pass](d69/live4-receipt.json) |
| Save a copy | [Pass](m74/live1-receipt.json) | [Pass](d69/live4-receipt.json) |
| Advice | [Pass](m74/live1-receipt.json) | [Pass](d69/live4-receipt.json) |
| Resize and folded Edits | [Pass](m74/live2-receipt.json) | [Pass](d69/live5-receipt.json) |

Each recipe captured real moving and frozen desktop controls. Playback, native edit input, chooser acceptance, and decoded export checks ran against the installed app. The surface driver marks visual comparisons to the synthetic catalog for review when the live captured content differs. The table reports the audited functional results.

## Chooser and recovery

On m74 the portal timed out and the driver bound the live Qt fallback before typing. On d69 AT-SPI exposed only the app’s hidden modal blocker for the portal request, so the review fixture used the Qt chooser. The Plasma recipe pastes the synthetic filename once into the verified Qt field and reads it back. KWin gave keyboard focus to a separate Qt completion surface during character-by-character input. [KWin witness](d69/chooser-kwin.jsonl). The save path was verified after real input, and Copy path and Dismiss were checked in the review. The retry and Details recipes induced a real failed chooser export, restored the original working media, and decoded the retry. Details closed with Escape and its own Try again button started the next export.

## First attempts and corrections

- The Debian profile initially refused Wayland geometry. The profile now uses the read-only KWin witness. The d69 accessibility launcher announced a socket that no longer existed. The stale launcher was replaced under the desktop lock and the native accessibility registry responded.
- The first trim recipe exported successfully but read the Right-arrow result too early. The reruns give the picture keyboard focus and wait for the new playhead position. The cover recipe restores picture focus after export before checking Delete.
- FFmpeg rounded an odd YUV crop before the RGB conversion. Converting first restored exactly 25,773 decoded bytes, compared with 25,200 before the correction. The covered pixel mean was 0.2, compared with 140.6 before the cover. [Retained-export replay](d69/odd-crop-replay.json).
- HEVC output contained the encoder vendor URL. Two synthetic clips were quarantined by the first receipt audit. The reruns retain raw media in a separate private directory, and the receipt boundary still audits every published file.
- The d69 live2 batch ended after Cut flow to release the desktop for another campaign. Its interrupted Trim rows were replaced by the completed return run.

## Contracts

`python3 tools/ci/contracts.py lab` passed. The CI surface pytest set passed with 446 passed and one skipped. The command was `python3 -m pytest -v tests/desktop/test_surface*.py tests/desktop/test_review_adversarial.py --junitxml=build/contracts/surface-tests.xml`.
