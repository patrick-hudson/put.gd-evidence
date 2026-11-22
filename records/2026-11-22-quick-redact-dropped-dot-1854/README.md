# Quick redact: a word joined to an address by a dropped dot, #1854 (PR #1864)

This is the desktop acceptance and the real-recognizer measurement for put.gd-desktop PR #1864, which fixes #1854. When `putgd-ocr` dropped the dot of `jane.doe@example.com` and returned `jane` and `doe@example.com` a word space apart, only the second word matched, and Quick redact left `jan` readable. The PR covers a neighbouring word as part of the match when the picture shows a small loose blob of ink (a dot) between the two boxes and no word-space blank. Joining only moves a cover's edge outward.

#1849 (a cover taking the last letter of "at") was tried in the same PR and dropped. Every pixel-only rule that ends a cover earlier than nightly had a geometry that exposes a matched glyph. It is closed as a documented limit; the analysis is on the issue.

## Build identities

| Build | Commit | Tree | Packages |
| --- | --- | --- | --- |
| Before: nightly at d86737a0e (#1842, #1851, #1857 and #1861 merged) | `d86737a0e70d50e16e641b1757aff8d8f7b65705` | `3a9a92d0fe6ba9ce6075e35bb6f5f0bc7d2c4109` | CI run 44995950659, `putgd_26.1122.6390~dev+gd86737a0e70d_amd64.deb` |
| After: PR head | `f13419e45af21fb58bcfd02e68bc968c6d40df3d` | `1fb76e20e89725ea5a73285220bf679580c0232e` | CI run 44996569518, `putgd_26.1122.6392~dev+gf13419e45af2_amd64.deb` |

The driver checked `diagnostics.build.gitTree` against the tree before each run. k72 ran the Ubuntu 26.04 deb and m74 the 24.04 deb.

## Desktop acceptance

Hosts: k72 (Kubuntu 26.04, Plasma Wayland) and m74 (Linux Mint 22.3, Cinnamon X11). Each run took its desktop lock through `desktop_lock.py run`, and restored the host's previous putgd package afterwards.

1. `harness/redact_fixture.cpp` drew `fixture/fixture.png` with Qt. It also wrote `labels.png`, holding each word's own ink, and `words.json`. The page has these blocks:
   - #1851's email lines in Red Hat Display 10 px, on a dark and a light panel;
   - #1842's five lines in Noto Sans 16 px (dark) and 18 px (light): a card, a token, an email in a sentence, a card at a line start, and an email at a line end;
   - short words before matches ("It is at", "Mail to", "Pay on", "Key is") in Liberation Sans 13 px (light), Cantarell 20 px (dark) and Red Hat Text 24 px (light).

   On the light 10 px line, the real `putgd-ocr` drops the dot of `jane.doe@example.com`.
2. `tools/acc.sh` installs the package and starts #1842's `tools/driver.py`, a private resident in the real session. The script then shows the fixture full screen and closes put.gd's first-run window. Next it runs `tools/leg.py` twice: once for the editor's Quick redact (card, key, email) and save, and once for Redact and upload through the sensitive-text check. Finally it restores the previous package.
3. `tools/check.py`, from #1851's record, compares each result with the fixture:
   - a matched word is hidden only when every ink pixel is black;
   - a neighbour counts as touched when any ink pixel changed.

| Host | Build | Path | Matched words fully hidden | Neighbour words touched |
| --- | --- | --- | --- | --- |
| k72 | nightly d86737a0e | editor | 45 of 47 (`jan` showing, 56 px) | 5 of 94 |
| k72 | nightly d86737a0e | Redact and upload (received PNG) | 45 of 47 (`jan` showing, 56 px) | 5 of 94 |
| k72 | PR f13419e45 | editor | 46 of 47 | 5 of 94 (the same five) |
| k72 | PR f13419e45 | Redact and upload (received PNG) | 46 of 47 | 5 of 94 |
| m74 | PR f13419e45 | editor | 46 of 47 | 5 of 94 |
| m74 | PR f13419e45 | Redact and upload (received PNG) | 46 of 47 | 5 of 94 |

The word not counted as hidden in both builds is "Reach me at jane.doe@example.com" on the light 10 px panel. Its one non-black ink pixel, (755, 79), is the faint tip of the "j" hook at 246 of 255. It lies in the column nightly's `reach()` leaves uncovered as the space's last column, so this is unchanged behaviour, not part of this PR.

The five touched neighbours are the same in both builds:

- "at" on the dark 10 px and Noto Sans 16 px lines (#1849, now a documented limit);
- "us." before `bob@example.com`;
- "ok" after the token on two blocks, which the key match takes in `find()`.

Pictures:

- `pictures/light10-before-after-k72.png`: the light 10 px block in the editor on k72, nightly against this PR. The `jan` leak is outlined in red.
- `pictures/email10-upload-before-after-k72.png`: both 10 px blocks in the received Redact and upload PNG on k72, nightly against this PR.
- `pictures/blocks-m74.png`: the five-line and short-word blocks on m74 with this PR, editor and Redact and upload.

## Real-recognizer measurement (d69, merged tree)

These ran on d69 because aurora was under a quiet lease. The fonts d69 lacks (Red Hat, Adwaita, Source Code Pro) were loaded from aurora's toolbox copies via `FIXTURE_FONTS`, with the shipped English data. Both binaries came from the same build tree, at nightly d86737a0e and at this head. The two corpora are 12 fonts × 11 sizes (9–32 px) × light, dark, tinted, noisy and gradient backgrounds:

- **Cover corpus:** #1842's `harness/redact_cover.cpp`, 5 lines, 3,300 line cases.
- **Matcher table:** #1851's `harness/redact_find.cpp`, 7 lines, 4,620 line cases.

| Corpus | Code | Line cases with secret ink visible | Line cases where a cover touches neighbour ink |
| --- | --- | --- | --- |
| cover | nightly d86737a0e | 1 | 89 |
| cover | this PR | 1 (the same) | 89 |
| matcher table | nightly d86737a0e | 0 | 121 |
| matcher table | this PR | 0 | 122 |

The one leak in the cover corpus is a recognition miss, not a cover problem. In Liberation Mono 20 px on the noisy background, `putgd-ocr` read the last card group as `99414-`, which `find()` does not match. Neither corpus produces the #1854 split, so the fixture above is the measurement for it.

The matcher table's one new neighbour case is on the noisy background in Red Hat Display 9 px. The 11 px case on the noisy background touches 8 more pixels of a word nightly already touched.

## Limits recorded

- #1849: a cover can take the last letter of a short word right before a match.
- Sol round 4 on #1864 (S7, declined as a magician case): a dropped dot of a single dark pixel whose fainter edge touches the letter before it is not seen. That word stays uncovered, as on nightly.

Both are in the design doc through PR #1868.
