# Quick redact: an email split in its local part, #1840 (PR #1851)

Acceptance and measurements for put.gd-desktop PR #1851, which fixes #1840. When recognition read `jane.doe@example.com` as two words, `jane.` (or `jane`) and `doe@example.com`, Quick redact covered only the second word, so the start of the address stayed readable.

All text is synthetic test text. The token in the fixture is the made-up one from the unit tests, built in pieces in the sources, and token text in the JSON and text files reads `<test token>`.

## Builds

- Before: published nightly 26.1121.6060 (commit 4a7730e4a, tree d1e55ab7).
- After: CI candidate packages for PR head 255a6db88a224a921707c6ddae11df2d0077acfd (tree 997c4bb1a4ff9eb45ab1bb87498f233790d81bb6, CI run 44989499680). The Ubuntu 24.04 deb was installed on m74 and the 26.04 deb on k72. The driver checked `diagnostics.build.gitTree` against the tree before each run.
- The corpus harness was built on aurora-amd against nightly 24565d0f3 (#1826 and #1842 merged) and against the PR head.

## Desktop acceptance

Hosts: m74 (Linux Mint 22.3, Cinnamon X11) and k72 (Kubuntu 26.04, Plasma Wayland), each under its desktop lock.

1. `harness/redact_fixture.cpp` drew `fixture/fixture.png` with Qt. It also wrote `labels.png` (each word's own ink) and `words.json`. The page holds the issue's lines in Red Hat Display at 10 px (light and dark panels) and 9 px, plus lines for #1839, #1846 and #1850.
2. `tools/driver.py` ran a private resident of the installed package in the real session, showed the fixture full screen at 1:1, and kept a loopback receiver. These tools are the #1842 record's, unchanged.
3. `tools/leg.py` ran the editor's Quick redact (card, key, email) and saved a copy. With `--sensitive`, it ran the sensitive-text check (card, key, email on) on a monitor capture, chose Redact, and submitted the editor. The receiver kept the uploaded PNG.
4. `tools/check.py` compared every result with the fixture's word masks:
   - a matched word counts as hidden only when every ink pixel is black;
   - a neighbour counts as touched when any ink pixel changed.

### Results on the email lines

| Host | Build | Path | Email lines | Light 10 px "Please write to jane.doe@…" | Dark 10 px "Please write to jane.doe@…" |
| --- | --- | --- | --- | --- | --- |
| m74 | nightly 26.1121.6060 | editor | jane. leaked on both 10 px blocks | `jan` visible (51 px) | `jan` visible (61 px) |
| m74 | PR 255a6db88 | editor | fixed on light | covered | `jan` visible (56 px), #1854 |
| m74 | PR 255a6db88 | Redact and upload (received PNG) | same as editor | covered | `jan` visible, #1854 |
| k72 | PR 255a6db88 | editor | same as m74 | covered | `jan` visible, #1854 |
| k72 | PR 255a6db88 | Redact and upload (received PNG) | same as m74 | covered | `jan` visible, #1854 |

The published nightly predates the sensitive-text check, so its leg ran in the editor only.

- On the dark line, recognition dropped the dot and left a 2 px gap between `jane` and `doe@example.com`, the same width as every word space at that size. Word boxes alone can't separate the two cases, so the fix (which joins only overlapping boxes) leaves it. This was filed as #1854, with the ink in the gap as the signal to use.
- The 9 px block wasn't matched at all on either desktop, before or after. This is a recognition limit on these hosts.
- The "at" cover on the dark line is #1849.
- The `edc"` tail is #1850 (PR #1853).
- "was leaked today" is #1839.
- The "Card" labels and "SIGNING_HEX =" are covered because of #1846 and a token following onto the lines below.

Picture: `pictures/email-before-after.png` shows nightly above and this PR below, on m74. Red outlines matched words with ink still showing, and orange outlines neighbours a cover touched.

## Corpus (real putgd-ocr, rendered captures)

`harness/redact_find.cpp` is adapted from #1842's harness. It draws 7 lines in 12 fonts × 11 sizes (9–32 px) × light, dark, tinted, noisy and gradient backgrounds, 4,620 line cases, recognizes them with the real `putgd-ocr`, and applies `find()` and today's covers (`marks()` with the image).

| Code | Line cases leaking matched ink | Matches taking a word outside the address |
| --- | --- | --- |
| nightly 24565d0f3 | 7 | 0 |
| PR 255a6db88 | 0 | 6 ("at" 5 times, "Mail" once: boxes overlapping the address) |

`corpus/` holds both summaries and the comparison output (`harness/compare.py`).

## Reproduce

Build `harness/redact_fixture.cpp` and `harness/redact_find.cpp` as extra targets against a put.gd build tree, linking `putgd_core`, `putgd_editor` and `Qt6::Gui`. Run them with `--helper build/dev/putgd-ocr --data <tessdata> --out DIR`. On a desktop host, follow the #1842 record's recipe with `fixture/` and `tools/`.
