# History page native desktop acceptance — 2026-11-10

Incomplete acceptance of merged History PR #1396. This record contains native desktop evidence for **m74 Cinnamon/X11 and k72 Plasma/Wayland only**. It establishes neither Fedora acceptance nor a standard outcome-suite pass. No product code, repository tests, harness or documentation were changed; no issues, commits or pull requests were created.

Primary CI run [42893168407](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42893168407) at `faa57142fbca1074de4c7fd47be7982a517ce1ee` completed **cancelled**, with only a contracts artifact. The permitted fallback [42893265063](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42893265063) at docs-only `8662a5fd13b38dd5fe922ed951be09a7e9ec2b69` completed **success**. Installed binaries report `26.1110.4614-dev+g8662a5fd13b3`, clean git provenance, tree `2e4e888dbd72187de60b5739b98554e594ac65bf`. These are CI development packages, not a published nightly or local build.

| Host / native session | Qt / desktop | Artifact | SHA-256 |
| --- | --- | --- | --- |
| m74, Mint 22.3, Cinnamon/X11 | Qt 6.4.2; Cinnamon package 6.6.9+zena | Ubuntu 24.04 `putgd_26.1110.4614~dev+g8662a5fd13b3_amd64.deb` | `759938890dc984327ee0be3d39ecfbb77f677a4d210528c4a2ccd384e846aafa` |
| k72, Kubuntu 26.04, Plasma/Wayland | Qt 6.10.2; Plasma 6.6.6 | Ubuntu 26.04 `putgd_26.1110.4614~dev+g8662a5fd13b3_amd64.deb` | `be531e2ed606a68b96189bbcc3d3c8a1b4a0a453796fd905a0ef17587e77d873` |
| f44, intended Fedora 44 GNOME/Wayland; no app launched | Installed packages GNOME 50.6, Qt 6.11.2; session not graphically verified | `putgd-26.1110.4614~dev+g8662a5fd13b3-1.fc44.x86_64.rpm` downloaded only | `4047509eca40271e63f2e7294ced24419a056f6ead9ee46958ac2a0ba2e7d3f0` |
| k72 download only; not executed | AppImage runtime not tested | `putgd-26.1110.4614-dev+g8662a5fd13b3-x86_64.AppImage` | `2796da5f169c64edf1865c3067611e1e3b779f99505cf5cbde2a41f32608bfba` |

Both native installs reported the version above. Fedora's installed-app version is unavailable because put.gd was not installed. AppImage was hashed, not executed.

## Check results

Pass refers only to the specifically described fixture coverage. No live destination, credentials in the application, S3 or Proton was used.

| Host | 1 Counts/categories | 2 Search/filters | 3 Paging/Alt keys | 4 Days/pinning | 5 Details | 6 Heading click | 7 Multi-select/deletion | 8 Gallery | 9 Themes/minimum | 10 Visual/focus review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m74 Cinnamon/X11 | pass | pass | pass | pass | pass | pass | not run | pass | pass | fail |
| k72 Plasma/Wayland | pass | pass | pass | pass | pass | pass | not run | pass | pass | pass |
| f44 GNOME/Wayland | not run | not run | not run | not run | not run | not run | not run | not run | not run | not run |

- Both hosts, check 7: the three-row header and byte/local-only note passed, but the fixture had no links or deletable destination IDs. Copy links and delete/cancel confirmation were not run. No deletion was confirmed.
- f44, all checks: `sudo -n dnf install --assumeno ~/putgd-lab/h1396-ci/f44/*.rpm` warned that installation would invalidate a pending `dnf5daemon-server` offline transaction. Installation was not attempted; the existing transaction was preserved.
- m74, check 10: toolbar labels touch/run together in the initial dark 1320 × 880 layout. Details below.

## Observations and coverage limits

Private roots `/tmp/h396m` and `/tmp/h396k` isolated config, data, state, cache and runtime. Every action shortcut was cleared before launch. Session discovery reused the read-only `record_run.py` environment function, preserving native display/bus values and an absolute Wayland socket. Socket preflight accepted both complete socket names at 37 UTF-8 bytes. Sessions stayed visible through their existing physical desktop wall tiles.

