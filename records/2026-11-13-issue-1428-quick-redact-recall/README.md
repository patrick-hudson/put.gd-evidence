# Issue 1428 Quick redact recall: per-page results through the real editor and helper

Branch `fix/quick-redact-recall` at 7eb218550, built on k72 (Kubuntu 26.04, Qt 6.10.2, GCC 15.2, Tesseract 5.5.0, ZXing-cpp 2.3.0), dev preset. Offscreen, never a desktop: a private headless resident (`putgd --background` under `dbus-run-session`, private XDG directories), `editor.open` of each page, `editor.apply` with `redactText` for all five categories, `editor.saveCopy`, and the measure of the fe838a950 receipt: an item counts as covered only when every pixel of its truth box is black in the export. The editor starts the real `putgd-ocr` itself.

| File | What |
| --- | --- |
| `corpus-28-pages.json` | The receipt's 28 pages (sources in the fe838a950 measurement record) |
| `realistic-heldout-negative-pages.json` | 24 pages with seeded random-looking tokens (`gen_real.py`), 16 held-out pages with new seeds, sizes 12, 13, 16 and 24 px and every item inside a sentence (`gen_held.py`), and 24 negative pages of ordinary interface, log, terminal and code text (`gen_neg.py`) |
| `editor_run.py` | The run and the measure |
| `dump.cpp`, `evaluate.py` | The throwaway diagnosis tool (the helper's unfiltered candidates, and matching on saved candidates) and the offline scorer used while iterating |

Every value on the generated pages is made up; the pages themselves are not published, only names, counts and rectangles.
