# Findings resolved so far

## Sol, round 1 (7/10)
- Must-fix, coloured label under the wash lost contrast (aurora mark 3): the
  wash is now a luminance-preserving tint (RULE.md §6); each pixel keeps its
  WCAG luminance, so the label's text contrast is exactly what it was. New
  export in exports/aurora.png, zoom/aurora-3.png.
- Pigment computed once per plan (hoisted out of the per-background loop).
- Noted, not changed (outside the look, pre-existing architecture shared with
  the blur tile): preview at zoom < 1 filters the resized tile; overlapping
  highlights are previewed each from the base; tables are built with doubles
  once per background, the per-pixel path is lookups only, and the same build
  renders both export and preview.
- Nice-to-have, red reads as pink: not changed (a lower floor for red alone
  would reopen the agreed palette treatment); recorded for the owner's look.
- Nice-to-have, faint lettering stays faint under a band: not changed (the rule
  keeps contrast as it was; boosting it is a separate decision).

## Sol, round 2 (8/10)
- Must-fix, neutral markers leave no mark in wash mode: neutral markers now
  move luminance instead of chroma (RULE.md §6); black shades, white lightens,
  contrast ratios kept. New exports: exports/aurora-neutral.png and its zooms
  (black and white on the painting and on the red label).
- Noted, not changed: red reads as salmon (palette decision kept), faint
  lettering stays faint (contrast kept, not boosted), yellow wash looks olive
  on warm artwork (luminance-keeping tint; the only honest yellow at that brightness).
- Follow-up on the black wash: the first version scaled Y+0.05 and crushed a
  dark painting to solid black (a redaction look); black now halves Y so dark
  detail survives. Code at 47d8190a7; exports regenerated.

## Sol, round 3 (8/10)
- Must-fix, black wash lowered the label's text contrast (3.74 → 3.34): the
  shade now keeps Y+0.05 ratios above a toe (`max(0.5·Y, 0.6·(Y+0.05) − 0.05)`),
  so the label pair keeps its ratio while the dark painting keeps its detail.
  The neutral test tolerance is 5 % now. White on the label is exported too
  (the label is split: black left half, white right half; zoom/aurora-neutral-3/4).

## Gemini 4 Argon's proposal (arrived after the vote)
Two candidates: "Velvet Ribbon" (band = 0.88·marker-dye + 0.35·page, dark ink
re-laid with a 3×3 local-peak coverage, faint ink lifted to ≥ 4.9:1) and
"Luminous Glaze" (a dark tint under light text, the round-1 family). The
Ribbon lands in the same family the council converged on (a paper-bright band
with dark lettering); its differences are a duller band that lets zebra rows
show through, a coverage-based ink relay (the council rejected coverage
unmixing as the source of round 2's fat glyphs), and a contrast floor for faint
text, which is the already-recorded separate decision. No change to the rule;
the faint-text floor stays a follow-up candidate.

## Sol, round 4 (8/10)
- Must-fix, white wash clipped white lettering while lightening the red label
  (3.74 → 2.33): the white gain is now common to the box and limited to the
  luminance headroom of its brightest sampled pixel (computed in the plan, so
  preview and export agree). A unit test now asserts a white label on a red
  badge over a photo keeps its contrast under white, black and yellow washes.

## Sol, round 5 (8/10)
- Must-fix, a big box's headroom came from the sampling grid and could miss a
  bright pixel: for a light neutral marker in wash mode the plan now scans every
  pixel of the box for the brightest luminance (only in that case, so paper
  marks pay nothing). A unit test puts a one-pixel bright line between the
  samples of a 1200×500 box and checks its contrast survives.

## Sol, round 6 (8/10): no blocking findings. Gate passed at commit 952220746.
Open aesthetic notes carried forward for the next reviewers: red reads salmon
(pigment floor 0.55 lifts #EF4444 to pink), faint source lettering stays faint
under a loud band, photographic washes read as colour filters.

## Astra, round 1 (8/10): no blocking findings. Gate passed at commit 952220746.
Same three aesthetic notes (red identity, faint lettering, artwork washes), each
flagged as needing the owner's comparison rather than an automatic change.

## Opus, round 1 (7/10)
- Must-fix, a 17 px box's one-pixel last block row let an icon's bottom stroke
  pass for a background, so the icon above it took the band colour
  (history-colours mark 6): every block now samples a full 16×16 window inside
  the box (a partial last row or column slides back over its neighbour). Unit
  test highlightKeepsIconsInAShortBox covers it.
- Red reads pink (all three reviewers): the pigment floor is 0.45 for every
  colour now (was 0.55); red is a coral, orange and blue deeper, black text on
  the darkest palette bands reads at 8.7:1 (dark pages) to 9.5:1 (white page). Exports regenerated.
- Noted, not changed: artwork washes read as filters, black and white washes
  grey a label, black on a dark page is a grey slab, faint lettering stays
  faint, pale blue with dark text can resemble a selection (the trade-offs the
  council accepted with the paper-band family).

## Opus, round 2 (8/10): no must-fix. Gate passed at commit dc52421b8.
Corrected the overstated "≥ 10:1" in this log and RULE.md (measured 8.7–9.5:1
on the darkest bands). Remaining notes are the accepted trade-offs.
