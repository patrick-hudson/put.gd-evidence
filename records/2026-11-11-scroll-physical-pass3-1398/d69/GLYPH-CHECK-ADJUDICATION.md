# Supplementary glyph checker is not the acceptance oracle

The fixed-position exact glyph checker assumes constant advances and context-independent rasterization. These native fonts do not satisfy that assumption. Its pass/fail output must not be interpreted as evidence of changed line order. Acceptance uses verify_text.py: all 1500 edge-inclusive, distinct line bands, one pitch, zero duplicates/gaps. Original diagnostic source and output are retained. No product OCR feature was implemented.
