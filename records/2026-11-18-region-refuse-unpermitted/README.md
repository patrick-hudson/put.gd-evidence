# Region capture refuses at once when KWin capture is not permitted

Found by the on-screen GUI fuzzer on Aurora Plasma 6.8.2: a resident without KWin ScreenShot2
permission still opened the region selector and failed only after the user selected.

## Setup

- Host: `f44` (Fedora 44 builder), QEMU/KVM guest from golden
  `aurora-testing-45.20261101.2-ec2-20261102-a1` (Aurora Fedora 45, Plasma/KWin 6.8.2, Wayland),
  run `bd64da71-554e-4ecf-b132-749409b1e1cf`, single 1280x800 head. The overlay was retired after
  this run. (aurora-amd was taken by the GUI fuzz campaign, which asked for the guest to run on f44.)
- Before: published nightly `putgd-26.1117.5114-nightly-x86_64.AppImage`,
  SHA-256 `923dccaedfde8a67e331c95a3d28daba96c90edaa6d44ded1f73306ba228771f`.
- After: candidate `putgd-26.1117.5130-dev+gbad21f056a3e-x86_64.AppImage` from CI run 44199665556
  (commit `bad21f056a3ea8270bed82574ff29c9e5a124a54`, tree `96e9754304f1964c0a72547aa7cae87c05f92eb5`),
  SHA-256 `8bf6a2ac91314b7e988532266c12ac4296c58c3696a06bd773dd4233b24d54e6`.
- Permitted: started with `putgd-launcher` through the AppImage, whose AppRun registers the
  restricted KWin entry for the mounted executable.
- Not permitted: the same image's extracted `usr/bin/putgd-launcher` started directly, so no
  desktop entry names that executable (`permission_entry_matches_executable: false`).
- Settings: development template, local-only output. Frames are QMP screendumps (no cursor).

## Results

| Build | Permission | `capabilities` region | `action.invoke region` | Picture |
| --- | --- | --- | --- | --- |
| nightly | not permitted | `available: false`, no `code` | `acquiring`, `putgd-region` running, selector shown | `2-nightly-unpermitted-annotated.png` |
| nightly | not permitted | same | after the selection: `failed`, `capture_permission` | `3-nightly-unpermitted-select-annotated.png` |
| candidate | not permitted | `available: false`, `code: capture_permission` | `failed`, `capture_permission` within 1 s, no `putgd-region` process, notification shown | `5-candidate-unpermitted-annotated.png` |
| candidate | permitted | `available: true` | selector shown, capture `completed` | `4-candidate-permitted-annotated.png` |

On the not-permitted candidate, `window`, `desktop`, `monitor` and `region` with `delaySeconds: 3`
were also refused at once with `capture_permission` and no countdown or selector
(`5-candidate-unpermitted.txt`). The `.txt` files are the CLI transcripts; the unannotated frames
are kept beside the annotated ones.
