# Council brief: the Highlight mark's look (put.gd-desktop #1237, PR #1238)

put.gd is a Linux screenshot tool (C++20, Qt 6 Widgets). Its image editor has a
Highlight tool: the user drags a box over part of a capture, usually text, with a
marker colour from the palette (red, orange, yellow, green, blue, white, black) or a
custom colour. Today the box is the marker colour at 41 % opacity over everything,
so text under it goes muddy. Issue #1237 asks for a highlighter that keeps the
text readable, like "newer tools that detect the contrast with the letter".

Everything else in PR #1238 is settled and NOT in question: the filter
architecture (block-local background estimate, per-pixel ink coverage, a pixel
filter instead of a vector paint, cached preview tiles), text snapping (drag
snaps to lines, click = word, double-click = line, Alt = free box), the agent
commands, the tests. Only the LOOK of the highlighted region is open: given a
pixel known to be background or ink (with a coverage value), and a marker colour,
what colour does it become? Possibly plus decorations (outline, underline) drawn
with the same marker. Light pages and dark pages may have different rules; the
rule may only depend on the background luminance and the marker colour.

## What Patrick (the owner) has rejected, and why

1. Round 1, "D′": light pages multiply, dark pages tinted the background to the
   marker hue at luminance 0.183 so white text keeps 4.5:1, ink untouched.
   Tried live on a dark put.gd window: "This is a mess, text is hard to read.
   You need to go back to the drawing board." See rejected/round1-patrick-live-screen.png
   (his screen), rejected/round1-sheet.png (the research sheet; the D′ column).
2. Round 2 (current PR head d64203743): dark pages become the marker colour
   itself (hue kept, luminance clamped to 0.45–0.7) and the light ink is darkened
   to 5:1 against it. "I still don't love it." rejected/round2-before-after.png,
   rejected/round2-zoom.png.
3. Candidate B: faint ink-preserving tint plus a 2 px marker-coloured outline on
   dark pages; sheets with 8 variations × 7 colours (survey/b-variations-*.png).
   He first liked B, then after seeing all variations: "I really don't like any
   of these solutions, they don't look great." So the whole B family (tint +
   outline, outline only, underline) is out as shown.

Survey of other tools (survey/real-tools-dark.png, survey/candidates-sheet.png,
survey/web-sheet1.png): Flameshot, ksnip/Spectacle, Snip & Sketch, Acrobat and
PixPin multiply (band invisible on dark pages, light text takes the marker
colour). CleanShot X and Snagit use a translucent fill. Nobody has a good answer
for dark pages, so there is no convention to copy.

## The design tests this must pass

- Readable: text under the highlight is at least as legible as before, on light
  pages, dark pages, and coloured panels (blue buttons, notification cards).
- Obvious: a reader of the exported PNG sees instantly what was highlighted and
  which marker colour was used, on a dark page as much as a light one.
- Honest: it reads as a highlighter, something a person would do with a pen,
  not as a UI frame, a selection rectangle or a filter effect.
- Every colour: the full palette (red, orange, yellow, green, blue, white, black)
  and any custom colour must work; white and black markers may need their own
  rule but must still produce a sensible result.
- Quiet: no halos, no fat glyphs, no thickened anti-aliasing, no visible block
  seams, no colour fringes on LCD subpixel-rendered text (bluish/reddish stems).
- Fits put.gd's visual language (docs/design/visual-language.md: warm charcoal
  surfaces, restrained, "as little design as possible"): Dieter Rams' ten
  principles and the Pragmatic Design Manifesto are the yardsticks.
- Deterministic integer sRGB arithmetic on source pixels, so export == preview;
  cheap (a 4K box in well under a second in release).

## Material

- crops/: ten real capture crops (LCD subpixel text on a light Mint dialog, GNOME
  menu and notification, put.gd History dark zebra table, dark settings
  subtitle, Plasma navy notification, wallpaper lettering, a notice over a
  painting, the painting alone).
- acc/: four full-size real captures used for headless acceptance (cinnamon
  light desktop, history dark window, plasma dark, aurora notice).
- tools/hl_research.py: the numpy/Pillow research harness. `python3 -I
  hl_research.py CROPS OUT` renders every mode in MODES on every crop into
  OUT/modes-*.png. `segment()` gives per-pixel coverage and background; add a new
  `mode_*` function and register it in MODES to render a candidate. Keep output
  in your own output directory.
- The C++ filter under review: src/editor/HighlightFilter.{h,cpp} in the
  worktree /home/patrick/work/put.gd-hl (branch feat/1237-highlight-contrast).
  The dark-page rule lives in `apply()`'s recolor branch and `paperMarker()`;
  the light-page rule is the multiply shift branch.
- Patrick's own words, in order: "This is a mess, text is hard to read";
  "I still don't love it"; "I like B but I need to see more options of colors
  and variations"; "I really don't like any of these solutions, they don't look
  great. Come up with a user friendly design."
