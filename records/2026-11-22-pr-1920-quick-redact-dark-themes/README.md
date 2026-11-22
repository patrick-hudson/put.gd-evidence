# PR #1920 Quick redact in dark themes

Physical desktop acceptance ran on 2026-11-22 UTC. The candidate fully covered the Monokai terminal comment token on both desktops, where nightly left part visible. It fully covered all 120 token occurrences across the 12 clear desktop scenes, up from 118. One blurred comment token remained partly visible. The #1912 size-specific check failed on three fixtures whose small controls passed on both builds. A separate fixture improved at both sizes.

- **m74** was Linux Mint 22.3 Cinnamon on native X11. Scenes used GNOME Terminal and Firefox.
- **k72** was Kubuntu 26.04 Plasma on native Wayland. Scenes used Konsole and Firefox.
- The two candidate DEBs came from [CI run 45078626297](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45078626297), which succeeded. The lab restored both hosts to the same [published nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1122.6439-nightly) after the comparison.

## Exact builds

The tree values were read from the live resident's `putgd-cli diagnostics` on each host. The candidate matches `git rev-parse c177344551d6b07dfabc6e110db92eb5bdbf3b42^{tree}`.

| Host | Build | CLI version | DEB version | Git commit | Git tree | SHA-256 of the staged DEB |
| --- | --- | --- | --- | --- | --- | --- |
| m74 | nightly | `putgd 26.1122.6439-nightly` | `26.1122.6439~nightly` | `28e9f91060cd10a69921268eefc89e2b6fe4a50e` | `65df546861260bcb92f41ce3f24d3130e90e0c11` | `36dc4b977ac7202f8bf113563bce36b53549b6973d9b29417b87f85dff09c226` |
| m74 | candidate | `putgd 26.1122.6635-dev+gc177344551d6` | `26.1122.6635~dev+gc177344551d6` | `c177344551d6b07dfabc6e110db92eb5bdbf3b42` | `667738ff4495562fd1dc4be3315683ae841ce63d` | `978d5a5f8f9f7770f099d2d8cc081ac8110a753320ce13d9542dfeb294a0e73b` |
| k72 | nightly | `putgd 26.1122.6439-nightly` | `26.1122.6439~nightly` | `28e9f91060cd10a69921268eefc89e2b6fe4a50e` | `65df546861260bcb92f41ce3f24d3130e90e0c11` | `b3479ac0dacdec045b19e763294cd060e7d299f474c311de9e349d39788d870c` |
| k72 | candidate | `putgd 26.1122.6635-dev+gc177344551d6` | `26.1122.6635~dev+gc177344551d6` | `c177344551d6b07dfabc6e110db92eb5bdbf3b42` | `667738ff4495562fd1dc4be3315683ae841ce63d` | `9f5acdce90a4f89996ae8e44c599e310b4355ae2725578f339f84ece786305fd` |

## Results

Each cell shows **fully covered / partly covered / missed**, followed by **decoys touched** and elapsed seconds for the Quick redact CLI call. The elapsed time includes CLI and editor handling. The CLI did not report a separate recognition duration. The file controls contain one target and zero decoys.

