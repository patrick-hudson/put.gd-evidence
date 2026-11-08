# Budgie adapter acceptance, round 3: review fixes (#1275, PR #1283)

Real-session re-checks of the behaviour that changed while answering the 58 review threads on #1283 and the 28 on #1297.

Build: CI run 42459876490, head `6aeda1c20` merged onto nightly, so `b56a39061dcb`. AppImage (sha256 `fcca3bcf…`) on Fedora 45 Budgie; Ubuntu 26.04 DEB (sha256 `de7c689d…`) on Ubuntu Budgie 26.04. VM goldens `fedora45-budgie` (two heads) and `ubuntu-budgie-2604`.

| Row | Result | Evidence |
|---|---|---|
| Rotated-output recording (F45, Virtual-2 at transform 90) | **pass**. The session canvas and the clip are 800x1280, upright. A clip frame matches the screen turned upright (mean difference 3.7) and not the opposite turn (134.8) | `images/budgie-rotated-output-recording.png`, `frames/f45-rotated-*` |
| Window recording at an odd size (F45, moving 421x301 window) | **pass**. Clip 420x300 (cropped to even), motion 14.3–17.9, 5/5 | numbers here |
| Cancel, then prepare at once (#1296) | **pass**. F45 window target 5/5; U26 monitor target 5/5 (a still desktop, so motion 0.03) | numbers here |
| Shortcut pause while recording a shortcut (F45, Settings → Shortcuts) | **pass**. While listening all three gsettings bindings are `''` and status is `recording`; after Escape they are restored and `bound` | `images/budgie-shortcut-pause.png` |
| Clipboard import while unfocused, PRIMARY unchanged | **pass** on F45 and U26 | numbers here |
| Tray on Ubuntu Budgie 26.04 | **pass**. `IconName` `putgd_tray_<pid>_1` with `IconThemePath` `/run/user/1000/putgd/tray`; the applet draws the tray glyph; no "too many keys" warnings in the journal | `frames/u26-tray-final-build.png` |

CI covers the rest, on the same head: `labwc_bridge_contract` (pause during a queued apply, conflicts, second resident), `portal_global_shortcuts_contract`, recording-frames-upright on headless labwc, `prepareRightAfterCancelWaitsForTheOldHelper`, and the assumed-empty clipboard case.
