# Sol review, round 6

**8/10. Acceptable for the look; no blocking findings remain.**

Read RESOLVED.md first, then REVIEW_TASK.md, CONTEXT.md and RULE.md. Inspected HEAD `952220746269062ca041d086a80c102e52f304b3`, the filter, preview/export callers and relevant highlight tests. Viewed all seven full exports and all 32 files in `exports/zoom/` individually with the image viewer. No builds, tests or lab operations performed.

## Look as exported

The strongest results remain the everyday text marks: `history-1`, `history-colours-3`, `cinnamon-1` and `plasma-1/2`. Yellow reads immediately as a highlighter on both light paper and dark panels. The polarity change produces readable dark lettering without conspicuous halos or swollen glyphs. Cinnamon's LCD fringes largely disappear inside the marks. Across the inspected crops I see no objectionable block seams or new coloured fringes. The small blue date mark (`history-2`) and green filename mark (`history-3`) also work at full-image scale.

The neutral Aurora exports remain convincing within their fallback treatment. `aurora-neutral-3/4` keep the split label's lettering visibly distinct from its darker red and muted grey-pink backgrounds. `aurora-neutral-1` retains the painting's texture and black linework rather than becoming a redaction. `aurora-neutral-2` leaves a conspicuous pale wash with the underlying drawing intact. The coloured label in `aurora-3` stays readable under the ochre wash.

Against Rams' principles, the result is useful, understandable and aesthetically coherent; its plain bands support unobtrusiveness and “as little design as possible.” Clean edges and retained image detail show care. The familiar marker metaphor has a credible basis for lasting use. Innovation serves readability here. Honesty is weaker on photographs, where the result resembles a filter. These exports cannot establish environmental friendliness or long-term durability. The remaining deductions are aesthetic trade-offs, not grounds to reopen the settled architecture.

## Must-fix

None found. The previous blocking headroom issue is addressed: `plan()` now scans **every pixel** for the brightest luminance, only after selecting wash mode for a light neutral marker. Its common gain therefore includes bright details missed by the background sampling grid. The added 1200×500 test puts a bright vertical line at off-grid x=601 and asserts retained contrast plus actual lightening. This is the targeted correction requested in round 5. I inspected the test; I did not execute it.

## Nice-to-have

- **Red identity:** `history-colours-1` and `cinnamon-colours-1` look salmon/pink rather than the selected strong red. Readers still see a deliberate mark, but the maker may find the pen colour surprising. A lower pigment floor specifically for red is the smallest rule change; it reopens the accepted palette choice and is optional.
- **Faint source lettering:** `plasma-3` makes the yellow band much more prominent than “26.04 LTS.” The words remain faint. A minimum ink-contrast floor would improve this, but it is the separately recorded contrast-boosting decision, not a regression in this revision.
- **Photographic pen fidelity:** `aurora-1/2` and `aurora-neutral-2` read as olive, violet and grey filter rectangles. This weakens the pen metaphor and, particularly for yellow, colour identification. I have no small correction that preserves the agreed luminance contract; retain this as an acknowledged limitation rather than add decorations or reopen the fallback.

## Preview, determinism and cost

The exact headroom scan uses the same source-derived plan in preview and export. Reduced-scale filtering and overlapping-highlight differences remain the documented existing limitations: preview filters resized source tiles and independently previews marks; export applies marks sequentially. Floating-point table construction and wash calculations provide repeatability within a build, not a strict cross-platform integer-arithmetic guarantee. Pigment is computed once per paper plan; the new exhaustive scan is correctly restricted to light neutral washes. No additional performance blocker found, and no fresh timing claim.

## Patrick's likely experience

On his dark put.gd window, yellow will produce an unmistakable warm band with dark, clean lettering, recognizably closer to a familiar marker than the rejected tints and frames. Red will be equally readable but visibly pastel salmon. I expect yellow to please him more; red's softened identity is still the likely reservation. That is a prediction from the exports, not evidence of his approval.
