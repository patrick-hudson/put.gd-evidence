# Sol review, round 5

**8/10 for the look. The supplied exports pass visually; one code-level headroom issue remains blocking.**

Read RESOLVED.md first, then CONTEXT.md, RULE.md, the filter, preview/export callers and highlight tests. Viewed all seven full exports and every one of the 32 zoom files individually. Inspected working-tree HEAD `6903237dad94ff6872c8ffe63c808ccb40176bbf`; no builds or lab work performed.

## Look and the revised label

The yellow bands in `history-1`, `history-colours-3`, `cinnamon-1` and `plasma-1` are immediately understandable highlighter marks. Dark lettering reads cleanly; the LCD colour fringes largely disappear without conspicuous halos, block seams or inflated glyphs. The palette remains coherent across light and dark pages. Broad rectangles are assertive, but line-sized marks feel intentional and restrained.

The revised `aurora-neutral-4` preserves the white lettering while turning the right label half into a muted grey-pink wash. It is visibly marked, and the lettering no longer merges with a lightened background. Measuring the dominant flat label/text colours in the actual PNG gives contrast **3.736 before, 3.755 after**; the black left half (`aurora-neutral-3`) gives **3.738**. These measurements support the visual improvement, without claiming every antialiased pixel has identical contrast. `aurora-neutral-1/2` retain the painting's lines and texture; black shades rather than redacts, and white leaves a conspicuous pale veil.

Against Rams' principles, this is useful, understandable and substantially more aesthetically coherent than the rejected families. The absence of extra decoration supports unobtrusiveness and minimal design; retained detail supports honesty and thoroughness. A familiar marker metaphor should age well. The supplied evidence cannot establish environmental impact or long-term durability. The remaining deductions concern colour fidelity and the photographic fallback's filter-like appearance.

## Must-fix

**Large white washes can still clip missed bright pixels.** This is a static code finding, not a defect visible in the supplied small `aurora-neutral-4` label region; that export is fixed. In `HighlightFilter.cpp:275–291`, `brightest` is collected only on the background sampler's grid. Above 500,000 pixels, `step > 1`, so thin white lettering or a bright detail between sample positions can be missed. `apply()` processes those pixels anyway and clamps their gained luminance to white, reopening the contrast loss this revision addresses.

For example, a wash plan whose sampled maximum is Y=0.4 chooses gain 1.6. Unsampled neighbouring luminances 0.6 and 0.9 become 0.99 and 1.0: contrast falls from 1.46 to 1.01. This follows directly from the implemented formula; it is not an application reproduction. The smallest correction is an exact maximum-luminance scan for a light neutral wash after fallback selection, keeping background sampling unchanged and storing one common gain in the plan. Add a >500k-pixel noisy-background case with bright lettering deliberately off the sampling grid. The current 260×80 badge test cannot catch this.

## Nice-to-have, not blockers

- `history-colours-1` and `cinnamon-colours-1`: red reads as salmon/pink. This weakens identification of the chosen red pen. A red-specific lower pigment floor is the smallest rule change, but reopens the explicitly accepted palette decision; I do not require it.
- `plasma-3`: the “26.04 LTS” lettering remains faint inside a very obvious yellow band. It attracts attention without making the words easy to read. A minimum ink-contrast floor would address this, but contrast boosting remains the separately recorded design decision.
- `aurora-1/2` and `aurora-neutral-2`: olive, violet and grey photographic rectangles read more like colour filters than pen strokes. This is the accepted luminance-preserving fallback trade-off; I have no small change that improves pen fidelity without compromising its contrast contract.

## Preview, determinism and cost

Both paths compute the plan from the redacted source before blur, including the common gain. Reduced-scale filtering and overlapping-highlight differences remain the documented pre-existing limitations. Tables use floating-point math, so this is repeatable within a build rather than a strict cross-platform integer contract. The new maximum calculation adds luminance work even for paper/coloured marks that never use it; restricting the exact scan to light neutral fallback also avoids that waste. No fresh timing claim.

## Patrick's likely experience

On his dark put.gd window, yellow will make an unmistakable warm band with dark, readable lettering, much closer to a familiar marker than the rejected dark tints and outlined treatments. Red will behave equally clearly but look pastel salmon. I expect him to prefer yellow substantially; red's washed-out identity remains the likeliest aesthetic reservation. His approval still requires trying this build himself.
