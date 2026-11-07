# Review: the Highlight look as built

Read /home/patrick/work/i1237-council/CONTEXT.md (the problem, what the owner
rejected, the design tests) and /home/patrick/work/i1237-council/review/RULE.md
(the rule as implemented). The code is src/editor/HighlightFilter.{h,cpp} in
/home/patrick/work/put.gd-hl (branch feat/1237-highlight-contrast); the tests
are the highlight* cases in tests/unit/test_editor.cpp.

The pictures are real exports from the application (headless editor on f44,
release build) in /home/patrick/work/i1237-council/review/exports/: full
captures `*.png` with highlights applied through the editor commands, and 2×
crops of every highlighted region in `zoom/`. `index.md` lists which marker
colour and which command made each mark. `before/` holds the untouched captures.

Judge the look as a reader of the exported PNG and as the person who made the
mark, against the design tests in CONTEXT.md and Dieter Rams' ten principles.
Look at every zoom. Then write
/home/patrick/work/i1237-council/review/<your-name>.md with:

1. A score out of 10 for the look as built, with the reasoning.
2. Problems, each with the picture and region it is visible in, what you see,
   why it matters, and the smallest change to the rule or code that would fix
   it. Separate the ones you consider must-fix from the ones that are nice-to-have.
3. Anything in the code that would make the export differ from the preview, or
   that is not deterministic, or that is slower than it needs to be.
4. One paragraph: what the owner will see when he tries it on his dark put.gd
   window with a yellow marker, then red, and whether he will like it.

Keep it under 800 words. Read-only: write only your review file. Do not run
builds or touch the lab builders. Nothing outside the look is in scope
(snapping, commands and the editor UI are settled).
