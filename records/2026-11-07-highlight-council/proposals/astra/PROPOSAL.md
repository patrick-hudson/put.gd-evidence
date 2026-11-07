# Astra: soft pigment, contrast-matched neutral ink

One candidate, ranked first. A pale, recognisably coloured marker band with clean neutral lettering. No frame, underline, shadow, rounded UI container, texture, invented handwriting, or extra badge. Yellow stays lemon; red becomes a red-ink wash rather than an error-state red rectangle.

**Recommendation:** show this candidate to Patrick as an improvement on round 2. Do not declare it accepted or claim it passes every test. It substantially addresses round 2's harsh colour and dirty glyphs, but the supplied coverage estimate and the finite contrast of coloured paper leave measurable exceptions. These are reported below, not hidden by the contact sheets.

## What the reader sees

- Light page: a pale marker stroke behind neutral dark lettering, with the surrounding page still visible.
- Dark page: a pale marker stroke with reversed dark lettering, clearly separate from the application's dark controls.
- Coloured panel: the same pigment band, with the selected content rendered in neutral lettering rather than mixing the panel colour into the marker.
- Photo or uncertain background: a transparent coloured wash through which the picture remains visible.
- White marker: a chalk-white band with dark lettering; black marker: a charcoal band with light lettering.

## Why this is different from the rejected designs

Round 1 put already-muted light text on a brighter dark colour, spending contrast the text did not have. I do not retain that polarity for coloured markers. Candidate B added the visual grammar of selection frames and rules; this proposal adds no decoration.

Round 2 correctly made the colour obvious, but uses a Euclidean distance-to-background threshold of 70 as though it were true glyph coverage. A partially covered pixel can already exceed 70 and be treated as opaque. Applying a coverage exponent after that clipping cannot recover the lost ramp. Darkening the unmixed RGB channels also retains the original LCD red/blue fringes. The result in the supplied zoom has heavy, colourful edges.

This proposal uses the supplied mask to identify exact background, but uses source-pixel contrast to determine the new pixel. It never assumes `coverage == 1` means a fully opaque glyph. Every output glyph pixel lies on one pigment-to-neutral ramp, so source LCD chromatic fringes cannot survive as unrelated red/blue edges. The softer pigment gives the text more contrast headroom and is less aggressive than a saturated selection-like fill. This is a deliberate improvement on round 2, not a claim that polarity reversal was never rejected.

## Exact pixel rule

`render.py::proposed` is the executable definition. All channels are unassociated sRGB bytes; retain original alpha. Inputs are source pixel P, estimated background B rounded to nearest byte, ink coverage c in [0,1], marker M, and the existing region confidence. Page classification may be supplied, but the confident-region output intentionally has the same rule on light and dark pages. Geometry and snapping are unchanged.

Integer rounding below is nearest with half upward, except explicitly named floor/ceiling operations. Intermediate arithmetic requires signed 64-bit integers. No spatial filtering, dilation, erosion or neighbour averaging is added.

1. Define the compile-time 256-entry linear-light table `T[v] = round(65535 * srgb_decode(v/255))`, using the standard sRGB transfer curve. Freeze these constants in production; do not evaluate powers at runtime.
2. Fixed-point luminance is `L(P) = floor((13933*T[R] + 46871*T[G] + 4732*T[B] + 32768)/65536)`. It ranges from 0 to 65535.
3. Choose pigment Q once per marker. For normal colours, examine integer white additions w from 89 through 255. Set each channel `Q = floor(((255-w)*M + 255*w + 127)/255)`. Use the first Q with `L(Q) >= 51117` (approximately 0.78). This white-mixing path preserves the colour family without clipping individual linear RGB channels into a different hue. Use neutral black ink F=(0,0,0).
4. Near-white markers, all channels >=240: Q=(232,232,232), F=(0,0,0). Near-black markers, all channels <=32: Q=(30,30,30), F=(255,255,255). Other custom colours use step 3. These exact thresholds are a documented discontinuity; they are not an adaptive colour picker or a new user control.
5. Construct the 256-entry ramp `R[a] = floor(((255-a)*Q + a*F + 127)/255)` for a=0..255.
6. Define fixed-point contrast `K(X,Y) = ((max(L(X),L(Y))+3277)*1048576)/(min(L(X),L(Y))+3277)`. Source target S is ceiling K(P,B); ramp entries are floor K(R[a],Q). Both are integers.
7. If c=0, output Q. Otherwise choose the smallest a whose ramp entry is >=S, and output R[a]. If no such entry exists, use a=255. This is a monotone 256-entry lookup/binary search, not iterative per-pixel colour fitting. There is **no multiplication by c** after lookup: doing that would once again mistake the clipped distance mask for optical alpha.
8. The mask boundary is the existing mark boundary, at original source resolution. Decoration sizes: zero. No new feathering or expansion. The supplied sheets use exact rectangular harness boxes to keep comparisons controlled; existing production text snapping is unchanged.

The fixed-point luminance approximation has small rounding differences from floating WCAG, so the measurement code separately reports floating WCAG on the actual byte outputs. The Python research segmentation still uses floats; this proposal does not replace or certify that existing architecture.

## Photos and uncertainty

