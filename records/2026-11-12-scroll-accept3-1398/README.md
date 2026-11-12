BLOCKED / INCOMPLETE — one false completion on Mint, omitted late headers, and live-page comparisons that do not establish full acceptance.

# Independent scroll-capture acceptance, round 3

Tested PR #1398 head `dbe04eedc3878c45d2cfa8b72c0587188b396deb`, issue #1376, using CI run `43202012192`. The head was unchanged at the start and on subsequent checks. No product code was changed and nothing was compiled on a host. Native CI DEBs/RPM were installed on the three physical desktops; the CI AppImage was used in four fresh guests. This is a blocking test report, not authorization to merge.

The installed runtime identifies itself as `26.1112.4716-dev+g0311647141ff`. The artifact is the CI merge `0311647141ff59a02edfb61518fa31080aad4b6d`, whose second parent is the requested head. `SOURCE.json`, `merge-identity.json`, `artifact-sha256.json`, and `download-container-sha256.json` record the identity and download checks. The Ubuntu DEB is `6ebe37cd7aa5e27d50b31d1d5db15b468135bf381fb710471dc2fd90910181d0`; Debian DEB `4c6119b03d34de56c6fc9b597801ef55b3c44604a4eb5f9093e1043e568928c3`; Fedora RPM `3d24eb2bdd612a45e7098905190105ce644df6e67525c392a8d01f8d79dbee38`; AppImage `b02c0cddb348a22b24b9037e96caaca1ca1a28be111b6f2f953cdabd8265b1d8`. ZIP digests and extracted members were independently rechecked. Distro dependencies and browsers were installed by APT/DNF/pacman, with transaction/version records; there is no separate SHA ledger for each package-manager download.

**Section A.** Columns identify native Mint/Cinnamon X11 (m74), Fedora GNOME Wayland (f44), Debian Plasma Wayland (d69), Omarchy/Hyprland, Fedora 45 Budgie/labwc, neon/KWin 6.8, and Kubuntu 26.04/KWin 6.6. `E` = image and requested end verified by the stated fixture oracle; `H` = honest partial/stop with a verified prefix; `F` = failed requested result; `X` = non-exact admitted pixels; `—` = not requested on that desktop. Counts are actual repeats. `E` on legacy fixtures is the retained barcode/text oracle, not a claim that every antialiased label pixel was compared. New generators use every RGB pixel. `O` means the legacy text-band oracle passed but independent glyph-order validation is incomplete.

| Requested row | Mint | GNOME | Plasma | Hyprland | Budgie | neon | Kubuntu |
|---|---|---|---|---|---|---|---|
| 1. 24,000 px ruler from end | 3 E | 3 E | 3 E | 3 E | 3 E | 3 E | 3 E |
| 2. Qt wide ×1 / narrow ×2; GTK ×2 | O 1/2/2 | O 1/2/2 | O 1/2/2 | O 1/2/2 | O 1/2/2 | O 1/2/2¹ | O 1/2/2 |
| 3. Browser end ×2 / top ×1 | E 2/1 | E 2/1 | E 2/1 | E 2/1 | E 2/1 | E 2/1 | 1 E + 1 H² / 1 E |
| 4. Halfway, top off | E | E | E | E | E | E | E |
| 5. Stop on way up | H | H | H | H | H | H | H |
| 6. 2,000 cap, warning, identical loopback PNG | E | E | E | E | E | E | E |
| 7. Immediate next; upload slot held busy | E / E | E / E | E / E | E / E | E / E | E / E | E / E |
| 8. Official-SDK MCP, fetched PNG | E | E | E | E | E | E | E |
| 9. Hotkey + selector drag, once | E | E | E | — | — | — | — |
| 10. Seven browser variants ×2 | 14 E | 14 E | 14 E (retry) | — | 14 E | 13 E + 1 F³ | — |
| 11. Committed resize ×4; timer resize | 4 H / E | 4 H / E | 4 H / E | 4 H / H600 | 4 H / H600 | 4 H / E | 4 H / E |
| 12. Pointer switch ×2; cancel races; next capture | E | E | E | E | E | E | E |
| 13. Own notices, 0/100/300 ms | E / E / E | E / E / E | E / E / E | E / E / E | E / E / E | E / E / E | E / E / E |
| 14. Own-pace minimap ×2 | 2 H600 | 2 H600 | 2 H600 | — | 2 H600 | 2 H600 | — |
| 15a. Near-identical rows ×2 | 2 X tail | 2 E | 2 E | — | 2 E | — | — |
| 15b. Equal-brightness blocks ×2 | 2 H600 + X tail | 2 H600 | 2 H600 | — | 2 H600 | — | — |
| 15c. Repeating 138 px blocks ×2 | 2 H600 + X tail | 2 H600 | 2 H600 | — | 2 H600 | — | — |
| 15d. Fixed counter ×2; non-fixed ×2 | 2 X; 1 full X + 1 false completion | 2 E; 2 E | 2 E; 2 E | — | 2 E; 2 H time limit⁴ | — | — |
| 15e. Late bars ×2, with stronger ruler follow-up ×2 | F header omitted | F header omitted | F header omitted | — | F header omitted | — | — |
| 15f. 40% centre, static side columns ×2 | 2 X tail | 2 H600 | 2 E | — | 2 H600 | — | — |

