# The implemented rule (src/editor/HighlightFilter.{h,cpp}, worktree /home/patrick/work/put.gd-hl)

Settled and unchanged: block-local background estimate (16 px blocks, 5-bit
colour modes, confident at ≥ 50 % share, unconfident blocks borrow the nearest
confident one, distinct backgrounds merged within distance 12; since the Opus
round every block samples a full 16-row and 16-column window inside the box, a
partial last row or column sliding back over its neighbour), per-pixel
assignment to the nearest candidate background, text snapping, commands, the
cached preview tile.

Per distinct background `B` of the box, with marker `M`:

1. Pigment `P` of the marker (marker only):
   - every channel ≤ 32 (black): `P = #959595` (a mid grey: a mark, not a redaction).
   - `Y(M) < 0.45`: `P` = `M` mixed with white, the smallest integer mix `w/255`
     (`P = ((255−w)·M + 255·w + 127) // 255`) whose WCAG luminance reaches 0.45
     (red #EF4444 → a coral at Y 0.45; black text on it reads at 9.5:1 on white and 8.7:1 on dark pages).
   - `Y(M) > 0.69`: `P` = `M` scaled down in linear light (hue kept) to luminance 0.69
     (white → #D8D8D8, contrast 1.43 on white).
   - otherwise `P = M` (yellow #FACC15 stays itself, Y 0.64).
2. Paper `E` of the page: `B` mixed with white the same way until `Y(E) ≥ 0.85`
   (white and near-white pages unchanged; #E0E0E0 lifted a little; dark pages
   become near-white with a faint tint of the page).
3. Band `Q = (E ⊙ P + 127) // 255` per channel (classic multiply of the pigment
   onto the paper). So: white page → the pigment itself; grey page → a darker
   band than the page; dark page → pigment at ~0.85 brightness. Continuous in the
   page luminance; no light/dark page class.
4. Ramp `R[a] = (Q·(255−a) + 127) // 255`, a = 0..255 (band to black).
5. Per pixel `p` on background `B`: `s = ln((max(Y(p),Y(B))+0.05)/(min(Y(p),Y(B))+0.05))`
   (log contrast with its own page); knee: `s < 0.04 → 0`, `0.04..0.12` smoothstep,
   above kept exactly; output = `R[a]` for the first `a` whose contrast against
   `Q` reaches `e^s` (or `R[255]` = black when the ramp cannot reach it).
   Implemented as a 4096-entry table per background indexed by the pixel's
   linear luminance; per pixel three table lookups, one index, one store.
6. No dominant background (confident blocks < half): a tint that keeps every
   pixel's luminance. In linear light `t = p + 0.6·(M − p)`, then `t` is scaled
   so its WCAG luminance equals the pixel's own (`out = t · Y(p)/Y(t)`; a channel
   over white is pulled toward the grey of the same luminance until it fits);
   black stays black. So text on a photo or on a coloured label keeps its exact
   contrast under the wash; the wash shows as a colour cast toward the marker.
   A neutral marker (channel spread ≤ 24: black, white, grey) has no chroma to
   lend, so it moves the luminance instead: black shades the region with
   `Y' = max(0.5·Y, 0.6·(Y+0.05) − 0.05)` (contrast ratios kept above a toe that
   keeps dark detail), white lightens it with `Y' = g·(Y+0.05) − 0.05` where
   `g = min(1.6, 1.05/(Ymax+0.05))` with `Ymax` over every pixel of the box, so the
   brightest pixel never clips and ratios are kept; when the box already holds
   white, only the chroma move remains (a desaturating mark).
7. No outline, underline, padding, texture or other decoration.

Known trade-offs (accepted by the council, stated so reviewers do not rediscover them):
- Text lighter than its page becomes dark lettering (polarity flips on dark pages);
  coloured text (links, syntax colours) becomes near-neutral dark on the band.
- The ramp's maximum contrast is (Y(Q)+0.05)/0.05 (≈ 11–14:1 for the palette):
  black-on-white text (21:1) saturates at black, so the darkest anti-aliasing
  levels merge into the stem.
- A black marker on a very dark page is a visible grey band, not black.

Cost on f44 (debug build): 4K export 0.9 s, 1.5 MP tile 0.2 s. The tables are built
with doubles once per background (log/exp/pow); the per-pixel path is lookups only,
so the export and the preview tile use identical tables on the same build.
