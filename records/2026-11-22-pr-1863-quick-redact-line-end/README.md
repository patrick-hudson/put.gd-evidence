# Quick redact line-end token desktop acceptance for PR #1863

Tested the native DEBs on Linux Mint 22.3 Cinnamon X11 (`m74`) and Kubuntu 26.04 Plasma Wayland (`k72`). The cases use live xed and Kate windows, xterm, and a local page in Firefox. The fixture uses synthetic text, an isolated local destination and a private resident. All captures came from the installed put.gd's desktop source. The record shows the source capture and the editor's Save a copy result for the fixture area.

## Builds

| Build | Package version | Commit | Tree |
| --- | --- | --- | --- |
| Published nightly | `26.1121.6060~nightly` | `4a7730e4a844582745b9cc3b7686826943c903b1` | `d1e55ab7ee93c954120d10913d4e81e2175044e1` |
| PR candidate | `26.1122.6372~dev+ga382e872cd39` | `a382e872cd39f5688819138c533954a96a9480ff` | `c68990d16dc0c34791a9d3f064bd690c3695673b` |

The [candidate CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44992999617) succeeded. Runtime manifests are in each run's `build.json`, from `diagnostics.build` (the `build` member of the `diagnostics` CLI response). Published nightly was verified against the release SHA-256 values. On Mint the apt index hash also matched the published native artifact.

| Platform | Nightly DEB SHA-256 | Candidate DEB SHA-256 |
| --- | --- | --- |
| ubuntu24.04 | `2c776f6cac269f02bbd342f2120932840e9dad9b7c4f7caa6bbc26ad4cd73424` | `c5c964a1a099449404bd3f262188ffcc56c3159f410ce06d408c4c2a3432306e` |
| ubuntu26.04 | `4b318b19010eebf79863bf70a013a2b24004857be3bc2e41e3a8dceec20e45d7` | `ec807ecd6808a43afcae902040ec57996415629e49dd302a56c9dc6b09d85512` |

## Pixel check

Each `apply.json` has the complete counts for email, phone, IP, card and key. Each `inspect-after.json` has the suggested mark IDs, categories and rectangles. Counts represent matches, which can use several rectangles across visual rows. The pre-redaction inspection preserves synthetic recognized words as `textPieces` arrays. Concatenating each array reproduces the OCR output. The `mark-ocr.json` files index words whose box had at least half its area within a mark.

The checker measures opaque black RGBA coverage within the saved intersection of every mark rectangle, plus changed pixels outside the union. It independently searches for dark fixture ink inside visually registered text regions and verifies that each expected secret has full coverage of its own category. When two correctly classified adjacent marks overlap because of padding, each match still needs its own correct coverage. It compares the entire plain-text region of case 4 pixel for pixel and reports the number of original ink pixels the key rectangle touched. Scripts and fixture dimensions are in [scripts](scripts/).

## Results

Pass requires the expected counts and coverage, opaque saved rectangles, and an untouched plain-text line in case 4. Zero email, phone, IP or card counts are omitted from the table. The CLI replies preserve every category.

