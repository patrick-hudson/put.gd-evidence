# Quick redact line-end token recheck after review for PR #1863

Rechecked the installed Ubuntu 24.04 DEB on the physical Linux Mint 22.3 Cinnamon X11 builder `m74`. This pass used the native candidate from commit `aa202c7a634c0ec4e789aea5709414bc282a225d` and verified source tree `1eee62d523786233134010ebab9aec49c1141008` against `diagnostics.build` before taking captures. The full CI run completed successfully. [Candidate CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44994509136).

The comparison for the earlier candidate and the published nightly remains in the [original acceptance record](https://github.com/patrick-hudson/put.gd-evidence/blob/7463304c091b9a8c74591de386e7124a7dfe653e/records/2026-11-22-pr-1863-quick-redact-line-end/README.md). This recheck exercised the editor Quick redact path on Mint. It did not rerun nightly, case 2, Kubuntu, auto-redact or upload.

The original xed, xterm and Firefox fixtures were repeated with the same display settings. The dot-break fixture uses soft break opportunities after the JWT dots in Firefox. The long fixture uses one logical xed line with a 731-character synthetic JWT. The loose-spacing fixture visibly wraps `edc"` to the next visual line of a 64-character hex string at 2.2 CSS line-height.

Each case has the put.gd desktop capture cropped to the fixture, the exported redacted PNG, the five category counts, mark rectangles, and the independent pixel check. `inspect-before.json` stores OCR words as reconstructible `textPieces` arrays to keep synthetic tokens split in the text files. A wrapping match can have one rectangle per visual row.

## Results

The installed package was `26.1122.6373~dev+gaa202c7a634c`. The Ubuntu 24.04 DEB SHA-256 was `c19d237a30c6089fbb6502e1cf2bb93e4f6a9afcc0df10cfa07ecea05db626ab`, verified both before and after transfer. The private session socket path was 40 UTF-8 bytes.

| Case | Result | Nonzero counts | Visible redaction rectangles |
| --- | --- | --- | ---: |
| Token, cards and signing hex | [Pass](m74/recheck/1/pixels.json) | 2 key, 2 card | 4 |
| Token and AWS key | [Pass](m74/recheck/3/pixels.json) | 2 key | 2 |
| Token and plain words | [Fail](m74/recheck/4/pixels.json) | 1 key | 1 |
| Token, right card and distant card | [Pass](m74/recheck/6/pixels.json) | 1 key, 2 card | 3 |
| Unlabelled three-row JWT | [Fail](m74/recheck/5-jwt/pixels.json) | None | 0 |
| Labelled three-row JWT | [Pass](m74/recheck/5-jwt-labeled/pixels.json) | 1 key | 3 |
| Four-letter hex tail | [Pass](m74/recheck/5-hex/pixels.json) | 1 key | 2 |
| Three-letter hex tail | [Pass](m74/recheck/5-hex-three/pixels.json) | 1 key | 2 |
| JWT wrapped at its first dot | [Pass](m74/recheck/a-dot-jwt/pixels.json) | 1 key | 3 |
| 731-character JWT in xed | [Pass](m74/recheck/b-long-jwt/pixels.json) | 1 key | 8 |
| Three-letter hex tail at 2.2 line-height | [Pass](m74/recheck/c-loose-hex/pixels.json) | 1 key | 2 |

All the line-ending GitHub tokens were fully covered. The separate key and card classifications from the original candidate held. Every rectangle was opaque black within the saved copy, with zero changed pixels outside the union.

All three new fixtures returned one key. The first-dot JWT's second row began with `eyJ` and all three rows were covered. The long JWT filled eight visual rows in xed and every row was covered. The loose-spaced hex wrapped the final three letters and quote onto a row 70 pixels below the first. Its final visible text was fully covered. [Dot-break source](m74/recheck/a-dot-jwt/capture.png), [long JWT pixel check](m74/recheck/b-long-jwt/pixels.json), [loose hex source](m74/recheck/c-loose-hex/capture.png).

The strict gate still failed for the two issues already seen on published nightly and on the first Mint candidate. In case 4 the padded key rectangle touched eight dark pixels at the top of `later`, four of which changed to black. The token was fully covered and the plain words remained readable. The unlabelled three-row JWT was entirely visible after Quick redact, with zero matches. The OCR output started `leyJ` where the fixture started `eyJ`. [Plain-text pixel check](m74/recheck/4/pixels.json), [unlabelled JWT inspection](m74/recheck/5-jwt/inspect-before.json).

Before acceptance, the first Firefox calibration put the first dot on the second row. Soft break opportunities after the dots fixed the fixture layout. The full-screen calibration frames were kept privately. The published source pictures came from the installed put.gd on the real desktop. After the saves, the package was removed and the Mint lease passed cleanup and was released at 06:46:06 UTC.
