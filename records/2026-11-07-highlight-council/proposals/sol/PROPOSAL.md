# Sol proposal: marker paper

One candidate, ranked first. Make the highlighted area read like pale marker paper, with clean dark lettering. On dark captures, reverse the text's polarity continuously, preserving its original local contrast wherever the output gamut permits. Do not reconstruct glyphs from the distance-based ink mask.

This is an improvement on round 2, not another outline/underline variation. The consequential change is the edge transfer, not just the pastel palette. Round 2 clips distance-to-background at 70 RGB units and uses that as opacity, then unmixes, darkens and lays the letters again. This is not the original font's anti-aliasing coverage: many intermediate edge pixels are treated as fully opaque ink. The resulting letter edges are fat, irregular and coloured. My rule maps the actual source pixel's luminance continuously onto one marker-to-black ramp. No per-channel unmixing, guessed ink colour, thresholded opacity or arbitrary coverage exponent enters the rendering.

The candidate looks materially cleaner on the supplied table and notification. **It is a design proposal, not a claim of passing every acceptance test.** The supplied cases expose the limits described below, particularly the photo fallback, near-black pages, and black/white marker visibility. Owner approval of its appearance is still unknown.

## Reader's view

- Light page: a familiar pale coloured stroke behind dark, clean lettering.
- Dark page: a pale coloured stroke containing dark lettering, with surrounding content remaining dark.
- Coloured panel: a local patch of the same marker paper, with its text contrast carried across from the original panel.
- Photo: a transparent marker wash through which the picture remains visible.
- Black marker: a graphite wash on light pages, or a carbon-black stroke with light lettering on dark pages.
- White marker: a light neutral stroke on dark pages, or a slightly grey chalk wash on light pages.

## Exact rule

`render.py` is the executable rule used for every proposal tile. Inputs: source sRGB byte pixel `P`, resolved background `B`, coverage `c ∈ [0,1]`, marker sRGB byte triplet `M`, existing segmentation confidence. Preserve source alpha. The treatment is independent of application theme.

Coverage remains available to segmentation, snapping and measurement. It is deliberately **not an opacity** in the confident rendering branch: `F(P,B,c,M) = F(P,B,M)` for every c. In particular, a source edge at `c=1` is not assumed to be an opaque reconstructed foreground. This does not change the segmentation or snapping contract.

### Integer luminance

All candidate arithmetic after the existing background resolution is integer. Quantize background means to bytes using round-half-up. The harness merges near-identical backgrounds; resolve each pixel to its closest distinct background as its existing ink-local mode does. Ties use the first background. This is prototype plumbing, not a proposed new estimator.

Let `Q=1048576`, `K=52429`. Use a checked-in 256-entry constant table:

```
T[i] = round_half_up(Q * linear_sRGB(i/255))
L(P) = (2126*T[P.r] + 7152*T[P.g] + 722*T[P.b] + 5000) // 10000
```

Here `linear_sRGB(v)=v/12.92` for `v≤0.04045`, otherwise `((v+0.055)/1.055)^2.4`. Table generation is offline; ship the integer constants. Use signed 64-bit intermediates. The continuous formula describes the constant table only; the pixel loop does not call powers or use floating point. The Python prototype generates this table at startup for convenience.

A background is dark when `L(B)<314573` (0.30 in linear luminance), otherwise light. A marker is neutral when `max(M)-min(M)<12`. A neutral marker is white when its arithmetic channel mean exceeds 220, black when it is below 40. Other neutrals follow the ordinary rule. These definitions include the seven exact requested palette values.

### Paper colour A

For ordinary colours, start with each channel `A_j=(M_j+256)//2`, a half-white pastel in sRGB.

White: start at `(250,250,250)` on dark pages and `(232,232,232)` on light pages.

Black: use `(min(B.r,8),min(B.g,8),min(B.b,8))` on dark pages and `(211,211,211)` on light pages. Skip the following lifting step for black.

On dark pages, for ordinary and white markers, repeatedly add one to each channel, saturating at 255, until both conditions hold, or A is white:

```
L(A) >= 880804
(L(A)+K) * (L(B)+K) >= K * (Q+K)
```

The first condition gives quiet, pale paper (minimum luminance approximately .84); the second reserves enough contrast range to reverse even a white source pixel. This lift preserves sRGB channel differences until a channel reaches the ceiling. Custom colours use exactly the same rule. There is no hue special case for yellow or red.

### Pixel transfer

Let `p=L(P)`, `b=L(B)`, `a=L(A)`.

```
n = max(p+K, b+K)
d = min(p+K, b+K)
```

Thus `n/d` is the original local WCAG contrast ratio, within the stated fixed-point precision. For every marker except black on a dark page, the new ink is dark:

```
u = clamp(((a+K)*d)//n - K, 0, a)
R[t,j] = (A[j]*(255-t)+127)//255     t=0..255
```

Choose the **smallest** t whose `L(R[t]) ≤ u`; if none exists, choose t=255. Emit `R[t]`. At p=b this selects the paper colour. As text departs from its background, output darkens smoothly through the single marker-to-black ramp. Source pixels of either contrast polarity map to this dark ramp; mixed-polarity content is therefore legible but loses its original polarity distinction.

For black on a dark page, keep light ink instead:

```
u = clamp(ceil_div((a+K)*n,d) - K, a, Q)
R[t,j] = (A[j]*(255-t)+255*t+127)//255
```

Choose the smallest t with `L(R[t]) ≥ u`, saturating at t=255, and emit it. This gives a black band with light text rather than a grey version of the white marker.

