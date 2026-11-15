# Page metrics — budgie

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| firefox-github-auto | done; 45793/45798 | 715/716 | 571/2 | 11.9 | 22.880 | 1 fresh; 0 added |
| firefox-github-user | done; 45793/45798 | 715/716 | 385/1 | 10.2 | 21.494 | 1 fresh; 0 added |
| firefox-news-auto | done; 3187/7511 | 29/43 | 22/294 | 16 | 181.917 | 1 fresh; 0 added |
| firefox-news-user | done; 7506/7511 | 95/105 | 67/622 | 16.1 | 126.657 | 1 fresh; 0 added |
| firefox-python-auto | height_cap; 52083/110214 | 814/814 | 599/0 | 28.6 | 23.296 | 0 fresh; 0 added |
| firefox-python-user | height_cap; 52083/110214 | 7/814 | 543/7 | 11.4 | 21.952 | 0 fresh; 0 added |
| firefox-stackoverflow-auto | lost_track; 12825/53108 | 3/199 | 105/483 | 10.3 | 62.048 | 1 fresh; 0 added |
| firefox-stackoverflow-user | height_cap; 52083/53125 | 203/812 | 482/26 | 11.4 | 23.903 | 0 fresh; 0 added |
| firefox-wiki-auto | done; 24089/24094 | 376/377 | 90/62 | 10.5 | 12.885 | 1 fresh; 0 added |
| firefox-wiki-auto-inside-body | end_of_content; 24854/24733 | 348/387 | 167/0 | 15.1 | unavailable | 0 fresh; see log added |
| firefox-wiki-user | done; 24089/24094 | 377/377 | 327/0 | 14.6 | 29.692 | 1 fresh; 0 added |
| firefox-wiki-user-inside-body | done; 24215/24094 | 377/377 | 299/0 | 13.9 | unavailable | 0 fresh; see log added |
| firefox-wiki-user-jump | done; 24089/24094 | 373/377 | 270/249 | 13.7 | 33.891 | 1 fresh; 0 added |
| firefox-wiki-auto-inside | end_of_content; 24854/24733 | unproved | 167/0 | 15.1 | 16.069 | 1 fresh; 0 added |
| firefox-wiki-user-inside | done; 24215/24094 | unproved | 299/0 | 13.9 | 25.874 | 1 fresh; 0 added |
