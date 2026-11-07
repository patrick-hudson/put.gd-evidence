# Highlight look: "true marker, kept contrast" (Opus proposal)

One design, no decorations. Sheets: `sheet-dark.png`, `sheet-light.png`,
`sheet-colours.png` (every tile labelled with today and round 2 beside it).
Numbers: `numbers.md` / `numbers.json`. Renderer: `opus_hl.py` (needs the harness copy
`hl_research.py` next to it; `python3 -I opus_hl.py OUTDIR`).

## The idea in one paragraph

A highlighter does two things: it paints the paper in its colour, and the
text stays exactly as readable as it was. So the rule is:

1. **The paper becomes the marker.** Every background pixel turns into the
   swatch the user picked. On a light page the marker is multiplied onto the paper,
   as ink on paper. On a dark page the band *is* the swatch. Either way the reader
   sees the palette colour, never an olive or a pastel version of it.
2. **Each pixel keeps its contrast ratio against its own paper**, re-expressed
   against the band. On a dark page the light text has nowhere to go on a bright band,
   so the contrast is *mirrored*: a pixel 7:1 brighter than its paper becomes 7:1
   darker than the band. This is a per-pixel function of luminance only, with no
   unmixing, no coverage threshold and no target ink colour. Anti-aliasing ramps
   therefore stay ramps, glyphs keep their weight, and the text hierarchy (bright
   title, muted subtitle) survives.

On a dark page the result is the most familiar highlighter look there is: a bright
yellow band with dark text, as on paper. The rejected designs were all
trying to avoid that look. Round 2 got close to it and failed on execution, as
the diagnosis below shows.

## Why the rejected versions failed, and what this changes

| Rejected | What the owner saw | Root cause | Here |
|---|---|---|---|
| Round 1 D′ (amber tint at L 0.183, ink untouched) | "a mess, text is hard to read" | A mid-dark tint compresses the contrast range. Light-grey text on olive drops to about 2–3:1, and the olive band is neither visible as yellow nor quiet. The live screen also showed block-coloured patches from per-block tint caps. | The band is the true, bright swatch. Contrast is kept per pixel, not compressed. There are no per-block decisions in the look, so no patches. |
| Round 2 (marker clamped to L 0.45–0.7, ink unmixed and darkened to 5:1) | "I still don't love it" | (a) **Fat, smeared glyphs**: coverage saturates at an sRGB distance of 70, so on white-on-dark text every edge pixel with more than about 23 % coverage is laid as full dark ink. Measured stroke weight is ×1.5–1.8 (`numbers.md`, `w` column). (b) Every ink is pulled to the same 5:1 grey-olive, so text looks soft and muted, and title and subtitle merge. (c) The luminance clamp turns blue into sky, red into salmon and black into light grey, so the band is not the swatch. (d) On light pages the ink is left untouched while the paper shifts, so grey LCD text sits pale on saturated colours (4.4–3.2:1). | (a) No unmixing: the output depends on the pixel's luminance alone, and the mapping is monotone, so stroke weight is ×0.92–1.17 (×1.0 typical). (b) Contrast is kept per pixel: black stays black, muted stays muted but readable. (c) Marker floor is L 0.30 instead of 0.45: red stays red (#FF5E5E; only the darkest swatches are lifted), blue stays blue. (d) Light pages also keep contrast: 6.6–6.8:1 instead of 3.2. |
| B family (tint + outline / underline) | "don't look great" | A frame reads as UI chrome (a selection or focus ring), not as a pen. The tint under it still compresses contrast. | No outline, underline or frame. The band itself carries the colour. |

## The rule, exactly

Notation: sRGB bytes `p` (pixel) and `b` (its paper, from the settled block-local
estimate). `lin()` is sRGB→linear and `Y()` is WCAG luminance from linear RGB.
`L = Y(p)`, `Lb = Y(b)`. The marker swatch is `m`.

Constants:

| name | value | meaning |
|---|---|---|
| `darkPage` | 0.30 | paper luminance below which the page is dark (unchanged from the PR) |
| `markerFloor` | 0.30 | the band is never darker than this, so black text on it keeps 7:1 |
| `lightVisibility` | 1.40 | the band must differ from light paper by at least this contrast (the white marker) |
| `readable` | 7.0 | the strongest ink on a band is lifted to at least this, if the band allows |
| `gainCap` | 1.6 | the most that lift may scale contrast |
| `knee` | 0.04 | log-contrast below this counts as paper (noise, gradients, seams) |
| `photoShift` | 0.80 | photo fallback strength |

### Step 1: the marker as the band shows it (per marker, once)

```
m' = m                                  if Y(lin m) >= 0.30
m' = atLuminance(m, 0.30)               otherwise   (scale lin RGB, hue kept; channels that
                                                     clip are made up by mixing toward white)
```

