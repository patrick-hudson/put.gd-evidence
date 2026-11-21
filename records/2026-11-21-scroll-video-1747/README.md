# Live scrolling capture with playing video on Aurora and Mint

**Desktop acceptance failed for PR #1747.** The candidate improved synthetic video compositing. The live Chrome for Developers article still stalled on both desktops in Chrome and Firefox. The Chrome first-viewport fixture also lost the last rows on the candidate, with the same failure on the Mint repeat. The MDN no-video controls showed no candidate regression.

This test covers issue #1537. The comparison uses packages produced by GitHub Actions and the latest nightly available when testing began at 03:15 UTC on November 21, 2026. Each tested resident reported its build through the production CLI. The runner queried the executable of the active recording helper for its own build metadata and copied it into the helper log.

| Build | Version | Commit | Tree |
|---|---|---|---|
| Candidate | `26.1121.5925-dev+g2b7e0b9c6df5` | `2b7e0b9c6df548021d93b41c5201267203dea51f` | `351efecd55b9c5a916d8352b322866ad3a0d99af` |
| Nightly | `26.1120.5875-nightly` | `779e2517303d8fcb08aca99840589e728d9b98ff` | `ab290cfe3e1171e07b1e82343822043638242e27` |

[Candidate CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44860051895) · [Published nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1120.5875-nightly) · [Results table](results.md)

The physical Aurora builder ran Plasma 6.8.2 on Wayland and used the mounted AppImage. The physical Linux Mint 22.3 builder ran Cinnamon 6.6.9 on X11 with Qt 6.4.2 and used the Ubuntu 24.04 DEB. Chrome for Testing 157.0.8103.78 ran on both desktops. Aurora used Firefox 160 and Mint used Firefox 158. Each case started with a fresh browser profile. A relative uinput wheel on Aurora and XTest wheel on Mint sent one notch about every 0.53 to 0.82 seconds. The local output destination was a private test archive. The auto-scroll rows sent input only to the test browser. The operator finished the capture after the browser reached the bottom.

- A-later places a 432 × 264 looping WebM below the first viewport of a 700-pixel article and inside a 704-pixel capture region. A-first puts the same video in the first viewport. The fixture includes a sticky header, fixed cookie notice, text and static maps. The main video used FFmpeg testsrc2 with a rotating crop. The pilot used unmodified testsrc2.
- B-aj uses the Al Jazeera article from issue #1537. B-chrome uses a Chrome for Developers article with real embedded MP4 videos. The B-wiki and B-mdn trials explored alternative pages. The per-row trace records visible media geometry and decoded-frame counts. [Al Jazeera](https://www.aljazeera.com/news/2026/11/14/un-says-25-seafarers-killed-in-around-hormuz-since-february) · [Chrome for Developers](https://developer.chrome.com/blog/scroll-animation-performance-case-study/)
- C uses MDN's z-index article with site navigation visible and no playing video. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/z-index)

The helper's frame trace gives tracker transitions and skip reasons. Its final capture status gives height, elapsed time, and total skipped frames. The browser's full-page screenshot is taken after capture. Each evaluation records page height before and after the reference, the fitted small translation and local offsets of mismatched bands. The static score masks detected pinned UI and playing video, then allows a one-pixel neighborhood when comparing colors. It counts 64-pixel bands with at most 1.5% mismatched pixels. Browser rendering and late layout changes can reduce this number. The images and vertical offset measurements show where that happened. A synthetic video crop can also be compared with all 288 decoded WebM frames.

The first Aurora Chrome Al Jazeera attempt included a notification from an earlier acceptance row. Its pictures are retained and it was repeated after dismissing the prior notice. Setup attempts that failed browser calibration or navigation are retained with their own run IDs.

The five static synthetic map anchors give a second check on vertical placement where browser screenshot antialiasing lowers the strict band score. Each synthetic run records these offsets in its map-alignment result. The source fixture is included. [Fixture](fixture/) · [Exact package hashes](packages.json) · [Other attempts](attempts.md)

## Aurora observations

- The candidate preserved one coherent source frame in both synthetic placements in Chrome and Firefox and in the Chrome auto-scroll run. Nightly stitched strips from different frames. The maps line up in both builds. The synthetic page did not reproduce a prolonged nightly stall.
- The candidate's first Chrome A-first capture lost the final 83 pixels after the video was far above the viewport. The exact-build repeat captured all 6,374 pixels with zero skips. Both outcomes are in the record.
- The clean Al Jazeera Chrome pair stalled after a browser layout change. As the inline video started, the page grew by hundreds of pixels and the browser reported a large jump in scroll position. Both builds returned a short capture. The Firefox candidate followed the page to its full height, although the first inline player's image has visible seams. [First inline player](aurora-amd/candidate-firefox-B-aj-user/first-inline-player.png)
- The Chrome for Developers article kept a stable document height. Both builds stalled in both browsers while the video was playing. The helper logged mostly `no_match`. The original issue reported a contradiction-heavy trace.
- Neither browser showed a candidate regression on the MDN no-video control. Both Chrome runs returned 6,104 rows and zero skips. Both Firefox runs had zero skips. The candidate returned 6,143 of 6,143 rows and nightly returned 6,135 of 6,143.

## Mint observations

- The synthetic later-video cases and Firefox first-viewport case reached the full page. The candidate kept a coherent video frame. Nightly finished the synthetic article and tore the video into strips.
- Candidate Chrome lost the end of the first-viewport fixture twice, after the video had scrolled out of view. Each candidate image had 6,297 of 6,374 rows. Nightly's Chrome image had all 6,374 rows.
- Both builds stopped early on both live sites in both browser families. On Al Jazeera, the Mint Chrome pair stopped at 2,697 rows and the Firefox pair at 2,539 rows. On the Chrome for Developers page, the candidate captured more rows and still stalled while the document height stayed constant. The first video in the candidate Firefox capture has visible seams. [First clip](m74/candidate-firefox-B-chrome-user/first-inline-player.png)
- Each build captured 6,104 rows on Chrome and 6,128 rows on Firefox in the MDN control, with zero skipped frames. Both candidate auto-scroll runs, one per desktop, reached the full synthetic page and kept a coherent video frame.

The two desktop leases were released after cleanup. Mint's test installation was purged. The host-side scratch directories were removed after the transferred archives matched their SHA-256 receipts.
