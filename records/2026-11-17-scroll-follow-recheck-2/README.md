# Scrolling capture final re-check — 2026-11-17 (round 2)

**WRONG: 0. DAMAGED: 1 run. CUTOUT: 5 runs / 5 measured areas.** CUTOUT and PINNED are separate from row verdicts, following the owner’s clarification. Across every saved image, including both notice-forcing attempts: **15 RIGHT, 10 HONEST, 0 WARNED, 0 WRONG, 1 DAMAGED**. The owner will judge DAMAGED and CUTOUT; this report does not turn them into HONEST or claim blanket acceptance.

Tested the CI **AppImage**, deployed in a private directory on each physical builder. Branch head `54c5281ac71b8c6a905b94586377d2ceaf604fce`; packaged merge `3a809d21927b5a42425859458328f43c83f8b8cb`, merging into nightly `4d4a6d97aac406f6859b1eac77219afe20e52750`; exact expected tree `18a701a57cb74324481d7d2877bde086819fc160`. Version `26.1117.5096-dev+g3a809d21927b`, clean git provenance. AppImage SHA-256 **`dd13a41924721fd6b470993b23da6437e8fb2bc3dda66252542376243d3706c6`**, 164,874,744 bytes. Both builders independently hash-verified the artifact and cold-start diagnostics verified the merge tree and local destinations. [Mint identity](m74/package-identity.json), [Aurora identity](aurora-amd/package-identity.json), [merge parents/tree](merge-identity.json).

[CI run 44015346469](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44015346469) passed, including the required **CI** summary. The foreground `gh run watch ... --interval 60 --exit-status` completed with status 0 before deployment/testing. [CI job record](ci.json). No builder compilation, product source change, product PR, product push, merge, release, VM, d69 work, object upload or link copy was performed. The workstation only controlled builders and assembled/published evidence. No native DEB/RPM was installed; the extracted CI AppImages were removed by their exact file manifests after testing.

Physical profiles: **m74 Linux Mint 22.3, Cinnamon 6.6.9 / Muffin 6.6.3, native X11, Firefox 158.0**; **aurora-amd Aurora Fedora 45, Plasma 6.8.2 / KWin 6.8.2, native Wayland, Firefox 160.0 and Chrome for Testing 157.0.8103.78**. [Mint session proof](m74/session-proof.json), [Aurora session proof](aurora-amd/session-proof.json). Mint’s raw user-manager environment in `host-proof.json.nativeSession` contains stale wlroots/:2 values from prior lab work: it is not the test environment. The harness explicitly used Cinnamon/:0/xcb, matching the live physical Cinnamon process and native desktop pictures.

