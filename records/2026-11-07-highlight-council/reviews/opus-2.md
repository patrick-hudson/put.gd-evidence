# Opus review, round 2: Highlight look at dc52421b8

## 1. Score: 8/10

The round-1 must-fix is gone. In history-colours mark 6 (zoom/history-colours-6) the image icon is now a dark grey glyph on the white-marker band: the pixels across its stroke run (60,60,60), (47,47,47), (48,48,48) on (202,202,202). "Screen-…" is uniformly black. That 17-px box now looks like every other row.

On paper pages (cinnamon-1, cinnamon-colours-2/3/4, cinnamon-3) the mark is still a clean marker stroke. The LCD text stays crisp, and I see no fringes, fat stems or seams. On the dark History window (history-1, history-colours-1…5) the band is one flat colour across zebra rows and across the neighbouring Settings window, with dark lettering and dark icons. It reads as "someone ran a pen over this", which passes Obvious, Honest and Quiet with very little design. Red is now distinguishable from pink: (239,150,150) against (237,146,191) on paper, cinnamon-colours-1 against cinnamon-4. Side by side that is a clear rose against magenta-pink.

It is not a 9 for the reasons the council already accepted. Washes on artwork read as colour filters, faint lettering under a loud band reads as an empty bar, and the neutral markers look "disabled" on coloured UI. None of these is a defect of the build. They are limits of the rule's scope.

## 2. Problems

### Must-fix

None.

### Nice-to-have

- **N1. Red is a coral, not a red** (cinnamon-colours-1, history-colours-1, where the dark page gives (230,144,144)). It is recognisable as "the red marker" next to pink, but on its own it still says salmon. That is the price of dark text on the band. I would leave it unless the owner says otherwise.
- **N2. The record overstates the contrast.** RESOLVED says "black text on any band still ≥ 10:1". Measured on dark pages, red, orange, green and blue all land at band Y ≈ 0.388, which gives **8.7–8.8:1** for black (history-colours-1/2/4/5). On paper, red is 9.5:1. That is still far above 4.5, and the glyphs in the zooms look fine. But the ramp now saturates sooner: white-on-charcoal text (~13:1) compresses into 8.8:1, so more of the darkest anti-aliasing merges into the stem. Smallest fix: correct the sentence in RESOLVED and RULE.md ("≥ 8.7:1 on any page"). No code change.
- **N3. Faint lettering stays a blank bar** (plasma-3). "26.04 LTS" measures 1.27:1 before and ~1.3:1 after, so the rule keeps its promise. Still, a loud yellow slab with invisible text tells the reader nothing about what was marked. The faint-text floor already recorded as a follow-up is the fix. It should go to the owner as an open question, not be treated as closed.
- **N4. Artwork washes look like filters** (aurora-1 olive, aurora-2 indigo, aurora-3 where the red label turns ochre). The text contrast is kept, but on aurora-1 the marker colour cannot be identified.
- **N5. Neutral markers on coloured UI look disabled** (aurora-neutral-3/4: the label greys). Black on a dark page is a grey slab (cinnamon-colours-7, (139,139,139)).
- **N6. Polarity split at a box edge** (history-1): the box starts mid-icon, so the icon is light blue outside the box and dark inside it. Snapping decides where the edge falls, and that is out of scope. I note it only because the owner will see it.

## 3. Code

- The sliding window (`plan()`, HighlightFilter.cpp:284) is correct. `max(area.left(), …)` keeps boxes under 16 px (cinnamon-colours-5 is 6 px tall) at their own origin, and the slid last block only re-reads pixels inside the box. It is deterministic, and preview and export share the same `Plan`.
- Unchanged from round 1. Below zoom 1, `apply()` filters the resized tile while the candidates come from the source, so the preview can differ slightly from the export. Wash mode does double math per pixel, and `toSrgbFast`'s 1/4096 linear step can band a black wash over very dark art. A finer table below linear 0.01 would fix that.
- Overlapping or abutting marks (the orange, yellow and green stack in cinnamon-colours-3) show no seam and no double application in the export.

## 4. What the owner will see

On his dark put.gd window a yellow marker gives a solid golden band (233,190,20) with crisp black lettering and dark icons. It is one stroke across zebra rows and window borders, legible at 11.8:1 and plainly a highlighter, not a selection, frame or filter. That is the look round 1 and round 2 failed to give him, and I expect him to like it. The one thing that may catch him is that his white text turns black inside the mark. That is the honest cost of a bright band, and with yellow it feels natural, like a real marker on paper. With red he gets a rose-coral band (230,144,144) with black text at 8.8:1. It is clearly a different marker from pink now, but he may still say "that's not quite red". If he does, the next lever is a red-specific floor, and that is a palette decision for him to make, not a defect. The icon ghost from round 1 is gone, so nothing in an ordinary use of the tool will spoil the first impression.
