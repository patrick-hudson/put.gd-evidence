# Issue 1428 Quick redact on the final candidate (357210d2f): the 14 px GitHub fixture

Branch `fix/quick-redact-prefix` at e2c6cefb5, on `feat/text-recognition` 357210d2f (engine round #1462). Built and run on k72 (Kubuntu 26.04, 4 CPUs, Tesseract 5.5.0, ZXing-cpp 2.3.0), offscreen in a private headless resident, never a desktop: `editor.open`, `editor.apply` `redactText` with all five categories, `editor.saveCopy`, and the measure of the fe838a950 receipt (every pixel of an item's truth box black in the export).

`all-92-pages.json`: the 28 acceptance pages, 24 realistic-token pages, 16 held-out pages and 24 negative pages (generators in the record `2026-11-13-issue-1428-quick-redact-recall`).

## Why item 7 failed at 14 px

The engine cuts a single-pass panel into `threads × 2` strips. On a 2200 × 1400 acceptance page with four workers that is eight parts, and the strips are [0,178) [178,345) [345,882) [882,1400) (`cuts.cpp`, the engine's own `putgd_ocr_logic`). The cut at 178 is the middle of the blank rows 175 to 181, under item 7's line (ink rows 161 to 174, descenders and underscore included), so it splits no line. Yet with that arrangement the line is read as `oho aeaaaaaaeae aad ...` (DejaVu) or `APC CCEEEECEEEEC...` (Liberation Sans), the prefix gone. The same page with one or two CPUs (2 or 4 strips; the line inside [0,345)) is read exactly, `ghp_aaaa...`, and so are crops of the same rows ending at 178, 182 or 186 and a crop where the line sits in the middle. Realistic random `ghp_` tokens at 14 px are read and covered on the same commit with four workers.