The previous method and original record are [f19043f6b932103d2a29f8fac10ac6164cf674e0](https://github.com/patrick-hudson/put.gd-evidence/tree/f19043f6b932103d2a29f8fac10ac6164cf674e0/records/2026-11-17-scroll-follow-recheck). Reused its public pages (GitHub PR #1398, Stack Overflow question 11227809, the same Al Jazeera article, Wikipedia/Linux), native magenta calibration, real relative uinput wheel, full-page browser reference, height checks, unchanged `where.py`, `seam.py`, `unwritten.py` and band scorer. `band-details.py` only exposes the original tolerant scorer’s failing bands. Normal input: randomly 1–5 notches and 220–500 ms gaps, with the previous six-notch reverse on news. Fast input: 18-notch commands with 60 ms loop gaps plus observation overhead; the actual device retained **12 ms per notch** because sudo reset the experimental timing environment variable. These traversed GitHub in about 8 s versus about 45–54 s for normal capture. The successful forced recovery explicitly passed 1 ms notch timing through sudo and disabled smooth scrolling only in its disposable Firefox profile.

Only one physical desktop was leased at a time. Mint lease 04:31:56–04:57:49 UTC; Aurora product-test lease 04:57:56–05:15:11 UTC; Aurora reference-only lease 05:18:40–05:20:22 UTC. Heartbeats and cleanup receipts were retained. All GUI work finished well within two hours of package availability and outside the prohibited lock window. Private resolved session sockets were preflighted before launch: **44 bytes Mint, 48 bytes Aurora**, with the session bus/PipeWire/Pulse/Wayland paths also checked against 107 bytes. No path-length failure.

**m74 — row verdicts**

| Case | Runs | RIGHT | HONEST | WARNED | WRONG | DAMAGED |
|---|---:|---:|---:|---:|---:|---:|
| A — Firefox GitHub, previous pace | 8 | 4 | 4 | 0 | 0 | 0 |
| A — Firefox GitHub, faster | 3 | 0 | 2 | 0 | 0 | 1 |
| B — Stack Overflow, you scroll | 2 | 1 | 1 | 0 | 0 | 0 |
| B — news + reverse | 2 | 0 | 2 | 0 | 0 | 0 |
| B — Wikipedia, one per mode | 2 | 2 | 0 | 0 | 0 | 0 |

**aurora-amd — row verdicts**

| Case | Runs | RIGHT | HONEST | WARNED | WRONG | DAMAGED |
|---|---:|---:|---:|---:|---:|---:|
| C — Firefox GitHub, you scroll | 3 | 3 | 0 | 0 | 0 | 0 |
| C — Chrome GitHub, you scroll | 1 | 0 | 1 | 0 | 0 | 0 |
| C — Wikipedia, one per mode | 2 | 2 | 0 | 0 | 0 | 0 |
| C — GitHub auto-scroll | 1 | 1 | 0 | 0 | 0 | 0 |
| D — notice forcing, two attempts (second qualifies) | 2 | 2 | 0 | 0 | 0 | 0 |

The first Aurora forcing attempt never lost the page and did not satisfy the notice test; its saved image is RIGHT. It is retained and counted as an image, not as a successful notice check. Its input cleanup also failed procedurally, described below. The second attempt supplies D’s actual recovery/notice evidence.

**Every non-RIGHT run**

- **m74 / firefox-github-user-A-4: HONEST** — Declared loss; saved prefix matches the reference body. 2025 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-A-4/result.json), [event excerpt](m74/runs/firefox-github-user-A-4/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-A-4/tail-seam.png).
- **m74 / firefox-github-user-A-5: HONEST** — Declared loss; saved prefix matches the reference body. 1616 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-A-5/result.json), [event excerpt](m74/runs/firefox-github-user-A-5/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-A-5/tail-seam.png).
- **m74 / firefox-github-user-A-6: HONEST** — Declared loss after one recovery; saved prefix and unique table headings match. A repeated-table probe has a non-unique -1010 tie, resolved by the paired tail seam. 4717 / 45801 px; foundAgain 1. [Result](m74/runs/firefox-github-user-A-6/result.json), [event excerpt](m74/runs/firefox-github-user-A-6/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-A-6/tail-seam.png).
- **m74 / firefox-github-user-A-7: HONEST** — Declared loss; saved prefix matches the reference body. 2164 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-A-7/result.json), [event excerpt](m74/runs/firefox-github-user-A-7/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-A-7/tail-seam.png).
- **m74 / firefox-github-user-Afast-1: HONEST** — Declared loss; saved prefix matches the reference body. 2030 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-Afast-1/result.json), [event excerpt](m74/runs/firefox-github-user-Afast-1/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-Afast-1/tail-seam.png).
- **m74 / firefox-github-user-Afast-2: DAMAGED** — Written-white tail: image rows 9913–10480 (568 rows), within the final placed-frame extent; declared loss. 10481 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-Afast-2/result.json), [event excerpt](m74/runs/firefox-github-user-Afast-2/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-Afast-2/tail-seam.png).
- **m74 / firefox-github-user-Afast-3: HONEST** — Declared loss; saved prefix matches the reference body. 2204 / 45801 px; foundAgain 0. [Result](m74/runs/firefox-github-user-Afast-3/result.json), [event excerpt](m74/runs/firefox-github-user-Afast-3/helper-excerpt.log), [tail seam](m74/runs/firefox-github-user-Afast-3/tail-seam.png).
- **m74 / firefox-news-user-Bnews-1: HONEST** — Declared loss after the required reverse; saved body prefix matches; ad/video/cookie differences are PINNED. 1184 / 7554 px; foundAgain 0. [Result](m74/runs/firefox-news-user-Bnews-1/result.json), [event excerpt](m74/runs/firefox-news-user-Bnews-1/helper-excerpt.log), [tail seam](m74/runs/firefox-news-user-Bnews-1/tail-seam.png).
- **m74 / firefox-news-user-Bnews-2: HONEST** — Declared loss after the required reverse; saved body prefix matches; ad/video/cookie differences are PINNED. 1527 / 7530 px; foundAgain 0. [Result](m74/runs/firefox-news-user-Bnews-2/result.json), [event excerpt](m74/runs/firefox-news-user-Bnews-2/helper-excerpt.log), [tail seam](m74/runs/firefox-news-user-Bnews-2/tail-seam.png).
- **m74 / firefox-stackoverflow-user-Bso-2: HONEST** — Declared loss; saved body prefix matches; pinned ad/cookie fragments are separate. 4509 / 54218 px; foundAgain 0. [Result](m74/runs/firefox-stackoverflow-user-Bso-2/result.json), [event excerpt](m74/runs/firefox-stackoverflow-user-Bso-2/helper-excerpt.log), [tail seam](m74/runs/firefox-stackoverflow-user-Bso-2/tail-seam.png).
- **aurora-amd / chromium-github-user-Cchrome-1: HONEST** — Declared loss; body rows match after accounting for three 15-pixel native horizontal scrollbars omitted by the CDP full-page reference. 36333 / 44118 px; foundAgain 0. [Result](aurora-amd/runs/chromium-github-user-Cchrome-1/result.json), [event excerpt](aurora-amd/runs/chromium-github-user-Cchrome-1/helper-excerpt.log), [tail seam](aurora-amd/runs/chromium-github-user-Cchrome-1/tail-seam.png).

