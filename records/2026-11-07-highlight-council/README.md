# Highlight look: design council and review gates (#1237, PR #1238)

Patrick rejected three looks for the editor's Highlight mark (the round-1 dark
amber tint, round 2's marker with darkened ink, the candidate-B tint-plus-outline
sheets) and asked the council to settle the design. This record holds the whole
council: the brief, four independent proposals, the vote, a fact check, the
rule as built, and the review gates on real exports from the application.

## Process

1. **Brief** (`CONTEXT.md`, `DESIGN_TASK.md`): the problem, the rejected
   looks with pictures, the design tests (readable, obvious, honest, every
   colour, quiet, fits the visual language, deterministic and cheap).
2. **Proposals** (`proposals/`): GPT Sol "marker paper", GPT Astra "soft
   pigment", Claude Opus "true marker, kept contrast", Gemini 4 Argon "velvet
   ribbon" (arrived after the vote). All four drop round 2's coverage
   unmixing for a luminance transfer: the page becomes a band of the marker
   and each pixel keeps the contrast it had with its page, as dark lettering.
   They differ in band strength (pastel vs the swatch).
3. **Vote** (`votes/`, sheets in `compare/`): Sol 3/4/7/8/6, Astra
   3/4/7.5/7/6.5, Opus 3/4/6/5.5/7.5 for today / round 2 / Sol / Astra / Opus.
   Two votes for the pastel base, one for the swatch; the coordinator took the
   shared mechanism with the band luminance as the knob (`compare/sweep-*.png`).
4. **Fact check** (`factcheck.md`, Claude Fable): the proposals' maths and
   numbers hold; the draft rule had a page-independent light band, a seam at
   the 0.30 page class boundary and weak white markers. The implemented rule
   is continuous in the page luminance and has no page class.
5. **Rule as built** (`reviews/RULE.md`): pigment = marker lifted with white
   to luminance 0.45 or dimmed to 0.69 (black marker: mid grey); band =
   pigment multiplied onto the page lifted to at least 0.85; lettering = the
   first point on the band-to-black ramp reaching the pixel's own contrast
   with its page (knee below 1.04:1); boxes without a dominant background get a
   luminance-keeping wash (neutral markers shade or lighten within headroom).
6. **Review gates** on real exports (`exports/`, `zoom/`, `reviews/`):
   headless editor on f44, release build, marks applied through editor
   commands on four real captures (Cinnamon light dialog with LCD text, put.gd
   History dark table, Plasma dark desktop, Aurora notice over a painting), all
   seven palette colours. Reviewers were never told a target score.

| Delegate | Rounds | Scores | Gate |
| --- | --- | --- | --- |
| GPT Sol | 6 (+1 confirmation) | 7, 8, 8, 8, 8, 8 (8) | passed |
| GPT Astra | 1 (+1 confirmation) | 8 (8) | passed |
| Claude Opus | 2 | 7, 8 | passed |

Findings fixed between rounds (`reviews/RESOLVED.md`): the wash lowered a
coloured label's text contrast (now luminance-preserving); black and white
markers left no mark on photos (now shade/lighten, contrast ratios kept, black
with a dark toe, white within the box's exact headroom); a 17 px box's
one-pixel block row let an icon stroke pass for a background (every block now
samples a full window inside the box); red read as pink (pigment floor 0.55 →
0.45 for every colour).

Accepted trade-offs every reviewer lists: light text becomes dark lettering;
coloured text loses its hue inside the band; faint source lettering stays
faint; washes over artwork read as colour casts; red is a coral rather than
the raw swatch. All three reviewers expect the yellow marker on a dark put.gd
window to land well and name red as the likeliest reservation.

## Identity

put.gd-desktop `feat/1237-highlight-contrast` at `dc52421b8` (HighlightFilter
`src/editor/HighlightFilter.{h,cpp}`), built on f44 (Fedora 44, GNOME) as a
release scratch tree; `test_editor` 51/51 on the dev tree. Exports made by
`tools/headless_editor.sh` from record `2026-11-06-highlight-acceptance`
extended with per-colour and neutral cases (`exports-index.md` lists every
mark, colour and command). Cost (debug build): 4K box export 0.88 s, 1.5 MP
preview tile 0.21 s.

## Reproduce

`compare.py` renders every proposal on the crops of
`2026-11-06-highlight-real-captures`; `converged.py` is the Python reference
of the rule with the band floor as a knob; `zoom.py` cuts the 2× before/after
crops from the exports and their `inspect.json`.
