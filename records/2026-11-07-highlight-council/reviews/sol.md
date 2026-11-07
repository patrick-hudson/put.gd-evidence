# Sol — look as built

**7/10. Hold for the coloured-label readability problem.** Inspected all six full exports and every one of the 28 files in `exports/zoom/`, using the image viewer. Read the implemented rule, filter, relevant renderer/preview code and highlight tests; no builds or lab work. Code inspected at `2ec1027cdcc948f92906de2e5258ff53a1a4757a`.

The ordinary text examples work considerably better than a translucent rectangle: Cinnamon's paragraph reads cleanly, History's bands are unmistakable, and Plasma's notification retains crisp lettering. Marker colours remain distinguishable, though red is conspicuously pink. I see no obvious block-grid seams or surviving red/blue LCD fringes in the text bands. I accept the stated polarity reversal, loss of text colour, contrast saturation and grey black-marker rule.

Against Rams: the approach is useful, understandable and an inventive response to dark screenshots; avoiding decorative borders supports restraint and “as little design as possible.” Aesthetics and honesty are weaker: the broad History band resembles pasted yellow paper, and the small blue date resembles a selection. Thoroughness fails on the coloured-label case below. Consistent behaviour would support longevity; nothing here establishes environmental performance beyond the opportunity to avoid redundant computation. Attractive restraint should not require texture, rounding or more decoration.

## Must fix

**Coloured text panel loses contrast.** `aurora.png`, mark 3, `zoom/aurora-3.png`: the yellow mark turns the red label orange while turning its white lettering cream. The words remain decipherable but become less separated from their background, and the mark reads as an orange filter rather than a yellow highlighter. This directly fails “at least as legible as before” on coloured panels. This is additional to the accepted dark-page polarity trade-off. The unconditional Wash blend in `HighlightFilter.cpp:315` moves both foreground and background toward the same colour. Smallest local rule change to try: replace that blend with a gamut-limited chroma tint that preserves each source pixel's luminance, rather than changing the segmentation architecture. Verify this exact label retains its original letter/background contrast; simply lowering the wash opacity reduces but does not remove the defect. The current fallback tests assert the blend formula, not readability.

## Nice to have

**Red looks like pink stationery.** `history-colours.png`, mark 1 (`zoom/history-colours-1.png`) and `cinnamon-colours.png`, mark 1: the red swatch produces a pale salmon band. It is distinct from orange, but the person choosing red may feel the tool substituted a colour. Smallest adjustment: modestly lower the red pigment's white-mix floor, with a measured readability bound, rather than lowering every marker's floor. This is a tuning suggestion, not a reason to reopen the accepted palette treatment.

**Low-contrast lettering stays too timid inside a loud band.** `plasma.png`, mark 3 (`zoom/plasma-3.png`), “26.04 LTS”: the yellow rectangle dominates while the letters remain faint mustard. Original lettering was already faint, so I do not call this a regression. A small minimum contrast for non-paper transfer entries would improve usefulness; keep true background entries unchanged to avoid reviving noise.

## Preview, determinism and cost

- Downscaled preview filters an already smoothly resized image; export filters source pixels. The nonlinear contrast transfer does not commute with resizing, so glyph weight/edges can differ. The parity test covers only scale 1. Filter at source resolution before reducing the tile if literal parity is required.
- Overlapping highlights differ: export applies every plan sequentially to the accumulated raster; each preview tile starts from the base and omits other highlights. Render overlaps using the same ordered filter stack. No supplied export tests this case.
- This is not integer-only arithmetic: runtime `pow`, `log`, `exp`, floating luminance and threshold comparisons feed byte decisions. Repeatability on one build is plausible; cross-platform bit identity is unproven. Fixed luminance tables and fixed-point decisions would satisfy the stated contract.
- `pigmentOf(marker)` is recomputed for every background through `bandFor`; hoist this marker-only calculation once per plan. The performance test permits 10 seconds for export, so it does not enforce the brief's subsecond release goal.

## Patrick's dark window

With yellow, Patrick will see a strong yellow paper band and dark, readable filenames: obvious emphasis, but still an opaque replacement of the dark surface. With red he will see essentially the same treatment in salmon pink. I expect him to prefer the readability to the rejected muddy tint, but I would not predict that he will love the look: it remains close to the bright-band family he already disliked, and red's pastel substitution makes it feel less like the marker he selected.