A real locally saved 64 × 64 synthetic image was produced with `editor.open` / `editor.submit`. The existing guarded `native_acceptance.grow_database` produced 236 independent local operation/item/history identities; integrity was `ok`. A private fixture script assigned three days (80, 80, 76 rows) and 14 labelled synthetic failed-history projections. The journals retain their actual local-save provenance. No remote destination or direct URL was fabricated. This is synthetic History content on real desktops, not evidence of a remote upload. Video/other category counts were tested empty. A second destination and In progress content were not exercised.

The category count labels and sidebar totals matched `history.counts`. The locked Failed uploads filter returned `history_filter_locked`. Two ordinary chips (`mime=image/png`, `localStatus=saved`), their removal/clear, and real-input search `001` yielded `1 of 236 items`. Setting `uploadStatus=failed` intentionally selects the Failed uploads category rather than creating a second removable chip; the first private script expectation was corrected and the failed attempt is preserved.

Pages 1, 2 and 5, last item 236 and `history_page_unavailable` were observed. Real Alt+Right/Left worked with a History row focused. Early keys with focus outside the History list navigated the main app tabs instead; those frames are preserved, not reported as a History shortcut defect. Pinned day headings remained above partially scrolled rows; the heading click preserved selected IDs. Page 2 showed Today · continued. Saved states and pictures cover the day headings and counts.

Details passed real close-button and Esc dismissal, selecting another row while closed, Enter and real double-click reopening, `toggleDetails`, and retaining `detailsWanted=false` through closing/reopening the main window. Initial coordinates missed the close button; corrected center `(1276,200)` passed on the 1320 × 880 window. Early followup JSON labels mentioning Esc actually used CLI closeDetails; the subsequent final-input logs contain the real-input results and supersede those labels.

Gallery day headings/captions, List/Gallery switching, real selection, Shift+Right (two selected after Esc returns focus from details to the gallery), and Down (selection changed to one different row) passed. The early Shift attempt while focus was in the details pane was not a gallery-key failure. Both dark/light 1060 × 680 captures were verified by image dimensions. No GNOME graphical claim is made.

**Test side effects / mistakes:** fixture editor submission copied its synthetic local result to each physical clipboard before a clipboard backup was taken. Previous clipboard contents could not be restored. No clipboard payload was read into logs or evidence. An early coordinate trial activated Retry on the synthetic failed row backed by the original local-only journal; that row reverted to its truthful local-save projection, reducing the failed count from 14 to 13. No remote upload occurred. These are test mistakes, not product regressions. Later count readbacks reflect the changed fixture. All screenshots contain only the owned app or the blue synthetic source asset.

## Defect observed

**D1 — Mint toolbar label spacing on initial dark layout; regression status unknown.**

- Host: m74, Mint 22.3 Cinnamon 6.6.9/X11, Qt 6.4.2, CI DEB identified above.
- Steps: launch the private installed resident in dark theme; open History at 1320 × 880; select three rows, switch to Gallery (also visible in initial category/list captures).
- Expected: distinct capture action labels with visible spacing and no touching text.
- Actual: “Capture window” touches “Capture monitor”; “Capture region & edit” also runs into adjacent content. The spacing is better after the theme/size relayout. k72's equivalent initial toolbar does not show the same effect. No prior-build run was made, so attribution to #1396 is unproven.
- Screenshot: [m74/08-gallery.png](m74/08-gallery.png), with [m74/01-all.png](m74/01-all.png) and [m74/09-light.png](m74/09-light.png) for context. No fix or issue was filed.

## Part B — not run

The required standard History recipes and History-traversing outcome cells were **not executed**. This remains an acceptance gap, not a pass or proof they cannot run. The documented nightly desktop controller selects published release tags (or named stable drafts); no nightly was cut or dispatched. The lower-level surface runner supports native placement and selected recipes, while `outcomes.py` explicitly admits only owned disposable guests. No CI-package disposable-guest campaign was prepared in this run. The automatic nightly check is still needed, and its later result must be associated with its own exact package identity.

Exact Part B commands actually run (interface inspection only, no functional recipes):

