# Evidence import and docs layout check (#1222), 2026-11-05

Proof that moving `docs/evidence` out of put.gd-desktop into this repository
lost nothing, and the link check of the documentation layout that replaces it.

## What was tested

1. Every file under `docs/evidence` in put.gd-desktop at
   `6677938767e732247f9097e0ae5f063cb63140ef` has the same git blob id and file mode
   at the same relative path under `records/` in this repository at
   `874703b35562c732268c6fe0bc9b42614ffda928`, and the reverse.
2. The reorganized documentation in put.gd-desktop pull request #1223
   (head `c1e12151a097220014fb52b5bba756a2b17ab6f6`) has no broken relative link or
   anchor, and every document is listed in its folder README.

## Where

Patrick's workstation (Linux Mint, shell only; no desktop session involved).
Compared with `git ls-tree -r` on both repositories.

## Result

- Pass: 13936 blobs. The two listings were byte-identical; one copy is attached
  (SHA-256 `d8677846197b5e8e843b3e1596ceb9143d87d560b49cdc273fbd63daba4e805d`).
- Pass with 18 deferred links: `docs-check.txt`. The deferred links are inside
  `docs/build.md` and `docs/proton-drive.md`, which are package inputs and move
  in a later code change.

## Files

- `blob-listing.txt`: mode, type, blob id and path of each file, with the
  `docs/evidence/` or `records/` prefix removed. Both repositories produce it.
- `docs-check.txt`: output of the documentation checker.
