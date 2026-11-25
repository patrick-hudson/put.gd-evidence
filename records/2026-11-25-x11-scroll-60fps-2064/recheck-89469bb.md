# Live recheck at 89469bb (after Sol round 1)

CI run 45720771528 built `26.1125.7091~dev+g89469bbc0410`. The DEB was unpacked on m74, and the driver was rebuilt incrementally at `89469bbc`; its build-info.json is identical to the package's. Harness: `harness/recheck.sh`, under the desktop lock and quiet lease. Per-run results: `data/m74-recheck-89469bb.jsonl`.

Brisk you-scroll at seeds 4 to 6, times the page was lost and found again, on the same seeds as the earlier rows:

| Build | GitHub PR #1398 | Stack Overflow | Total |
| --- | --- | --- | --- |
| nightly 26.1125.7045 | 3, 1, 1 | 4, 3, 4 | 16 |
| d526c747 | 0, 2, 0 | 1, 0, 1 | 4 |
| 89469bb | 0, 0, 3 | 2, 2, 3 | 10 |

- Stack Overflow seed 6 fell back to 30 at 1080p ("the loop missed 31% of the frames"); the fallback fired on a real page.
- Wikipedia auto-scroll: `end_of_content`.
- GitHub auto-scroll: lost the page once near the top (127 `no_match` skips at about 1,240 px), found it again and reached the page end at full height (40,164 of 40,164 rows). It ends `done` because frames were skipped.
- 3840×2160 Xvfb: fell back to 30, helper 101% of a core, Xvfb 26%: the same as before.
