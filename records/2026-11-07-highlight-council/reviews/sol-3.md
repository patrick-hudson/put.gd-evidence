# Sol review, round 3

**8/10; one blocking finding remains.** Reviewed commit `47d8190a7307c8ea54191fb1b0e1d5b85be9e589`, all seven full exports, all 32 zoom files, and the four untouched captures. No builds or lab work performed.

The ordinary text bands are convincing. Cinnamon's yellow looks like a highlighter, and History's yellow makes the marked rows immediately identifiable without sacrificing readable lettering. Orange, green and blue remain distinguishable. The neutral washes now visibly mark the painting; importantly, `aurora-neutral-1.png` retains the tree, ladder and pumpkin instead of becoming a redaction. The yellow label in `aurora-3.png` retains clear white text. I see no new halos, block seams or conspicuous subpixel fringes across the exports.

Against Rams: useful, understandable, restrained, unobtrusive around the marked content, and largely thorough in detail. The fixed palette treatment supports consistency and longevity. Innovation is less important here than reliable reading. Honesty and good design still suffer when a marker dims the very text it calls attention to. Environmental impact cannot be established from these pictures; cheap processing is relevant but requires measurements, not aesthetic inference.

## Must fix

**Black wash reduces the red label's text contrast.** In `exports/aurora-neutral.png`, mark 3 (`zoom/aurora-neutral-3.png`), the bright white lettering becomes noticeably grey and less clear against the shaded red. This is milder than the former crushed painting, but violates “at least as legible as before.” Pixel inspection confirms it: a common background pixel changes from `(255,40,60)` to `(185,32,45)`; white glyph interiors become `(188,188,188)`. Their WCAG luminance contrast falls from approximately **3.74:1 to 3.34:1**. This is a new neutral-wash issue, not the resolved yellow-label problem.

Cause: `HighlightFilter.cpp:337` halves `Y`, which does not preserve ratios of `Y+0.05`. Smallest targeted rule change: retain the shadow-preserving toe, but give the upper range a contrast-preserving affine segment. For example, `max(0.5*Y, 0.6*(Y+0.05)-0.05)` keeps dark detail while placing this label background and its lettering on the same affine segment. Verify the actual label and painting again; this example fixes their conflict but is not a universal contrast guarantee for pairs spanning the toe. Do not restore the globally clipped shading rule that crushed the painting.

## Nice to have / retained trade-offs

- `history-colours-1.png` and `cinnamon-colours-1.png`: red remains salmon/pink. The chosen marker is less immediately identifiable than yellow. The smallest adjustment would be a red-specific pigment floor, but that reopens the explicitly retained palette decision; I am not making it a gate.
- `plasma-3.png`: faint wallpaper lettering remains faint under a very obvious yellow rectangle. Improving it would require a minimum ink-contrast floor; that is the already recorded, separate decision to boost contrast.

## Code, parity and evidence limits

The same plan/filter serves export and preview. Previously noted limitations remain: preview filters a resized raster below full scale; overlapping preview tiles independently read the base while export applies marks sequentially. Neither is a new look regression.

Tables use floating-point `pow/log/exp`, and the wash performs floating-point work per pixel; this is repeatable within the build, not the brief's strict integer-only arithmetic. Pigment is correctly hoisted. Wash colour conversion/gamut mapping could be cached or tabled if measured slow; I did not measure performance or rerun tests. The neutral test allows 15% contrast drift and therefore misses the observed label loss.

White lightening also clips above `Y=0.60625`, so its contrast-preservation claim has a saturation exception. **White-on-label is not demonstrated:** mark 4 and `aurora-neutral-4.png` cover painting to the label's right. Reposition that mark over lettering before claiming that case passes.

## Patrick's likely experience

On dark put.gd, yellow will produce a strong yellow band with dark, cleanly readable lettering, like `history-1.png`; I expect him to prefer this to the rejected muddy versions. Red will behave consistently but look salmon rather than red. He may like the yellow immediately and remain lukewarm about red; the exports cannot establish his approval.