Palette results: red, blue and black are lifted (red #EF4444 → #FF5E5E, blue #3B82F6
→ #4C94FF, black → #959595 neutral grey). Orange, yellow, green and white are
unchanged. A custom navy becomes a medium blue, and any custom colour works.

### Step 2: the band and ink direction (per paper colour, in the plan)

* **Light paper** (`Lb ≥ 0.30`): `band = srgb(lin(b) ⊙ lin(m'))` (multiply in linear
  light). If `contrast(band, b) < 1.40` (only a white or near-white marker), `m'` is
  darkened in linear light until it reaches 1.40. That gives a light grey band
  (#DADADA on white), as visible as yellow is on white (1.54). Ink stays on the dark side (no flip).
* **Dark paper** (`Lb < 0.30`): `band = m'`. The ink flips to the dark side.
* `LB = Y(band)`.

### Step 3: readability gain (per paper colour, in the plan)

Over the sampled pixels of this paper that are at least half ink (the settled
coverage ≥ 0.5), take `s90` = the 90th percentile of `|ln((L+0.05)/(Lb+0.05))|`.
`limit` is the most contrast the band offers on the ink's side: `(LB+0.05)/0.05` toward
black. Then

```
gain = clamp( ln(min(7, limit)) / s90 , 1.0 , 1.6 )
```

The gain is 1 for normal text, which is already 7:1 or more. It only lifts text that
was low-contrast to begin with: white on a blue button goes from 4.6:1 to 6.1:1,
and a muted dark subtitle from 5.2:1 to 5.5:1. One factor scales every pixel of that
paper, so shapes and hierarchy are untouched. *This is the one input beyond paper
luminance and marker. It comes from the same plan samples. Drop it and the rule still
works, keeping low-contrast text exactly as it was.*

### Step 4: per pixel, the contrast transfer

```
s  = ln((L + 0.05) / (Lb + 0.05))           signed log-contrast against its own paper
s  = s · smoothstep(0.04, 0.12, |s|)        knee: |s| < 0.04 is paper, |s| > 0.12 is kept exactly
s  = gain · s
s' = −s on dark paper (mirror), +s on light paper
L' = clamp((LB + 0.05) · e^{s'} − 0.05, 0, 1)
```

Equivalently, without logs: `L'+0.05 = (LB+0.05)·((L+0.05)/(Lb+0.05))^(±gain)`.
**Every pixel's contrast with the band equals its contrast with the page** (times the
gain), until it reaches black or white.

Colour of the pixel:

* **Dark paper** (mirrored), with `B = lin(band)`:
  * `L' ≤ LB`: `out = srgb( L' · (1 + (B/LB − 1) · L'/LB) )`. The ink takes the band's
    hue at its anti-aliased edges and turns neutral at its core, so stems are crisp
    near-black, not olive. The luminance is exactly `L'`.
  * `L' > LB` (pixels that were *darker* than their paper, such as a shadow or a dark
    separator): `out = srgb( B + (1 − B)·(L' − LB)/(1 − LB) )`, lighter than the band.
* **Light paper** (contrast kept): `Q = lin(p) ⊙ lin(m')`, the classic multiply in
  linear light, so ink hue and LCD subpixel structure are kept. Then rescale it to the
  luminance `L'`:
  `Q·(L'/Y(Q))` when `L' ≤ Y(Q)`, else `Q + (1−Q)·(L'−Y(Q))/(1−Y(Q))`.

Paper pixels (s = 0) land exactly on the band, so there are no seams. Zebra rows and
two panels inside one box both become the same band, because each paper maps to it.

### Step 5: no paper found (photo, painting, gradient): the fallback

When fewer than half the blocks are confident (the settled test):

```
μ   = mean sRGB colour of the box (plan samples)
out = clamp( p + trunc(0.8 · (m − μ)) , 0, 255 )      per channel
```

The region's average moves 80 % of the way to the swatch, while every local
difference (line work, lettering, texture) is kept, because all pixels move by the
same offset. A translucent fill or a multiply/screen halves or crushes the detail.
The result reads as a dye wash: bright yellow over the painting with the ink lines
intact (`sheet-dark.png`, painting rows). The colour shift is one constant, so there
are no seams and preview tiles match export. A white marker brightens, a black one darkens.

### White and black

* **White on a dark page**: a pure white band with dark text whose contrast is mirrored
  (10:1 kept on the Plasma notice). It reads unmistakably as "white marker".
* **White on a light page**: a light grey band (contrast 1.40 with the paper), text
  kept at 6.8:1.
* **Black**: lifted to a neutral mid grey (#959595) on both page types, with dark text
  at 7:1. A black highlighter that hid the text would be a redaction, and put.gd has a
  Redact tool for that. On light pages it is a visibly darker grey than the white
  marker's, so the two stay distinct.

## What the reader sees

* **Light page**: the words sit on a band of the chosen marker colour, exactly like a
  highlighter on paper, with the text as dark as before (6.6–6.8:1 on the Cinnamon paragraph).
* **Dark page**: the words sit on a bright band of the chosen marker colour with crisp
  dark text, the way a printout of the screen would look highlighted. The title is
  still bolder and brighter in relative terms than the muted line under it.
* **Coloured panel** (blue button, navy notification, red accent): the band is the
  marker colour over the panel, and the panel's light text turns dark at 6–10:1.
* **Photo or painting**: the area is washed in the marker colour with every line and
  texture of the picture still visible.

## Against the design tests

* **Readable.** Worst text contrast (10th percentile of glyph cores, `numbers.md`):
  dark table 7.0–7.7 (original 7.7), dark notice 7.0–7.1 (7.1), Plasma 7.0–10.2 (10.2),
  light paragraph 6.6–6.8 (6.8), menus and popups 7.0–9.7 (8.8–9.7), syntax sample
  7.0–8.7 (8.7), white-on-blue button 6.1 (4.6). Round 2 sits at 4.9 everywhere on dark
  pages and 3.2 on light pages; today sits at 2.5–4.4. The one place under the original
  is a red, blue or black band under text that was 10:1, which drops to 7:1 (WCAG AAA).
  That is the price of keeping those swatches saturated (see trade-offs).
* **Obvious.** The band is the palette swatch at full strength on every page type
  (the only lifts are dark swatches to L 0.30). Band-to-page contrast on dark pages is
  4.5–17:1, and yellow on a dark table is unmissable. In the user's "yellow, then red"
  scenario the two bands are #FACC15 and #FF5E5E, which no one confuses.
* **Honest.** It is what a highlighter does: colour under the words, words still
  black. There is no frame, outline, glow or rounded chip, so it doesn't read as a
  selection (selections in dark UIs keep light text on a dark-blue band, and this keeps
  dark text on the marker).
* **Every colour.** All seven colours are rendered on four scenes in
  `sheet-colours.png`. Custom colours follow the same two steps (floor at 0.30;
  white-like colours get the light-page visibility floor).
* **Quiet.** Stroke weight ×0.92–1.17 (round 2: ×1.5–1.8). There are no halos,
  because no pixel is left at its old colour while its neighbour moves. The dark-page
  output is a function of luminance alone, so LCD colour fringes collapse to neutral
  and cannot turn into blue or red stems. On light pages the multiply keeps each
  subpixel's coverage exactly, so the text looks as it would if rendered on that colour.
  The knee absorbs paper noise and gradient steps, so no block seams appear.
* **Rams / Pragmatic.** One idea ("the paper becomes the marker, the text keeps its
  contrast"), no decoration, the user's colour shown as picked. As little design as
  possible.
* **Deterministic and cheap.** See below.

## Implementation sketch (C++, fits the settled filter)

The plan already holds `backgrounds`. Add per background: `band` (RGB), `flip`, `gain`,
and for dark paper a **4096-entry RGB table** indexed by quantised linear luminance
`idx = (2126·lin16[r] + 7152·lin16[g] + 722·lin16[b]) >> k` (12-bit). The table holds
the finished output colour, because the dark-page output depends only on `L` and per-paper
constants. Building it costs 4096 evaluations per paper; the knee, gain and mirror are
all inside it. Per pixel on dark paper: three table loads for `idx`, then one RGB load.

For light paper, per pixel: `Q_c = lin16[p_c]·lin16[m'_c] >> 16`, `Yq` (three
multiply-adds), `L'` from a per-paper 4096 table indexed by `idx`, then one integer
divide and three `srgb4096[]` loads. The photo fallback is one add and clamp per channel.

All per-pixel work is integer table arithmetic. The tables are built in double from
the same constants in the same code path for preview tiles and export, so export ==
preview. Cost is below the round-2 apply (which did a square root, an unmix and a
darkening per pixel); a 4K box stays well under the measured 173 ms export.

## Trade-offs I'd rather state than hide

1. **Syntax colours lose their hue on dark pages.** Coloured light ink becomes neutral
   dark ink at its own contrast (`syn-syntax` rows). The text stays readable and the
   hierarchy stays, but "this string was orange" is gone. A real yellow highlighter on
   coloured print also shifts hues; keeping hue under a polarity flip produces
   complementary colours, which looked worse.
2. **Red, blue and black bands cap dark-page text at 7:1.** Raising `markerFloor` to
   0.45 (round 2's value) gives 10:1 but turns red salmon and blue sky. 0.30 keeps the
   swatch recognisable and the text AAA.
3. **A big, saturated band on a light page is loud** (a red paragraph, `sheet-light.png`).
   That is what a red marker is; the user picked it.
4. **Readability gain** reads one per-paper statistic beyond paper luminance. It is
   optional (set `gainCap = 1`), and only matters for text that was low-contrast before.
5. **Fallback colour clip.** In the shift fallback, strongly coloured text on a
   misclassified label can swing hue (white text on a red label under a black marker
   turns cyan-ish). Such labels are normally classified as paper (the real app snapped
   the Aurora label as paper in round 2's acceptance), so the fallback only shows on
   true photos and gradients.

## Considered and dropped

* **Ink in the marker's hue all the way to the core** (dark olive text on yellow): it
  measured the same but looked muddy next to neutral cores. Neutral cores read crisper,
  and the ink edges still blend into the band without fringes.
* **Fallback as a translucent fill, multiply/screen, or a contrast-relative lift**:
  fill and multiply/screen flatten detail, and the lift washes photos to grey (tried in
  `fallback_try.py`).
* **Rounded "marker tip" ends or any outline**: decoration that the band doesn't need,
  and the B family showed that frames read as UI.