**DAMAGED — preserved full image**

[m74 / firefox-github-user-Afast-2](m74/runs/firefox-github-user-Afast-2/damaged.json): GitHub PR #1398, Firefox, you-scroll at faster pace, Cinnamon X11. Zero-based image rows **9913–10480 inclusive, 568 rows**, are written white where the reference has table content. This is the image tail, inside the final placed frame’s extent **9560–10480**, before tracking became lost. It is not a skipped page-position join between two accepted frames: the placements preceding it remain aligned. `unwritten.py` flags 5,155 black cells in 35 rows beginning at row 0 (the real black GitHub header); **zero black/unwritten tail cells** occur in the damaged band. These are white pixels, not the spool’s zero-initialized cells. Without raw frame dumps, whether the browser supplied unpainted pixels cannot be established.

Last placement: local `22:46:05.571`, source t=673797, position 9560. First skipped frame: `22:46:05.586`, t=673821. Lost: `22:46:05.671`, t=673864. `lost_track`, truncated true, endedLost true, foundAgain 0. [Full saved image](m74/runs/firefox-github-user-Afast-2/capture.png), [reference seam](m74/runs/firefox-github-user-Afast-2/tail-seam.png), [loss excerpt](m74/runs/firefox-github-user-Afast-2/loss-helper-excerpt.log). SHA-256 `ad22bab9fcc0dfc5323df7b95ae51833c95f54543a75c9e1c19f181e921462e1`. The original and reference remain on m74. Helper wall times are the builder’s local UTC−6 clock.

**CUTOUT — separate from row verdicts**

Five runs, five measured bounding areas of confirmed missing white content. Bounds are zero-based; X is half-open, row ranges below inclusive. Area is bounding width × height, not a claim that every pixel in the rectangle should contain ink. Each comparison shows current capture beside its reference and then the same location in the retained prior capture. All five are GitHub PR #1398 / Firefox 158.0 / you-scroll / m74 Cinnamon X11.

| Run | Image rows | X interval | Bounding size / area | Confirmed white missing-ink pixels | foundAgain / note |
|---|---|---|---|---:|---|
| [firefox-github-user-A-1](m74/runs/firefox-github-user-A-1/cutout.json) | 1932–1980 | 976–1207 | 231×49 / 11319 px | 5973 | 1 / found-again warning |
| [firefox-github-user-A-2](m74/runs/firefox-github-user-A-2/cutout.json) | 442–472 | 976–1168 | 192×31 / 5952 px | 1481 | 0 / none |
| [firefox-github-user-A-5](m74/runs/firefox-github-user-A-5/cutout.json) | 695–737 | 936–1196 | 260×43 / 11180 px | 1714 | 0 / lost-track note |
| [firefox-github-user-A-6](m74/runs/firefox-github-user-A-6/cutout.json) | 1104–1162 | 936–1207 | 271×59 / 15989 px | 14088 | 1 / lost + found-again warning |
| [firefox-github-user-A-8](m74/runs/firefox-github-user-A-8/cutout.json) | 1794–1849 | 936–1207 | 271×56 / 15176 px | 9578 | 1 / found-again warning |

