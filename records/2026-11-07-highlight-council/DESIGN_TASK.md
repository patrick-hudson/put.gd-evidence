# Design task

Read /home/patrick/work/i1237-council/CONTEXT.md first, then look at every image
under /home/patrick/work/i1237-council/ (rejected/, survey/, crops/, acc/) with
your image viewing tool. You cannot design this without seeing what was rejected.

Design the look of put.gd's Highlight mark so that it passes every design test in
CONTEXT.md and the owner would call it great. Think about it from the reader's
side (someone opening the exported screenshot) and the user's side (someone
marking up a dark-theme capture with a yellow marker, then a red one). You may
propose a rule that is nothing like the rejected ones; you may also propose an
honest improvement on one of them if you can say exactly why the rejected version
failed and yours does not. Prefer one strong design to several weak ones; at most
three candidates, ranked.

Deliver, in your proposal directory (and nowhere else; the repo and the research
tools are read-only for you, copy hl_research.py into your directory to modify):

1. PROPOSAL.md: the rule in exact pixel maths (per-pixel, given background
   colour, ink coverage in 0..1, the marker colour, light/dark page decision),
   any decorations with sizes, how white and black markers behave, how the
   fallback for photos behaves, and the rationale against each design test.
   State what the reader sees in one sentence per page type.
2. sheet-dark.png, sheet-light.png, sheet-colours.png: renders of your candidate(s)
   on the real crops at 2× zoom, with the seven palette colours (red #EF4444,
   orange #F97316, yellow #FACC15, green #22C55E, blue #3B82F6, white #FFFFFF,
   black #111111) on at least the dark table, the dark notice, the Plasma
   notification and the light paragraph. Label every tile. Also include "today"
   and "round 2" tiles next to yours for comparison. Render with Pillow/numpy
   (both are installed; run python3 -I).
3. Numbers: for each tile, worst WCAG contrast of the text against its new
   background and the mean RGB shift of ink-core pixels (coverage ≥ 0.9); the
   harness's measure() does most of this.

Work on this workstation only (small numpy jobs are fine); do not touch the lab
builders or any git branch. Do not post on GitHub. Finish with a short summary
listing your proposal directory's files.
