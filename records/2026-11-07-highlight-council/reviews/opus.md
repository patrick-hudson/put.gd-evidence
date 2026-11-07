# Opus review: Highlight look at 952220746

## 1. Score: 7/10 (8 once M1 is fixed)

On paper pages the mark is right: Cinnamon yellow, orange, green and blue (cinnamon-1, cinnamon-colours-2/3/4) look like a real marker, and the LCD text stays crisp, with no fringes or fat stems. On the dark History window the paper band with dark lettering (history-1, history-colours-2/3/4) reads as a highlighter, not a selection or a frame. It shows the marker (yellow #E9BE14, green #66CB8B) and is more legible than before. The band stays one colour across zebra rows and the neighbouring window, so it looks like one stroke. That passes Readable, Obvious and Quiet in the common case, with "as little design as possible".

Three things cost points: one mark in the set is visibly broken (M1), washes on artwork read as filters, and neutral markers on coloured UI look "disabled".

## 2. Problems

### Must-fix

**M1. A one-pixel edge block turns an icon into background.** history-colours.png mark 6 (white, 118,432 97×17), zoom/history-colours-6.
- What I see: the blue image icon becomes a ghost, (197,202,211) on the band (202,202,202), about 1.05:1. The "S" of "Screen-…" is grey and the rest of the word is black.
- Cause (checked against the source pixels): the box is 17 px tall, so its second block row is 1 px. At y=448, x 134–149, ten of the sixteen pixels are the icon's bottom stroke (135,164,222). That passes `share>=0.5` and the stroke becomes a confident background. `Grid`'s 3×3 candidate list then offers it to the rows above. The icon pixels and the blue LCD fringe of the "S" are nearest to it, so they map to its paper band.
- Why it matters: snapped boxes have arbitrary heights, and rows with icons, separators and focus rings are what people mark. This fails Readable outright.
- Fix: in `plan()`, sample each block over its full 16×16 cell clipped to the image, not to `area`. The confident-block count stays the same and preview still equals export. Add a unit test: a 17-px box whose last row is a coloured stroke.

### Nice-to-have

- **N1. Red reads as pink.** Red gives (241,173,174) and the pink #EC4899 gives (240,170,204) (cinnamon-colours-1 vs cinnamon-4); on a dark page red is (231,166,167). A reader can't tell which marker was used. A lower pigment floor for red (e.g. 0.45) would bring back a red.
- **N2. Washes read as filters.** aurora-1 is olive, the red label in aurora-3 turns ochre-brown, and the yellow marker can't be recognised on the painting. This fails Obvious and Honest there. It is the owner's call.
- **N3. Neutral washes look "disabled".** Black dims the white lettering on the label to grey (aurora-neutral-3), and white only desaturates the label (aurora-neutral-4).
- **N4. Black on a dark page** is a lighter grey slab: (138,138,138) on (29,30,32) in cinnamon-colours-7, and the wallpaper line inside it vanishes. It reads like a redaction bar.
- **N5. Faint lettering under a loud band:** "26.04 LTS" in plasma-3 sits at about 1.2:1 on yellow and the mark looks like a blank bar. This is the follow-up the council already recorded.
- **N6. Pale blue with dark text** (history-2, cinnamon-3) is the toolkit text-selection look, so it is the colour most likely to be misread as "selected".

## 3. Code

- Paper mode is lookups from one `Plan`, so preview and export match at zoom 1. Below zoom 1, `apply()` reads pixels from the resized tile, while candidates come from the source. That mismatch is already recorded.
- Wash mode does double math per pixel. It is deterministic within a build but is not the brief's integer sRGB. `toSrgbFast` quantises linear light to 1/4096, about one 8-bit step near black, so a black wash over dark art can band. A finer table below linear 0.01 would fix that.
- The `brightest` scan is three lookups per pixel and runs only for light neutral markers, so it is fine. `Sampler::mode` is integer and `nearest` ties go to the first candidate, so results are order-stable.

## 4. What the owner will see

On his dark put.gd window with yellow, he gets a solid marker-yellow band with crisp near-black lettering and dark icons. It reads at once as "someone highlighted this", and it is far cleaner than D′ or the round-2 recolour. I expect him to like it, unless the dark-lettering flip bothers him on his own theme. With red he sees a salmon-pink band with the same dark text. It is readable and calm, but he will likely say "that's pink". If a snapped box ends one pixel into an icon row, he hits M1's ghost icon, and that would undo the good impression. Fix M1 first, and show him red with a slightly deeper floor.
