# Sensitive text prompt acceptance on Kubuntu and Mint

PR [#1907](https://github.com/patrick-hudson/put.gd-desktop/pull/1907) implements issue [#1898](https://github.com/patrick-hudson/put.gd-desktop/issues/1898). Both physical desktops ran the platform DEB from [CI run 45060225088](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45060225088). The installed package version was `26.1122.6541~dev+g882c74fd1465`. Each resident reported commit `882c74fd146549d1e78ba2a43863f639386d0f88` and tree `d316f99f5f93353293c37212b73d80aa6e5b13f4` in `diagnostics.build`.

- **k72** · Kubuntu 26.04, Plasma 6.6.6 on Wayland, distro Qt 6.10.2. The region source reported the native `kde-wayland` adapter and KWin ScreenShot2.
- **m74** · Linux Mint 22.3, Cinnamon 6.6.9 on X11, distro Qt 6.4.2. The region source reported the native `cinnamon-core-x11` adapter.

The hotkey selected a rectangle in an owned synthetic fixture window. Card numbers and keys or tokens were set to Warn in isolated settings. Keep a local copy was enabled. Each host published to a unique prefix in the authorized S3 test bucket. The shared images in the Firefox pictures were deleted during cleanup.

| Cell | k72 · Plasma Wayland | m74 · Cinnamon X11 |
| --- | --- | --- |
| 1. Prompt | **PASS** · [Full desktop](k72-prompt-full.png), [panel crop](k72-prompt.png) | **PASS** · [Full desktop](m74-prompt-full.png), [panel crop](m74-prompt.png) |
| 2. Redact and upload | **PASS** · [Notification](k72-notification.png), [Firefox](k72-browser.png), [archive and object checks](k72-operations.txt) | **PASS** · [Notification](m74-notification.png), [Firefox](m74-browser.png), [archive and object checks](m74-operations.txt) |
| 3. Open in editor | **PASS** · [Two suggested marks](k72-editor.png) | **PASS** · [Two suggested marks](m74-editor.png) |
| 4. Upload anyway | **PASS** · [Uncovered published image matches archive](k72-operations.txt) | **PASS** · [Uncovered published image matches archive](m74-operations.txt) |
| 5. Cancel with Escape | **PASS** · [Local-only result and archive](k72-operations.txt) | **PASS** · [Local-only result and archive](m74-operations.txt) |
| 6. Move and raise | **PASS** · [Drag, obscure, tray click](k72-move-raise.png) | **PASS** · [Drag, obscure, tray click](m74-move-raise.png) |
| 7. Large text | **PASS** · [1024 × 768 at app text scale 1.75](k72-large-text.png) | **PASS** · [Cinnamon text scale 2.0](m74-large-text.png) |
| 8. CLI and MCP | **PASS** · [CLI](k72-cli.txt), [report-mode desktop](k72-report-mode.png), [official MCP SDK over stdio](k72-mcp.txt) | Outside this host's assignment |

Both dark and gold panels were frameless with the four buttons in one row. Clicking the primary button and, on a fresh capture, pressing Enter completed directly. Firefox opened the exact History link through the desktop portal. The public image and covered archive copy matched pixel for pixel. Each covered image had two opaque bands, and the separate `-original` archive copy had the same dimensions and no covers. Open in editor showed two suggestions before Upload. The independently fetched edited images contained both covers. Upload anyway preserved both warning matches as original pixels. Escape kept a local image with no remote request. A body drag moved each panel, the fixture window covered it, and a physical click on the tray icon brought it back.

Cinnamon used its native text scale 2.0 at 1920 × 1080. On k72 the candidate was restarted with the test text scale override `PUTGD_TEXT_SCALE=1.75` and the physical output changed to 1024 × 768. It displayed two button rows, with every label visible above the desktop panel.

On k72, both CLI and MCP waited in `sensitive_text_found` with one finding of each kind. Direct redact had no editing phase and published with `covered: {card: 1, key: 1}`. The edit branch reached `editing` and submitted. Upload anyway returned the original file byte for byte. Cancel returned a local-only item. The CLI returned `invalid_request` for the old `redact` choice.

The example with four repetitions of the same group fails Luhn. The scored runs used a Luhn-valid synthetic Visa test value built at runtime. Early launch attempts exposed the SSH environment's invalid display or runtime variables. The retry took native display variables from the active shell process and set the isolated runtime inside the systemd scope. The resolved Unix socket paths were 38 UTF-8 bytes. The CLI's first generated PNG only produced a card detection, so the scored CLI and MCP runs reused the original PNG from a region capture already proven to contain both findings. The first MCP harness incorrectly expected a JSON Schema enum and stopped before calling the tool. The retry used the declared string parameter and exercised the actual choices. No acceptance cell failed on the candidate, so no nightly regression comparison was needed.

Firefox was temporarily selected as the real default on k72 because the acquire-time HTTPS handler was ChatGPT. The original handler configuration was restored. m74 already used Firefox. Cinnamon notifications and Plasma notifications were captured with the fixture maximized. A fullscreen fixture triggered Plasma's notification suppression.

## Cleanup

The test credentials were imported into fresh native keychain entries using the existing stdin-only lab bridge. Only the disposable entries were deleted. The test profiles and local archives were removed after recording the checks. [Mint cleanup](m74-cleanup.txt) records the exact package restoration and clean release. [Kubuntu cleanup](k72-cleanup.txt) records the corresponding restoration and clean release.