| Host | Scene | Nightly | Candidate | Annotated PNGs |
| --- | --- | --- | --- | --- |
| m74 | Terminal · Solarized Dark | 10/0/0 · 2 · 1.139 s | 10/0/0 · 1 · 1.723 s | [Nightly](m74/pictures/terminal-solarized-nightly.png) · [#1920](m74/pictures/terminal-solarized-candidate.png) |
| m74 | Terminal · GitHub dark | 10/0/0 · 2 · 1.168 s | 10/0/0 · 1 · 1.837 s | [Nightly](m74/pictures/terminal-github-nightly.png) · [#1920](m74/pictures/terminal-github-candidate.png) |
| m74 | Terminal · Monokai | 9/1/0 · 2 · 1.149 s | 10/0/0 · 1 · 1.874 s | [Nightly](m74/pictures/terminal-monokai-nightly.png) · [#1920](m74/pictures/terminal-monokai-candidate.png) |
| m74 | Firefox config · Solarized Dark | 10/0/0 · 2 · 0.987 s | 10/0/0 · 0 · 1.483 s | [Nightly](m74/pictures/browser-solarized-nightly.png) · [#1920](m74/pictures/browser-solarized-candidate.png) |
| m74 | Firefox config · GitHub dark | 10/0/0 · 2 · 1.094 s | 10/0/0 · 0 · 1.735 s | [Nightly](m74/pictures/browser-github-nightly.png) · [#1920](m74/pictures/browser-github-candidate.png) |
| m74 | Firefox config · Monokai | 10/0/0 · 2 · 1.035 s | 10/0/0 · 0 · 1.685 s | [Nightly](m74/pictures/browser-monokai-nightly.png) · [#1920](m74/pictures/browser-monokai-candidate.png) |
| m74 | Firefox config · GitHub dark with blurred values | 9/1/0 · 2 · 1.162 s | 9/1/0 · 0 · 1.646 s | [Nightly](m74/pictures/browser-blur-github-nightly.png) · [#1920](m74/pictures/browser-blur-github-candidate.png) |
| m74 | #1912 · whole 3840×2160 | 0/0/1 · 0 · 1.134 s | 0/0/1 · 0 · 0.882 s | [Nightly](m74/pictures/file-whole-v8-nightly.png) · [#1920](m74/pictures/file-whole-v8-candidate.png) |
| m74 | #1912 · same-window crop | 1/0/0 · 0 · 0.798 s | 1/0/0 · 0 · 0.641 s | [Nightly](m74/pictures/file-crop-v8-nightly.png) · [#1920](m74/pictures/file-crop-v8-candidate.png) |
| k72 | Terminal · Solarized Dark | 10/0/0 · 2 · 1.092 s | 10/0/0 · 1 · 1.848 s | [Nightly](k72/pictures/terminal-solarized-nightly.png) · [#1920](k72/pictures/terminal-solarized-candidate.png) |
| k72 | Terminal · GitHub dark | 10/0/0 · 2 · 1.084 s | 10/0/0 · 1 · 1.883 s | [Nightly](k72/pictures/terminal-github-nightly.png) · [#1920](k72/pictures/terminal-github-candidate.png) |
| k72 | Terminal · Monokai | 9/1/0 · 2 · 1.024 s | 10/0/0 · 1 · 1.713 s | [Nightly](k72/pictures/terminal-monokai-nightly.png) · [#1920](k72/pictures/terminal-monokai-candidate.png) |
| k72 | Firefox config · Solarized Dark | 10/0/0 · 2 · 0.936 s | 10/0/0 · 0 · 1.756 s | [Nightly](k72/pictures/browser-solarized-nightly.png) · [#1920](k72/pictures/browser-solarized-candidate.png) |
| k72 | Firefox config · GitHub dark | 10/0/0 · 2 · 1.121 s | 10/0/0 · 0 · 1.663 s | [Nightly](k72/pictures/browser-github-nightly.png) · [#1920](k72/pictures/browser-github-candidate.png) |
| k72 | Firefox config · Monokai | 10/0/0 · 2 · 1.111 s | 10/0/0 · 0 · 1.700 s | [Nightly](k72/pictures/browser-monokai-nightly.png) · [#1920](k72/pictures/browser-monokai-candidate.png) |

The six clear Firefox scenes and the additional blurred Firefox scene left both decoys visible on the candidate. Both decoys were covered on nightly in every desktop scene. In the candidate terminals, a mark still clipped the Git SHA in every theme on both hosts. The UUID remained visible. In the blurred Firefox scene the comment token box had 10,207 of 10,935 pixels black on nightly and 10,259 on the candidate, leaving visible text on both.

## #1912 file controls on m74

All whole images were 3840×2160. Each small image is a pixel-identical crop of the same window in its corresponding whole image. The target is a trailing synthetic fine-grained GitHub token below the last brighter line. Three fixtures were fixed before testing the candidate because they reproduced the nightly whole-screen miss with a passing crop. All three still missed at 3840×2160 on the candidate.

| Fixture | Crop size | Nightly whole / crop | Candidate whole / crop | Whole PNGs | Crop PNGs |
| --- | --- | --- | --- | --- | --- |
| V8, primary | 1790×488 | Missed / full | Missed / full | [Nightly](m74/pictures/file-whole-v8-nightly.png) · [#1920](m74/pictures/file-whole-v8-candidate.png) | [Nightly](m74/pictures/file-crop-v8-nightly.png) · [#1920](m74/pictures/file-crop-v8-candidate.png) |
| V9 | 1790×488 | Missed / full | Missed / full | [Nightly](m74/pictures/file-whole-v9-nightly.png) · [#1920](m74/pictures/file-whole-v9-candidate.png) | [Nightly](m74/pictures/file-crop-v9-nightly.png) · [#1920](m74/pictures/file-crop-v9-candidate.png) |
| V10 | 1790×488 | Missed / full | Missed / full | [Nightly](m74/pictures/file-whole-v10-nightly.png) · [#1920](m74/pictures/file-whole-v10-candidate.png) | [Nightly](m74/pictures/file-crop-v10-nightly.png) · [#1920](m74/pictures/file-crop-v10-candidate.png) |
| V3, fainter comment against bright lines | 1790×466 | Missed / missed | Full / full | [Nightly](m74/pictures/file-whole-v3-nightly.png) · [#1920](m74/pictures/file-whole-v3-candidate.png) | [Nightly](m74/pictures/file-crop-v3-nightly.png) · [#1920](m74/pictures/file-crop-v3-candidate.png) |
| Initial fixture | 1790×1100 | Missed / missed | Missed / full | [Nightly](m74/pictures/file-whole-nightly.png) · [#1920](m74/pictures/file-whole-candidate.png) | [Nightly](m74/pictures/file-crop-nightly.png) · [#1920](m74/pictures/file-crop-candidate.png) |

The ordered recognized word list from a separate Copy text operation had the same SHA-256 on both builds in each of these ten file controls. The captures before redaction were pixel-identical for every matched scene, as recorded for [m74](m74/comparison.json) and [k72](k72/comparison.json).

## How to rerun

1. On the workstation, detach the desktop checkout at the tested head. Download the distro DEBs from the CI run and the corresponding published nightly. Verify the package hashes above before installing. Follow the physical builder rules and hold its desktop lock for package changes and GUI work.
2. On the builder, create a private, short directory such as `$HOME/q1920.XXXXXX` with `mktemp -d`. Copy `scripts/` to it. Run `python3 scripts/fixtures.py fixture "$(cat scripts/fixture-seed.txt)"` from that directory. Run `python3 scripts/probe-fixture.py fixture "$(cat scripts/fixture-seed.txt)"` on m74 as well. The seed generates synthetic values at runtime.
3. With the matching package installed, run `python3 scripts/driver.py "$PWD" HOST BUILD` using `m74` or `k72` and `nightly` or `candidate`. For the Mint blur scene pass `browser-blur-github` as an extra run for each build. The driver opens actual fullscreen windows, captures through `editor.open` with the desktop source, then invokes `redactText` with category `key` and exports `editor.saveCopy` before and after.
4. On m74, drive the file controls in a private offscreen resident using `dbus-run-session -- python3 scripts/headless.py "$PWD" BUILD controls file-whole-v8 file-crop-v8`. Pass the other scene names from the table as needed. Run `python3 scripts/compare.py "$PWD"` and then `dbus-run-session -- python3 scripts/headless.py "$PWD" candidate annotate` with the candidate installed.
5. Restore the published nightly. The installer uses a simulated apt transaction followed by an apt transaction limited to putgd. Confirm the installed package and run the desktop lock cleanup check before releasing.

Each host directory has the per-build original and redacted PNG exports and per-token boxes and pixel counts in `*-verify.json`. A strict pixel check compared every export to the original plus the reported opaque-black rectangles. Coverage is full when every pixel in the value box is opaque black, partial when only some are, and missed when zero are. Red ellipses in the annotated pictures mark the uncovered or newly covered token boxes. Rectangles identify touched decoys. The annotations were made through put.gd's own offscreen editor using `editor.apply` and `editor.saveCopy`.

An early Mint setup attempt wrote its temporary terminal profile into the default dconf database. The test keys were reset and the GNOME Terminal branch matched the acquire-time backup byte for byte. Successful runs used an isolated profile and the physical session bus for the hand-started terminal server. The final release checks verified the restored package and that our test processes were gone. [Mint cleanup](m74/cleanup.txt) · [Kubuntu cleanup](k72/cleanup.txt)
