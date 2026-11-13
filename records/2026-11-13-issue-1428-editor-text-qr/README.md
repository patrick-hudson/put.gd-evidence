# Issue 1428 item 5: editor Copy text, Quick redact, Show QR code (catalog renders)

Synthetic `putgd-ui-catalog` renders from pull request #1441 (`feat/text-editor`), built on k72 (Kubuntu 26.04, Qt 6.10.2, GCC 15.2), offscreen. They show design and widget behaviour, not desktop support. The pink boxes call out the new controls; nothing else was edited.

| File | State |
| --- | --- |
| `editor-copy-text.png` | Copy text tool (G) after Blur behind its own separator; selected words tinted; the panel with its state, Copy selection, Copy all text, the note and a code row (dark) |
| `editor-quick-redact.png` | Quick redact in the Redact panel with its permanent "Suggestions only" line, after email, phone and IP addresses were redacted (light) |
| `history-inspector-qr-and-copy-text.png` | History inspector: Show QR code and Copy text in the action row (icon-only at this width; dark) |
| `history-qr-code-window.png`, `history-qr-code-window-light.png` | The Show QR code window: black on white in both themes, 15 px per module for a version 3 code |
| `qr-short-link-export.png`, `qr-longest-link-export.png` | put.gd's exported PNGs for a 34-byte link and the 2,331-byte longest link; ZXingReader 2.3.0 and zbarimg 0.23.93 on d69 read each back to the exact link |

The editor renders use a fake recognition backend that returns the drawn words; the text is synthetic.
