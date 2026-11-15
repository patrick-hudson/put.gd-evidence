# Page metrics — hyprland

These are measured raw comparisons, not blanket passes. Read README.md for page-layout changes, caps, geometry and known limits. Bands are equal/total tolerant 64-row bands; 0/0 is unproved. Seconds per 10,000 px uses the capture elapsedMs and saved height (not wall time). User mode must be done and non-truncated; AUTO may reach its height cap. FPS is the actual helper source rate.

| Case | End; height/document | Bands | Placed/skipped | FPS | s/10,000 px | Fresh/Done-added |
|---|---|---:|---:|---:|---:|---|
| firefox-github-auto | end_of_content; 44941/44941 | 698/702 | 132/0 | 6.3 | 24.344 | 1 fresh; 0 added |
| firefox-github-user | done; 38161/44941 | 80/597 | 119/194 | 8.9 | 32.584 | 1 fresh; 0 added |
| firefox-news-auto | lost_track; 899/5645 | 0/7 | 1/75 | 3.1 | 338.954 | 1 fresh; 0 added |
| firefox-news-auto-native-page2 | lost_track; 945/5645 | 10/11 | 1/107 | 3 | 447.090 | 1 fresh; 0 added |
| firefox-news-user | done; 7303/7155 | 0/102 | 42/339 | 3.6 | 219.174 | 1 fresh; 0 added |
| firefox-python-auto | height_cap; 52742/110485 | 824/824 | 156/0 | 5.9 | 23.722 | 0 fresh; 0 added |
| firefox-python-user | height_cap; 52742/110485 | 432/824 | 147/339 | 7.8 | 27.194 | 0 fresh; 0 added |
| firefox-stackoverflow-auto | lost_track; 899/53941 | 0/12 | 1/71 | 3.3 | 308.710 | 1 fresh; 0 added |
| firefox-stackoverflow-auto-native-page2 | done; 1743/53924 | 23/26 | 4/12 | 4.6 | 145.955 | 1 fresh; 0 added |
| firefox-stackoverflow-user | lost_track; 51543/53125 | 5/804 | 158/782 | 7.1 | 45.606 | 1 fresh; 0 added |
| firefox-wiki-auto | end_of_content; 24514/24510 | 139/383 | 85/0 | 9.8 | 34.639 | 1 fresh; 0 added |
| firefox-wiki-auto-full-width | end_of_content; 23343/23343 | 365/365 | 113/0 | 7.2 | 39.643 | 1 fresh; 0 added |
| firefox-wiki-user | done; 24514/24510 | 130/383 | 86/73 | 10 | 28.923 | 1 fresh; 0 added |
| firefox-wiki-user-full-width | done; 23343/23343 | 365/365 | 61/274 | 9.3 | 30.036 | 1 fresh; 0 added |
| firefox-wiki-user-jump | done; 23343/23343 | 365/365 | 67/422 | 11 | 37.432 | 1 fresh; 0 added |
| firefox-wiki-user-inside | done; 23478/23343 | unproved | 53/197 | 10.2 | 28.105 | 1 fresh; 0 added |