¹ neon's default GTK font puts 1,500 lines above the 30,000 px lab cap: the two initial attempts correctly capped at 30,000. Two qualified GTK runs with the explicitly retained 14 px CSS fixture contain 1,500 lines at 17 px pitch (25,500 px). Both original capped attempts remain in the archive. No higher cap was used to force a guest pass.

² Kubuntu `firefox-end-0`, operation `d5d69f4d-fac5-4120-8030-d178de565a71`, contains all 2,400 rows with zero barcode mismatch, but reports `top_not_reached`, `topReached:false`, `truncated:true`: the source supplied no fresh frame to prove the top. This is not an exact successful termination and is not erased by the successful second end run. It did not admit a wrong complete image.

³ neon `firefox-probe-shrink-1`, operation `26fe2950-ea22-4c34-8e28-79b445e10425`, failed `scroll_no_movement`, no PNG. The first shrinking-header image and the other twelve variant images are exact under their fixture-specific oracle. This is a failed regression attempt, not a false `end_of_content` image. The previous pass had two successful shrinking-header runs.

⁴ Budgie non-fixed V1 runs return `time_limit` with exact 18,540 and 20,700 px prefixes. V1 rebuilds a large QImage on each wheel event. Both additional V2 runs, updating only the small changed patch, return all 24,000 px with zero RGB mismatch. GNOME and Plasma also have two full V2 checks. Mint V2 was not run; its two V1 attempts, including the false completion, remain the requested evidence.

The legacy text oracle proves exactly 1,500 distinct ink bands, one pitch, and no duplicate bands; it does not independently render/decode every line label or prove glyph order. This row remains limited rather than a full exact-image acceptance. No OCR was used.

All three physical user-style rows used exactly one hotkey press and one selector drag over our own fixture. Start-cancel / stop-cancel 1 ms / stop-cancel 50 ms counts were 3/5/3 on GNOME and Plasma, 1/1/1 elsewhere. Two pointer-target switches and the subsequent clean capture ran on every desktop. Ring/bar masks are zero; neon's 11 and Hyprland's 8 original mask pixels were the visibly verified parked pointer, with raw masks retained separately. No GNOME Shell coredump was found for the test period. Minimap results are `lost_track`, 600 px, both main column and independent strip exact; none was admitted as complete.

Notices are actual put.gd Notify calls, with observed timing recorded, not merely a synthetic desktop bubble. Their entire blank margin was checked against RGB250. Capped multipart loopback payloads were parsed and their image bytes/hash compared with the PNG. The MCP helper is the locked Python 3.12+ official SDK stdio helper forwarding to the production CLI; all seven captures began at the end and fetched images match their reported SHA-256. The helper exposes no PNG-download method, so the resulting archived PNG was fetched by SCP after the MCP operation.

