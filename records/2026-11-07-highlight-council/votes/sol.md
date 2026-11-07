# Vote: sol

I read the brief and all three proposals, and viewed all seven comparison sheets plus Patrick's rejected live screen. Scores concern the rendered designs, not their authors or implementation claims.

## 1. Scores

| Column | /10 | Reason |
| --- | --- | --- |
| Today | 3 | Familiar transparent marking, but dark-table and notification lettering becomes muddy; wallpaper lettering nearly disappears. |
| Round 2 | 4 | Colour and marked extent are obvious, but notification glyphs look heavy and ragged, and saturated light-page fills compete with the words. |
| Sol | 7 | Clean, readable lettering and useful light-page pigment; dark red approaches white, orange approaches yellow, black is weak on dark pages, and the fallback repeats today's detail loss. |
| Astra | 8 | Best balance of clean lettering, restrained colour and photographic detail; light-page red is too faint, and black becomes either inconspicuous on dark pages or an intrusive reversed strip on light pages. |
| Opus | 6 | Strongest colour identification and a useful visible graphite marker, but saturated red/blue dominate the screenshot and the photo fallback visibly changes the picture's character. |

## 2. Build choice

Build **Astra's contrast-matched neutral-ink design**, with Sol's ordinary light-page pigment and Opus's graphite treatment for black. Astra's dark notification and KDE tiles read cleanly without making every annotation an alarm-coloured panel. Its weaker photo wash preserves more of the drawing than Sol's. From the maker's perspective, stronger light-page pigment and visible graphite would make the result easier to predict. This is a preferred next design, not acceptance: every column still leaves the fallback wallpaper lettering difficult to read.

Against Rams: the continuous contrast transfer is useful innovation; the restrained bands are more aesthetic, understandable and unobtrusive; the familiar geometry should endure. Honest colour identification needs the changes below. Thoroughness means retaining the difficult fallback cases as failures. Integer tables support economical implementation, but environmental efficiency and runtime performance are unmeasured. Zero decoration satisfies “as little design as possible.”

## 3. Concrete changes

- Retain Astra's chromatic dark-page paper floor **L >= 0.78**, neutral ink, 256-entry contrast ramp and source-pixel contrast matching. Keep **zero** outline, underline, feathering and extra padding.
- For ordinary chromatic markers on **light paper, L(B) >= 0.30**, replace the 0.78 paper floor with Sol's half-white pigment: **Q[j] = (M[j] + 256) // 2**. Use Astra's same black-ink contrast ramp. In `overview-light.png`, Sol's red menu and popup marks are easier to identify than Astra's almost-white pink; its paragraph remains restrained.
- For Astra's near-black class (**all channels <= 32**), use Opus's **Q = (149,149,149)** and **F = (0,0,0)** on both page types. Keep Astra's contrast matching. The Opus black rows visibly identify the marked area in both dark notification sheets; Astra's black light-paragraph strip looks closer to redaction.
- Keep Astra's near-white threshold (**all channels >= 240**) and **Q = (232,232,232)**, and its uniform **71/255** photo wash. Do not strengthen the wash to disguise failed text recognition. These sheets do not establish a fallback rule that passes the readability requirement.

## 4. Strengths overstated elsewhere

- **Sol:** “quiet, pale paper” goes too far for colour honesty. In `colours-dark-table.png`, red is close to white and orange close to yellow; `colours-kde-notify.png` also makes blue cyan-like. Extra contrast headroom does not compensate for weakening the maker's colour choice.
- **Opus:** “every line and texture … still visible” overstates the additive fallback. In `overview-fallback.png`, yellow changes the painting's dark linework into greenish lines against a much brighter wash. Clipping means a constant offset cannot preserve every local difference. Likewise, keeping saturated red because “the user picked it” does not resolve the visually aggressive red paragraph in `overview-light.png`.
