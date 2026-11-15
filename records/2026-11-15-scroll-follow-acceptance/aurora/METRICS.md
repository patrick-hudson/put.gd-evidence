# Page metrics — aurora

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| chromium-github-auto | lost_track; 36948/44491 | 260/578 | 2413/987 | 20.7 | 48.871 | 2 fresh; 0 added |
| chromium-github-user | lost_track; 37278/44491 | 260/583 | 4461/6091 | 23.2 | 128.959 | 2 fresh; 0 added |
| chromium-news-auto | done; 7531/7531 | 56/111 | 59/195 | 45.2 | 18.500 | 1 fresh; 0 added |
| chromium-news-user | done; 7533/7533 | 52/103 | 212/0 | 49.5 | 17.548 | 2 fresh; 0 added |
| chromium-python-auto | height_cap; 52493/110440 | 819/820 | 3086/0 | 30.3 | 25.413 | 0 fresh; 0 added |
| chromium-python-user | height_cap; 52493/110440 | 819/820 | 1516/0 | 31.3 | 10.417 | 0 fresh; 0 added |
| chromium-stackoverflow-auto | height_cap; 52493/54249 | 11/818 | 3019/0 | 28.7 | 25.270 | 0 fresh; 0 added |
| chromium-stackoverflow-user | height_cap; 52493/54266 | 21/818 | 1569/0 | 28.4 | 13.335 | 0 fresh; 0 added |
| chromium-wiki-auto | end_of_content; 23943/23943 | unproved | 1377/0 | 25.7 | 26.744 | 1 fresh; 0 added |
| chromium-wiki-user | done; 23304/23304 | unproved | 635/0 | 26.1 | 13.215 | 2 fresh; 0 added |
| firefox-github-auto | end_of_content; 46171/46171 | 722/722 | 2650/0 | 59.6 | 26.860 | 1 fresh; 0 added |
| firefox-github-user | done; 46171/46171 | 720/722 | 793/0 | 59.7 | 11.160 | 2 fresh; 0 added |
| firefox-news-auto | end_of_content; 7510/7510 | 0/0 | 391/0 | 59.1 | 28.401 | 1 fresh; 0 added |
| firefox-news-auto-visible-pins | end_of_content; 7510/7510 | 88/110 | 391/0 | 59.1 | 28.401 | 0 fresh; 0 added |
| firefox-news-user | done; 7527/7527 | 83/103 | 183/0 | 59.7 | 22.451 | 2 fresh; 0 added |
| firefox-python-auto | height_cap; 52083/110214 | unproved | 3115/0 | 59.9 | 25.881 | 0 fresh; 0 added |
| firefox-python-user | height_cap; 52083/110214 | unproved | 1139/0 | 52.6 | 10.569 | 0 fresh; 0 added |
| firefox-stackoverflow-auto | height_cap; 52083/54221 | 799/812 | 2999/0 | 57.8 | 25.789 | 0 fresh; 0 added |
| firefox-stackoverflow-user | height_cap; 52083/53240 | 202/812 | 939/0 | 52.4 | 10.416 | 0 fresh; 0 added |
| firefox-wiki-auto | end_of_content; 24094/24094 | 377/377 | 1401/0 | 59.5 | 26.976 | 1 fresh; 0 added |
| firefox-wiki-user | done; 24094/24094 | 377/377 | 524/0 | 59.3 | 11.744 | 2 fresh; 0 added |
| firefox-wiki-auto-inside | end_of_content; 24225/24094 | unproved | 472/0 | 59.3 | 12.032 | 1 fresh; 0 added |
| firefox-wiki-user-inside | done; 24225/24094 | unproved | 481/0 | 59.9 | 12.870 | 2 fresh; 0 added |
