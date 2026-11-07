# Astra council vote

Reviewed all three proposals, all seven comparison sheets, and Patrick's rejected live screenshot. Scores judge both exported readability and whether the maker's chosen mark is communicated; they are not acceptance scores.

## Scores

| Column | Score | Reason |
|---|---:|---|
| Today | 3/10 | Familiar transparent marking, but dark-table and notification letters become muddy, and black barely communicates a mark. |
| Round 2 | 4/10 | Clearly identifies the marked area, but dark-notify letters have heavy, ragged edges and KDE text has conspicuous coloured edging. |
| Sol | 7.5/10 | Clean lettering and restrained bands give the strongest overall reading experience; dark orange/yellow converge, black is weak, and fallback text remains compromised. |
| Astra | 7/10 | Clean, quiet dark-page results, but light-page red/blue are excessively faint and light-page black looks like inverse selection or redaction. |
| Opus | 6.5/10 | Best immediate colour identification and a usable visible black treatment, but saturated red/orange dominate the content and the photo treatment reads as recolouring. |

## Build choice

Build **Sol as the base**, borrowing Astra's dark-page pigment construction and weaker photographic wash, and Opus's visible grey treatment for black on dark pages. Sol's light-page bands balance recognisable marking with readable text better than Astra's pale washes or Opus's saturated blocks. Its continuous source-contrast transfer produces substantially cleaner letters than round 2 without ornament. This is a direction for owner review, not a claim that the combined result has been rendered or that every design test passes.

Against Rams' ten principles: the useful innovation is the cleaner transfer; usefulness, understandability and honesty require both readable words and recognisable marker colour. Aesthetics, unobtrusiveness and minimal design favour the restrained bands. Thoroughness requires treating black and fallbacks as real failures. Longevity favours a simple untextured mark. Environmental responsibility cannot be established from sheets; the proposed bounded integer implementation is appropriate, but runtime remains unmeasured.

## Concrete refinements

1. Keep Sol's light-page chromatic paper rule, `A=(M+256)//2`, and its continuous contrast-to-ramp lookup without treating coverage as optical opacity. Keep decoration and added padding at zero.
2. For dark chromatic bands, replace Sol's initial channel-addition lift and 0.84 floor with Astra's white-mixing search: integer `w=89..255`, `Q=((255-w)*M+255*w+127)//255`, first luminance at least 0.78. Retain Sol's source-background contrast-headroom condition, continuing along that same mixing path if necessary. This targets the weak orange/yellow distinction and cyan-shifted blue visible in Sol's dark palette sheets. The hybrid needs fresh visual review.
3. For black on dark pages, use Opus's `#959595` band with dark contrast-matched ink instead of near-black paper with light ink. Its black rows in both notification sheets visibly communicate the mark. Keep Sol's light-page black `(211,211,211)` and white `(232,232,232)` rules initially.
4. For confidence below 0.5, use Astra's uniform `(184*P+71*M+127)//255` wash instead of Sol's 40.8% wash. The painting retains more detail. This does **not** fix faint wallpaper lettering or guarantee label contrast; those remain blocking exceptions to universal readability claims.

## Strengths overstated elsewhere

- **Astra:** “every colour” being defined does not make every mark useful. In `colours-dark-table.png`, black nearly disappears; in `colours-light-paragraph.png`, blue and red are weak, while black creates a conspicuous reversed strip.
- **Opus:** “every local difference … is kept” excludes clipping, explicitly present in its rule. In `overview-fallback.png`, yellow turns the painting into a bright yellow/green patch, and wallpaper lettering remains low-contrast. Stronger colour is not automatically better communication.
- **Sol:** quiet pale paper also loses colour information. In `colours-kde-notify.png`, orange approaches yellow and blue approaches cyan. The clean glyphs are a strength; those palette shifts are a cost.
