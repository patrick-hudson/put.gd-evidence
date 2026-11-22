# Quick redact: a mark per column, #1846 (PR #1861)

Acceptance for put.gd-desktop PR #1861, which fixes #1846. With two card numbers at the same height in two columns, Quick redact covered the whole row with one mark, including the space and words between the columns. All text is synthetic test text; token text in the JSON files reads `<test token>`.

## Builds

- Before: published nightly 26.1121.6060 (tree d1e55ab7).
- After: CI candidate packages (run 44993364023) for PR head ffeead0fc. Nightly has gained only documentation since, so this is the merged tree's code. Tree 01f3957abcb3eb8492155f724f8d8fcbdbbac71c, checked by the driver on each host. The later head 5fff5f988 adds only a unit test.

## Desktop acceptance

Hosts: m74 (Linux Mint 22.3, Cinnamon X11) and k72 (Kubuntu 26.04, Plasma Wayland), each under its desktop lock.

`fixture/` is the #1840 record's page plus one row. It shows `Card 4111 1111 1111 1111` at x 40 and, on the same row, `MC 5555 5555 5555 4444` at x 1200, in Noto Sans 16 px (`harness/redact_fixture.cpp`). The driver, leg and checker are the #1840 record's `tools/`. `tools/acc46.sh` runs one build's legs. "Gap black" is the share of opaque black pixels between the columns: x 275–1160 on the text's rows, 40 px clear of each column.

| Host | Build | Path | Card digits showing | Gap between columns black |
| --- | --- | --- | --- | --- |
| m74 | nightly 26.1121.6060 | editor Quick redact | none | 100% |
| m74 | candidate | editor Quick redact | none | 0% |
| m74 | candidate | Redact and upload (received PNG) | none | 0% |
| k72 | candidate | editor Quick redact | none | 0% |
| k72 | candidate | Redact and upload (received PNG) | none | 0% |

In both builds the labels "Card" and "MC" are covered. The two repeated-digit test numbers on one row are matched together as one key, and the labels are inside that match; matching is unchanged by this PR.

The first k72 run, about 06:30–06:33Z, was made while another session held k72's lock, so it doesn't count; that session was told what to redo. The k72 rows above are from the rerun under this session's own lock (06:39:49Z). On m74 the first editor leg in each build timed out waiting for the fixture viewer to go full screen; the retries, recorded here, ran normally.

Picture: `pictures/columns-before-after.png` shows the row with nightly above and the candidate below, on m74. Orange outlines neighbour words a cover touched.

## Corpus

#1838's real-OCR harness (4,620 line cases, no column gaps) gives the same covers on nightly c586ad3ad and on this PR's tree: 0 line cases leaking matched ink, and the same 120 line cases touching a neighbour (`corpus/summary.txt`).
