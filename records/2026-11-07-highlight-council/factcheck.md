# Fact-check of the #1237 council (proposals, votes, CONVERGED draft)

Method: proposals, votes, CONVERGED.md, the sheets in compare/ and proposals/*/sheet-*.png,
numbers.csv/json, HighlightFilter.{h,cpp} at d64203743, and python3 -I recomputation
(scripts in the session scratchpad; nothing in the council tree was changed).

## 1. Claims checked

| # | Claim | Source | Verdict | Evidence |
|---|---|---|---|---|
| 1 | Sol's integer table (Q=2^20, K=52429, 314573, 880804) reproduces WCAG luminance; thresholds 0.30 / 0.84 | Sol §Integer luminance | confirmed | max abs error 9.2e-7 over 200k random colours; K=round(52428.8); 314573/2^20=0.3000; 880804/2^20=0.8400 |
| 2 | Astra's 16-bit luminance (13933/46871/4732, 51117≈0.78, 3277≈0.05) | Astra step 1–2, 6 | confirmed | weights sum to 65536; max abs error 1.9e-5; 51117/65535=0.77999; 3277/65535=0.05000 |
| 3 | Sol's headroom condition (a+K)(b+K) ≥ K(Q+K) reserves enough range to reverse a white source | Sol §Paper colour A | confirmed | equivalent to (a+.05)(b+.05) ≥ 0.0525 ⇔ (a+.05)/.05 ≥ 1.05/(b+.05) |
| 4 | Astra's white-mix search (w=89..255) is monotone and always terminates | Astra step 3; CONVERGED | confirmed | each channel is non-decreasing in w; w=255 gives white. Found w: red 210, orange 196, yellow 123, green 186, blue 203 → Q #FCDEDE #FEDFC9 #FCE586 #C3EFD3 #D7E6FD, all Y 0.780–0.785 |
| 5 | Ramp lookup is a monotone search; pixel equal to page returns Q | Sol, Astra, CONVERGED | confirmed | ramp luminance strictly decreasing in a; c=1 → a=0 |
| 6 | Round 2 C++: coverage = sRGB distance clipped at 70 | all three | confirmed | HighlightFilter.cpp `cover=d2>=inkSquared?inkDistance:lround(sqrt(d2))`, inkDistance=70 |
| 7 | Round 2 C++: paper luminance clamped 0.45–0.7, ink darkened to 5:1, laid with cover^1.5 | all three | confirmed in intent, wrong in effect | `paperMarker` clamps the *target*, but `atLuminance` clips channels without compensation, so red lands at #FF5F5F Y=0.303, orange #FF861B Y=0.384, blue #52AFFF Y=0.397 (not 0.45). inkContrast=5 and layTable (pow 1.5) as stated |
| 8 | Round 2 C++ light page: multiply shift, ink untouched | Opus, CONTEXT | confirmed | `if(d2>=inkSquared)continue;` full-ink pixels untouched; partial pixels shifted by (70-d)/70 |
| 9 | Opus's round-2 port is "faithful" | Opus opus_hl.py docstring | wrong | port's `at_luminance` mixes toward white after clipping, so the sheets' round-2 red band is #FE9595 (sampled) where the app produces #FF5F5F; blue #71B7FE vs app #52AFFF. Sol's and Astra's reproductions use the harness `hue_at_luminance` and show the same salmon. Yellow, green, white, black match |
| 10 | "Round 2 turns red into salmon, blue into sky"; Opus's 0.30 floor "keeps red red (#FF5E5E)" as a difference from round 2 | Opus §Why rejected, (c) | wrong for red | the app's round-2 red band is already #FF5F5F (Y 0.303) = Opus's #FF5E5E; the difference exists only in the Python reconstructions. Round-2 blue #52AFFF vs Opus #4C94FF, both sky. Black → #B3B3B3 confirmed |
| 11 | Round 2: "every edge pixel with more than about 23 % coverage is laid as full dark ink" | Opus | confirmed (approx.) | 70/390=18 % for white on #1E1E1E, 70/336=21 % for #E0E0E0 text |
| 12 | Round 2 stroke weight "×1.5–1.8" | Opus proposal + numbers.md | overstated | own numbers.json: dark pages 1.21–1.79 (button 1.21/1.22, settings 1.3/1.4) |
| 13 | Opus stroke weight "×0.92–1.17" | Opus | confirmed | numbers.json min 0.92 (dark-notify green), max 1.17 (kde-notify red) |
| 14 | "Round 2 sits at 4.9 everywhere on dark pages and 3.2 on light pages" | Opus | half wrong | dark 4.93–4.98 confirmed; light pages run 3.22–6.33 (yellow 4.43, white 4.82, popup 6.33, menu 5.78) |
| 15 | White-on-blue button 4.6→6.1; subtitle 5.2→5.5; light paragraph 6.6–6.8; dark table 7.0–7.7; Plasma 7.0–10.2 | Opus | confirmed | numbers.json: 4.61→6.11, 5.16→5.54, 6.63–6.79, 7.0–7.7, 7.0–10.19 |
| 16 | Red #EF4444→#FF5E5E, blue→#4C94FF, black→#959595 at floor 0.30 | Opus | confirmed | recomputed with opus at_luminance |
| 17 | Y(#FACC15)≈0.65, Y(#DADADA)≈0.70, floor 0.45 gives black text ≈10:1 instead of 6.6 | Opus vote | confirmed | 0.636, 0.701, (0.45+.05)/.05=10, 6.63 from numbers.md |
| 18 | Opus fallback "the only one that keeps the painting's lines and the wallpaper lettering" | Opus vote, Opus proposal | wrong | wallpaper lettering p90:p10 luminance contrast: source 1.32, today 1.23, round 2 1.18, Sol 1.23, Astra 1.30, Opus 1.30. Painting: Astra 1.62, Opus 1.63, Sol 1.47, today 1.47. Opus is brighter, not more detailed; 1.5 % of its photo channels clip |
| 19 | Sol and Astra fallbacks "darker and muddier than today" | Opus vote §4 | half wrong | Astra is darker (mean Y 0.064 vs 0.118) but keeps more relative contrast than today; Sol is numerically identical to today (40.8 % vs 41.2 %) |
| 20 | "every local difference is kept" by the offset fallback | Opus proposal | wrong as stated | clipping (0.011–0.015 of channels on the photo) and the hue swing the author lists himself; both votes already note this |
| 21 | Sol dark-table red 10.47→10.35, core shift 184.16; dark-notify black 1.18→1.20; light-paragraph red 4.04→4.07 | Sol numbers.md | confirmed | numbers.csv rows match |
| 22 | Astra: "no pixel loses more than 0.02 contrast" on table, Plasma, paragraph yellow/red; notice has small exceptions | Astra §Readable | confirmed | contrast_regression_fraction 0.0 for those six rows; dark-notify 0.0007 / 0.0033 |
| 23 | Astra core_wcag_min ≈1:1 so not a headline | Astra | confirmed | dark-table red 1.204→1.209 |
| 24 | Sol: "orange approaches yellow, red near white, blue cyan-like" on dark pages | Astra vote, Sol vote, Opus vote | confirmed | Sol paper on every dark crop background: red #FFE7E7, orange #FFEBBD, yellow #FFEE92, blue #CFF3FF (headroom + 0.84 floor drive all to Y ≥ 0.84); visible in colours-dark-table.png and colours-kde-notify.png |
| 25 | Sol black on dark pages is (8,8,8), invisible | Opus vote | confirmed | paper = min(B,8) → #080808 on #1B1E25; sheet shows a barely darker strip |
| 26 | Astra black on dark pages (30,30,30) invisible; on light pages a black bar with white text | Opus vote, Sol vote, Astra vote | confirmed | colours-dark-table.png and colours-light-paragraph.png, Astra column, black row |
| 27 | Astra light-page red/blue/white "barely distinguishable from the page" | Opus vote, Sol vote | confirmed | Astra light Q is the same 0.78-luminance pigment; colours-light-paragraph.png Astra column |
| 28 | Opus light-page red/orange/blue "loud", "solid paint bars" | all votes | confirmed | overview-light.png Opus column |
| 29 | Opus yellow fallback turns the painting's linework greenish | Sol vote | confirmed | dark line (20,10,5)+0.8·(yellow−mean) ≈ (178,160,21); overview-fallback.png |
| 30 | "Today" = 41 % fill = 105/255; Sol wash 40.8 % = 104/255; Astra 27.8 % = 71/255 | CONTEXT, Sol, Astra | confirmed | arithmetic |
| 31 | Opus vote states Opus's tables are built in double, contradicting "export == preview" | Opus vote §4 | confirmed | opus_hl.py and §Implementation sketch say "built in double" |
| 32 | "Opus vote pending" | CONVERGED.md header | wrong | compare/votes/opus.md was written 00:12:56, CONVERGED.md at 00:14:09 |
| 33 | Converged 12-bit linear-luminance index loses dark tones | (question 4) | not a problem | 256 greys map to 256 distinct indices (first: 0,1,2,4,5,…); contrast error vs a black page ≤ 0.0012 at grey 1, ≤ 0.0005 elsewhere |
| 34 | "a 4K box stays well under the measured 173 ms export" | Opus | unverifiable | no C++ timing of any proposal exists |
| 35 | Each vote's scores | votes | noted | Sol: 3/4/7/8/6; Astra: 3/4/7.5/7/6.5; Opus: 3/4/6/5.5/7.5. Sol ranks Astra first, Astra ranks Sol first, Opus ranks itself first |

## 2. Real problems in the converged rule (values from the rule as written)

1. **The light-page band has no dependence on the page, so on light grey pages it is faint or invisible.** Q is `(M+256)//2` regardless of B. Yellow Q=#FDE68A (Y 0.793) on page #E0E0E0 (Y 0.745): band/page contrast 1.06, band *lighter* than the page. White Q=#E8E8E8 on #E0E0E0: 1.08; on #F0F0F0: 1.07 (band darker). Red Q=#F7A2A2 (Y 0.48) on a #BCBCBC panel (Y 0.50): 1.03, visible only by hue. Opus's multiply band is always darker than its page; the converged rule drops that property for every light page that is not white.
2. **The white marker on a light page is weak even on white.** Q=#E8E8E8 vs white: 1.23. Opus's 1.40 floor (#DADADA) was argued for in the Opus vote and not adopted; no vote asked for 232 on white specifically beyond "keep Astra's".
3. **Discontinuity at the 0.30 page boundary.** Red on page #909090 (Y 0.279, dark): Q=#FCDEDE (Y 0.78), white text → #8A7A7A, black text → #554B4B. Red on page #959595 (Y 0.301, light): Q=#F7A2A2 (Y 0.48), white text → #865858, black text → #3C2727. Two mid-grey panels 5 sRGB apart in one box get two different red bands and two ink shades.
4. **Two backgrounds, one box, different page classes, different bands.** Red: dark panel #FCDEDE, light panel #F7A2A2 (seam of 0.30 in luminance). Yellow: #FCE586 vs #FDE68A (negligible). Red, orange, blue, green show the seam.
5. **Dark custom markers on light pages give dark bands with capped contrast.** #202060 → Q=#9090B0 (Y 0.29): black text on white drops 21:1 → 6.8:1, and every grey AA level 0..91 becomes pure black (thicker glyphs). #280000 → Q=#948080 (Y 0.23), max ink contrast 5.7:1. Black marker (Q=#959595, Y 0.30): greys 0..89 → black, 21→7.0:1. Dark pages are safe (the search lifts everything to Y 0.78).
6. **Near-white custom markers that miss the 240 threshold vanish on white.** #EFEFEF is chromatic by the rule: light Q=#F7F7F7, contrast with white 1.07. (#F0F0F0 and (240,240,255) hit the white class and get #E8E8E8.)
7. **Saturation on white pages for every chromatic colour.** Black text is 21:1; the ramp's maximum is (Y(Q)+0.05)/0.05: red 10.6, orange 12.5, blue 11.5, green 13.7, yellow 16.9, white 17.1. Source greys that become pure black: red 0..62, blue 0..57, orange 0..52, green 0..45, yellow 0..29, white 0..28 (of 256). Sol's proposal already states this loss; CONVERGED's "contrast preserved" does not carry the caveat.
8. **Black page (#000000).** Yellow/red: white text 21:1 vs ramp max 16.6, so greys 229..255 collapse to black (mild). Black marker: greys 149..255 → black (107 levels; AA pixel 200 → #000000, fat glyphs). White marker Q=250: greys 250..255 → black. Sol's headroom condition would have lifted the paper to Y≈1.0 on a black page; Astra's vote asked to keep that condition "continuing along the mixing path"; CONVERGED omits it.
9. **Polarity.** Pixels darker than a dark page become lighter than Q, not darker: black separator on #2B2B2B → #D1BD6F (1.49:1 against Q); #101010 → #DAC674. Harmless but it is the opposite of what "neutral dark ink" suggests. On a page at Y 0.25 (#8A8A8A), white text → #847575 (3.5:1) and black text → #5B5050 (6.2:1): both dark, hierarchy inverted (the formerly black text is now the darker one).
10. **Coloured text on dark pages becomes greys of nearly one shade.** On #1E1E1E with yellow: link #3B82F6 → #71663C (4.5:1), comment #6A9955 → #695F38 (5.1:1), keyword #569CD6 → #615833 (5.7:1), string #CE9178 → #59512F (6.3:1), white → #000000. Hue is gone and four syntax colours land within 25 sRGB of each other. Sol and Opus state this; CONVERGED does not.
11. **Zebra rows give two ink shades for the same text.** White text on #1E1E1E → #000000, on #262626 → #110F09, on #2B2B2B → #1A170E; grey-160 text → #58502F / #5F5632 / #635A35. Same Q, different a. Small but visible at 2×, and it is exactly the "block-coloured patch" class of artefact round 1 was rejected for, in a milder form.
12. **No knee.** A 5-level page gradient (#1E1E1E→#232323) maps to Q→#F4DE82, i.e. a 3–4 sRGB step on the pale band; sensor noise of ±1 reproduces 1:1. Opus's knee (0.04) absorbed this; the converged rule has none.
13. **Anti-aliased edges.** Away from saturation the mapping preserves each edge pixel's contrast (AA pixel 200 on black → #262214 at 12.6:1, source 12.6). Edge geometry is fine except in the saturated cases above (items 5, 7, 8).

## 3. What the converged draft does and does not take from the votes

- Sol vote: Astra base + Sol light pigment + Opus grey black on both pages + Astra 71/255 wash. CONVERGED matches this exactly.
- Astra vote: Sol base + Astra dark search **with Sol's headroom condition retained** + Opus black on dark pages only + Sol's light-page black (211) and white (232). CONVERGED drops the headroom condition and uses 149 for black on light pages.
- Opus vote (exists, not "pending"): Opus base; light pages white-mix to Y ≥ 0.45 then multiply; gain and knee kept; 0.8 offset fallback; integer tables from a frozen 256-entry table. CONVERGED takes only the 4096-entry table idea; its light band `(M+256)//2` for red is Y 0.48 (close to the 0.45 floor) but blue 0.52, green 0.64, yellow 0.79, so the Opus floor is roughly met by accident for red and exceeded for the rest; the multiply (page dependence) is not taken, which causes item 1 above.
- "Ink F=(0,0,0) in every class" and "same rule on light and dark" are consistent with the Sol/Astra ramp; nothing in the votes asked for the 12-bit table, which is Opus's. Internally the draft is consistent; its only self-contradiction is "contrast preserved" vs the saturation cases.

## 4. Other things the coordinator should know

- **The round-2 column in every compare sheet is not the app's output for red, orange and blue.** All three reproductions lift the paper to Y 0.45 with white-mixing; the C++ `atLuminance` clips and lands red at #FF5F5F (Y 0.30), orange #FF861B (0.38), blue #52AFFF (0.40), with ink targets of 0.021/0.037/0.039 instead of 0.05. The real export (rejected/round2-before-after.png) shows the deeper red/blue. Opus's "true swatch" red band is byte-for-byte the current app's red band; Patrick's "I still don't love it" was given on a yellow table, so this is not yet a rejection of Opus's red, but Opus's claim (c) is false for red and the Opus vote's own item 6 ("close in hue to round 2") understates it.
- Opus's weight and p10-contrast metrics are its own, not the harness's; Sol's and Astra's "core min" numbers (≈1.2:1) are a different metric again. The three proposals' numbers are not comparable to each other; only the sheets are.
- Sol's dark paper is identical on every dark crop (the 0.84 floor dominates the headroom condition for pages at Y ≤ 0.02), so "custom colours use exactly the same rule" is true but the rule washes every hue to Y ≥ 0.84.
- The "every colour" test and the custom-colour cases (items 5–6) are not covered by any sheet; no proposal rendered a custom marker.
- None of the proposals or votes measured C++ timing or rendered through the app; all three say so.
