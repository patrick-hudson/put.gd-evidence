# Final revisions: redaction edge patches and runtime Qt accessibility branch

PR1378 source 1194b9e788908d8315a5ff04f03c7618b0c51d4a; PR1380 source 0125ada526addfa868503d26add510f9393bb4c1. Baseline for paint comparison: origin/nightly cdac6e4b3174b59e0292b2a16af9abdd110e7514. New nightly c265e2c67 changes different files; both branches are mergeable. No source docs changed, no docs PR needed.

## Redaction view

The retained source-resolution sanitized raster is removed entirely. The base is read through a non-owning QImage view. Opaque mask interiors are filled directly; only narrow device-pixel edge bands are replaced with sanitized patches, each with a two-source-pixel sampling halo and the same source-to-target transform as the base. Patch source extents are limited by adaptive device tiling (64 physical pixels maximum along each axis, source span target1020 pixels); only one transient patch is alive at a time. It is released at the end of that tile, never stored in the canvas/document. A mask covering most of the image therefore costs its visible perimeter, not an image-sized copy. Four-pixel span alignment follows Qt's SIMD sampling groups. The crop view uses local coordinates and bounded sampling, matching the cropped export. Alpha edges first restore the canvas backdrop to avoid a second blend of unsanitized base pixels.

Blur/highlight source preparation now produces only the requested display-resolution tile through the same sanitized edge path. Pixelation continues to average sanitized source samples. No new persistent cache exists: the written steady-state memory contract stays one base raster R, Qt backing store, and the existing <=64 MiB display effect tiles (each <=1.5 MP). Export functions are unchanged.

f44 Fedora44, distro Qt6.11.2, official pinned AWS SDK1.11.924. Final production headers (class final restored) and implementation: editor_contract PASS9.74s, gui_editor_window PASS9.76s. The original magenta-versus-green 16-row property test is unchanged, byte-exact and passing. Reused-versus-fresh canvas test is retained. Additional36 rows cover 29%,83%,137%, DPR1/1.5/2, alpha and crop. Covered-colour invariance is byte-exact in these too; comparison with a scaled sanitized export permits one channel level for clipped/full-span Qt filter rounding, two with alpha compositing. No privacy tolerance. Earlier failed crop/high-DPI experiments are retained in f44/iterations and logs: those exposed an insufficient inner filter band when logical downscale becomes physical magnification, corrected from actual device scale.

### Paint cost

Offscreen1200x800 canvas at Fit, RGB32 source3840x2160 or6000x4000. Small mask600x50 at100,100; large mask image minus100-pixel border. Twenty warmup paints then300 measured paints per row. Drag moves the mask across the available image range, resize grows it toward image bounds; doc.preview updates live geometry outside the timed paintEvent. Timer surrounds only EditorCanvas::paintEvent; QWidget::render setup is excluded. Scratch-only subclass instrumentation removes final from the header for the benchmark, production paint code unchanged. Restore final before the full tests and native picture. Reproduce: add tools/paint-move.cpp as a scratch target linked to putgd_editor, build with dev presets on builder, QT_QPA_PLATFORM=offscreen executable label. CSV preserves mean and maximum across all300 samples; individual samples were not emitted. No best-run selection or maxima filtering; the52.33ms maximum remains visible. Shared host load/scheduling can influence maxima; the exact cause of any individual outlier was not measured.

| Source | Redaction | Interaction | Nightly mean / worst ms | Head mean / worst ms |
| --- | --- | --- | ---: | ---: |
| 8.29 MP | none | still | 8.34 / 16.01 | 8.36 / 14.06 |
| 8.29 MP | small | still | 7.22 / 8.48 | 8.47 / 14.96 |
| 8.29 MP | small | drag | 7.27 / 11.27 | 9.72 / 52.33 |
| 8.29 MP | small | resize | 7.30 / 9.68 | 10.65 / 26.82 |
| 8.29 MP | large | still | 7.64 / 12.72 | 10.03 / 18.88 |
| 8.29 MP | large | drag | 7.40 / 8.06 | 9.32 / 14.95 |
| 8.29 MP | large | resize | 7.45 / 8.26 | 9.27 / 13.09 |
| 24 MP | none | still | 8.66 / 9.48 | 10.43 / 23.83 |
| 24 MP | small | still | 8.71 / 13.81 | 10.07 / 17.96 |
| 24 MP | small | drag | 8.65 / 9.25 | 10.16 / 18.35 |
| 24 MP | small | resize | 8.73 / 14.58 | 11.03 / 31.40 |
| 24 MP | large | still | 8.98 / 20.38 | 13.12 / 18.01 |
| 24 MP | large | drag | 8.94 / 12.65 | 13.76 / 18.83 |
| 24 MP | large | resize | 9.07 / 13.58 | 13.19 / 27.85 |


