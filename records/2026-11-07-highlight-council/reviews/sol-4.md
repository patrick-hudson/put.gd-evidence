# Sol review, round 4

**8/10; one blocking finding remains.** Reviewed commit `3e4ec46f8242284c9399f0823abc6e96573bd7f4`, all seven full exports, every one of the 32 zoom files, the four untouched captures, and the filter/preview code. Read `RESOLVED.md` first. No builds or lab work performed; only this review file written.

The ordinary text bands remain convincing: Cinnamon yellow and History yellow read immediately as highlighter marks, with clean dark lettering. Orange, green and blue are distinguishable; notification text stays crisp. I see no conspicuous new halos, fat glyphs, block seams or LCD colour fringes. The revised black wash now keeps the label's contrast: its common red background becomes `(187,32,45)`, white glyph interiors become `(200,200,200)`, and measured contrast is **3.74:1 before and after**. `aurora-neutral-1` still retains the tree, ladder and pumpkin. That round-3 finding is resolved.

Against Rams' principles, this is useful, understandable and visually restrained, with an innovative but coherent treatment of dark pages. The simple bands support unobtrusiveness, longevity and as little design as possible; the remaining white-wash failure weakens honesty and thoroughness in detail. Aesthetics are strongest on text, weaker on photographs where the marks resemble colour filters. Environmental friendliness cannot be established from exports; execution cost needs measured evidence.

## Must fix

**White wash makes the label substantially harder to read.** In `exports/aurora-neutral.png`, right half of the red label, mark 4 (`zoom/aurora-neutral-4.png`), the label turns pale dusty pink while the lettering stays white. It looks washed out beside both the original and the corrected black half. Pixel inspection confirms the loss: common background `(255,40,60)` becomes `(200,160,161)`, while white interiors remain `(255,255,255)`. Contrast falls from **3.74:1 to 2.33:1**, about 38%. This violates the explicit readability test; the new crop demonstrates the previously untested saturation problem.

Cause: `HighlightFilter.cpp`, neutral wash in `apply()`, uses `min(1, 1.6*(Y+0.05)-0.05)`. Above `Y=0.60625`, the glyph clips while the background continues lightening. Tightening the random-pixel test tolerance to 5% does not cover this white-glyph/red-background pair.

Smallest targeted rule correction: make white-wash gain common to the whole region and limit it to available luminance headroom, rather than clipping individual pixels. With maximum source luminance `Ymax`, use `g=min(1.6,1.05/(Ymax+0.05))` and `Y'=g*(Y+0.05)-0.05`. Where white ink forces `g=1`, retain the existing white-directed chroma mix and gamut mapping at unchanged luminance: on this coloured label it produces a visible desaturating mark without sacrificing contrast. Determine the gain from source pixels in the plan so preview/export agree. Recheck the actual label and painting; this is a targeted remedy, not proof that white can visibly mark every neutral image. Add a white-glyph/coloured-label contrast assertion.

## Nice to have / retained choices

- `zoom/history-colours-1.png` and `zoom/cinnamon-colours-1.png`: red reads salmon/pink. This weakens immediate marker identity. A red-specific lower pigment floor is the smallest adjustment, but reopens the expressly retained palette decision; not a gate.
- `zoom/plasma-3.png`: the yellow band is obvious while faint lettering remains faint. A minimum ink-contrast floor would improve it; that remains the separately recorded contrast-boost decision.

## Code and evidence limits

Export and preview share the filter. Existing differences remain: preview applies the nonlinear filter after resizing, and overlapping preview tiles independently read the base whereas export applies highlights sequentially. These are recorded architecture limitations, not new blockers here.

`pow/log/exp`, floating-point luminance and rounding mean this is repeatable within the build, not strictly integer-only or a proven cross-platform byte guarantee. Pigment is hoisted correctly. Wash still does floating-point scaling/gamut work per pixel; caching repeated source-colour results is a possible optimization if measured slow. I did not run performance or unit tests.

## Patrick's likely experience

On his dark put.gd window, yellow will produce an unmistakable yellow band with clean dark lettering, as in `history-1`; I expect him to prefer it to the rejected muddy versions. Red will be equally readable but look salmon. Yellow is likely to satisfy him sooner than red; only his trial can establish whether he likes the palette treatment.
