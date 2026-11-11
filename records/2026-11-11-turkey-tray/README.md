# Rounded turkey tray artwork

Source: `f70b048180302e8a0dc172ddb4157746fda30975`, tree `7127e0306d3cf9b78682dd461115d81cd0ad9395` on `improve/tiny-turkey`, based on nightly `7badab6e4`. The selected 16px geometry is Astra A. The selected sample and the current-nightly software render are byte-identical.

## Validation

- Fedora 44 builder `192.168.68.70`, isolated export `/home/patrick/work/tk1110`; GCC 16, distro Qt 6.11.2, official AWS SDK 1.11.924 (source `e8c12a9fd0cbbc4e1ff36b90e35ede7cd20e7bc8`). The SDK prefix was reused read-only.
- `cmake --preset dev`, bounded `cmake --build --preset dev`, `ctest --preset dev -R '^(gui_tray_art|gui_theme|native_tray_integration)$'`: all three passed. Export provenance is supplied from the exact Git commit/tree/count/time, without a release tag override.
- The two new optical-frame tests cover direct Qt frame selection/fallbacks and the observed progress alpha/tint regression across all 101 percentages on both panel palettes. Removed seasonal paint pins were not restored.
- 1,008 unchanged mark/tree pixel-and-DPR comparisons against this nightly base match byte-for-byte. The current Christmas tree geometry is preserved.
- Physical GNOME Shell 50.6, native Wayland session `11738`, boot `06940f74-cbcc-4acf-8214-6d7fc5146ec6`. Resident PID `3541873`, executable SHA-256 `fd5693bbcef74cc53f6f67ec8d5c050dc2441d08face8862aed3f646bb9f882e`. Owned SNI `:1.227` exported 24/48/72/16 frames. The live panel crop matches the resident's 16px frame (1/256 foreground-mask pixels differ); the pre-launch baseline differs at 53/256 pixels. Only the verified owned-icon crop left the host.
- The packaged AppIndicator extension was initially disabled. It was temporarily enabled for this check, then restored to disabled. The app exited through `ui.quit`; the desktop lease passed cleanup and was released. The wall remained visible throughout. No other applications were closed or altered.

## Limits

This is targeted artwork, transport and GNOME panel evidence. It is not full release acceptance. Current-build Cinnamon/KDE, other required distro profiles, and full functional/memory release gates were not run here. The GNOME capture extension was unavailable; no native capture/upload claim is made.

## Failure context

An earlier pre-selection GNOME attempt could not register an SNI while AppIndicator was disabled; no framebuffer was exported or claimed as acceptance. The corrected setup above passed and restored the original setting. A discarded antialiased prototype exposed double painting of progress edges; the clipped band now replaces idle pixels before the active fill, and the all-percent alpha/tint regression passes. Full private scratch history remains under `work/turkey-review/`.

## Art and review provenance

All six requested models contributed during exploration. Initial threshold-informed scores were discarded after the user requested independent briefs. Later briefs omitted the threshold and other reviewers' scores. Earlier prototype scores are not ratings of Astra A. The final rounded 16px candidate was chosen by the user; final integration checks returned Sol 9/10 and Fable 8/10 with no blocking implementation regression. Fable's test-policy and documentation points were addressed by removing legacy paint pins and preparing a separate documentation PR.