Use a monotone binary lookup into these 256-entry ramps; build ramps once per distinct background/marker. Export and preview must use the same tables, background plan and integer operations. Keep source pixels outside the existing mark rectangle unchanged. Decoration sizes are **zero**: no outline, underline, halo, feather, shadow, simulated pen texture, handles or additional padding in the export. Existing snapping owns the rectangle.

### Photos and uncertain backgrounds

If fewer than half the existing blocks are confident, use one uniform wash, with no text detection and no blockwise mode switching:

```
out[j] = (151*P[j] + 104*M[j] + 127)//255
```

This is a 40.8% marker wash, including white and black. It is intentionally a recognizable marker treatment of a photograph. It does not promise preserved text contrast inside a photograph. The red annotation over the painting falls into this fallback with the supplied region and shows a contrast loss. That is an explicit failed readability case, not something the aggregate numbers should conceal.

## Against the design tests

| Test | Assessment |
|---|---|
| Readable | Dark table and Plasma lettering have smooth, high-contrast dark strokes. Most flat-background pixels preserve their source contrast by construction. Rounding chooses the higher-contrast ramp entry. Light-page high-contrast ink may hit black and then lose contrast because the paper is darker than the source. The photo/accent fallback also loses contrast. This is not a universal pass. |
| Obvious | The five chromatic bands occupy the marked region and retain recognizably different pastel hues; yellow followed by red is easy to distinguish in these sheets. Black on the already-dark table is visibly weaker than the coloured bands. Near absolute black, the contrast budget forces the paper towards white, eventually erasing hue. |
| Honest | A flat, pale band and ordinary-looking dark letters read as marker paper. No frame or line suggests widget selection. The polarity change remains a digital accommodation; the sheets let the owner judge it directly. |
| Every colour | All seven palette colours are rendered. White and black are neutral material treatments, rather than claiming white ink can visibly stain white paper or black ink can visibly stain black paper. Black on dark remains the weakest choice. Custom hues are deterministic; highly dark neutrals become grey paper on light pages. |
| Quiet | One colour ramp eliminates source blue/red channel fringes; no spatial dilation or blur can create halos or expand glyph geometry. The contrast transfer can change perceived stroke weight, so this still needs a reader comparison at 1x. Real panel boundaries remain visible, and the supplied notice has different backgrounds; this proposal does not promise to repair estimator mistakes. Source syntax colours are intentionally lost within the mark. |
| put.gd language | Flat restrained paper colours, no ornaments, no extra interaction or properties. Content supplies hierarchy. The mark is quieter than full saturated round 2 without retreating into the rejected outline family. |
| Deterministic and cheap | Integer fixed-point table lookups and 64-bit integer products/divisions, one ramp per background, no per-pixel histogram or neighbourhood convolution beyond the existing estimator. C++ 4K timing is not measured here; sub-second release performance is a gate, not a result of this workstation study. |

## Why the universal wording needs a decision

A pure black/white source has contrast 21:1. A visible, non-white coloured paper behind black letters cannot retain 21:1: even pure black output ink has less contrast. Conversely, preserving a white source glyph on pure black at 21:1 leaves no room to add a coloured background. Without an additional mark outside the text (already rejected), an absolute “at least as before” guarantee for all screenshots conflicts with an obvious coloured band. This proposal exposes the tradeoff instead of lowering the numeric floor silently. It does **not** justify ignoring the supplied failures.

My recommendation is to take this one clean-edge treatment to owner visual review if the council wants a round-2 successor. Do not declare the brief fully satisfied or merge from these sheets alone. The remaining decisions are whether the pale colours, black-marker weakness and transparent photo fallback are acceptable. If exact contrast preservation on every source remains mandatory, this candidate does not qualify.

## Evidence and reproduction

I viewed all 24 supplied images across `acc/`, `crops/`, `rejected/` and `survey/` before designing. `acc/plasma.png` is actually a Netpbm file: its first image-tool call failed; `plasma-decoded.png` is a pixel-preserving PNG conversion, then viewed successfully. All work stayed in this proposal directory. No lab, repository, branch or GitHub changes.

Run `python3 -I /home/patrick/work/i1237-council/proposals/sol/render.py`. The workstation's default isolated Python did not expose numpy; the script adds the existing Codex runtime's Python 3.12 site-packages explicitly. No packages were installed and no replacement toolchain was built. `hl_research.py` is the unmodified local copy of the supplied research harness.

- `sheet-dark.png`: yellow/red on table, notice, Plasma, subtitle and wallpaper.
- `sheet-light.png`: yellow/red on paragraph, heading, menu and popup.
- `sheet-colours.png`: seven colours on each of the four required real crops.
- `sheet-extra.png`: photo, photographed accent text, synthetic syntax and blue button, four colours.
- Every displayed image pixel is enlarged exactly 2x with nearest-neighbour sampling. Labels identify crop, colour, mode, raw core contrast and shift. Zero in a label means unavailable when no coverage≥.9 pixels exist; the machine-readable value is null, not a measured zero.
- `numbers.json` and `numbers.csv`: all 273 crop/colour/mode combinations, a superset of the displayed tiles. `numbers.md` explains the metrics and summarizes the required cases.

“Today” is the exact 105/255 flat-fill model rounded to nearest. “Round 2” is a reconstruction of the current C++ rule (luminance clamp .45–.7, 5:1 ink cap, coverage exponent 1.5), using the supplied Python segmentation, not a pixel-exact app export. Its fallback follows the existing multiply/screen pair. All three use identical input rectangles and background resolution. The original full-size rejected app exports remain the authoritative evidence of round 2.