For every CUTOUT, **hiddenCells and hiddenRows are absent/not reported**, not zero. The raw `unwritten.py` result, full note, missing-ink measurements and prior comparison counts are in each linked `cutout.json`. The detected black cells are real black page/header/image pixels; the CUTOUT areas themselves are written white. No result explicitly describes these white cutouts.

- [firefox-github-user-A-1: current / reference / prior crop](m74/runs/firefox-github-user-A-1/cutout-comparison.png). `unwritten.py`: firefox-github-user-A-1                   45800 rows  unwritten cells    5155  in    35 rows  first 0. Note: The capture lost the page once and found it again. Rows may be missing there: check the image..
- [firefox-github-user-A-2: current / reference / prior crop](m74/runs/firefox-github-user-A-2/cutout-comparison.png). `unwritten.py`: firefox-github-user-A-2                   45800 rows  unwritten cells    5155  in    35 rows  first 0. Note: none.
- [firefox-github-user-A-5: current / reference / prior crop](m74/runs/firefox-github-user-A-5/cutout-comparison.png). `unwritten.py`: firefox-github-user-A-5                    1616 rows  unwritten cells    2515  in    24 rows  first 0. Note: Finished while put.gd had lost its place. The image ends where it last found the page..
- [firefox-github-user-A-6: current / reference / prior crop](m74/runs/firefox-github-user-A-6/cutout-comparison.png). `unwritten.py`: firefox-github-user-A-6                    4717 rows  unwritten cells    5155  in    35 rows  first 0. Note: Finished while put.gd had lost its place. The image ends where it last found the page. The capture lost the page once and found it again. Rows may be missing there: check the image..
- [firefox-github-user-A-8: current / reference / prior crop](m74/runs/firefox-github-user-A-8/cutout-comparison.png). `unwritten.py`: firefox-github-user-A-8                   45800 rows  unwritten cells    5160  in    36 rows  first 0. Note: The capture lost the page once and found it again. Rows may be missing there: check the image..

**Prior check:** the retained `firefox-github-user-A1-3/capture.png` is the exact prior-record file: SHA-256 `2986ec87858480e380b0d8650fdc3a40a335957d17e8e792c9e8207df2341038`, verified against f19043f6b’s restore index. The corresponding content is intact at all five current CUTOUT locations in that one prior image. Thus the same cutouts are **not present in the prior image checked**; this single comparison cannot establish when they were introduced or prove that earlier builds never produced them. [Prior identity](m74/prior-comparison/identity.json).

**PINNED — independent list, not CUTOUT**

- m74 / `firefox-news-user-Bnews-1`: advertisement/video and full-width cookie banner. [Picture](m74/runs/firefox-news-user-Bnews-1/prefix-seam.png).
- m74 / `firefox-news-user-Bnews-2`: advertisement/video and cookie banner. [Saved-tail picture](m74/runs/firefox-news-user-Bnews-2/tail-seam.png).
- m74 / `firefox-stackoverflow-user-Bso-1`: pinned sidebar, ad and cookie fragments; body geometry +130/+180. [Picture](m74/runs/firefox-stackoverflow-user-Bso-1/tail-seam.png).
- m74 / `firefox-stackoverflow-user-Bso-2`: pinned ad/cookie area at saved tail. [Saved-tail picture](m74/runs/firefox-stackoverflow-user-Bso-2/tail-seam.png).
- aurora-amd / `firefox-wiki-user-D-forced-2`: pinned contents/appearance sidebar fragments after forced recovery. [Picture](aurora-amd/runs/firefox-wiki-user-D-forced-2/recovery-seam.png).

Stack Overflow run 1’s document height changes are measured in its scroll samples. Body probes are shift 0 before later advertisement geometry, +130 afterward, then +180; the paired footer seam retains the same body text. The final page is 54,065 px and the capture 53,884 px, including the one-pixel bottom inset and 180 px of dynamic ad-height change. These are preserved as dynamic document/pinned differences, as the prior round did.

