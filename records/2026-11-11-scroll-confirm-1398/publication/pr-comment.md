Confirmation on `eaa1ba198fa537d3cac58879b676ad34e268b96a`, CI merge `47f90af4ed8bda4630c5865fe82023460f4b4697`.

**140 exact PNGs, seven correct intentional Stop viewports, zero wrong admitted images, zero requested cases unrun.** Every from-end completion begins at row/line 0 and proves the top. All seven MCP PNGs were fetched and verified; cap payloads match loopback uploads.

| Desktop | Exact | Honest intentional Stop | Wrong |
|---|---:|---:|---:|
| Cinnamon X11 — Mint 22.3 | 20 | 1 | 0 |
| GNOME 50.6 Wayland — Fedora 44 | 20 | 1 | 0 |
| Plasma 6.3.6 Wayland — Debian 13 | 20 | 1 | 0 |
| Hyprland 0.56.2 — Omarchy | 20 | 1 | 0 |
| Budgie / labwc 0.20.2 — Fedora 45 | 20 | 1 | 0 |
| KWin 6.8.1 Wayland — KDE neon | 20 | 1 | 0 |
| KWin 6.6.6 Wayland — Kubuntu 26.04 | 20 | 1 | 0 |

**Overall acceptance remains blocked:** after the GNOME matrix, an additional prepare/cancel/quit cleanup operation caused GNOME Shell SIGSEGV in Mutter window placement through GJS. The responsible caller and whether it predates this build are unproven. No capture started and no PNG/source-fresh summary exists for that cleanup operation. The [record](https://github.com/patrick-hudson/put.gd-evidence/blob/92a1b0a1e0dac1231ed2353e0ea0e5e9a14c43a3/records/2026-11-11-scroll-confirm-1398/README.md) retains its exact operation/RPCs, backtrace, all case PNGs/logs, way-up timings, harness refusals, annotated pictures and cleanup receipts.

All native test packages and gained Fedora runtime dependencies are removed; settings restored; all five overlays retired, wall entries/tunnels removed and locks released. The PR description now has the annotated pictures, one results table per desktop, limits and all previous pass links. PR stays draft; no product edits or PR-branch push.
