# Page metrics — m74

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| chromium-github-auto | lost_track; 36865/44527 | 270/576 | 879/1476 | 30 | 34.475 | 2 fresh; 0 added |
| chromium-github-user | done; 44527/44527 | 270/696 | 869/960 | 30 | 25.048 | 2 fresh; 0 added |
| chromium-news-auto | end_of_content; 7310/7530 | 13/102 | 130/0 | 28.9 | 26.055 | 1 fresh; 0 added |
| chromium-news-user | done; 7530/7530 | 50/110 | 128/27 | 27.9 | 22.328 | 2 fresh; 0 added |
| chromium-python-auto | height_cap; 52493/110440 | 819/820 | 1193/0 | 30 | 19.479 | 0 fresh; 0 added |
| chromium-python-user | height_cap; 52493/110440 | 819/820 | 862/0 | 30 | 11.809 | 0 fresh; 0 added |
| chromium-stackoverflow-auto | height_cap; 52493/54229 | 53/818 | 1143/0 | 29.8 | 19.811 | 0 fresh; 0 added |
| chromium-stackoverflow-user | height_cap; 52493/54368 | 18/818 | 821/1 | 29.9 | 11.642 | 0 fresh; 0 added |
| chromium-wiki-auto | end_of_content; 23300/23300 | unproved | 519/0 | 30 | 20.621 | 1 fresh; 0 added |
| chromium-wiki-user | done; 23300/23300 | unproved | 433/0 | 30 | 15.237 | 2 fresh; 0 added |
| firefox-wiki-user-jump | done; 24117/24117 | 373/377 | 240/0 | 30 | 11.652 | 2 fresh; 0 added |
| firefox-inside-user-page | done; 24275/24117 | 370/377 | 225/0 | 30 | unavailable | 0 fresh; see log added |
| firefox-inside-auto-page | end_of_content; 24275/24117 | 370/377 | 168/0 | 29.9 | unavailable | 0 fresh; see log added |
| firefox-lostauto-final | done; 24015/24117 | 366/375 | 392/408 | 30 | unavailable | 0 fresh; see log added |
| firefox-mixed | done; 3392/24117 | 48/53 | 41/0 | 29.9 | unavailable | 0 fresh; see log added |
| firefox-user-recovered | done; 1234/24117 | 15/20 | 6/47 | 30 | unavailable | 0 fresh; see log added |
| firefox-github-auto | end_of_content; 46173/46173 | unproved | 743/0 | 30 | 17.535 | 1 fresh; 0 added |
| firefox-github-user | done; 46037/46173 | unproved | 538/0 | 30 | 12.238 | 2 fresh; 0 added |
| firefox-news-auto | done; 7554/7554 | unproved | 140/18 | 29.1 | 25.483 | 1 fresh; 0 added |
| firefox-news-user | done; 7530/7530 | unproved | 97/70 | 29.5 | 28.774 | 2 fresh; 0 added |
| firefox-python-auto | height_cap; 52083/111974 | unproved | 909/0 | 30 | 16.996 | 0 fresh; 0 added |
| firefox-python-user | height_cap; 52083/111974 | unproved | 587/0 | 30 | 11.522 | 0 fresh; 0 added |
| firefox-stackoverflow-auto | height_cap; 52083/54116 | unproved | 851/0 | 30 | 17.321 | 0 fresh; 0 added |
| firefox-stackoverflow-user | height_cap; 52083/54235 | unproved | 577/19 | 29.9 | 12.290 | 0 fresh; 0 added |
| firefox-wiki-auto | end_of_content; 24117/24117 | unproved | 391/0 | 30 | 18.392 | 1 fresh; 0 added |
| firefox-wiki-auto-inside | end_of_content; 24275/24117 | unproved | 168/0 | 29.9 | 10.830 | 1 fresh; 0 added |
| firefox-wiki-user | done; 24117/24117 | unproved | 267/0 | 30 | 12.439 | 2 fresh; 0 added |
| firefox-wiki-user-inside | done; 24275/24117 | unproved | 225/0 | 30 | 11.016 | 2 fresh; 0 added |
