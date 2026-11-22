# Quick redact: a wrapped secret's letter-only tail, #1850 (PR #1853)

Acceptance and measurements for put.gd-desktop PR #1853, which fixes #1850. When an editor soft-wraps a 64-character hex secret in a string literal, its last letters and closing quote (`edc"`) start the next line. Quick redact and auto-redact covered the first line and left `edc"` readable. All text is synthetic test text; token text in the JSON files reads `<test token>`.

## Builds

- Before: published nightly 26.1121.6060. Its "before" capture is in the #1840 record (`m74/m74-nightly-saved.png`), taken on the same fixture.
- After: CI candidate packages (run 44990882967) for commit 7b99514c7. That commit is PR #1853's head ee3d652e2 merged onto nightly c586ad3ad, which already holds #1851. Tree f928a28a1aef43146fa78235041f002830433f59, checked by the driver on each host.

## Desktop acceptance

Hosts: m74 (Linux Mint 22.3, Cinnamon X11) and k72 (Kubuntu 26.04, Plasma Wayland), each under its desktop lock. The fixture, driver, leg and checker are the ones in the #1840 record: `records/2026-11-22-quick-redact-email-split-1840/fixture` and `tools`. The page's Noto Sans Mono 15 px block shows:

- `SIGNING_HEX =`;
- the hex line `"6311…343`;
- `edc"`;
- `OWNER = "ops-alerts"`.

| Host | Build | Path | `edc"` | `OWNER` line |
| --- | --- | --- | --- | --- |
| m74 | nightly 26.1121.6060 | editor Quick redact | visible | untouched |
| m74 | candidate | editor Quick redact | covered | untouched |
| m74 | candidate | Redact and upload (received PNG) | covered | untouched |
| k72 | candidate | editor Quick redact | covered | untouched |
| k72 | candidate | Redact and upload (received PNG) | covered | untouched |

`SIGNING_HEX =` is covered in both builds. The card line above it is taken as a key that runs on over the next lines; that is #1846's area and #1826's soft-wrap rule, not this change. The first m74 editor leg timed out waiting for the fixture viewer to go full screen; the retry, recorded here, ran normally.

Picture: `pictures/hex-tail-before-after.png` shows nightly above and the candidate below, on m74. Red outlines matched words with ink still showing, and orange outlines neighbours a cover touched.

## Corpus (real putgd-ocr, rendered captures)

`harness/redact_find.cpp --set wrapped` draws `SIGNING_HEX = "6311…343`, `edc"`, `OWNER = "ops-alerts"`, an unquoted digest, and `add more tests later` in 12 fonts × 11 sizes (9–32 px) × 5 backgrounds (660 pages). It recognizes them with the real `putgd-ocr` and applies `find()`. See `corpus/wrapped-hex-tail.txt`.

| Code | Pages where the `edc"` tail is covered | Pages where a key match takes a line below |
| --- | --- | --- |
| nightly 24565d0f3 | 0 of 660 | 0 |
| PR #1853 | 638 of 660 | 0 |

The 22 left are recognition damage. The close was read as `™` or `*`, or the tail as `ae` or `aia`. In 5 of them the hex line itself wasn't read as a key.
