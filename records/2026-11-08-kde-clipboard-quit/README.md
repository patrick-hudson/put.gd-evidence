# KDE clipboard after put.gd quits

Investigation on 2026-11-08, d69 builder, two fresh KVM overlays visible throughout on Patrick's workstation display wall. **Image loss reproduces, predates #1317, and follows Klipper's image-history policy. No product fix or PR is appropriate.** A helper that keeps ignored images would bypass that policy. Text links survive.

## Results

“Lost” means the copied image is no longer offered; Klipper can restore an older image or text instead. Both image actions were tested: desktop capture's automatic copy, and production `history.copyImage` (History → Copy image). Text used production clipboard acquisition and explicit `operation.copy` on a synthetic URL, with the operation and retained file checked; no remote upload was needed.

| Actual desktop/session | Build/package | Text after quit | Auto-copy image / History image, stock | Independent owner-exit control, stock | Image history enabled |
|---|---|---|---|---|---|
| Kubuntu 26.04.1, Plasma/KWin 6.6.6 Wayland | Published 26.1105.3986-nightly AppImage | Exact; real Kate paste/save matches | Lost / lost | Plain foreground wl-copy loses PNG; text retained | Both put.gd PNGs exact after quit |
| Same | CI 26.1108.4267, 76821fe6f, Ubuntu26.04 DEB | Exact; real Kate paste/save matches | Lost / lost | Same independent control | Both put.gd PNGs exact after quit |
| Released KDE neon User, Plasma/KWin 6.8.1 Wayland | Published 26.1105.3986-nightly AppImage | Exact; real Kate paste/save matches | Lost / lost | Plain foreground wl-copy loses PNG; text retained | Both put.gd PNGs exact after quit |
| Same | CI 26.1108.4267, 76821fe6f, AppImage | Exact; real Kate paste/save matches | Lost / lost | Same independent control | Both put.gd PNGs exact after quit |
| Kubuntu native X11: workspace 6.6.6, kwin_x11 6.6.4 | Same current CI DEB | Exact; real Kate paste/save matches | Lost / lost; earlier history can be restored | Plain foreground xclip loses new PNG | Capture pixels identical after quit; PNG can be re-encoded. History PNG exact |

No KDE keeper process remains after any tested quit. The code only invokes `keepSelectionAfterExit` from Budgie/Hyprland destructors, not KDE; X11 uses its separate X11 adapter (the API's historical adapter label is `cinnamon-x11`, but this was the real `kwin_x11` Plasma session, not XWayland). No source change was made. GNOME/Budgie product-regression reruns were unnecessary because there is no fix; prior #1317 evidence is background, not current KDE proof.

## Klipper policy and controls

Stock user configuration had no image-retention override. The default is to ignore images, while `NoEmptyClipboard` (Prevent the clipboard from being cleared) and `KeepClipboardContents` (Save history across desktop sessions) default true. Those settings do not opt images into history.

Plasma 6.6 uses `IgnoreImages=true`; setting it false enables image retention. Plasma 6.8 uses `SaveImages=false`; setting it true enables it. Tests changed only the disposable guests and called Klipper's real DBus `reloadConfig`; the physical desktops and goldens were untouched. Upstream schemas corroborate the installed settings: [Plasma 6.6](https://github.com/KDE/plasma-workspace/blob/Plasma/6.6/klipper/klipper.kcfg), [Plasma 6.8](https://github.com/KDE/plasma-workspace/blob/Plasma/6.8/klipper/klipper.kcfg).

Controls used no put.gd code: a known synthetic PNG owned by foreground `wl-copy` / `xclip`, exact recorded holder PID terminated, independent read before/after. Stock loses the new PNG. Enabled retention keeps it: neon preserves bytes; Kubuntu re-encodes the synthetic PNG with identical RGBA pixels. See `k1/control-pixels.json` and `k1/x11-control/control-pixels.json`. Treating a changed PNG encoding as image loss would be incorrect. Real KolourPaint Ctrl+V shows the capture with retention enabled; stock instead produces no captured image, sometimes pasting the previous text. Saved QMP visuals cover both outcomes. Kate Ctrl+V and Ctrl+S yield an independently read file equal to each URL on all five build/session rows.

## Identities and reproducibility

Own worktree `t3/kde-clipboard-survival` began at 8182da248, an ancestor of origin/nightly, and was fast-forwarded to **76821fe6fd0319a34428cffedc3bb15caaf4f531** before investigation. No tracked changes. The current packages came from [CI run 42536016981](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42536016981), completed **success**. Older published build: 3986 / source **191f2f41f5ba649e4f471ec100dd7a4ffed1c358**. Each row's `package.json` records package and executable SHA-256; `current-running-identity.json` records verified resident identity. The older AppImage checksum matches the published `old-SHA256SUMS`.

- n1: run `649b7ed0-27d6-4a91-ab48-4f3a4aabb6da`, released-neon golden SHA `191852a5b552492daa9eac1093acd7e15578b0cc5374f4c9a660037af5863238`; SSH22469, remote VNC6100, workstation6090, unit `putgd-vm-kq-n1`.
- k1: run `35910aed-a045-4c9a-9238-fe89348d974f`, provisioned-Kubuntu golden SHA `49fcacff969b81ac38e36fefdf21407d20c82187e1725c58f128a3b76065a81c`; SSH22434, remote VNC6101, workstation6091, unit `putgd-vm-kq-k1`. Rebooted this owned overlay into its installed native Plasma X11 session after the Wayland comparisons. `state-wayland.json` preserves the prior identity.

VM launch sockets were checked before launch (51 UTF-8 bytes); resident socket `/run/user/1000/putgd/session.sock` is 33 bytes. Saved sources under `scripts/` reproduce the investigation. `old/` (neon), `old-final/` (Kubuntu), `current-final/`, and `x11-final/` hold completed acceptance results and visuals. Other directories/logs retain failed setup attempts and are not acceptance: missing builder `convert` corrected to PIL; private config path corrected to the real absolute Klipper file; 6.6 setting name corrected; AppImage permission application-path link corrected; short cold-start/copy waits corrected; native receipt has no `version` field; text owner's inherited SSH descriptors corrected by redirecting them. The first X11 read was premature; final reads waited for actual PNG availability. These were private investigation scripts, not changes to a frozen harness or product tests.

Debian13 Plasma was optional and not run; this investigation stayed in owned VMs rather than occupying a shared physical desktop. No physical desktop lock, EC2, credentials, live bucket, GitHub issue or PR was used. This is clipboard-policy evidence, not full desktop/release acceptance.

## Cleanup

Both VMs stopped and their overlays retired through guarded cleanup, with hashed completion evidence and `overlay-cleanup.json` receipts retained under each run's directory. All manifest member hashes were verified after export. Only the two owned wall entries were removed atomically and their tunnel units stopped. All other wall entries and worker resources were preserved. Golden hashes and final process sweep are in `final-sweep.txt`. No owned VM, keeper, resident, tunnel or desktop lease remains; host-side evidence and test source are retained.
