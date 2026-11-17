# Scrolling capture re-check — 2026-11-17

The short re-check found one silently wrong image on physical Cinnamon X11: **A1 run 3 triggers the owner’s stop rule**. Aurora also fails one of ten no-post-hand-injection trials, although every first click stopped capture. This is the requested two-desktop re-check, not a new acceptance matrix. Product code, PR comments and merges were untouched. All capture/input ran on the builders, against windows opened by this worker; no guests, local product builds, native package installs, uploads or copied links were used.

Branch head: `f1a178aae9f29aa740893067768c207baec18cbe` (original tree `2d55d814bae57949b39304544d1ecc4ae949f1f9`). CI 43992585364 actually packaged merge commit `4dc11b6622350785c55f7719fc1bee93d06329c1`, tree `671181cbe38717da9a5a50da76effbef1dd87db8`, merging the head into nightly `4d4a6d97aac406f6859b1eac77219afe20e52750`. The coordinator explicitly authorized that merge tree. Diagnostics on **each** desktop prove it; both used AppImage SHA-256 `d141da5c796a6db44310092b5a733dc13516f5f53b8afd8b7fccd4b693cfb869`. CI completed successfully, including its required `CI` summary. See each host’s cold-start and host proofs. Physical profiles were Linux Mint 22.3 / Cinnamon 6.6.9 / Muffin 6.6.3 on X11 (Firefox 158.0), and Aurora Fedora 45 / Plasma 6.8.2 / KWin 6.8.2 on Wayland (Firefox 160.0; Chrome for Testing 157.0.8103.78).

| Case | RIGHT | HONEST | WRONG |
|---|---:|---:|---:|
| A1 Mint Firefox GitHub ×5 | 3 | 1 | 1 |
| A2 Mint Firefox Stack Overflow ×2 | 1 | 1 | 0 |
| A3 Mint blank gap ×3 | 0 | 3 | 0 |
| A4 Mint news + reverse ×2 | 0 | 2 | 0 |
| A5 Mint Wikipedia manual + auto | 2 | 0 | 0 |
| B1 Aurora Firefox GitHub ×5 | 5 | 0 | 0 |
| B2 Aurora news + reverse ×2 | 2 | 0 | 0 |
| B3 Aurora Wikipedia manual + auto | 2 | 0 | 0 |
| B4 Aurora auto: Chrome Python + Firefox GitHub | 1 | 1 | 0 |
| B5 Aurora blank gap | 0 | 1 | 0 |

| Control case | Passed | Observation |
|---|---:|---|
| A6 inside bar | 3/3 | Each centre click acts first time; no bar pixels |
| A7 Mint mouse pause | 10/10 | 10 first-click stops; zero post-hand injections |
| B6 Aurora mouse pause | 9/10 | 10 first-click stops; try 2 sends pointer + wheel after hand |

A6 is a control check: all three inside-bar centre clicks (Auto-scroll, Done, Cancel) acted first time; neither saved image contained capture-bar pixels, and Cancel admitted no image. Pause results are listed below separately from whole-page image verdicts.

**The WRONG run.** Mint `firefox-github-user-A1-3`, operation `bc304615-06d6-4570-b2fd-e5aeaab9d5f4`, loses 1,010 image rows at a join near image row 4,799. The document remained 45,801 px tall; the saved image is 44,790 px, with probes changing from shift 0 to +1,010. At Done the browser had been at its real end (`scrollY 44879`, viewport 922) for several samples while the bar activity remained Following. It ended `done`, `endedLost: false`, `truncated: false`, without a loss note. The accepted false recovery is:

```text
2026-11-16T19:25:52.716 scroll track: t=660908 placed offset 498 position 4376 added 0/498 confidence 0.80 hint none state following recovered
```

[Side-by-side seam](m74/runs/firefox-github-user-A1-3/seam-overview.png), [wide probes](m74/runs/firefox-github-user-A1-3/where.log), [join probes](m74/runs/firefox-github-user-A1-3/join-where.log), [helper excerpt](m74/runs/firefox-github-user-A1-3/join-helper-excerpt.log), [result](m74/runs/firefox-github-user-A1-3/result.json). Raw images and full helper trace remain on m74; its restore index gives exact paths and hashes. Helper timestamps retain the builder’s local clock.

