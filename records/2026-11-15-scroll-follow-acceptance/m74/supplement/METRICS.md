# Cinnamon supplementary USER metrics

Original capture/reference/score files are retained. Chrome effective bands use only the measured six-pixel top/two-pixel bottom reference inset. A missing reference is unproved. Configured height caps fail the literal whole-page criterion without proving stitching loss.

| Case | End; truncated | Height/document | Effective bands | Placed/skipped | Source fps | s/10,000px | Inject/step |
|---|---|---:|---:|---:|---:|---:|---:|
| chromium-github-user | done; False | 44651/44154 | 65/690 | 1718/4947 | 30 | 73.556 | 0/0 |
| chromium-news-user | done; False | 7538/7546 | 51/102 | 137/87 | 28.9 | 34.625 | 0/0 |
| chromium-python-user | height_cap; True | 52493/110440 | 819/820 | 876/0 | 30 | 12.907 | 0/0 |
| chromium-stackoverflow-user | height_cap; True | 52493/54215 | 30/819 | 769/0 | 29.8 | 10.900 | 0/0 |
| chromium-wiki-user | done; False | 23292/23300 | unproved | 395/0 | 30 | 14.447 | 0/0 |
| firefox-github-user | done; False | 45928/45801 | 75/716 | 495/22 | 30 | 12.460 | 0/0 |
| firefox-news-user | done; False | 7546/7547 | 83/110 | 111/200 | 29.8 | 32.801 | 0/0 |
| firefox-python-user | height_cap; True | 52083/111974 | 814/814 | 509/0 | 29.9 | 10.470 | 0/0 |
| firefox-stackoverflow-user | height_cap; True | 52083/54170 | 127/812 | 556/4 | 30 | 11.287 | 0/0 |
| firefox-wiki-user | done; False | 24116/24117 | 377/377 | 248/0 | 30 | 12.677 | 0/0 |

| Native Saving case | Equal/total | rowsAtDone |
|---|---:|---:|
| chromium-github-user | 13/13 | 0 |
| chromium-news-user | 8/8 | 0 |
| chromium-stackoverflow-user | 0/0 | 0 |
| chromium-wiki-user | 14/14 | 0 |
| firefox-github-user | 13/14 | 0 |
| firefox-news-user | 9/10 | 0 |
| firefox-stackoverflow-user | 0/0 | 0 |
| firefox-wiki-user | 14/15 | 0 |

These are the original acceptance comparisons. The separately labelled two-pixel control-edge diagnostic improves GitHub to14/14 but leaves Wiki14/15 and news9/10. It does not replace the original scores or establish content loss. Automatic cap finishes are not explicit Done proofs.