Chrome’s late drift was investigated, rather than treated as either an error or a pass from height alone. The native image contains three horizontal scrollbars below wide tables; CDP’s full-page pictures omit their 15-pixel rows, giving cumulative 0/−15/−30/−45 probe offsets. [First boundary](aurora-amd/runs/chromium-github-user-Cchrome-1/first-drift-seam.png), [second](aurora-amd/runs/chromium-github-user-Cchrome-1/second-drift-seam.png), [third](aurora-amd/runs/chromium-github-user-Cchrome-1/third-drift-seam.png), [tail](aurora-amd/runs/chromium-github-user-Cchrome-1/tail-seam.png). Text occurs once across these boundaries. A fresh reference-only Chrome run with the measured 1905 px client width reproduced the same offsets; it rejected the width-reflow hypothesis. Both original references and the fresh version remain private with hashes in the restore index. No pixels from the capture were copied into a reference; no reference was warped to erase the differences. The original full-page reference remains authoritative, with the measured 6 px top / 2 px bottom native-origin transform retained from the previous method. The horizontal scrollbar difference is reference geometry, not a PINNED fragment or CUTOUT.

**Notices and pause checks**

Mint `A-1` and Aurora `D-forced-2` each have `foundAgain: 1` and exactly “The capture lost the page once and found it again. Rows may be missing there: check the image.” in captured `scroll.inspect`. Both show the desktop title **put.gd — check the scrolling capture**, and resident log summary **scroll_found_again**. The same note persists in History. [Mint inspect](m74/runs/firefox-github-user-A-1/scroll-inspect.json), [Mint notice](m74/runs/firefox-github-user-A-1/desktop-notice.png), [Mint History](m74/history-note.png), [Aurora inspect](aurora-amd/runs/firefox-wiki-user-D-forced-2/scroll-inspect.json), [Aurora notice](aurora-amd/runs/firefox-wiki-user-D-forced-2/desktop-notice.png), [Aurora History](aurora-amd/history-note.png). The notice event logs preserve the summary/title/text and History JSON preserves exact operation IDs. Mint’s first operation aged out of the 32-result live inspect cache before the later History check; its inspect JSON was already captured at completion, and persistent History was checked by the exact operation ID.

Pause sanity: **Mint 5/5 paused, 5/5 first-click stops; Aurora 5/5 paused, 5/5 first-click stops.** Mint has no post-hand injections. Aurora trial 1 logs one pointer `16,-26` after the first-motion marker, and no post-hand wheel event; this is retained, not silently called an injection-free pass. [Mint summary](m74/pause-summary.json), [Aurora summary](aurora-amd/pause-summary.json), [Aurora trial 1](aurora-amd/pause/pause-random-1.json), [trace](aurora-amd/pause/trial-random-1.log). The prior strict no-post-hand benchmark is not expanded here beyond the requested five sanity trials.

Frame rates: **m74 normal GitHub median 30.0 fps, range 29.8–30.0**, versus about 29.9 in the prior record: no observed overall reduction. All m74 cases are 29.6–30.0 fps, median 30.0. Aurora Firefox is 58.5–59.7 fps (including forcing attempts); Chrome is 24.9 fps. Per-run source rates and frame counts are below.

**Per-run metrics**

`trunc` = truncated, `lost` = endedLost, `again` = foundAgain; booleans are explicit. Document heights are before → after. Per-run result/inspect JSON retains full helper statistics, notes and operation IDs.