| Case | Mint nightly | Mint candidate | Kubuntu nightly | Kubuntu candidate |
| --- | --- | --- | --- | --- |
| 1 Token, two cards and hex | [Fail](m74/nightly/1/pixels.json) · 2 key, 1 card | [Pass](m74/candidate/1/pixels.json) · 2 key, 2 card | [Fail](k72/nightly-clean/1/pixels.json) · 2 key, 1 card | [Pass](k72/candidate/1/pixels.json) · 2 key, 2 card |
| 2 Token and email | [Pass](m74/nightly/2/pixels.json) · 1 key, 1 email | [Pass](m74/candidate/2/pixels.json) · 1 key, 1 email | [Pass](k72/nightly-clean/2/pixels.json) · 1 key, 1 email | [Pass](k72/candidate/2/pixels.json) · 1 key, 1 email |
| 3 Token and AWS key | [Fail](m74/nightly/3/pixels.json) · 1 key | [Pass](m74/candidate/3/pixels.json) · 2 key | [Fail](k72/nightly-clean/3/pixels.json) · 1 key | [Pass](k72/candidate/3/pixels.json) · 2 key |
| 4 Token and plain words | [Fail](m74/nightly/4/pixels.json) · 1 key | [Fail](m74/candidate/4/pixels.json) · 1 key | [Fail](k72/nightly-clean/4/pixels.json) · 1 key | [Fail](k72/candidate/4/pixels.json) · 1 key |
| 5-jwt JWT wrapped across three rows | [Fail](m74/nightly/5-jwt/pixels.json) · 0 matches | [Fail](m74/candidate/5-jwt/pixels.json) · 0 matches | [Fail](k72/nightly-clean/5-jwt/pixels.json) · 2 key | [Pass](k72/candidate/5-jwt/pixels.json) · 1 key |
| 5-jwt-labeled Labeled JWT variant | [Fail](m74/nightly-wrap/5-jwt-labeled/pixels.json) · 2 key | [Pass](m74/candidate/5-jwt-labeled/pixels.json) · 1 key | [Fail](k72/nightly-clean/5-jwt-labeled/pixels.json) · 2 key | [Pass](k72/candidate/5-jwt-labeled/pixels.json) · 1 key |
| 5-hex Wrapped hex with four-letter tail | [Fail](m74/nightly/5-hex/pixels.json) · 1 key | [Pass](m74/candidate/5-hex/pixels.json) · 1 key | [Fail](k72/nightly-clean/5-hex/pixels.json) · 1 key | [Pass](k72/candidate/5-hex/pixels.json) · 1 key |
| 5-hex-three Wrapped hex with three-letter tail | [Fail](m74/nightly-wrap/5-hex-three/pixels.json) · 1 key | [Pass](m74/candidate/5-hex-three/pixels.json) · 1 key | [Fail](k72/nightly-clean/5-hex-three/pixels.json) · 1 key | [Pass](k72/candidate/5-hex-three/pixels.json) · 1 key |
| 6 Token, right card and distant card | [Fail](m74/nightly/6/pixels.json) · 1 key, 1 card | [Pass](m74/candidate/6/pixels.json) · 1 key, 2 card | [Fail](k72/nightly-clean/6/pixels.json) · 1 key, 1 card | [Pass](k72/candidate/6/pixels.json) · 1 key, 2 card |

The candidate separated all the expected matches in cases 1, 2, 3 and 6, with every tested line-ending token fully covered. On nightly, case 1 took the `4539 1488 0343 6467` row as part of the token's key match. The `4111 1111 1111 1111` card and the signing hex retained their own matches. Case 3 counted the GitHub token and the AWS access key as one key, with two rectangles. Case 6 counted the right-column `5555 5555 5555 4444` card as part of the key, while the distant `4539` card retained its own category. The candidate gave every one of those items its own match of the expected kind.

Both builds on both hosts produced one key for case 4. The padded key rectangle touched eight dark pixels at the top of `later`, four of which changed to black. The line stayed readable and the token was fully covered. The strict plain-text gate failed. [Mint candidate case 4](m74/candidate/4/pixels.json), [Kubuntu candidate case 4](k72/candidate/4/pixels.json).

Both Mint builds missed the unlabelled JWT completely when OCR prefixed its first token word with `l`, yielding `leyJ…`. The labeled JWT variant on Mint and both JWT variants on Kubuntu returned one fully covering key on the candidate. Kubuntu nightly covered all three visual rows using two key matches. Mint nightly's labeled variant left most of its middle row visible. The candidate covered the wrapped `fedc"` and `edc"` tails in full on both hosts. Nightly left ink visible in both tails. [Mint unlabelled JWT](m74/candidate/5-jwt/inspect-before.json), [Mint candidate labeled JWT](m74/candidate/5-jwt-labeled/pixels.json), [Kubuntu candidate three-letter hex tail](k72/candidate/5-hex-three/pixels.json).

Every suggested rectangle was opaque black where it intersected the saved copy. No pixels changed outside the rectangles. The Kubuntu nightly suite was replayed after a competing session interrupted the first browser leg. Both hosts returned to their pre-test uninstalled package state and passed the desktop lease cleanup checks. Evidence covers these two physical hosts and the editor Quick redact path. No other desktop, upload or auto-redact flow was exercised.