**Wrong images and false ends.** `wrong-images.json` enumerates 26 confirmed non-exact fixture outputs, including extra guest cases: 14 late-header omissions and 12 other Mint pixel failures (one is the false completion). Four of the twelve are honestly truncated but contaminated prefixes. The two Mint late-header images additionally have footer-shadow pixels. These are confirmed findings, not an upper bound on all possible failures in the unqualified live comparisons.

 Mint `new-nonfixed-1` is the primary false completion: operation `acff15cd-e66d-4136-95a9-9fd773622ee9`, `end_of_content`, height 1,020 of 24,000, `truncated:false`; PNG SHA-256 `2628e254f6c20fdaace42cbdcccfaca11b49e13cf06a9b67aa7af952dd89ab63`. The fixture remained at scroll position 1,140, maximum 23,400. Its first 1,015 scanlines match the event-replayed generator; the last five contain 1,842 non-exact pixels. Another 22,980 document rows are absent. Helper debug shows two NoMovement decisions, source fresh 4 / quiet 0 / unproven 0, no retry. Suspected components are `ScrollStitcher` matching/no-movement classification and `ScrollRun` end confirmation; this run does not isolate the root cause. The V1 redraw overhead is a fixture limitation, not evidence that the false success is safe to accept. See `desktops/m74/new-nonfixed-1/`, `late_fixture.py`, and `new-nonfixed-1-fixture.log`.

The stronger late-bar ruler returns `end_of_content`, height 24,036, on Mint, GNOME, Plasma and Budgie (two each). The body has all 24,000 rows in order and the 36 px bottom banner is present. The required 36 px late top bar is absent: expected composite height 24,072. This is a missing-header contract failure, not proof of an early body end. GNOME/Plasma/Budgie body and footer comparisons are zero mismatch; Mint has the same footer shadow described below. Additional neon and Hyprland late-ruler runs show the same omission. Suspected component is late-header adoption/final image assembly in `ScrollStitcher`. The original text-based late-bar cases also end honestly after 834/864 body rows on several desktops; the exact prefix is retained, and the ruler follow-up makes the missing final header measurable.

Mint's strict generator images retain a small tail contamination consistent with the control bar's compositor shadow. Near-identical table rows: 2,259 mismatch pixels at x0..455 and rows 23,995..23,999, maximum RGB delta 3. Equal-brightness prefixes: 2,259 pixels at their last five rows; repeating-block prefixes: 2,238. Narrow-centre full images: 1,671. Counter/footer composites: 1,334 pixels in their last three rows. The full non-fixed V1 run has 2,259 tail pixels. These are strict failures, even where all document rows are correct; no tolerance was added to the new generators to hide them. The compositor/control-bar source is an inference from position and shape, not a proven root cause.

There is one confirmed early false completion in the new fixture above. No verified legacy fixture was admitted as `end_of_content` with an early document end. Raw generic flags that expected a plain ruler inside a sidebar/blank/shrunk-header layout are retained but replaced for qualification by the fixture-specific oracles. The two invalid first Mint late-ruler attempts captured unrelated private test History because a generated fixture's SIGTERM lambda was corrupted; they are unqualified harness attempts, not evidence for or against the stitcher. The corrected fixture and both corrected runs are retained. A stale saved generator after an idle Qt SIGTERM handler was also corrected by deterministic replay of fixture-only pos/step events; original results, replay code, font/reference hashes and corrected oracle are all retained. No product pixels construct the replay reference.

