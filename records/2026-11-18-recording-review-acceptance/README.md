# Recording review acceptance, first pass

Tested [PR #1635](https://github.com/patrick-hudson/put.gd-desktop/pull/1635) at branch head `77228c78e721cfd06b993f12c0ff7a6223ef65c3`, with artifacts from [CI run 44261648379](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44261648379). The jobs checked out GitHub's merge commit `425278cb8a7a7be545d2be80fcf7785e9f4270c7`. Both commits have tree `eb7ba22552c86826e0c1847b2f18dc17e03ea6a6`, which was also reported by the running residents. Version `26.1118.5309-dev+g425278cb8a7a`. The coordinator kept the first pass on these packages while the PR head moved.

## Desktops × rows

| Desktop | A | B | C | D | E | F | G | H | I | S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m74 Cinnamon/X11 | Pass | Pass | Pass | Pass | **Fail** | Blocked | Pass | Partial | Pass (worker) | — |
| d69 Plasma/Wayland | Pass | Pass | Pass | Pass | Pass | Blocked (diagnostic failure) | Pass | Partial | — | — |
| f44 GNOME/Wayland | — | — | — | — | — | — | — | — | — | Partial |
| Omarchy Hyprland guest | — | — | — | — | — | — | — | — | — | **Fail** |
| Fedora 45 Budgie guest | — | — | — | — | — | — | — | — | — | Pass |

Both physical full rows used real input for hover, both trim brackets, the C key, and the Save a copy chooser. Mid-drag captures show the pending edge in the viewer while the playhead stays at zero. The released brackets update both trim boundaries and the clip clock. See the [Mint measurements](m74/B-edge-measurements.json) and [Plasma measurements](d69/B-edge-measurements.json).

H is partial on both desktops because the catalog-backed recipe lacked the exact-build catalog. The direct action traces list the controls exercised against each live window. GNOME's smoke export passed its media checks. Its normal-workspace opening required Escape from Activities, so the automatic foreground opening remains unverified.

## Confirmed product findings

1. **Mint MP4 duration exceeds the displayed duration by two frames.** On Cinnamon/X11 at 30 fps, trim to 1.266667–11.333333 s, cut 5.133333–6.266666 s, place a solid redaction from 3.8–7.6 s, and use Save a copy. Inspect recorded 8.933333 s of output. The MP4 contains 270 frames and 9.000000 s of video and AAC audio. The counters next to the join match the intended kept frames, 134 and 167. The export excludes all 19 pink-marker frames and the counters unique to the cut. Sampled mask pixels matched in both kept spans. See [review state](m74/E-edit.json) and [decoded result](m74/E-decoded.json).
2. **A redaction wholly inside a source video gap exposes the covered area.** Keep the original static Plasma capture, then use FFmpeg to retain every 30th video frame while copying its audio. This diagnostic copy has video packets one second apart. Review it with trim 0.2–10.8 s, cut 4.8–7.8 s and a solid box at source 8.2–8.6 s, wholly inside the 8.0–9.0 s gap. Save MP4. All nine decoded frames sampled inside output 5.0–5.4 s expose the blue pixels. The complete 500 and 1300 Hz tones survived and the cut removed the complete 900 Hz tone. Both attempts reproduced the cover failure. See [edit state](d69/F-tone-edit.json), [packet, audio and pixel measurements](d69/F-tones-decoded.json) and [decoded exposed frame](d69/gap-cover-exposed.png). This is a product-path diagnostic with a derived clip. Both unmodified live captures kept 30 fps packet cadence, so F's live gate remains blocked.

## Full desktop measurements

| Desktop | MP4 review / video duration | Left / right motion, frozen control | Flash/beep offsets | Seam counters | Cut marker frames, input / output |
| --- | --- | --- | --- | --- | --- |
| Mint 22.3 Cinnamon 6.6.9 X11 (Ubuntu 24.04 DEB) | 8.933333 / 9.000000 s | 25.119 / 27.330, 0.014 | −13.3 / −13.3 ms | 134 → 167 | 19 / 0 |
| Debian 13 Plasma 6.3.6 Wayland (Debian 13 DEB) | 9.533333 / 9.566667 s | 25.991 / 27.532, 0.022 | −13.3 / −13.3 ms | 133 → 167 | 19 / 0 |

The frozen controls use the steady interval of the separate recorded still fixture, after playback initialization. The working clips contain scrolling SMPTE bars, a ball, a visible counter with pixel-readable binary encoding, a pink cut marker and paired white flashes and 1 kHz beeps. The desktop review accepted Save a copy through each native portal chooser. All exports used local Save a copy. Encoders and recording configuration are attached per host.

On m74, the edited GIF and WebP had 135 decoded frames each, ran 9.000 s and 8.999 s and showed zero cut-marker frames. A separate exact-helper leading cut kept one source frame, with counter 337. Both GIF and WebP decoded to one 640×320 image carrying that counter.

Filmstrip on m74 used the retained 3840×2160 180 s, 60 fps lab fixture and five warm runs for each tile count. Nearest-rank p95 was **403.7 ms** (12 tiles, 450 ms budget) and **710.9 ms** (24 tiles, 750 ms budget). Baseline host CPU busy share was 0.005. Whole-command p95, including process startup and the independent clip probe, was 555.4 ms for 12 tiles and 859.0 ms for 24 tiles. [Raw timings](m74/I-timing.json).

The hovered exact image decoded to a known non-keyframe on each desktop. Mint displayed counter 97 at a 3.910535 s skim request, between the 3.900 and 3.933 s non-keyframes carrying that counter. Plasma displayed counter 87, the 3.733 s non-keyframe, at a 3.713690 s request. Both API trace results transitioned from approximate to exact.

The 26.04 Linux CI test failed before the exact UI catalog could be uploaded. The catalog-backed surface driver recipe could not be run green. Direct live `recording.review` actions were executed and inspected. The removed-control and saved-path issues identified in recipe review are recipe findings from inspection. The AppImage job failed during upstream dependency builds and produced no AppImage binary, so the guest plan uses the exact native CI packages.

## Smoke measurements

| Desktop | Capture / export duration | Left / right motion, frozen control | Cut marker frames, input / output |
| --- | --- | --- | --- |
| Fedora 44 GNOME 50.6 Wayland, physical RPM | 13.900 / 13.000 s | 20.491 / 18.011, 0.009 | 19 / 0 |
| Fedora 45 Budgie 10.10.3 / labwc 0.20.2 Wayland, guest RPM | 14.633 / 13.733 s | 34.347 / 18.015, 0.002 | 19 / 0 |
| Omarchy 4.5 Hyprland 0.56.2 Wayland, guest Arch package | Blocked at CLI startup | — | — |

- GNOME initially showed the review in Activities after the fullscreen fixture closed. Escape brought the 1440×900 review to the normal workspace, clear of the panel. After a cut and a redaction, Save a copy retained the seam counters 136 → 164 and both sides moved. Flash/beep offsets were +15.3 and −18.0 ms. The scoped host RPM install and removal each invalidated a pending offline DNF transaction staged by the daemon. DNF installed or removed only put.gd. [Initial window](f44/av-review.png), [normal workspace](f44/S-window-visible.png), [decoded export](f44/S-decoded.json).
- Budgie's first prepare refused Fedora's placeholder H.264 implementation. The retry used Cisco OpenH264. Review opened at 1256×752, a cut and a redaction applied, and the MP4 retained seam counters 136 → 164. This smoke recording used video only. [Review](budgie/S-review.png), [decoded export](budgie/S-decoded.json).
- Hyprland's golden had OpenSSL 3.6.5. After installing the verified CI Arch package, `putgd-cli --version-json` exited 127. The loader reported `libcrypto.so.4: cannot open shared object file`. The package's recording helper could report its build identity. The matching CI run produced no AppImage. [Loader output](hyprland/cli-loader.log), [VM witness](hyprland/startup-block.png).

## Lab lifecycle

The main physical leases, the two f44 guest leases and the two follow-up trim leases were held one at a time, with cleanup checks before release. d69's prior nightly lease had expired. The coordinator was notified before it was broken. Its recorded guest and pre-existing host processes remained in place.

Both guest displays used independent live wall tiles. The Hyprland overlay was retired at 08:25:02 UTC and the Budgie overlay at 08:31:40 UTC. Their tiles and tunnels were removed, and both builder leases were released. The retirement receipts are in [Hyprland](hyprland/retire.json) and [Budgie](budgie/retire.json). First-pass screenshots are unannotated as requested.
