# Vote: opus

## 1. Scores

| Column | Score | Reason |
|---|---|---|
| Today | 3 | Dark pages turn olive and maroon with grey text (dark-table yellow and red). The colour is not the swatch, and contrast drops on every dark tile. |
| Round 2 | 4 | The colour is obvious, but the glyphs are fat and smeared, with doubled grey-olive edges (zoom of the dark-table and kde-notify yellow tiles). Title and subtitle merge into one weight. |
| Sol | 6 | Clean dark glyphs on a pale band. But the pastels lose the colour: on dark-table, orange reads as cream, nearly the same as yellow. Red and white are almost the same near-white on dark-notify. Black is invisible on dark-table, at (8,8,8) on a near-black page. The photo wash is olive, like today's. |
| Astra | 5.5 | Same clean ramp as Sol, with even paler pigment. On light-paragraph, blue and white almost vanish. Black on a light page is a black bar with white text, which reads as redaction. Black on dark-table is invisible, and the 28 % photo wash dims the picture. |
| Opus | 7.5 | Clean, crisp dark glyphs on the true swatch. Every colour is distinct on every scene, black included (mid grey), and its fallback is the only one that keeps the painting's lines and the wallpaper lettering. On light pages, the red, orange and blue bands are loud and heavy. |

## 2. What to build

Build Opus: the swatch as the band, contrast mirrored per pixel on dark pages, and the offset-wash fallback. It is the only column where a reader of the exported PNG names the marker colour at a glance on a dark page; Sol and Astra both turn red, orange, blue and white into near-white tints. Its glyph edges are as clean as Sol's and Astra's, which removes round 2's real defect. The one place it falls short is light pages, where a saturated multiply looks like paint rather than a highlighter pen (light-paragraph red, orange and blue). For light pages, use Astra's way of mixing towards white, which keeps the hue, applied with the floor below. Take nothing else from Sol or Astra.

## 3. Changes to Opus

1. **Light-page band floor.** On light paper, before the multiply, mix `m'` towards white in sRGB, using Astra's `Q = ((255−w)·M + 255·w)/255` with the smallest `w`, until `Y(m'') ≥ 0.45`. Then `band = lin(b) ⊙ lin(m'')`. Yellow (Y about 0.65) is unchanged. Red, orange, blue and green become fluorescent-marker tints (pink, apricot, sky, mint), and black text keeps about 10:1 instead of 6.6:1. Dark pages keep `markerFloor = 0.30` and the true swatch.
2. **Black on light pages** follows the same floor, so the band becomes grey at Y 0.45. It must stay visibly darker than the white marker's #DADADA (Y about 0.70), and it does.
3. **White on light pages:** keep the 1.40 visibility floor as proposed.
4. **Integer tables.** Build the 4096-entry per-paper tables from a frozen 256-entry fixed-point linear table, as Sol does with `T[]` and Q = 2²⁰, with no doubles anywhere in the build. This meets the "deterministic integer sRGB" test without relying on matching floating-point behaviour across compilers.
5. **Keep `gainCap = 1.6` and `knee = 0.04/0.12`.** The white-on-blue button tile shows the gain doing useful work. Keep the fallback strength at 0.80: the photo and wallpaper tiles are the best on the sheet.
6. **Show the owner the dark table and the light paragraph for all seven colours side by side** before merging. Opus's dark band is close in hue to round 2, so his "still don't love it" has to be checked against the clean-glyph version, not assumed to be fixed.

## 4. Strengths claimed that the sheets contradict

- **Sol:** "the five chromatic bands … retain recognizably different pastel hues." In colours-dark-table (Sol column), the orange and yellow rows are both pale cream. On dark-notify, the red and white tiles are both near-white. Sol's "black: carbon-black stroke" on dark-table is a band at (8,8,8) that cannot be seen.
- **Astra:** "the selected colour family survives on light pages." In colours-light-paragraph (Astra column), blue, white and red are barely distinguishable from the page. Astra presents "charcoal marker with light lettering" as a writing material, but on a light page it is a black bar with white text, which reads as a selection or redaction, not a pen. Astra also presents applying the same rule on light and dark pages as a strength, but black at (30,30,30) on dark-table disappears.
- **Sol and Astra:** both present the paler fallback wash as honest. In overview-fallback, both make the painting and the wallpaper lettering darker and muddier than today does.
- **Opus (my own model's proposal):** "As little design as possible / Quiet." Its light-page bands are the loudest thing on any sheet. The light-paragraph red and blue tiles look like solid paint bars, which is what change 1 fixes. Opus also says it "fits the settled filter, export == preview" while building its tables in double. Change 4 fixes that.
