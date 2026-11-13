# Issue 1428 corpus first light

Partial corpus, not acceptance. Two published-nightly Capture region PNGs from m74, Mint Cinnamon X11, light/dark at 100%, DejaVu Sans Mono 16 px (xterm 12 pt at 96 dpi). Each contains exactly 22 complete source lines, 264 words. The transcript was cut from the known source and visually checked. Build identity is in build.json. Images are original local-only outputs, no upload destination. Operation IDs are retained in each receipt.

Scoring: python3 tests/performance/text/score.py manifest.json --tesseract --scale 1 --output new-1.json (repeat with --scale 2). PSM 3 baseline is intentionally unmodified; PSM 6 comparison uses --psm 6. Engine and English data hash are in each score receipt. No URLs/emails in this slice, so exact-match rate is unmeasured.

Missing: fractional scale, every other class, d69/f44/k72/Budgie/Hyprland captures, full 4K monitor, German quality, complete feature workload and actual phase latency. Pre-feature workload is blocked by the nightly method refusal, not a pass. The synthetic generator rendered successfully on m74; those fixtures are separate from this first real-target slice.

Failed setup and clipped/wrapped capture attempts remain privately on m74 under ~/work/ocr-corpus-1428 and /tmp/t1428m; they are excluded from scored inputs. Corrected capture uses xterm -geometry 192x53 before printing the known source, then region (0,32)-(1000,450). Desktop lease receipts remain on m74.