| Host / run | Verdict | Image / document before → after | End | trunc | lost | again | Placed | Skipped | fps |
|---|---|---|---|---|---|---:|---:|---:|---:|
| [m74/firefox-github-user-A-1](m74/runs/firefox-github-user-A-1/result.json) | RIGHT | 45800 / 45801 → 45801 | done | false | false | 1 | 490 | 16 | 30 |
| [m74/firefox-github-user-A-2](m74/runs/firefox-github-user-A-2/result.json) | RIGHT | 45800 / 45801 → 45801 | done | false | false | 0 | 489 | 0 | 30 |
| [m74/firefox-github-user-A-3](m74/runs/firefox-github-user-A-3/result.json) | RIGHT | 45800 / 45801 → 45801 | done | false | false | 0 | 520 | 0 | 30 |
| [m74/firefox-github-user-A-4](m74/runs/firefox-github-user-A-4/result.json) | HONEST | 2025 / 45801 → 45801 | lost_track | true | true | 0 | 8 | 1392 | 30 |
| [m74/firefox-github-user-A-5](m74/runs/firefox-github-user-A-5/result.json) | HONEST | 1616 / 45801 → 45801 | lost_track | true | true | 0 | 6 | 1513 | 30 |
| [m74/firefox-github-user-A-6](m74/runs/firefox-github-user-A-6/result.json) | HONEST | 4717 / 45801 → 45801 | lost_track | true | true | 1 | 20 | 1262 | 29.8 |
| [m74/firefox-github-user-A-7](m74/runs/firefox-github-user-A-7/result.json) | HONEST | 2164 / 45801 → 45801 | lost_track | true | true | 0 | 29 | 1373 | 30 |
| [m74/firefox-github-user-A-8](m74/runs/firefox-github-user-A-8/result.json) | RIGHT | 45800 / 45801 → 45801 | done | false | false | 1 | 543 | 2 | 30 |
| [m74/firefox-github-user-Afast-1](m74/runs/firefox-github-user-Afast-1/result.json) | HONEST | 2030 / 45801 → 45801 | lost_track | true | true | 0 | 5 | 219 | 30 |
| [m74/firefox-github-user-Afast-2](m74/runs/firefox-github-user-Afast-2/result.json) | DAMAGED | 10481 / 45801 → 45801 | lost_track | true | true | 0 | 27 | 198 | 29.9 |
| [m74/firefox-github-user-Afast-3](m74/runs/firefox-github-user-Afast-3/result.json) | HONEST | 2204 / 45801 → 45801 | lost_track | true | true | 0 | 5 | 219 | 30 |
| [m74/firefox-news-user-Bnews-1](m74/runs/firefox-news-user-Bnews-1/result.json) | HONEST | 1184 / 4156 → 7554 | lost_track | true | true | 0 | 4 | 390 | 29.9 |
| [m74/firefox-news-user-Bnews-2](m74/runs/firefox-news-user-Bnews-2/result.json) | HONEST | 1527 / 4156 → 7530 | lost_track | true | true | 0 | 12 | 399 | 29.6 |
| [m74/firefox-stackoverflow-user-Bso-1](m74/runs/firefox-stackoverflow-user-Bso-1/result.json) | RIGHT | 53884 / 53839 → 54065 | done | false | false | 0 | 570 | 0 | 30 |
| [m74/firefox-stackoverflow-user-Bso-2](m74/runs/firefox-stackoverflow-user-Bso-2/result.json) | HONEST | 4509 / 53992 → 54218 | lost_track | true | true | 0 | 50 | 1638 | 29.8 |
| [m74/firefox-wiki-auto-Bwiki-1](m74/runs/firefox-wiki-auto-Bwiki-1/result.json) | RIGHT | 24116 / 24117 → 24117 | end_of_content | false | false | 0 | 372 | 0 | 29.9 |
| [m74/firefox-wiki-user-Bwiki-1](m74/runs/firefox-wiki-user-Bwiki-1/result.json) | RIGHT | 24116 / 24117 → 24117 | done | false | false | 0 | 265 | 0 | 30 |
| [aurora-amd/chromium-github-user-Cchrome-1](aurora-amd/runs/chromium-github-user-Cchrome-1/result.json) | HONEST | 36333 / 44118 → 44118 | lost_track | true | true | 0 | 1008 | 193 | 24.9 |
| [aurora-amd/firefox-github-auto-Cauto-1](aurora-amd/runs/firefox-github-auto-Cauto-1/result.json) | RIGHT | 45796 / 45798 → 45798 | end_of_content | false | false | 0 | 2624 | 0 | 59.7 |
| [aurora-amd/firefox-github-user-Cff-1](aurora-amd/runs/firefox-github-user-Cff-1/result.json) | RIGHT | 45796 / 45798 → 45798 | done | false | false | 0 | 871 | 2 | 59.6 |
| [aurora-amd/firefox-github-user-Cff-2](aurora-amd/runs/firefox-github-user-Cff-2/result.json) | RIGHT | 45796 / 45798 → 45798 | done | false | false | 0 | 753 | 0 | 59.7 |
| [aurora-amd/firefox-github-user-Cff-3](aurora-amd/runs/firefox-github-user-Cff-3/result.json) | RIGHT | 45796 / 45798 → 45798 | done | false | false | 0 | 845 | 1 | 59.4 |
| [aurora-amd/firefox-wiki-auto-Cwiki-1](aurora-amd/runs/firefox-wiki-auto-Cwiki-1/result.json) | RIGHT | 24092 / 24094 → 24094 | end_of_content | false | false | 0 | 1403 | 0 | 59.6 |
| [aurora-amd/firefox-wiki-user-Cwiki-1](aurora-amd/runs/firefox-wiki-user-Cwiki-1/result.json) | RIGHT | 24092 / 24094 → 24094 | done | false | false | 0 | 445 | 0 | 59.7 |
| [aurora-amd/firefox-wiki-user-D-forced](aurora-amd/runs/firefox-wiki-user-D-forced/result.json) | RIGHT | 24092 / 24094 → 24094 | done | false | false | 0 | 136 | 0 | 58.5 |
| [aurora-amd/firefox-wiki-user-D-forced-2](aurora-amd/runs/firefox-wiki-user-D-forced-2/result.json) | RIGHT | 1541 / 24094 → 24094 | done | false | false | 1 | 2 | 850 | 59.4 |

