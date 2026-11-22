# Quick redact: an unlabelled JWT behind a text caret (#1875, PR #1883)

Tests of PR #1883 (put.gd-desktop): Quick redact finds and covers an unlabelled JSON web token whose start a text caret garbled in recognition. Final head `be49494725e96097cced2cc635fbab334158d829`, tree `6cea694a58734b700ae933d5853743dc2ab8823f`, package `26.1122.6447~dev+gbe49494725e9` from [CI run 45013251352](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45013251352).

## What a caret does to a JWT

In xed on m74, recognition read the caret before an unlabelled JWT as `leyJ…` (PR #1863's recheck), and Quick redact matched nothing. In a Firefox text field on both desktops it read `kyJ…`. In Kate on k72 it read `byJ…` (in two of three captures on the final head). The real-OCR corpus with a caret drawn in front of the token gave `leyJ`, `|eyJ`, `JeyJ`, `jeyJ`, `[eyJ` and `{eyJ`. It also gave headers misread past the prefix (`|eyfhbGci…`) and heads split off as words (`ley` `JhbGci…`, `Jew` `hbGci…`).

## Desktop acceptance (`m74/`, `k72/`)

Physical builders, real desktops: m74 is Linux Mint 22.3 Cinnamon X11 (Ubuntu 24.04 DEB), k72 is Kubuntu 26.04 Plasma Wayland (Ubuntu 26.04 DEB). Each run started a private resident of the installed package. The driver checked `diagnostics.build` against the commit and tree before any capture. Fixtures:
- an editor with its caret at the start of the file: xed, or Kate;
- xterm printing the file;
- a Firefox page: a wrapped JWT, the other lines, and a text field holding a second JWT with a steady caret at its start.

Each fixture holds an unlabelled JWT, then `ops-alerts@example.com`, `Card 4539 1488 0343 6467`, `id = AKIA…EXAMPLE` and `add more tests later`. Each was captured three times through `editor.open {"source":"desktop"}`, Quick redact with every category, and `editor.saveCopy`. `scripts/verify1875.py` checks every recognized word's ink against the saved copy: a secret must lie under an opaque black mark of its kind, and a plain word must be unchanged.

| Run | Build | JWTs | Other kinds | Plain words |
| --- | --- | --- | --- | --- |
| `before` | m74 `26.1122.6373~dev+gaa202c7a634c`, k72 `26.1122.6374~dev+gffeead0fc1f3` (the packages found installed; matcher as nightly) | Firefox field left readable on both (`kyJ…`); Kate's first JWT row left readable when read `byJ` (k72) | covered | `Card` touched by the address mark in the editors |
| `fix` | `26.1122.6427` (34591351, first candidate) | same Firefox and Kate failures | covered | same |
| `fix2` | `26.1122.6428` (8338e528f) | every JWT covered, 18 of 18 captures | covered | same |
| `final` | `26.1122.6447` (be4949472, the merged head) | every JWT covered, 18 of 18 captures | covered | same |

The `Card` touch is the address mark's padding reaching the top of the next line (420 changed pixels on m74, 100 on k72). It is identical on the builds found installed, so this change didn't cause it. Afterwards both builders got their previous packages back and the desktop locks were released.

Pictures (`pictures/`): `m74-firefox-field-before-after.png`, `k72-firefox-field-before-after.png` and `k72-kate-before-after.png` show the `before` and `final` redacted copies with the JWT row called out. `m74-xed-after.png`, `m74-xterm-after.png` and `k72-xterm-after.png` show the final head with every kind on the page.

## Real-OCR corpus (`corpus/`)

The #1856 harness on d69 renders each line set in 12 fonts × 11 sizes × 5 backgrounds, recognizes it with putgd-ocr and runs `quickRedact::find` (`scripts/redact_find.cpp`, sets `jwt`, `caret`, `caret0`). Nightly `129e2c9cf` is compared with the final matcher (`j10`). The JWT sets hold five unlabelled JWT lines (alone, after `$ echo`, quoted, in a sentence) plus ordinary lines containing `ey` words. `caret` draws a caret a little left of each token, and `caret0` draws one touching it.

| Set (3,300 JWT lines) | Not found | Leaking cases | Covered → leaking | Leaking → covered |
| --- | --- | --- | --- | --- |
| `jwt` (no caret) | 3 → 2 | 105 → 101 | 0 | 4 |
| `caret` | 149 → 5 | 311 → 182 | 2 | 150 |
| `caret0` | 136 → 3 | 307 → 177 | 12 | 145 |

The 12 `caret0` regressions are heads read as `Hey`, `fey` or `ly`; they leave those few head letters visible. Ordinary words covered whole by a match fell from 3,986 to 3,267 (`caret`) and from 4,422 to 3,282 (`caret0`). Most remaining over-cover is the words after a JWT on its line, which nightly covers too. Nightly put some neighbour words, such as `Seen` and `echo`, inside the match outright. The fix leaves them out, but the mark's padding still grazes them, so neighbour-word touches rose from 137 to 199 (`caret`) and from 115 to 174 (`caret0`). On the existing ordinary, wrapped, cards and line-end sets (`j0` against `j10`), all 2,640 pages give identical matches.

`corpus/jwt-sets.txt` has the per-set summaries and the per-line transitions; `scripts/jwtstat.py` and `scripts/trans.py` compute them.
