# Astra review — 8/10; gate passed

Reviewed commit `952220746269062ca041d086a80c102e52f304b3`. I read RESOLVED.md first, then the brief and implemented rule, independently viewed all seven full exports and every one of the 32 zoom files, and inspected the filter, preview/export callers and highlight tests. No builds or lab work performed.

## Look and reasoning

Acceptable, with no blocking findings in these exports. Yellow on History (`history-1`) and the Plasma notification (`plasma-1`) is immediately understandable: strong marker colour, readable dark lettering, no decorative frame. Cinnamon's small LCD text remains readable across the coloured bands; the original coloured fringes become quieter. The dark table's row boundary survives without looking like a segmentation seam. I see no conspicuous halos or newly fat glyphs. The neutral washes retain painting detail and readable label text.

Against Rams: useful and understandable are strong; aesthetic and unobtrusive are good for text-sized bands, weaker for broad artwork boxes. The restrained, undecorated treatment supports “as little design as possible” and longevity. Detail handling is thoughtful. Honesty is imperfect where red becomes pink or a wash resembles image recolouring. Innovation serves a real dark-page problem. Resource economy is plausible from the implementation, but environmental friendliness cannot meaningfully be established from PNGs. This is a good text highlighter, not yet an equally convincing pen across every kind of picture.

## Must-fix

None for this look gate. This does not certify universal preview equivalence or every possible custom colour/background combination.

## Nice-to-have

- **Red loses its identity:** `cinnamon-colours-1` and `history-colours-1` show salmon/pink, not the palette's strong red. The band remains attractive and readable, but the person choosing red may feel ignored. Smallest experiment: a lower pigment luminance floor for saturated red in `pigmentOf()`, leaving the transfer rule intact. This reopens an accepted palette choice and trades contrast headroom for saturation; it needs owner comparison, not an automatic change.
- **Faint content receives louder emphasis than its lettering can support:** `plasma-3`, the “26.04 LTS” band, is striking yellow around barely readable ochre letters. The source was already faint, but attention is drawn to a phrase that remains effortful to read. Smallest experiment: a modest minimum contrast for non-background ink in `transferTable()`, retaining the noise knee. This could also promote wallpaper texture; keep it a separate decision rather than blindly lifting every low-contrast pixel.
- **Artwork washes look like colour correction:** `aurora-1/2` are olive and blue-violet patches; `aurora-neutral-2` looks selectively desaturated. Texture survives, but these do not have the straightforward pen quality of the text bands. Reducing `washChroma` is the smallest experiment to soften the filter appearance, particularly blue/white; it also weakens visibility. There is no demonstrated one-constant fix that makes yellow bright while preserving every pixel's luminance. Keep the present compromise unless the owner prefers that trade.

## Code observations

`EditDocument::highlightPreview()` resizes before applying the nonlinear filter; export filters full-resolution pixels. Reduced previews can therefore differ in glyph weight and background assignment. The 1.5 MP cap can cause this even at nominal 100% for large marks. Overlapping preview tiles independently read the base, whereas export applies highlights sequentially. These are existing architectural limitations, not new blockers for the supplied isolated marks; the full-scale unit test does not cover them.

The implementation is repeatable on the same build, but is not integer-only: tables use `pow/log/exp`, and pixel processing uses doubles. Cross-platform byte identity is not established. Avoidable setup cost includes `sqrt/lround` for background-distance comparisons; squared-distance thresholds can preserve the current rounding boundary. Background deduplication also scans prior backgrounds linearly. The timing test permits 10 seconds for export, so it does not prove the brief's subsecond release target. I did not benchmark.

## What Patrick will see

On his dark put.gd window, yellow produces a bright, fairly opaque strip with dark, clearly readable lettering. I expect him to prefer its clarity and lack of ornament, although a large box still resembles applied coloured paper. Red produces a softer salmon strip with equally readable text. He may like the usability while still objecting that his red marker looks pink; the exports justify confidence in readability, not a prediction that his aesthetic reservations are finished.
