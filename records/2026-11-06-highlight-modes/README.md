# Highlight compositing modes: prototype comparison

Research for the editor Highlight tool after user feedback that it "just puts a
translucent tinted box over everything" instead of keeping text contrast.

`highlight-modes.png` applies the same default highlight color (#FACC15) to four
samples (light UI text, dark UI text, white text on an accent button, dark-theme
syntax colors) with five compositing modes:

1. Today: `fillRect` with alpha 105/255 (`EditDocument::paintAnnotation`).
2. Multiply (kImageAnnotator/ksnip, Acrobat, PixPin default).
3. Darken, per-channel min (Greenshot's text highlighter).
4. Ink-preserving background tint: find the dominant background color, tint only
   background pixels, keep ink pixels; the tint strength is capped so every ink
   color keeps min(original contrast, 4.5:1).
5. Full marker on dark backgrounds, with light ink darkened (same hue) to 4.5:1.

`highlight_proto.py` is the Pillow script that produced the sheet
(`python3 highlight_proto.py out.png`). It is a sketch: sRGB math, 4-bit color
bins, and a naive coverage unmix that thickens glyph edges in mode 5.
