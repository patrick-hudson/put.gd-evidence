# History page refinement: before and after pictures

Pictures for put.gd-desktop pull request #1396 (`feat/history-page-refinement`), which refines the History page: a labelled count, page position beside Previous / Next, day sections with a pinned heading, a time column, a details pane that can be closed, a selection bar in the header, filter chips, sidebar counts and gallery day sections.

## What these show

- **Before** pictures are the History page of nightly `77c9d278d`.
- **After** pictures are commit `62d732e98` of the pull request.
- Both were rendered on the Debian 13 builder d69 with Qt 6.8.2 on the offscreen platform, from a development build, with a synthetic history of 236 files over 16 days (five pages, two destinations, six failed uploads). `15-in-progress-dark.png` is the UI catalog's `history-in-progress` state from the same commit.
- The red bar, boxes and numbers were added afterwards by `tools/annotate.py`; they are not part of the app.
- The version in the window footer is the catalog's fixed synthetic build identity, not a release version.

These are offscreen renders of widgets. They are not desktop acceptance evidence: no compositor, real session or real destination was involved.

## Checks run on the same commit (d69)

- `cmake --build --preset dev`: built.
- `ctest --preset dev`: 151 of 151 tests passed.
- MCP integration suite `tests/integration/test_mcp.py`: 8 tests, OK.
- `tools/ci/check_catalog_render.py --scheme dark`: 234 captures.
- `tools/lab/surface_map/surface_map.py check`: catalog ok.
- `tools.lab.surface_driver.gate check-catalog`: secret-control states match the pin (33 states).

## Files

| File | Shows |
| --- | --- |
| `01-list-before-dark.png`, `02-list-after-dark.png` | List with the details pane, dark |
| `03-pane-closed-light.png` | A row selected with the pane closed, light |
| `04-page2-dark.png` | Page 2 with a continued day |
| `05-pinned-day-light.png` | Pinned day heading while scrolled |
| `06-filters-before-dark.png`, `07-filters-after-dark.png` | Search with two filters |
| `08-multiselect-before-light.png`, `09-multiselect-after-light.png` | Three rows selected |
| `10-failed-before-dark.png`, `11-failed-after-dark.png` | Failed uploads |
| `12-gallery-before-dark.png`, `13-gallery-after-dark.png` | Gallery |
| `14-compact-150-light.png` | 1060 × 680 window at 150 % text |
| `15-in-progress-dark.png` | Uploads in progress |