```sh
python3 -m tools.lab.surface_driver.run --help
python3 tools/lab/nightly_desktops.py --help
```

The outputs are preserved in `part-b-runner-help.txt` and `part-b-controller-help.txt`. Source inspection covered `surface_driver/recipes/history.py`, `recipes/outcomes.py`, `fixtures/history.py`, and the controller release admission. There is no outcome-suite acceptance receipt here.

## Host changes and cleanup

| Host | Before | Installed during test | Final state / leftovers |
| --- | --- | --- | --- |
| m74 | put.gd absent (`deinstall ok config-files`), residual version `26.1110.4480~dev+g20f4c6911013` | CI Ubuntu 24.04 DEB, only put.gd added | `apt-get remove putgd` removed only put.gd; residual dpkg config record now identifies the tested version. Private root removed, residents gone. `~/putgd-lab/h1396-ci/` retains download, package/build receipts, scratch scripts and install/removal logs. Clipboard caveat above. |
| k72 | put.gd absent (`deinstall ok config-files`), residual version `26.1110.4437~dev+g289b2f4e4f7f` | CI Ubuntu 26.04 DEB, only put.gd added | Same package removal/private-root cleanup. Uinput agent PID 2613760 stopped; wrapper 2613757 gone. No workstation tunnel or user desktop entry was added. `~/putgd-lab/h1396-ci/` retains DEB/AppImage artifacts, scratch scripts and logs. Clipboard caveat above. |
| f44 | put.gd not installed | none | RPM, download helper/log and preflight scratch remain in `~/putgd-lab/h1396-ci/`; pending offline transaction untouched. No GUI lease acquired or app launched. |

Temporary download authentication inputs were private, removed after downloads and never included in evidence. The existing workstation SSH key was not copied. No broad upgrade, logout, compositor restart, VM or user-window manipulation occurred. Package removals restored the prior absent-package state according to the lab cleanup rules; they were not purges of existing residual configuration.

Desktop locks: k72 acquired 20:26:50Z, m74 20:30:27Z. Heartbeats were retained during work. Both passed the separate release cleanup check and were released with `--verified-clean` at **2026-11-10T20:39:20Z**. Receipts are on each host at `~/putgd-lab/locks/history/2026-11-10T20-39-20Z-release.json`; the copied release outputs and final status are included here. No own desktop process remained. Existing m74 SSH processes 313646/313651 were pre-existing and untouched. This slot was outside both documented nightly quiet windows; all leases are released.

## Evidence navigation and privacy review

The JSON command logs preserve actions, readbacks, failed private-script attempts and native crop witnesses. Filenames do not alone establish a pass: use the result explanations above. `05-real-closed.png` is an initial missed-click attempt; `05-real-close-centered.png` is the corrected result. Likewise early “alt-right” frames showing Settings are preserved as focus-context attempts.

KWin screenshots were cropped on the host only after checking the own `putgd-ui` PID, active native window, client bounds and absence of overlapping windows. Failed occlusion guards wrote no screenshot. X11 screenshots used the owned active app XID. Every exported image was subsequently reviewed in contact sheets; no other desktop, files, user windows, login values or credentials are present. Logs and scripts were reviewed for private data before publication. The two `synthetic.png` files are the synthetic source image, not desktop screenshots.

Every screenshot below is captioned with host/session/Qt/package. Duplicate root-level frames are retained from initial investigations.

