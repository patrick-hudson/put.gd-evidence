# Quick redact: words after a whole token, #1839 (PR #1857)

Acceptance and measurements for put.gd-desktop PR #1857, which fixes #1839. On `Your token ghp_<36 characters> was leaked today`, Quick redact also covered "was leaked today". All text is synthetic test text; token text in the JSON and text files reads `<test token>`.

## Builds

- Before: published nightly 26.1121.6060. Its capture is in the #1840 record (`m74/m74-nightly-saved.png`), taken on the same fixture. That nightly also predates #1842's cover bounds, so its covers reach further into neighbouring words than today's.
- After: CI candidate packages (run 44991965851) for commit 26c8fcd5d. That commit is PR #1857's head f68ebfbbd merged onto nightly 2306ba3a3, which holds #1851 and #1853. Tree 3c37c2fe0c7203233df4f5c7cf4fbaab9c78ec31, checked by the driver on each host.

## Desktop acceptance

Hosts: m74 (Linux Mint 22.3, Cinnamon X11) and k72 (Kubuntu 26.04, Plasma Wayland), each under its desktop lock. The fixture, driver, leg and checker are the ones in the #1840 record (`records/2026-11-22-quick-redact-email-split-1840/fixture` and `tools`). The token blocks are:

- Liberation Serif 14 px: `Your token ghp_… was leaked today` and `Bearer ghp_… (expires next week).`;
- Noto Sans 18 px: `Your token ghp_… was leaked today`.

| Host | Build | Path | Token ink showing | "was leaked today", "(expires next week).", "token", "Bearer" touched |
| --- | --- | --- | --- | --- |
| m74 | nightly 26.1121.6060 | editor Quick redact | none | 12 words |
| m74 | candidate | editor Quick redact | none | none |
| m74 | candidate | Redact and upload (received PNG) | none | none |
| k72 | candidate | editor Quick redact | none | none |
| k72 | candidate | Redact and upload (received PNG) | none | none |

On m74 the first editor leg timed out waiting for the fixture viewer to go full screen; the retry, recorded here, ran normally.

Picture: `pictures/token-before-after.png` shows nightly above and the candidate below, on m74. Orange outlines neighbour words a cover touched.

## Corpus (real putgd-ocr, rendered captures)

`harness/redact_find.cpp` (default set) draws the token followed by "was leaked today" and by "(expires next week).", and a Stripe test key followed by "was rotated". It renders them in 12 fonts × 11 sizes (9–32 px) × 5 backgrounds and recognizes them with the real `putgd-ocr`. `harness/words1839.py` counts the ordinary words inside key matches (`corpus/ordinary-words-after-tokens.txt`).

| Code | GitHub-token matches that also take ordinary words | Token ink left visible |
| --- | --- | --- |
| nightly c586ad3ad | 1,320 of 1,327 | none |
| PR #1857 | 12 of 1,327 (reads of 38–39 characters: one word starts within the usual length) | none |

The Stripe test key (32 characters, a kind with no single length) keeps covering "was rotated", as on nightly.
