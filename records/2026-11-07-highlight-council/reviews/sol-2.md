# Sol — revised look

**8/10. Hold only for the neutral-marker Wash gap below.** Reviewed commit `725a32c8a83cc3bf4881cf4dc9653cfa93f612ab`, all six full exports and all 28 zoom files individually with the image viewer. Read RESOLVED first, then the brief, rule, filter, rendering paths and highlight tests. No builds or lab activity.

The revised Aurora label (`aurora.png`, mark 3; `zoom/aurora-3.png`) keeps white lettering clearly separated from the orange background. The prior readability blocker is resolved visually. “Exactly” preserved contrast overstates the implementation: finite sRGB tables and byte rounding introduce small luminance errors, and the test allows drift below 0.02. The gamut correction itself correctly moves toward equal-luminance grey before conversion.

Cinnamon's text remains clean, History's emphasis is immediate, and Plasma's notification is crisp. I see no conspicuous halos, block seams or coloured LCD fringes in the text marks. Against Rams: useful, understandable, restrained and thoughtfully detailed; innovative in adapting dark captures. Honesty and aesthetics remain qualified by the paper-like replacement of dark surfaces. Longevity benefits from one consistent paper rule. Environmental friendliness is not established by screenshots; bounded processing is its relevant consideration here. The neutral-marker omission prevents a full “thorough down to the last detail” pass.

## Must fix

**Pure-black custom markers disappear in Wash mode.** This is a code-derived finding, **not an observed black export**: the supplied Wash examples use yellow/blue. The relevant pictured source is `aurora.png`, mark 1 (`zoom/aurora-1.png`), whose yellow wash visibly marks the painting. In the same Wash branch with `M = #000000`, `t = 0.4p` and luminance restoration multiplies by 2.5, giving the original pixel back. An in-memory evaluation of that formula and the conversion table on the untouched mark-1 region produced zero channel change throughout. Thus a permitted custom marker can leave no mark, failing “every colour” and “obvious.” Neutral washes on neutral content have the same fundamental problem. Smallest rule-level fix: special-case achromatic Wash markers with a visible neutral luminance treatment instead of chroma-only tinting; retain a measured text-contrast bound. Exact luminance preservation and a visible neutral mark on grey pixels cannot both be required. Add actual black/white Wash exports on this painting and a neutral gradient before passing this gate. No segmentation or UI redesign is needed.

## Nice to have

- **Red reads as salmon pink.** `history-colours.png` and `cinnamon-colours.png`, mark 1, corresponding zooms: readable and distinct from orange, but less faithful to the chosen red. The smallest adjustment would be a modest red-only pigment-floor reduction. RESOLVED explicitly declines that trade-off; I accept it as non-blocking and do not require reopening it.
- **Faint lettering remains faint.** `plasma.png`, mark 3 (`zoom/plasma-3.png`): “26.04 LTS” becomes mustard lettering inside a dominant yellow band. A small minimum non-background contrast could improve emphasis, but would change the accepted contrast-preservation rule. No regression or required change.
- **Yellow Wash looks olive over warm artwork.** `aurora.png`, mark 1, corresponding zoom: the rectangle is visible but less immediately identifiable as yellow than the text bands. A slightly stronger chroma mix is the smallest tuning experiment; check gamut and label readability. This is subjective, not a gate.

## Preview, determinism and cost

The acknowledged architectural differences remain: preview filters resized pixels, while export filters source pixels; overlapping export highlights filter accumulated pixels, while preview tiles each start from the base. Nonlinear filtering therefore cannot promise general pixel parity. These settled issues do not block this look review.

The implementation uses floating-point luminance, `pow`, `log` and `exp`, not integer-only arithmetic. Same-build repeatability is credible; cross-platform byte identity is unproven. Fixed tables/fixed-point decisions would be needed for that stronger contract. Pigment is now correctly hoisted once per plan. The Wash path adds per-pixel floating-point work and table conversions; the existing 10-second export test does not establish the requested subsecond release performance. I did not benchmark it.

## Patrick's dark window

Yellow will produce a conspicuous golden paper band with readable dark filenames, without decorative frames or muddy white text. Red will produce the same treatment in pale salmon. I expect Patrick to appreciate readability and immediate emphasis, especially yellow, but liking it is uncertain: the surface still looks replaced by bright paper, and red still looks pink. His earlier rejection of bright bands makes an owner look essential rather than predictable.