**Harness failures and limits**

- The first second-Stack-Overflow setup failed before capture because a dynamically defined Python function no longer had inspectable source. Its error and batch log are retained; the same missing case was run once from a fresh harness process. No product fix.
- The first Aurora notice-forcing attempt followed all the way to the page end, so it did not qualify for D. **Its queued wheel input outlived the browser-close call and the five-second input-helper wait timed out. This did not meet the intended browser-only input confinement.** The helper PID was 2897292; a later exact-PID stop found it had already exited. Precise post-close wheel-event counts were not logged, so outside-window delivery cannot be excluded. The desktop outside the owned browser was empty. This procedural failure is preserved in `force-notice.log`; the saved image is separately RIGHT. The successful retry explicitly passed fast timing through sudo, disabled smooth scroll in its isolated browser, produced loss/recovery, and its input helper exited cleanly.
- Some workstation SSH command wrappers returned status 143 while the remote controller was still finishing. Completion was verified from the exact saved operation JSON, helper end trace, per-trial files and cleanup/process checks. No incomplete trial was counted as a pass.
- A reference-only helper’s first attempt had a Python syntax error before any browser opened; its log is retained and the corrected script collected the reference. The cutout-analysis helper also needed a NumPy integer serialization correction; it did not run product code or alter images.
- No row error was repaired, and no reference pixels were synthesized to make a capture pass. CUTOUT, PINNED, DAMAGED and original failed attempts remain separately inspectable.

**Retention and final state.** All original captures, browser references, full helper traces, failed attempts and source harnesses remain on their respective builders under `~/work/sfr2`; [Mint restore index](m74/restore-index.json) and [Aurora restore index](aurora-amd/restore-index.json) give canonical paths, hashes and sizes. No capture/source evidence was deleted. The DAMAGED full PNG is also published here. Passing/other raw images are represented by hashes plus comparison pictures. Original prior evidence was read, never changed. No golden, guest or user objects were touched.

Both desktops were left on their unlocked native wallpaper with owned windows closed, owned product/browser/helper/input processes stopped, temporary extracted AppImage runtime files removed, and mouse settings restored exactly. [Mint cleanup](m74/cleanup-receipt.json), [picture](m74/cleanup-desktop.png), [Aurora cleanup](aurora-amd/cleanup-receipt.json), [picture](aurora-amd/cleanup-desktop.png), [post-reference picture](aurora-amd/cleanup-reference-desktop.png). Pre-existing shared SSH PIDs 313646/313651 on Mint and 4102 on Aurora were preserved. Both locks are released, including the short Chrome reference lease: [Mint release](m74-lock-release.txt), [Aurora release](aurora-amd-lock-release.txt), [reference release](aurora-amd-reference-lock-release.txt), [final lock state](final-lock-status.txt). No desktop/compositor/package update, logout, session switch, wall change or workstation input occurred.