When the supplied harness confidence is below 0.5, use `O = floor((184*P + 71*M + 127)/255)` per channel: a 27.84% wash, identical for every colour, including white and black. Do not convert photographic structures into neutral lettering or pretend their mask is text. This fallback is deliberately weaker than today's 41% fill. It is visible in `sheet-photo.png`.

This is not a universal text-preserving fallback. The red accent crop enters it with the current estimator; wallpaper lettering has no coverage>=0.9 cores, making that core metric unavailable. That is a remaining failure against a literal “all coloured panels” guarantee. There is no OCR, semantic text detection or new segmentation architecture in this proposal.

## Assessment against the design tests

- **Readable:** contrast matching preserves each source contrast until the ramp saturates. In the required yellow/red table, Plasma and paragraph examples, no pixel loses more than 0.02 contrast ratio in the matched-background metric. The dark notice still has small exceptions, including panel and icon structures. The aggregate harness text estimate also changes slightly because averaging colours before measuring contrast is nonlinear. Pixel contrast is evidence, not proof of equal perceived legibility after polarity reversal.
- **Obvious:** the pale coloured area is immediately visible on dark captures; the selected colour family survives on light pages. Red is intentionally pastel pink-red, not the literal palette RGB. The charcoal marker on an already near-black surface is the weakest case. An identical source and pigment cannot visibly mark that area without a different rule or decoration.
- **Honest:** a flat marker band is familiar. No outline or line makes it resemble a focused UI control. A pale block spanning many table rows can still resemble a label or tape; the already-agreed line snapping matters here.
- **Every colour:** all seven colours and arbitrary custom RGB values have defined output. White and black are explicitly achromatic writing materials, not malformed yellow markers. Near-white pastel custom colours become less distinguishable from white; this is a colour-gamut tradeoff, not solved by these maths.
- **Quiet:** no independent LCD chroma remains within the confident mark. No neighbourhood operation can enlarge a glyph's support. Perceived weight can nevertheless change because polarity and contrast change, and source background estimation errors can still produce seams or treat an icon as ink. The original subpixel geometry cannot be recovered perfectly from one RGB raster. Do not certify “no fat glyphs” from a WCAG number alone.
- **Fits put.gd:** one mark, one pigment, no added chrome or decorative motif. The band is quieter than round 2. The restrained pastel choice is intentional, not a random palette expansion.
- **Deterministic and cheap:** integer source-pixel rule, frozen LUTs, same source-resolution processing for preview and export. Cost is linear in pixel count, with at most eight ramp comparisons per pixel. No C++ 4K benchmark was run; the sub-second release gate remains unproven.

A literal universal promise is impossible for an opaque coloured band: black text on white has 21:1 contrast; any nonwhite coloured paper with black ink has less. Keeping 21:1 would require changing the shape of the mark, leaving paper uncoloured around ink, or retaining white paper. Those conflict with other requested properties or the rejected families. I would not hide this contradiction by reporting a 4.5:1 threshold as “at least as legible as before.”

## Evidence and reproduction

Run `python3 -I /home/patrick/work/i1237-council/proposals/astra/render.py`. The script imports the copied harness and its locally installed NumPy wheel. NumPy was not available to the workstation's Python despite the brief, so NumPy 2.5.4 was installed only into this proposal's `vendor/`, with its download cache also inside the proposal. No system packages, repository files, branches, builders, or research source were changed.

`sheet-dark.png`, `sheet-light.png`, and `sheet-colours.png` contain exact 2x nearest-neighbour source crops; only surrounding uninteresting crop margin is trimmed. All seven colours appear on all four required crops, with today and round 2 alongside. `sheet-photo.png` adds the fallback comparison. `*-overview.png` are reduced browsing copies, not the 2x evidence. `inspect-*.png` retain four individual yellow tiles.

“Today” is 105/255 source-over. “Round 2” is a research reproduction of the inspected C++ paper luminance clamp, darkened ink and coverage^1.5 rule, using the Python harness segmentation. It is **not** an actual application export or guaranteed byte-exact C++ reproduction. The supplied real round-2 export was also visually inspected.

`numbers.csv` and `numbers.json` contain 231 crop/colour/mode records, including extra crops beyond the contact sheets. `contrast_min`/`contrast_orig` are the supplied harness's estimated text contrast against an averaged background. `core_wcag_min` measures every coverage>=0.9 pixel against its corresponding transformed local background; it is conservative and includes antialiased pixels, icons and panel edges, so values around 1:1 are not a valid headline contrast for glyph interiors. Both metrics are retained. `core_rgb_shift_mean` is mean Euclidean RGB distance on exactly coverage>=0.9; `core_channel_abs_shift_mean` provides mean absolute channel change. Photo text contrast is N/A, not a pass. The RGB shifts are intentionally substantial because neutralising or reversing the text changes it.

All 24 supplied images in rejected/, survey/, crops/ and acc/ were inspected using the image tool before design. `acc/plasma.png` contains a PPM payload; after the image tool rejected it, it was decoded losslessly to `plasma-source-decoded.png` inside this proposal and inspected. `input-sha256.json` records the source identities. `optical-experiment.py` preserves the discarded first attempt; it is not a second recommended candidate and should not be used to regenerate the final sheets.
