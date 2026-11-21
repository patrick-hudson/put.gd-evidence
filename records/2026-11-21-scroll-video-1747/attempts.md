# Setup attempts and repeats

| Desktop | Browser | Row | Build | Lost events / longest | Skipped / contradicted | Time | Capture / page px | Static bands | Image and video | Images |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| aurora-amd | Chrome | A-first (user) | Nightly | 1 / 0.153 s | 9 / 4 | 35.45 | 6374 / 6374 | 19/98 | Fail. Full page. Torn across source frames | [Bar](aurora-amd/base-chromium-A-first-user-repeat/bar.png), [Capture](aurora-amd/base-chromium-A-first-user-repeat/capture.png), [Browser ref](aurora-amd/base-chromium-A-first-user-repeat/reference.png), [Video crop](aurora-amd/base-chromium-A-first-user-repeat/video.png) |
| aurora-amd | Chrome | A-first (user) | Candidate | 0 / 0 s | 0 / 0 | 35.5 | 6374 / 6374 | 19/98 | Pass. Full page. One coherent source frame | [Bar](aurora-amd/candidate-chromium-A-first-user-repeat/bar.png), [Capture](aurora-amd/candidate-chromium-A-first-user-repeat/capture.png), [Browser ref](aurora-amd/candidate-chromium-A-first-user-repeat/reference.png), [Video crop](aurora-amd/candidate-chromium-A-first-user-repeat/video.png) |
| aurora-amd | Chrome | A-later (auto) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-A-later-auto/failure.png) |
| aurora-amd | Chrome | A-later (auto) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-A-later-auto-retry-1795231528/failure.png) |
| aurora-amd | Chrome | A-later (user) | Nightly | 0 / 0 s | 0 / 0 | 17.79 | 6367 / 6374 | 19/98 | See video review. Full page | [Bar](aurora-amd/base-chromium-A-later-user-pilot/bar.png), [Capture](aurora-amd/base-chromium-A-later-user-pilot/capture.png), [Browser ref](aurora-amd/base-chromium-A-later-user-pilot/reference.png), [Video crop](aurora-amd/base-chromium-A-later-user-pilot/video.png) |
| aurora-amd | Chrome | A-later (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-A-later-user-probe/failure.png) |
| aurora-amd | Chrome | B-aj (user) | Nightly | 1 / 27.962 s | 1071 / 0 | 40.59 | 2673 / 7549 | 10/35 | Fail (stalled). 4,876 px short. Inline video incomplete | [Bar](aurora-amd/base-chromium-B-aj-user/bar.png), [Lost bar](aurora-amd/base-chromium-B-aj-user/lost.png), [Capture](aurora-amd/base-chromium-B-aj-user/capture.png), [Browser ref](aurora-amd/base-chromium-B-aj-user/reference.png) |
| aurora-amd | Chrome | B-mdn (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-B-mdn-user/failure.png) |
| aurora-amd | Chrome | B-mdn (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-B-mdn-user-retry-1795231491/failure.png) |
| aurora-amd | Chrome | B-wiki (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-B-wiki-user/failure.png) |
| aurora-amd | Chrome | B-wiki (user) | Nightly | 0 / 0 s | 0 / 0 | 21.8 | 3971 / 3971 | 12/62 | Playback unverified. Full page | [Bar](aurora-amd/base-chromium-B-wiki-user-retry-1795231457/bar.png), [Capture](aurora-amd/base-chromium-B-wiki-user-retry-1795231457/capture.png), [Browser ref](aurora-amd/base-chromium-B-wiki-user-retry-1795231457/reference.png) |
| aurora-amd | Chrome | C (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-C-user/failure.png) |
| aurora-amd | Chrome | C (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-chromium-C-user-retry-1795231495/failure.png) |
| aurora-amd | Firefox | A-first (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-A-first-user/failure.png) |
| aurora-amd | Firefox | A-first (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-A-first-user-retry-1795231503/failure.png) |
| aurora-amd | Firefox | A-later (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-A-later-user/failure.png) |
| aurora-amd | Firefox | A-later (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-A-later-user-retry-1795231499/failure.png) |
| aurora-amd | Firefox | B-aj (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-aj-user/failure.png) |
| aurora-amd | Firefox | B-aj (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-aj-user-retry-1795231508/failure.png) |
| aurora-amd | Firefox | B-mdn (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-mdn-user/failure.png) |
| aurora-amd | Firefox | B-mdn (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-mdn-user-retry-1795231517/failure.png) |
| aurora-amd | Firefox | B-mdn (user) | Nightly | 0 / 0 s | 0 / 0 | 100.85 | 18923 / 18923 | 284/294 | Playback unverified. Full page | [Bar](aurora-amd/base-firefox-B-mdn-user-retry-1795231710/bar.png), [Capture](aurora-amd/base-firefox-B-mdn-user-retry-1795231710/capture.png), [Browser ref](aurora-amd/base-firefox-B-mdn-user-retry-1795231710/reference.png) |
| aurora-amd | Firefox | B-wiki (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-wiki-user/failure.png) |
| aurora-amd | Firefox | B-wiki (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-B-wiki-user-retry-1795231512/failure.png) |
| aurora-amd | Firefox | C (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-C-user/failure.png) |
| aurora-amd | Firefox | C (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-C-user-retry-1795231522/failure.png) |
| aurora-amd | Firefox | C (user) | Nightly | — | — | — | — / — | — | Setup failed | [Setup](aurora-amd/base-firefox-C-user-retry-1795231826/failure.png) |
| m74 | Chrome | A-first (user) | Candidate | 1 / 3.274 s | 99 / 3 | 36.27 | 6297 / 6374 | 19/98 | Fail (stalled). 77 px short. Visually coherent. Seven strips match the same source frame | [Bar](m74/candidate-chromium-A-first-user-repeat/bar.png), [Lost bar](m74/candidate-chromium-A-first-user-repeat/lost.png), [Capture](m74/candidate-chromium-A-first-user-repeat/capture.png), [Browser ref](m74/candidate-chromium-A-first-user-repeat/reference.png), [Video crop](m74/candidate-chromium-A-first-user-repeat/video.png) |
