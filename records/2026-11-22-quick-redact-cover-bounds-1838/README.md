# Quick redact cover bounds, #1838 (PR #1842)

Desktop acceptance and the real-recognizer measurement for #1842. That PR stops Quick redact's covers from reaching into the word next to a match, without letting any matched glyph show.

## Build identities

| Build | Commit | Tree | Packages |
| --- | --- | --- | --- |
| Candidate (PR head, Sol-approved in round 4) | `2eeaea339b06a6c8968f0a2d208fec2dfd1d6a2b` | `61d636098f211d2110770a88f2525abe0b86847f` | CI run 44985996736, `release-native-ubuntu26.04` and `release-native-ubuntu24.04`, `putgd_26.1122.6304~dev+g2eeaea339b06_amd64.deb` |
| Before: published nightly | `4a7730e4a844582745b9cc3b7686826943c903b1` | `d1e55ab7ee93c954120d10913d4e81e2175044e1` | `putgd-26.1121.6060-nightly-ubuntu26.04-x86_64.deb` from release `v26.1121.6060-nightly` |

The driver read each tree from the running resident's diagnostics and refused any other build.

## How it ran

On each host, under its desktop lock:

1. A private resident ran in the real desktop session, with its own config and data folders and a loopback HTTP receiver. The driver came from the #1806 and #1820 records (`tools/driver.py`).
2. A GTK viewer showed `fixture/fixture.png` full screen at 1:1. The page is synthetic test text in four fonts and sizes: Liberation Sans 40 and 13 px, Noto Sans 18 px, Noto Sans Mono 15 px, and Noto Sans 16 px on a dark panel. The viewer checked the fixture was showing before each capture.
3. Each block has five lines:
   - `Card 4111 1111 1111 1111`;
   - a token with words on both sides;
   - an email in a sentence;
   - a card at a line's start;
   - an email at a line's end.
4. `fixture.py` drew every word alone, so `labels.png` holds each word's exact ink (coverage of 32/255 or more).
5. Editor Quick redact: `editor.open {"source":"desktop"}`, then `editor.apply` `redactText` with card, key and email, then `editor.saveCopy`.
6. Redact and upload: the sensitive-text check on for card, key and email, then a monitor capture with `sensitiveText: prompt`, `operation.decide redact`, and `editor.submit`. The receiver kept the uploaded PNG.
7. `tools/check.py` compared each result with the fixture:
   - a matched word counts as hidden only when every ink pixel is black;
   - a neighbouring word counts as touched when any ink pixel changed.

## Results

| Host | Build | Path | Matched words fully hidden | Neighbouring words touched |
| --- | --- | --- | --- | --- |
| k72 Kubuntu 26.04 Plasma Wayland | nightly 26.1121.6060 | editor Quick redact | 48 of 48 | **25 of 57** |
| k72 Kubuntu 26.04 Plasma Wayland | candidate 2eeaea33 | editor Quick redact | 48 of 48 | 1 of 57 |
| k72 Kubuntu 26.04 Plasma Wayland | candidate 2eeaea33 | Redact and upload (received PNG) | 48 of 48 | 1 of 57 |
| m74 Mint 22.3 Cinnamon X11 | candidate 2eeaea33 | editor Quick redact | 48 of 48 | 1 of 57 |
| m74 Mint 22.3 Cinnamon X11 | candidate 2eeaea33 | Redact and upload (received PNG) | 48 of 48 | 1 of 57 |

Nightly covered part of the word before and after every match: "Card", "token", "to", "before", "is" and "at" in every block. The large `Card 4111 1111 1111 1111` line lost the "d" of Card, as in #1806.

With the candidate, one word is touched on both desktops: "at" in "Reach me at jane.doe@example.com" on the dark panel (33 of 81 ink pixels). The recognizer's box for "at" ends 2 px inside its "t", outside the 1 px the rule trusts, so the cover keeps going past the "t". The trade-off is filed as #1849.

In both builds, "was leaked today" after the token is covered because `find()` puts those words in the match (#1839). The check lists them separately as `takenByFind`; they aren't neighbours.

Pictures, with each touched neighbouring word outlined:

- `pictures/card-before-after.png`: the #1806 card line, nightly against the candidate (k72).
- `pictures/sans18-before-after.png`: the Noto Sans 18 px block (k72).
- `pictures/dark16-before-after.png`: the dark panel (k72), including the "at" case.
- `pictures/m74-redact-and-upload.png`: the received Redact and upload PNG on m74.

## Real-recognizer measurement

`harness/redact_cover.cpp` rendered the same five lines in 12 fonts (Adwaita Sans and Mono, Cantarell, Liberation Sans, Serif and Mono, Noto Sans, Serif and Sans Mono, Red Hat Text and Display, Source Code Pro). It used 11 sizes from 9 to 32 px on light, dark, tinted, noisy and gradient backgrounds: 3,300 line cases. It ran the real `putgd-ocr` with the shipped English data and compared nightly's cover with the candidate's (`harness/real-ocr-3300-cases-2eeaea3.json`).

| Code | Line cases leaking matched ink | Line cases covering a neighbour's ink |
| --- | --- | --- |
| nightly | 6 | 2,977 |
| candidate 2eeaea33 | 6, the same ones | 91 |

All six leaks are one recognizer split in Red Hat Display at 9–10 px: it read `jane.` and `doeg@example.com` as two words, and `find()` matched only the second (#1840). nightly leaks the same pixels.

## Follow-ups found here

- #1839: the key rule takes ordinary words after a token.
- #1840: an email split at a dot leaves its first half visible.
- #1846: two card numbers on one line become one key match across the whole line.
- #1849: the "at" case above.

## Rerun

Run `python3 tools/fixture.py fx` on a host with the Noto and Liberation fonts. Then copy `tools/` and `fx/` to the desktop host. Start `driver.py ROOT --leader plasmashell|cinnamon --vnc PORT --tree TREE` and run `dc.py ROOT/c.sock '["start"]'`. Then run `leg.py ROOT ROOT/fx LABEL` and `leg.py ROOT ROOT/fx LABEL --sensitive`, and check with `check.py fx RESULT.png`. The harness builds as an extra target against a put.gd build tree: link `putgd_core`, `putgd_editor` and `Qt6::Gui`.