**Section B.** Site keys: [pr](https://github.com/patrick-hudson/put.gd-desktop/pull/1398), [wiki](https://en.wikipedia.org/wiki/Linux), [py](https://docs.python.org/3/library/stdtypes.html), [mdn](https://developer.mozilla.org/en-US/docs/Web/CSS/position), [repo](https://github.com/patrick-hudson/put.gd-desktop), [hn](https://news.ycombinator.com/), [rust](https://www.rust-lang.org/learn). Redirected final URLs are retained in each result.

 All runs use a new signed-out browser profile, maximized, over the page viewport, with a 30,000 px cap on d69. The other two desktops use the Settings maximum; their 100-megapixel limit caps Python at 52,083 px (Firefox) or 52,493 px (Chromium). `half` starts halfway with scroll-to-top on; `top` starts at the top with it off. Browser document heights are the values measured before each capture. Each detailed result retains after-capture and after-reference geometry, operation ID, SHA, helper log and timing. Seconds include settings/prepare/start/poll and the archived PNG lookup/copy; they exclude reference collection.

`E` = reported end_of_content, `C` = height_cap, `H` = lost_track/time_limit/top_not_reached. These end codes do not by themselves qualify an image. The quality column uses `complete` only for the four all-column pixel-exact GNOME Chromium HN/Rust images. `U(E/C/H)` means image/reference validation remains unqualified although that termination was observed. It is not an accepted complete/capped/honest-partial classification. `T*` is a top-proved helper-log observation, not a returned topReached field; `?` means absent and not established; `n/a` is top-off. The actual API omits topReached on most successful runs. True/false truncation is shown independently.

| Desktop | Browser | Site | Mode | End | Top reached | Truncated | PNG px | Browser doc px | Seconds | Quality |
|---|---|---|---|---|---|---|---:|---:|---:|---|
| m74 | Firefox | pr | half | E | T* | false | 36501 | 36502 | 44.37 | U(E) |
| m74 | Firefox | pr | top | E | n/a | false | 36501 | 36502 | 29.25 | U(E) |
| m74 | Chromium | pr | half | H | T* | true | 20480 | 34765 | 31.21 | U(H) |
| m74 | Chromium | pr | top | H | n/a | true | 20480 | 34765 | 26.53 | U(H) |
| m74 | Firefox | wiki | half | H | T* | true | 2163 | 24756 | 12.06 | U(H) |
| m74 | Firefox | wiki | top | E | n/a | false | 24116 | 24117 | 22.0 | U(E) |
| m74 | Chromium | wiki | half | E | T* | false | 23299 | 23300 | 24.74 | U(E) |
| m74 | Chromium | wiki | top | E | n/a | false | 23299 | 23300 | 20.86 | U(E) |
| m74 | Firefox | py | half | C | T* | true | 52083 | 111974 | 48.17 | U(C) |
| m74 | Firefox | py | top | C | n/a | true | 52083 | 111974 | 43.59 | U(C) |
| m74 | Chromium | py | half | C | T* | true | 52493 | 110440 | 46.14 | U(C) |
| m74 | Chromium | py | top | C | n/a | true | 52493 | 110440 | 39.91 | U(C) |
| m74 | Firefox | mdn | half | H | T* | true | 16101 | 18632 | 25.25 | U(H) |
| m74 | Firefox | mdn | top | H | n/a | true | 16101 | 18632 | 20.85 | U(H) |
| m74 | Chromium | mdn | half | E | T* | false | 18628 | 18629 | 27.22 | U(E) |
| m74 | Chromium | mdn | top | E | n/a | false | 18628 | 18629 | 23.58 | U(E) |
| m74 | Firefox | repo | half | E | T* | false | 4712 | 4713 | 10.03 | U(E) |
| m74 | Firefox | repo | top | E | n/a | false | 4712 | 4713 | 10.88 | U(E) |
| m74 | Chromium | repo | half | E | T* | false | 4716 | 4717 | 10.06 | U(E) |
| m74 | Chromium | repo | top | E | n/a | false | 4716 | 4717 | 6.18 | U(E) |
| m74 | Firefox | hn | half | E | T* | false | 1290 | 1291 | 7.24 | U(E) |
| m74 | Firefox | hn | top | E | n/a | false | 1290 | 1291 | 3.93 | U(E) |
| m74 | Chromium | hn | half | E | T* | false | 1182 | 1183 | 7.65 | U(E) |
| m74 | Chromium | hn | top | E | n/a | false | 1182 | 1183 | 4.28 | U(E) |
| m74 | Firefox | rust | half | E | T* | false | 3198 | 3199 | 8.88 | U(E) |
| m74 | Firefox | rust | top | E | n/a | false | 3198 | 3199 | 5.93 | U(E) |
| m74 | Chromium | rust | half | E | T* | false | 3199 | 3200 | 8.83 | U(E) |
| m74 | Chromium | rust | top | E | n/a | false | 3199 | 3200 | 5.24 | U(E) |
| f44 | Firefox | pr | half | E | T* | false | 36436 | 36436 | 47.92 | U(E) |
| f44 | Firefox | pr | top | E | n/a | false | 36436 | 36436 | 35.3 | U(E) |
| f44 | Chromium | pr | half | E | T* | false | 34729 | 34729 | 35.93 | U(E) |
| f44 | Chromium | pr | top | E | n/a | false | 34729 | 34729 | 29.64 | U(E) |
| f44 | Firefox | wiki | half | E | T* | false | 24094 | 24094 | 32.26 | U(E) |
| f44 | Firefox | wiki | top | E | n/a | false | 24094 | 24094 | 24.97 | U(E) |
| f44 | Chromium | wiki | half | E | T* | false | 23304 | 23304 | 29.42 | U(E) |
| f44 | Chromium | wiki | top | E | n/a | false | 23943 | 23943 | 28.08 | U(E) |
| f44 | Firefox | py | half | C | T* | true | 52083 | 111755 | 57.2 | U(C) |
| f44 | Firefox | py | top | C | n/a | true | 52083 | 111755 | 51.26 | U(C) |
| f44 | Chromium | py | half | C | T* | true | 52493 | 110440 | 50.32 | U(C) |
| f44 | Chromium | py | top | C | n/a | true | 52493 | 110440 | 43.8 | U(C) |
| f44 | Firefox | mdn | half | E | T* | false | 18649 | 18649 | 27.09 | U(E) |
| f44 | Firefox | mdn | top | E | n/a | false | 18649 | 18649 | 22.71 | U(E) |
| f44 | Chromium | mdn | half | E | T* | false | 18629 | 18629 | 26.08 | U(E) |
| f44 | Chromium | mdn | top | E | n/a | false | 18629 | 18629 | 22.32 | U(E) |
| f44 | Firefox | repo | half | E | T* | false | 4708 | 4708 | 11.29 | U(E) |
| f44 | Firefox | repo | top | E | n/a | false | 4708 | 4708 | 8.77 | U(E) |
| f44 | Chromium | repo | half | E | T* | false | 4717 | 4717 | 10.77 | U(E) |
| f44 | Chromium | repo | top | E | n/a | false | 4717 | 4717 | 7.47 | U(E) |
| f44 | Firefox | hn | half | E | T* | false | 1288 | 1288 | 8.75 | U(E) |
| f44 | Firefox | hn | top | E | n/a | false | 1288 | 1288 | 4.85 | U(E) |
| f44 | Chromium | hn | half | E | T* | false | 1186 | 1186 | 7.81 | complete |
| f44 | Chromium | hn | top | E | n/a | false | 1186 | 1186 | 4.62 | complete |
| f44 | Firefox | rust | half | E | T* | false | 3199 | 3199 | 9.42 | U(E) |
| f44 | Firefox | rust | top | E | n/a | false | 3199 | 3199 | 5.96 | U(E) |
| f44 | Chromium | rust | half | E | T* | false | 3200 | 3200 | 10.13 | complete |
| f44 | Chromium | rust | top | E | n/a | false | 3200 | 3200 | 5.82 | complete |
| d69 | Firefox | pr | half | C | T* | true | 30000 | 36481 | 29.67 | U(C) |
| d69 | Firefox | pr | top | C | n/a | true | 30000 | 36481 | 27.16 | U(C) |
| d69 | Chromium | pr | half | C | T* | true | 30000 | 34750 | 37.83 | U(C) |
| d69 | Chromium | pr | top | H | n/a | true | 3827 | 34750 | 11.45 | U(H) |
| d69 | Firefox | wiki | half | E | T* | false | 24754 | 24756 | 39.23 | U(E) |
| d69 | Firefox | wiki | top | H | n/a | true | 3640 | 24504 | 11.7 | U(H) |
| d69 | Chromium | wiki | half | E | T* | false | 23937 | 23939 | 28.08 | U(E) |
| d69 | Chromium | wiki | top | E | n/a | false | 23298 | 23300 | 22.74 | U(E) |
| d69 | Firefox | py | half | C | T* | true | 30000 | 111991 | 31.17 | U(C) |
| d69 | Firefox | py | top | C | n/a | true | 30000 | 111991 | 24.52 | U(C) |
| d69 | Chromium | py | half | C | T* | true | 30000 | 110440 | 40.34 | U(C) |
| d69 | Chromium | py | top | C | n/a | true | 30000 | 110440 | 26.48 | U(C) |
| d69 | Firefox | mdn | half | E | T* | false | 18673 | 18675 | 33.8 | U(E) |
| d69 | Firefox | mdn | top | E | n/a | false | 18673 | 18675 | 26.7 | U(E) |
| d69 | Chromium | mdn | half | E | T* | false | 18627 | 18629 | 23.78 | U(E) |
| d69 | Chromium | mdn | top | E | n/a | false | 18627 | 18629 | 40.28 | U(E) |
| d69 | Firefox | repo | half | E | T* | false | 4711 | 4713 | 11.94 | U(E) |
| d69 | Firefox | repo | top | E | n/a | false | 4711 | 4713 | 7.51 | U(E) |
| d69 | Chromium | repo | half | E | T* | false | 4715 | 4717 | 10.77 | U(E) |
| d69 | Chromium | repo | top | E | n/a | false | 4715 | 4717 | 6.52 | U(E) |
| d69 | Firefox | hn | half | E | T* | false | 1289 | 1291 | 8.99 | U(E) |
| d69 | Firefox | hn | top | E | n/a | false | 1289 | 1291 | 6.33 | U(E) |
| d69 | Chromium | hn | half | E | T* | false | 1181 | 1183 | 7.93 | U(E) |
| d69 | Chromium | hn | top | E | n/a | false | 1181 | 1183 | 3.99 | U(E) |
| d69 | Firefox | rust | half | E | T* | false | 3197 | 3199 | 9.7 | U(E) |
| d69 | Firefox | rust | top | E | n/a | false | 3197 | 3199 | 8.91 | U(E) |
| d69 | Chromium | rust | half | E | T* | false | 3198 | 3200 | 9.1 | U(E) |
| d69 | Chromium | rust | top | E | n/a | false | 3198 | 3200 | 5.21 | U(E) |


**Live comparison findings and limits.** Every saved capture was compared band by band with a browser-produced reference, with both the inherited content-matching oracle and an independent every-RGB-pixel/all-column/zero-offset oracle. The inherited coarse oracle averages 4×4 grey blocks and excludes static pinned sidebars and Firefox's overlay scrollbar. Its passing count is insufficient for this acceptance: it could conceal precisely the few-pixel differences under investigation. All-column per-band deltas, bounding boxes, maximum delta, pixels over 8/32, geometry changes and SHA-256 are in `strict-allcolumns.json`. Unexplained static differences remain unverified. I did not waive whole static columns, label them dynamic, or call a visual resemblance a pass.

The Chromium PR reference method changes sticky elements to relative positioning to build small browser-owned tiles. On Mint it changes document height 34,765→34,825; on GNOME 34,729→34,789. That inserts a 60 px white gap above the embedded image. The resulting +60 alignment change is a reference-layout defect, not proof that the product dropped 60 rows. A separate native CDP full-page attempt on Mint also changes client width 1,905→1,920 and document height 34,765→34,705, so that attempt remains unqualified. The Firefox PR-half embedded image has unresolved static bands and a transient one-row offset; it is not excluded as an animation. Mint Firefox repository-top also has a transient -1/+1 alignment change that remains unresolved. Firefox screen-vs-snapshot antialiasing and overlay-scrollbar differences account for some differing pixels, but those have not been turned into a complete independent glyph oracle.

Specifically identified changing/reference-contaminated bands: Mint Firefox Wikipedia-half appends the late donation footer at rows 2,048..2,163; its body prefix to 2,048 aligns under the inherited content oracle with the contemporaneous reference (literal RGB differences remain unqualified), but the footer is absent after returning to the top. GNOME Chromium Wikipedia-top shows the same late donation footer at approximately 23,825..23,943; bands 23,808..23,936 are retained as differing, not silently discarded. Mint Firefox Rust's original reference has a hover outline at rows 640..704, x796..1124. A neutral-toolbar-pointer reference removes that mismatch; the original and neutral references/results remain. No avatar, relative-time, animated-image or other static mismatch was automatically exempted without identifying a band and cause. The remaining differing bands stay U.

The visible magenta viewport calibration is one pixel shorter than the browser-reported innerHeight on Mint and two on native Plasma. End-of-content images there are correspondingly docHeight−1 / docHeight−2. Both measurements are reported; these images are not silently promoted to exact full-document height. GNOME does not have that metric gap. Full Python references are taller than the product cap and were built from small browser-owned tiles, releasing snapshots between tiles. Mint's initial immediate partial reference and later full-page reference are both retained; comparisons of its partial/capped image use the immediate reference rather than a later changed page. All seven representative capture/reference pairs have stable paths under `live/representatives/`, with provenance; other original captures and references are in the verified private cold archives.

The author's four named early cells: Mint Chromium PR ends `lost_track`, 20,480/34,765 in both modes (confirmed early termination; its reference-layout defect prevents certifying the prefix); Mint Firefox MDN ends `lost_track`, 16,101/18,632 in both modes (confirmed early termination; helper says a notch exceeded safe overlap); Mint Chromium Wikipedia-top reaches end 23,299/23,300 without the donation appeal, so that specific early failure was not reproduced under this page variant; Plasma Firefox PR-half reaches the 30,000 cap in 29.67 s, with top proved, so the 90 s way-up limit was not reproduced in this attempt. These observations do not refute content-dependent failures on other page variants.

**Section C.**

| Row | Observed result | Qualification |
|---|---|---|
| 16. Ubuntu 24.04 native DEB in neon, `selection:none` | `action.invoke(scroll)`, no-rectangle prepare, and explicit-rectangle prepare all refused `scroll_unavailable` with `region_unavailable`; History remains empty and no PNG exists | API guard verified. The UI shows an unavailable warning badge but its button is still enabled; a disabled-button requirement is not established. Actual tray and physical key requests were not injected in the guest under BUILD.md's input rule; the production action dispatcher was tested. |
| 17. GNOME published nightly extension loaded, CI installed without re-login | Loaded 21 / packaged 22; same Shell PID; action and explicit rectangle both refuse `helper_outdated`; no History/image. After re-login, extension 22 ACTIVE and captures work | Guard and recovery verified; exact original extension lists/packages/autostart restored afterwards. The observed code is `helper_outdated`, not `region_unavailable`. |
| 18. Capped capture, HTTP500 upload failure on Mint | History's first row says upload failed, retains the local copy and “Stopped at 2,000 px. The page continues below.”; failure notification shown | Verified against History API and the actual History-window screenshot; no real destination or user object was used. |

**Method defects, unrun details, and cleanup.** Failed attempts were preserved and never overwritten as passes: missing-font fixture launches; Budgie's initial 40/60k requested caps (cancelled at 14,760 px before correction); Hyprland's first private-runtime attempt without compositor IPC (no capture); Firefox Terms-of-Use modal/profile launch failures; the Plasma post-live fixture batch that inherited scroll-to-top off and whose affected cases were rerun after an explicit preference reset; the invalid Mint late fixture; and a mislabeled Budgie archive caught by its checksum before retirement. Caps were corrected to at most 30,000 on d69/guests before qualified runs. Native Debian and Ubuntu artifacts have the same basename; a staging overwrite was detected and corrected before any native Debian install, which used an explicitly named Debian directory and SHA.

The late banner fixture appears after two steps; an animated slide transition was not exercised. Static coloured side columns occupy 30% each, leaving a 40% centre; the fixture tests their constant visible pixels, not changing sidebar widgets. The new equal-brightness fixture has two different 48-row text blocks with exactly equal summed RGB brightness and 2,518 differing pixels; source and generators are retained. Only Budgie is the required guest for the new generator matrix; extra neon/Hyprland cases are separately retained and do not substitute for it.

The session socket preflight checked 43 UTF-8 bytes on native hosts and 39 in guests (nested C16:43), before resident launch. Lab launch also checks QMP/VNC socket paths; Hyprland explicitly checked both aliased and resolved compositor IPC paths. A complete pre-launch byte-length inventory of every other IPC socket was not retained on all hosts; this report does not retroactively claim one. No socket-ownership check or frozen performance harness was changed. No Ctrl+Alt+Fn was sent. The only button/key injection was the once-per-physical permitted hotkey/selector test. One reference collector parked the pointer in GNOME's panel; subsequent native Plasma collection uses the owned browser toolbar. Neither action clicked another application. Protected login values, credentials.txt, user files and real bucket writes were not used.

| Desktop / resource | Cleanup receipt | State |
|---|---|---|
| m74 | lock released 15:46:08 UTC; scratch retired 16:34:39 UTC, 7,301 exact files | Native package and installed Chromium removed; full package/version status restored; no scale/global notification changes. |
| f44 | lock released 15:43:15 UTC; scratch retired 16:34:39 UTC, 6,049 exact files | CI/nightly packages and Chromium/dependency gains removed; package versions, original extension lists/disable flag and autostart restored; relogin completed; no GNOME Shell core found. |
| d69 | lock released 16:49:23 UTC; scratch retired 16:58:40 UTC, 11,971 exact files | Packages/versions/status and APT manual flags restored; owned browser/resident PIDs closed, pre-existing signer gpg-agent preserved. put.gd shortcut component matches pre-user-style snapshot; initial pre-launch global-file state is unproven. |
| Budgie s3b2 | overlay retired 15:11:48 UTC | Workstation archive verified first; own wall entry/forward removed. |
| neon s3n | overlay retired 16:06:12 UTC | Workstation archive verified first; own wall entry/forward removed. |
| Hyprland s3h | overlay retired 16:14:24 UTC | Workstation archive verified first; own wall entry/forward removed. |
| Kubuntu s3k | overlay retired 16:31:35 UTC | Workstation archive verified first; own wall entry/forward removed. |
| Extra lab-tools source export | exact 253 files retired 16:53:18 UTC | Archived privately, indexed, and SHA verified on workstation before deletion. |
| Display wall | original five physical entries verified | No accept3 guest tile or own forward remains; own preview tab closed. |


At most one physical desktop lock was held, with heartbeats; guest campaigns used at most two VMs. Nightly's corrected 12:15–13:00 UTC exclusion was respected. Every guest export was checked on the workstation before the guarded cleanup retired its overlay. All original golden disks and canonical run metadata are preserved. Plasma shortcuts match the saved put.gd component immediately before the user-style binding; the full global shortcut file was not snapshotted before initial app launch, so restoration to that earlier state is not independently proven. Every wall entry/forward added here was removed; the five original wall entries remain. Cold archives have SHA-256 indexes and verified workstation copies; scratch was removed only from exact-file manifests after preservation. Private profiles, environment snapshots, protected bootstrap inputs, full user configuration backups and payload archives are excluded from the public record. Public operation IDs and PNG bytes are unchanged. The public History JSON omits ten synthetic local concurrency references flagged by the repository scanner; `public-redactions.json` records field paths and original/public SHA-256, while the raw records remain in the verified private archive. No product commit, PR-description edit, review request, mark, merge or close was performed.
