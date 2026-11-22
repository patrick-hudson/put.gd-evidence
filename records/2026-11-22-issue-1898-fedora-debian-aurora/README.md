# Sensitive-text prompt acceptance on Fedora, Debian and Aurora

Tested 2026-11-22 on the three physical build machines. The candidate came from CI run [45060225088](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45060225088). Every running resident reported commit `882c74fd146549d1e78ba2a43863f639386d0f88` and tree `d316f99f5f93353293c37212b73d80aa6e5b13f4`.

| Host | Native session | Candidate asset | SHA-256 |
|---|---|---|---|
| f44 | Fedora 44, GNOME and Mutter 50.6, Wayland. AppIndicator enabled and registered. | Fedora 44 RPM | `e4b65655207744c1243f41f78decc734194792b731b9772a67d0d21f5fada0e0` |
| d69 | Debian 13, Plasma and KWin 6.3.6, Wayland | Debian 13 DEB | `29f04cb23ffe3b6c5b11dd58bd984f17e5ab5dc020e60c9c532502e07a6ba26a` |
| aurora-amd | Aurora Fedora 45, Plasma and KWin 6.8.2, Wayland | x86_64 AppImage | `090477542f278bf8a95ed42e06c761b025377ad3204fa1149c1aaa4716b209d9` |

| Cell | f44 | d69 | aurora-amd |
|---|---|---|---|
| 1. Prompt with four buttons, theme and initial focus | PASS | PASS | PASS |
| 2. Redact and upload, notification, default Firefox and both archive copies | PASS | PASS | PASS |
| 3. Open in editor with two marks, then upload | PASS | PASS | PASS |
| 4. Upload anyway, original pixels | PASS | PASS | PASS |
| 5. Escape, local copy and no upload | PASS | PASS | PASS |
| 6. Drag, cover and raise | PASS, notification Show | PASS, tray icon | PASS, tray icon |
| 7. Large text, complete labels and panel onscreen | PASS | — | — |
| 8. Four decisions through CLI and MCP, plus CLI rejection of legacy choice | — | PASS | — |

## How the results were checked

- All GUI captures used Ctrl+Shift+1 and a pointer drag over a dedicated fixture. The fixture used a checksum-valid test card number and the documented example AWS access key, assembled at runtime. An initial fixture repeated the first group of the card number and failed its checksum. The corrected fixture produced one finding of each kind.
- The primary button completed directly. Enter on a second prompt also completed directly and produced the captured **Covered 1 card number and 1 key or token.** banner. History's Open link action opened the actual desktop default browser through the portal. The original and covered archives were both read from disk. For every host, the public GET matched the covered archive's bytes, the browser showed both black boxes and the image uploaded from the editor matched the covered result. Upload anyway kept the original text visible. Escape saved a local-only item.
- d69's active session and display wall were Plasma Wayland. The previous GNOME X11 session was closing, so the Debian desktop results apply to Plasma. Debian's HTTPS handler was temporarily set to Firefox ESR for the link witness and restored to the original handler afterward.
- GNOME's 2.0 text setting enlarged the fixture and system chrome while the Qt labels stayed the same size. Restarting the candidate with `PUTGD_TEXT_SCALE=1.75` enlarged the prompt. All four labels fit on the native 1920×1080 display. A separate attempt to use a narrower logical display at 200% monitor scale disrupted the VNC feed. The lab wall recovered at the original monitor scale. That attempt did not establish narrow-screen wrapping.
- The Debian CLI and locked MCP helper each exercised `redact_upload`, `edit`, `upload` and `cancel` in report mode. Direct redaction passed from the pending choice to upload without an editing phase and counted both covers. Edit entered editing and was submitted. Upload returned the source PNG bytes. Cancel left a local-only result. The CLI returned `invalid_request` for the old `redact` choice. The first MCP harness used the wrong SDK result attribute. The four pending calls were cancelled by exact ID, the attribute was corrected and all four were rerun.

## Cleanup

The run used isolated configuration and session-only credentials. It created no persistent keyring entries. The exact S3 keys were deleted and HEAD-checked after deletion, including the extra Fedora upload from the interrupted screen-scale attempt. The deletion counts were five on f44, ten on d69 and four on aurora-amd.

Fedora's nightly RPM `26.1122.6439~nightly-1.fc44` and original scale settings were restored. Debian's candidate DEB was purged to restore its original uninstalled state, and Aurora's candidate AppImage and scratch files were removed. The three locks passed the cleanup checks.
