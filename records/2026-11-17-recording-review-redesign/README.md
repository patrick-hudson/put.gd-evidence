# Recording review redesign: council design, mock pictures and filmstrip measurement

This record holds the agreed design for put.gd's recording review window (the "video
editor"), the pictures of it, and the measurement that settled how its filmstrip is
filled. Nothing here is built yet; it is the reference for the build.

## Contents

- `design.md`: the agreed spec (rev 4). Its links to `../mock/` and `../test/` refer to
  the working directory it was written in; here those files are `mock/` and
  `filmstrip-test/`.
- `before-review.png`, `before-many-masks.png`: today's window from the CI UI catalog
  (`ui-catalog` artifact of nightly CI run 44208567082, renders `30-review.png` and
  `48-review-many-masks.png`).
- `after-open.png` (as the window opens), `after-edit.png` (a trim, a cut and two covers;
  insets for a time selection, cover placement and the Blur warning), `after-compact.png`
  (1100×700, right panel folded into the Edits overlay with a cut selected),
  `after-light-timeline.png` (the timeline in the light theme at normal and 150 % text).
  These are HTML mocks drawn with the app's Theme.cpp tokens and IBM Plex fonts, not
  renders of the app. Source: `mock/review4.html` (`#open`, `#edit`, `#compact`, `#light`)
  and `mock/scene.js`; the page loads the fonts from a `fonts/` folder next to it (copy
  `src/ui/fonts/IBMPlex*.ttf`), rendered with headless Chrome at 1.5× device scale.
- `filmstrip-test/`: the m74 benchmark. `results.md` has the answers, tables, versions
  and reproduction; harness `bench.cpp`, fixture generator `fixture.cpp`, runner and
  summarizer, raw `*.jsonl` timings.

## How the design was reached

Council per the `council` skill: Claude Opus 5.5 and GPT Sol 6.2 at high effort (Gemini
Pro unreachable: the Antigravity provider was not installed; GPT Astra's proposal was
read as input only). Round 1 independent proposals; rounds 2–4 a merged draft with
agree / can live with it / object; from round 5 each member scored the design against
put.gd's design manifesto (Dieter Rams' ten principles and the Pragmatic Design
Manifesto, as the ten-item UI checklist) and researched how shipping apps handle each
moment (Loom, CleanShot X, Screen Studio, Tella, Snagit, Camtasia, Clipchamp, ScreenPal,
QuickTime, Photos, Final Cut Pro, with sources in their reviews).

| Delegate | R2 | R3 | R4 | R5 | R6 | R7 | R8 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus | 7.5 | 8 | 8.5 | 8 | 9 | 9.5 | 9.9 |
| GPT Sol | 8 | 8.5 | 9 | 8 | 8.5 | 9.1 | 9.8 |
| Gemini Pro | no score | no score | no score | no score | no score | no score | no score |

Rounds 2–4 were general scores; rounds 5–8 used the manifesto checklist. Final round:
no checklist item below 9, no open objections. Patrick lifted the 1366×768 fit rule for
this window only (default 1440×900).

## Filmstrip measurement (m74, 2026-11-18 UTC)

Host m74: Intel Core i5-6500T, 4 threads, Linux Mint 22.3. Harness linked to the nightly
AppImage v26.1117.5114's bundled FFmpeg 9.0.2. Fixture: 180 s, 60 fps, H.264 in Matroska,
keyframe every 2 s, no B-frames, put.gd's x264 settings, generated offline with moving
screen-like content. Result for the 4K clip (p95 of five warm runs): keyframe tiles show
the two ends in 156 ms, 12 tiles in 433 ms, 24 in 739 ms on one core and 55 MiB; today's
exact-time method takes 2.7 s for 12; decoding every frame takes 24 s. An exact frame for
hover takes 217 ms median, 328 ms p95. aurora-amd was not measured (its desktop lock was
held by the GUI fuzz campaign). Result: method and density in `design.md` hold.