Blank cases crossed the measured 2,600 px gap to the actual page end. Every qualified blank run stayed Lost afterward, recovered 0 times, and ended `lost_track` with the explicit loss note. Text probes in each saved prefix match at shift 0; the final featureless white bands do not have a unique reference location. Native past-gap pictures and matching-prefix seams are retained.

On Mint, both news runs were Lost before the six-notch reverse, reported Following again afterward, then became Lost again on onward scrolling; each recovered once and finished honestly lost. On Aurora, news run 1 stayed Following through the reverse; run 2 lost/recovered before the reverse and stayed Following through it and onward. Body-text probes and seam inspection found no wrong body join. Playing/pinned videos, ads and cookie-bar fragments remain the known pinned-content limitation (#1538). A weak Aurora band at row 3300/3350 crosses the ad label/video boundary and picks a 1 px offset; adjacent paragraph probes align at 0, and the native seam shows no missing/repeated text. All original probes are retained rather than silently discarded.

Mint Stack Overflow run 1 has a later 130 px advertisement inserted near reference row 12,970. The geometry samples record that +130 change at scrollY 12,972; body probes are 0 before it and a constant +130 after it. Visual comparison showed the added advertisement, with body content preserved. Run 2 explicitly lost the page; every saved-prefix probe matches at 0.

Python currently redirects to `/3/builtins/stdtypes.html` (Python 3.15.2), measured at 110,440 px. Its correct 60,000 px prefix ended `height_cap`, `truncated: true`, with “Stopped at 60,000 px. The page continues below.” Per the coordinator’s explicit clarification, this is **HONEST (height cap)**. All 25 probes through row 59,800 align at 0 and the earlier acceptance’s unwritten-cell checker reports **0 cells in 0 rows**. The native Chrome image is visibly dark.

Native magenta calibration was used without weakening its coverage check. Mint’s selected content is 1 px shorter than Firefox’s reported viewport; Aurora Firefox is 2 px shorter. These fixed bottom-edge exclusions are shown in the per-run viewport metadata and height columns; text rows remain aligned. Chrome’s measured origin is 6 px below its browser report, with a further 2 px bottom inset: its browser-owned reference is explicitly cropped by that measured transform (the full original remains private), as in the earlier corrected acceptance.

**Per-run image results.** Capture seconds come from the helper’s `elapsedMs`; wall seconds include control/finishing overhead when recorded. Blank wrappers recorded only helper duration, so their wall-time column is blank. JSON retains operation IDs, flags, notes, source frame totals and original geometry.

| Host / run | Verdict | End | Image / doc before → after | Placed / skipped | Recovered | Source fps | Capture s | Wall s |
|---|---|---|---|---:|---:|---:|---:|---:|
| [m74 / A3-1](m74/runs/A3-1/result.json) | HONEST | lost_track | 3776 / 9217 → 9217 | 17 / 213 | 0 | 30 | 10.167 | — |
| [m74 / A3-2](m74/runs/A3-2/result.json) | HONEST | lost_track | 3771 / 9217 → 9217 | 17 / 215 | 0 | 30 | 10.230 | — |
| [m74 / A3-3](m74/runs/A3-3/result.json) | HONEST | lost_track | 3799 / 9217 → 9217 | 17 / 213 | 0 | 30 | 10.165 | — |
| [m74 / firefox-github-user-A1-1](m74/runs/firefox-github-user-A1-1/result.json) | RIGHT | done | 45800 / 45801 → 45801 | 543 / 1 | 1 | 29.9 | 54.668 | 60.17 |
| [m74 / firefox-github-user-A1-2](m74/runs/firefox-github-user-A1-2/result.json) | RIGHT | done | 45800 / 45801 → 45801 | 465 / 1 | 1 | 29.9 | 49.352 | 54.67 |
| [m74 / firefox-github-user-A1-3](m74/runs/firefox-github-user-A1-3/result.json) | WRONG | done | 44790 / 45801 → 45801 | 473 / 51 | 2 | 29.9 | 48.743 | 54.30 |
| [m74 / firefox-github-user-A1-4](m74/runs/firefox-github-user-A1-4/result.json) | HONEST | lost_track | 1710 / 45801 → 45801 | 7 / 1446 | 0 | 30 | 49.553 | 50.87 |
| [m74 / firefox-github-user-A1-5](m74/runs/firefox-github-user-A1-5/result.json) | RIGHT | done | 45800 / 45801 → 45801 | 517 / 18 | 1 | 30 | 52.530 | 57.91 |
| [m74 / firefox-news-user-A4-1](m74/runs/firefox-news-user-A4-1/result.json) | HONEST | lost_track | 3098 / 4156 → 7533 | 33 / 287 | 1 | 28 | 15.837 | 17.48 |
| [m74 / firefox-news-user-A4-2](m74/runs/firefox-news-user-A4-2/result.json) | HONEST | lost_track | 4698 / 4156 → 7531 | 53 / 278 | 1 | 29.8 | 17.279 | 19.18 |
| [m74 / firefox-stackoverflow-user-A2-1](m74/runs/firefox-stackoverflow-user-A2-1/result.json) | RIGHT | done | 52757 / 52713 → 52888 | 579 / 0 | 0 | 29.9 | 65.082 | 72.43 |
| [m74 / firefox-stackoverflow-user-A2-2](m74/runs/firefox-stackoverflow-user-A2-2/result.json) | HONEST | lost_track | 36048 / 52565 → 52565 | 347 / 627 | 0 | 29.9 | 54.716 | 59.74 |
| [m74 / firefox-wiki-auto-A5-1](m74/runs/firefox-wiki-auto-A5-1/result.json) | RIGHT | end_of_content | 24116 / 24117 → 24117 | 374 / 0 | 0 | 30 | 44.765 | 49.48 |
| [m74 / firefox-wiki-user-A5-1](m74/runs/firefox-wiki-user-A5-1/result.json) | RIGHT | done | 24116 / 24117 → 24117 | 224 / 0 | 0 | 30 | 25.929 | 30.72 |
| [aurora-amd / B5-1](aurora-amd/runs/B5-1/result.json) | HONEST | lost_track | 3946 / 9217 → 9217 | 26 / 220 | 0 | 38.9 | 9.197 | — |
| [aurora-amd / chromium-python-auto-B4-1](aurora-amd/runs/chromium-python-auto-B4-1/result.json) | HONEST | height_cap | 60000 / 110440 → 110440 | 3585 / 0 | 0 | 31.6 | 135.681 | 138.09 |
| [aurora-amd / firefox-github-auto-B4-1](aurora-amd/runs/firefox-github-auto-B4-1/result.json) | RIGHT | end_of_content | 45796 / 45798 → 45798 | 2619 / 0 | 0 | 59.7 | 122.829 | 124.69 |
| [aurora-amd / firefox-github-user-B1-1](aurora-amd/runs/firefox-github-user-B1-1/result.json) | RIGHT | done | 45796 / 45798 → 45798 | 888 / 1 | 1 | 59.5 | 50.117 | 51.95 |
| [aurora-amd / firefox-github-user-B1-2](aurora-amd/runs/firefox-github-user-B1-2/result.json) | RIGHT | done | 45796 / 45798 → 45798 | 855 / 1 | 1 | 59.3 | 48.416 | 50.68 |
| [aurora-amd / firefox-github-user-B1-3](aurora-amd/runs/firefox-github-user-B1-3/result.json) | RIGHT | done | 45796 / 45798 → 45798 | 824 / 0 | 0 | 59.5 | 47.115 | 49.37 |
| [aurora-amd / firefox-github-user-B1-4](aurora-amd/runs/firefox-github-user-B1-4/result.json) | RIGHT | done | 45796 / 45798 → 45798 | 804 / 0 | 0 | 59.7 | 47.097 | 49.37 |
| [aurora-amd / firefox-github-user-B1-5](aurora-amd/runs/firefox-github-user-B1-5/result.json) | RIGHT | done | 45796 / 45798 → 45798 | 848 / 0 | 0 | 59.7 | 48.546 | 50.80 |
| [aurora-amd / firefox-news-user-B2-1](aurora-amd/runs/firefox-news-user-B2-1/result.json) | RIGHT | done | 7511 / 4153 → 7513 | 197 / 0 | 0 | 59.8 | 15.147 | 16.54 |
| [aurora-amd / firefox-news-user-B2-2](aurora-amd/runs/firefox-news-user-B2-2/result.json) | RIGHT | done | 7526 / 4153 → 7528 | 137 / 31 | 1 | 59.6 | 13.380 | 14.70 |
| [aurora-amd / firefox-wiki-auto-B3-1](aurora-amd/runs/firefox-wiki-auto-B3-1/result.json) | RIGHT | end_of_content | 24092 / 24094 → 24094 | 1405 / 0 | 0 | 59.6 | 65.029 | 66.84 |
| [aurora-amd / firefox-wiki-user-B3-1](aurora-amd/runs/firefox-wiki-user-B3-1/result.json) | RIGHT | done | 24092 / 24094 → 24094 | 468 / 0 | 0 | 59.8 | 27.563 | 29.61 |

**Pause trials.** Each used a random 1–6 s start and relative input at 600 px/s. The independent cursor was sampled after the first nonzero hand motion. Pass requires the first click to stop and no post-hand injection (or the specifically permitted same-instant correction). Mint is **10/10**; Aurora is **9/10** on that strict gate, with **10/10 first-click stops on each**. Aurora random try 2 (`311888a0-6a0e-415f-8c61-8afdd45029e1`) logs a pointer move and a wheel event after the first-motion marker, about 5 ms later at 1 ms log resolution: `2026-11-16T20:17:08.967 scroll inject: t=208222 pointer 48,48 sent` and `... t=208222 wheel 1 sent`. The pause line is at the same `t=208222`; this is not the permitted single same-instant put-back. Its full trace, excerpt, capture JSON and raw image are retained.

| Host / trial | First click stopped | Post-hand inject lines | Placed / skipped | Recovered | Source fps | Capture s | End |
|---|---|---:|---:|---:|---:|---:|---|
| [m74 / random-1](m74/pause/pause-random-1.json) | True | 0 | 15 / 0 | 0 | 29.2 | 2.380 | done |
| [m74 / random-2](m74/pause/pause-random-2.json) | True | 0 | 45 / 0 | 0 | 29.8 | 5.643 | done |
| [m74 / random-3](m74/pause/pause-random-3.json) | True | 0 | 28 / 0 | 0 | 29.5 | 3.693 | done |
| [m74 / random-4](m74/pause/pause-random-4.json) | True | 0 | 13 / 0 | 0 | 29.2 | 2.275 | done |
| [m74 / random-5](m74/pause/pause-random-5.json) | True | 0 | 59 / 0 | 0 | 29.7 | 6.871 | done |
| [m74 / random-6](m74/pause/pause-random-6.json) | True | 0 | 58 / 0 | 0 | 29.7 | 6.786 | done |
| [m74 / random-7](m74/pause/pause-random-7.json) | True | 0 | 27 / 0 | 0 | 29.4 | 3.449 | done |
| [m74 / random-8](m74/pause/pause-random-8.json) | True | 0 | 30 / 0 | 0 | 29.5 | 3.780 | done |
| [m74 / random-9](m74/pause/pause-random-9.json) | True | 0 | 56 / 0 | 0 | 29.9 | 6.902 | done |
| [m74 / random-10](m74/pause/pause-random-10.json) | True | 0 | 32 / 0 | 0 | 29.6 | 4.484 | done |
| [aurora-amd / random-1](aurora-amd/pause/pause-random-1.json) | True | 0 | 37 / 0 | 0 | 59.6 | 2.714 | done |
| [aurora-amd / random-2](aurora-amd/pause/pause-random-2.json) | True | 2 | 50 / 0 | 0 | 58.9 | 2.864 | done |
| [aurora-amd / random-3](aurora-amd/pause/pause-random-3.json) | True | 0 | 36 / 0 | 0 | 59.7 | 2.810 | done |
| [aurora-amd / random-4](aurora-amd/pause/pause-random-4.json) | True | 0 | 90 / 0 | 0 | 59.8 | 5.397 | done |
| [aurora-amd / random-5](aurora-amd/pause/pause-random-5.json) | True | 0 | 85 / 0 | 0 | 59.8 | 4.848 | done |
| [aurora-amd / random-6](aurora-amd/pause/pause-random-6.json) | True | 0 | 126 / 0 | 0 | 59.2 | 6.313 | done |
| [aurora-amd / random-7](aurora-amd/pause/pause-random-7.json) | True | 0 | 95 / 0 | 0 | 59.6 | 5.232 | done |
| [aurora-amd / random-8](aurora-amd/pause/pause-random-8.json) | True | 0 | 121 / 0 | 0 | 59.9 | 6.447 | done |
| [aurora-amd / random-9](aurora-amd/pause/pause-random-9.json) | True | 0 | 38 / 0 | 0 | 59.5 | 2.314 | done |
| [aurora-amd / random-10](aurora-amd/pause/pause-random-10.json) | True | 0 | 40 / 0 | 0 | 58 | 2.714 | done |

**Inside-bar controls (A6).** All three clicks used the actual visible bar’s measured centre; there was no upper-edge fallback or second click.

| Button | First click | End | Placed / skipped | Recovered | Source fps | Capture s |
|---|---|---|---:|---:|---:|---:|
| autoScroll | True | done | 6 / 0 | 0 | 29.4 | 3.961 |
| done | True | done | 1 / 0 | 0 | 29.5 | 2.853 |
| cancel | True | cancelled | 0 / 0 | 0 | 29.9 | 3.019 |

Cancel’s final helper statistics are Discarded / 0 placed / 0 skipped; immediately before the real click the live inspect showed 1 placed / 0 skipped. No image was admitted. The helper log is retained for those final cancellation statistics.

**Harness attempts and corrections.** A first Mint launch raced the still-running SCP and stopped with “Text file busy”; nothing launched, and the completed transfer was hash-verified before retry. A stale Mint 0-byte disk warning (actual free space 89 GiB) overlapped the first preliminary GitHub attempt; it was dismissed and that attempt preserved outside the qualified five. The initial 100 MP profile allowance capped Stack Overflow at 52,083 px; it was increased to 120 MP while keeping the existing 60,000 px scrolling limit, and the qualified two runs were repeated. A Cloudflare “Just a moment” page was not counted as the question; the successful earlier lab browser profile was reused for the retry.

The Mint blank script initially copied the previous archive PNG because admission follows the stop reply. Those wrong copies and preliminary analyses are preserved as `artifact-copy-attempt1*`; each final capture was recovered by the exact SHA-256 returned by its operation, without rerunning capture. Only the corrected `where.log` is authoritative. The Aurora blank script waits for the exact admitted hash. Aurora’s first GitHub-auto and blank/pause setup attempts were blocked before capture by the persistent owned height-cap notification and a stale browser profile. Sources/logs were preserved; the notification was visibly identified and closed at its own close button, and fresh-profile handling was corrected. Calibration’s 98% coverage threshold was unchanged. No case consumed 30 minutes of harness repair and no requested case was dropped.

**Retention and cleanup.** Every WRONG run retains all raw files on its builder; every HONEST run also retains its original pictures. RIGHT-run PNGs were deleted by exact owned-file manifests only after hashes/results were exported and verified. Host restore indexes and deletion receipts record what remains and what was deliberately removed; sources and failed attempts were preserved. No frame dumps were recorded. Both extracted AppImages were removed by their file lists, original mouse settings restored, all owned product/helper/browser/input processes stopped, and both locks released with verified-clean. Final native cleanup pictures and host checks are included. Pre-existing shared SSH processes (Mint 313646/313651 and Aurora 4102) were preserved.