8MP small drag mean overhead2.45ms, resize3.34ms;24MP worst-size drag13.76 vs8.94ms (1.54x), resize13.19 vs9.07ms (1.45x). Large-mask still24MP13.12 vs8.98ms. All results include patch creation and destruction. No whole-view copy occurs on a mask move/resize. Old full-copy85ms and source-cache measurements remain historical in record2026-11-10-small-fixes-followup; they describe superseded code.

### Picture

a-patches-head.png is the final production EditorWindow at Fit77%, source 1194b9e788908d8315a5ff04f03c7618b0c51d4a, built on f44 and run unchanged on Aurora Fedora45 native Plasma/Wayland Qt6.11.2. Synthetic covered block, own editor surface only. Red label/arrow produced using the production editor's annotation/export renderer. Binary SHA2564394f68ecfc67496ca8037816b9a58de12fd0778baadf9a6010b94535cc95ce9. Driver uses QCoreApplication::exit after grabbing its surface, preventing standalone discard-dialog leftovers. aurora initial/idle frames and clean release receipt retained; lease03:21:19-03:23:48UTC. Existing round-start32a9 and baselinecdac before images remain in record2026-11-10-small-fixes (pins in PR).

## X11 helper

Runtime QLibraryInfo::version(), not build headers, selects behavior. Qt>=6.11 retains the invisible cursor warm-up until after bootstrap; older Qt uses exactly the original stack QWindow lifetime. Qt6.11 introduced QAccessible::isActive in its destructor, bypassing the existing QCoreApplication loop deferral. The runtime-version branch replaces the prior timing claim. No new timing run was made for the unchanged older path.

Source 0125ada526addfa868503d26add510f9393bb4c1: strict capture_preparation_x11 PASS on f44 Qt6.11.2 (9.76s), m74 Mint22.3 Qt6.4.2 (7.82s). Existing test unchanged: zero before selector map, positive after. Source builds with official pinned SDK and dynamically linked distro Qt; development archive builds have unknown embedded version, so these source SHAs and binary hashes are the identity.

Physical m74 Cinnamon6.6.4/X11, own desktop lock, private roots /tmp/v13/fixed: real Ctrl+Shift+F12 maps selector; drag saves400x250 local syntheticPNG; Escape cancels without another PNG. XCURSOR_RESIZED=1 scoped to private processes forces warm-up fallback (normal Qt6.4 static seed skips it). HelperPID3921334 has selector plus intended1x1 cursor child, no160x160 warm-up: on older Qt it is already destroyed. helper-windows.txt contains xprop/xwininfo. Synthetic full-screen cover prevents unrelated desktop content in selector/drag captures. Private settings used profiles[] and only local output, no credentials/uploads. m74/results.txt and pg-version-terminal.png are a real xterm capture under private Xvfb illustrating the preserved test and native results, not itself physical-desktop evidence. Native selector/drag/output frames separately retained. Native driver in tools/native-m74.py spells the shortcut using join to avoid the evidence scanner's generic key= false positive; behavior is identical to the executed literal string.

m74 binaries hashes in m74/binaries.sha256. Lock released02:56:29UTC after visible idle and process cleanup. No installed package, user preferences, desktop restart or logout. B CI42745579753 success at exact head, attempt2: attempt1 lost only Ubuntu24.04 Install distro dependencies to runner timeout; failed jobs re-run. No product test failed in that attempt. Review bodies for both current heads read in full: generic docstring coverage warning only, no Outside diff range comments, no review threads. Existing header/implementation comments describe rendering and lifetime contracts; no unrelated docstring rewrite.

## Scope and cleanup

No workstation builds/tests; all compiles/tests on f44/m74, physical GUI on m74/Aurora. No package run, complete release-desktop matrix, memory campaign, or new latency measurement. Headless results are widget/helper contracts only. No VM, tunnel or new package started. No own live app or build process remains. Scratch build caches/source exports on f44 /home/patrick/work/pg-small and m74 /home/patrick/work/pg1380 are retained as isolated reproducible build artifacts, not installed apps; scratch targets/driver sources are identified above. All leases released. CI receipts are in ci-*.json; final result will be added after A's running CI completes.
