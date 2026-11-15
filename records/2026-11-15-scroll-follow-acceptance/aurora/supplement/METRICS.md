# Supplementary USER metrics

The capture, original reference and raw score remain unchanged. Chrome effective bands use the explicit measured six-pixel top/two-pixel bottom reference inset; see analysis/chrome-native-inset-scores.json. No fitted shift or scaling is used. A missing reference is unproved, never a pass. The reported height caps are unmet whole-page checklist criteria, not by themselves stitching-loss diagnoses.

| Case | End; truncated | Height/document | Effective bands | Placed/skipped | Source fps | s/10,000px | Inject/step lines |
|---|---|---:|---:|---:|---:|---:|---:|
| chromium-github-user-native-retry | done; False | 37819/44118 | 59/591 | 3590/5272 | 18.8 | 127.197 | 0/0 |
| chromium-news-user-notice-dismissed | done; False | 7538/7546 | 58/112 | 229/12 | 43.8 | 21.003 | 0/0 |
| chromium-python-user-native-retry | height_cap; True | 52493/110440 | 819/820 | 1510/0 | 22.7 | 13.404 | 0/0 |
| chromium-stackoverflow-user | height_cap; True | 52493/54249 | 33/819 | 1524/0 | 28.2 | 12.208 | 0/0 |
| chromium-wiki-user | done; False | 23296/23304 | unproved | 700/0 | 23.8 | 14.565 | 0/0 |
| firefox-github-user | done; False | 46738/45798 | 88/716 | 856/2 | 59.9 | 10.658 | 0/0 |
| firefox-news-user | done; False | 7508/7510 | 95/111 | 190/0 | 59.8 | 15.891 | 0/0 |
| firefox-python-user | height_cap; True | 52083/110214 | 814/814 | 965/0 | 48.8 | 9.949 | 0/0 |
| firefox-stackoverflow-user | height_cap; True | 52083/53262 | 133/812 | 1007/0 | 54.1 | 11.232 | 0/0 |
| firefox-wiki-user | done; False | 24092/24094 | 377/377 | 455/0 | 59.8 | 11.586 | 0/0 |
| firefox-wiki-user-jump | done; False | 24092/24094 | 377/377 | 410/0 | 59.5 | 10.583 | 0/0 |

## Native final-screen observations

The selected native Saving-frame ROI is compared directly, without translating the image; current pinned DOM regions, browser chrome and the actual capture bar are excluded. Chrome uses the retained browser-reported viewport origin and observed chrome-height change for its DOM mask.

| Case | Native equal/total | rowsAtDone | Qualification |
|---|---:|---:|---|
| chromium-github-user-native-retry | 0/13 | 0 | Ended mid-recovery at scrollY35160; not a qualified end-of-page Done case and not proof that Done ignored its fresh frame. |
| chromium-news-user-notice-dismissed | 11/11 | 0 | Actual native Saving framebuffer; source coordinates retained. |
| chromium-wiki-user | 14/14 | 0 | Actual native Saving framebuffer; source coordinates retained. |
| firefox-github-user | 14/14 | 0 | Actual native Saving framebuffer; source coordinates retained. |
| firefox-news-user | 10/10 | 0 | Actual native Saving framebuffer; source coordinates retained. |
| firefox-wiki-user | 15/15 | 0 | Actual native Saving framebuffer; source coordinates retained. |
| firefox-wiki-user-jump | 15/15 | 0 | Actual native Saving framebuffer; source coordinates retained. |