| Image | Caption |
| --- | --- |
| [k72/01-all.png](k72/01-all.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/01-failed.png](k72/01-failed.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/01-images.png](k72/01-images.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/01-text+other.png](k72/01-text+other.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/01-videos.png](k72/01-videos.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/02-cleared.png](k72/02-cleared.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/02-search-two-filters.png](k72/02-search-two-filters.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/02-two-filters.png](k72/02-two-filters.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-alt-left-success.png](k72/03-alt-left-success.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-focused-left.png](k72/03-focused-left.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-focused-right.png](k72/03-focused-right.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-last.png](k72/03-last.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-page2.png](k72/03-page2.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/03-real-alt-right.png](k72/03-real-alt-right.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/04-continued.png](k72/04-continued.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/04-page2.png](k72/04-page2.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/04-pinned-scroll.png](k72/04-pinned-scroll.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-before-close-retry.png](k72/05-before-close-retry.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-before-real-close.png](k72/05-before-real-close.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-close-correct-center.png](k72/05-close-correct-center.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-doubleclick.png](k72/05-doubleclick.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-open.png](k72/05-open.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-openDetails.png](k72/05-openDetails.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-real-close-centered.png](k72/05-real-close-centered.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-real-closed.png](k72/05-real-closed.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-real-details.png](k72/05-real-details.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-real-enter.png](k72/05-real-enter.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-real-esc.png](k72/05-real-esc.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-stays-closed.png](k72/05-stays-closed.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-toggle.png](k72/05-toggle.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/05-window-reopened.png](k72/05-window-reopened.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/06-heading-click.png](k72/06-heading-click.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/07-selection.png](k72/07-selection.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-caption-arrow.png](k72/08-caption-arrow.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-caption-shift.png](k72/08-caption-shift.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-down-final.png](k72/08-down-final.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-esc-shift.png](k72/08-esc-shift.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-gallery-down.png](k72/08-gallery-down.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-gallery.png](k72/08-gallery.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/08-list.png](k72/08-list.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/09-dark-minimum.png](k72/09-dark-minimum.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/09-light-final.png](k72/09-light-final.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/history.png](k72/history.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/initial.png](k72/initial.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/real-input-focused.png](k72/real-input-focused.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72/synthetic.png](k72/synthetic.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 · synthetic source asset |
| [k72-details.png](k72-details.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72-history.png](k72-history.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72-initial.png](k72-initial.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72-input-attempt.png](k72-input-attempt.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [k72-real-input-focused.png](k72-real-input-focused.png) | k72 · Kubuntu 26.04 Plasma 6.6.6 / Wayland / Qt 6.10.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/01-all.png](m74/01-all.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/01-failed.png](m74/01-failed.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/01-images.png](m74/01-images.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/01-text+other.png](m74/01-text+other.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/01-videos.png](m74/01-videos.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/02-cleared.png](m74/02-cleared.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/02-search-two-filters.png](m74/02-search-two-filters.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/02-two-filters.png](m74/02-two-filters.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/03-focused-left.png](m74/03-focused-left.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/03-focused-right.png](m74/03-focused-right.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/03-last.png](m74/03-last.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/03-page2.png](m74/03-page2.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/04-continued.png](m74/04-continued.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/04-pinned-scroll.png](m74/04-pinned-scroll.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-before-real-close.png](m74/05-before-real-close.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-doubleclick.png](m74/05-doubleclick.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-open.png](m74/05-open.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-openDetails.png](m74/05-openDetails.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-real-close-centered.png](m74/05-real-close-centered.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-real-closed.png](m74/05-real-closed.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-real-enter.png](m74/05-real-enter.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-real-esc.png](m74/05-real-esc.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-stays-closed.png](m74/05-stays-closed.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-toggle.png](m74/05-toggle.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/05-window-reopened.png](m74/05-window-reopened.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/06-heading-click.png](m74/06-heading-click.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/07-selection.png](m74/07-selection.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-arrow.png](m74/08-arrow.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-caption-arrow.png](m74/08-caption-arrow.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-caption-shift.png](m74/08-caption-shift.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-down-final.png](m74/08-down-final.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-esc-shift.png](m74/08-esc-shift.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-gallery-down.png](m74/08-gallery-down.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-gallery.png](m74/08-gallery.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-list.png](m74/08-list.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/08-shift-range.png](m74/08-shift-range.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/09-dark-minimum.png](m74/09-dark-minimum.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/09-light-final.png](m74/09-light-final.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/09-light-minimum.png](m74/09-light-minimum.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/09-light.png](m74/09-light.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 |
| [m74/synthetic.png](m74/synthetic.png) | m74 · Mint 22.3 Cinnamon 6.6.9 / X11 / Qt 6.4.2 · 26.1110.4614-dev+g8662a5fd13b3 · synthetic source asset |
