# Page metrics — f44

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| firefox-github-auto | end_of_content; 46171/46171 | 714/722 | 1878/0 | 31.9 | 34.902 | 1 fresh; 0 added |
| firefox-github-user | done; 46171/46171 | 719/722 | 476/35 | 31.6 | 11.043 | 2 fresh; 0 added |
| firefox-stackoverflow-auto | height_cap; 52083/53240 | 789/812 | 2902/304 | 32.3 | 45.150 | 0 fresh; 0 added |
| firefox-stackoverflow-user | height_cap; 52083/54184 | 780/812 | 609/9 | 32.4 | 10.375 | 0 fresh; 0 added |
| firefox-wiki-auto | end_of_content; 24094/24094 | 374/377 | 616/0 | 32.6 | 24.663 | 1 fresh; 0 added |
| firefox-wiki-user | done; 24094/24094 | 377/377 | 286/0 | 32.3 | 12.954 | 2 fresh; 0 added |
| firefox-news-auto | end_of_content; 7510/7510 | 77/112 | 127/0 | 34.9 | 24.988 | 1 fresh; 0 added |
| firefox-news-user | done; 7314/7534 | 32/110 | 90/31 | 31.8 | 27.996 | 2 fresh; 0 added |
| firefox-python-auto | height_cap; 52083/110214 | 814/814 | 2941/0 | 34.1 | 41.078 | 0 fresh; 0 added |
| firefox-python-user | height_cap; 52083/110214 | 814/814 | 605/0 | 32.3 | 11.479 | 0 fresh; 0 added |
| firefox-wiki-user-jump | done; 24094/24094 | 373/377 | 256/0 | 33.1 | 11.528 | 2 fresh; 0 added |
| firefox-inside-user-page | done; 24211/24094 | 377/377 | 296/0 | 34.3 | unavailable | 0 fresh; see log added |
| firefox-inside-auto-page | end_of_content; 24211/24094 | 373/377 | 191/0 | 32 | unavailable | 0 fresh; see log added |
| user-script-recovery | done; 1216/24094 | 19/19 | 14/9 | 34.2 | unavailable | 0 fresh; see log added |
| auto-script-recovery | done; 23951/24094 | 372/374 | 1370/421 | 35.9 | unavailable | 0 fresh; see log added |
| mixed-focused | done; 5465/24094 | 86/86 | 97/0 | 36.3 | unavailable | 0 fresh; see log added |
| firefox-github-user-doneproof2 | done; 46171/46171 | unproved | 514/0 | 31.7 | 12.277 | 0 fresh; 0 added |
| firefox-news-user-doneproof2 | done; 7472/7493 | unproved | 85/109 | 31.6 | 36.262 | 0 fresh; 0 added |
| firefox-wiki-auto-inside | end_of_content; 24211/24094 | unproved | 191/0 | 32 | 12.018 | 1 fresh; 0 added |
| firefox-wiki-user-doneproof2 | done; 24094/24094 | unproved | 271/0 | 32.5 | 11.379 | 0 fresh; 0 added |
| firefox-wiki-user-inside | done; 24211/24094 | unproved | 296/0 | 34.3 | 12.817 | 2 fresh; 0 added |
