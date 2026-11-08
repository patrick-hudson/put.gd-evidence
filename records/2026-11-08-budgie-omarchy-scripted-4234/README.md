# Budgie and Omarchy scripted outcomes — nightly 4234

| Row / package | Region | Window / desktop | Recording → upload | Edit → upload | Link → browser | History delete | Auto-copy | Upload clipboard | Copy image | Survives exit | Right-click upload | Live S3 | Live Proton | Pass / fail / not-run | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fedora45-budgie / AppImage | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass* | pass | pass | pass | 13 / 0 / 0 | 13 |
| fedora44-budgie / RPM | pass | pass† | pass | pass | pass | pass | pass | pass | pass | pass* | pass | pass | pass | 13 / 0 / 0 | 13 |
| ubuntu-budgie-2604 / DEB | pass | pass† | pass | pass | pass | pass | pass | pass | pass | pass* | pass | pass | pass | 13 / 0 / 0 | 13 |
| omarchy-hyprland-20261108 / Arch | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass* | pass | pass | pass | 13 / 0 / 0 | 13 |
| omarchy-hyprland-20261108 / AppImage | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass* | pass | pass | pass | 13 / 0 / 0 | 13 |

**Observed total: 65 pass, 0 fail, 0 not-run on the prepared VMs.** This is a scripted outcome pass, not Tier 1 driver acceptance or full release/memory acceptance. All five rows ran in fresh disposable overlays on f44/d69, starting 2026-11-08 19:46 UTC. All five overlays were guarded-retired and all campaign wall tiles/tunnels removed by 20:34 UTC.

**Exit pass\*** required a VM setup correction: Fedora/Ubuntu Budgie used the distro `clipman` package, and Omarchy used the distro `wl-clip-persist` package. The process was owned only for this cell; Clipman history lived on tmpfs and was removed. All five stock goldens failed clipboard persistence after explicit Quit, giving **12 pass / 1 fail / 0 not-run per stock row**, or **60 / 5 / 0** total. Independent ordinary foreground `wl-copy` controls also lost text on owner exit. With the manager, independent `wl-paste` retained the exact URL two seconds after Quit and after restart; `/proc` and the socket confirmed the resident had exited. Published put.gd is unchanged; users without a clipboard manager retain this stock limitation.

**Window/desktop pass†** means desktop pixels matched the independent frozen framebuffer exactly, and window capture reported `window_unavailable` with the documented missing `ext-foreign-toplevel-image-capture-source-manager-v1` reason on labwc 0.9 (Fedora44 and Ubuntu26). Fedora45 labwc0.20 and both Hyprland rows captured the fullscreen external fixture window with exact pixels.

**Exact build:** published `v26.1108.4234-nightly`, version `26.1108.4234-nightly`, clean commit `2b5e1b2d3c11757f805331e4104eb06b2c79ad5c`, tree `33b8f29b0a44ec5c0dc37d154cc0938d3612d328`, count4234. Release was published 2026-11-08 17:43 UTC. The worktree and builder clones are based on origin/nightly 2b5; harness draft #1314 remains at `c155c3ec855aa69bdb7b49b07081847fe013af65`. No product change or new PR was needed. Every row retains VM/golden identity, exact package checksum and binary hashes, build/capability observations, commands/script snapshots, functional artifacts, original failures and cleanup receipts.

| Run | Host | Profile | Exact published package | SHA-256 |
|---|---|---|---|---|
| sp1 | f44 | fedora45-budgie | putgd-26.1108.4234-nightly-x86_64.AppImage | `26c1817ac867d41884ffbc3f78e2027c392eb766a2654066a76b148f0276f30b` |
| sp3 | d69 | fedora44-budgie | putgd-26.1108.4234-nightly-fedora44-x86_64.rpm | `d329dbc4c05e1ece1fdc0f6e3b16b8e19512023046a9c595ef09987b2a2fd119` |
| sp4 | f44 | ubuntu-budgie-2604 | putgd-26.1108.4234-nightly-ubuntu26.04-x86_64.deb | `97ccd1ea8dea350bd7cc765023b46c8df050ac1c06bfc74394c877fe01cc1e30` |
| sp2 | d69 | omarchy-hyprland | putgd-26.1108.4234-nightly-archlinux-x86_64.pkg.tar.zst | `e4232089dea0fdf72c2991ca51159b983f30e61f809bb81b5ecf86de7e504756` |
| sp5 | d69 | omarchy-hyprland | putgd-26.1108.4234-nightly-x86_64.AppImage | `26c1817ac867d41884ffbc3f78e2027c392eb766a2654066a76b148f0276f30b` |

The Arch overlay refreshed package metadata with `sudo pacman -Sy` during the protected probe setup before `pacman -U` installed the published Arch package. Protected package inventories before/after each recorded setup transaction are retained. Fedora45 correctly used the published AppImage; Fedora44 used its published RPM.

Real input and production session methods

Real QEMU hotkeys and the existing Wayland virtual-pointer helper drove region/window/desktop capture. The same QEMU input drove browser copy/paste and actual file-manager menus. Where native control geometry/hit-test was unavailable, the script used production put.gd session methods/CLI. No frozen surface-driver witness was added or weakened. Scripts reuse B/D acceptance routes and the suite’s existing fixture/provider/browser/cleanup implementations.

| Outcome | Route actually used | Independent outcome check |
|---|---|---|
| Region | QEMU Ctrl+Shift+1 and real Wayland drag100,100→500,350 | 400×250 RGBA equals independent frozen framebuffer crop; HTTP object hash; one durable History row |
| Window / desktop | QEMU Ctrl+Shift+2 /3 | Exact framebuffer pixels for desktop/fullscreen external window; expected capability reason on labwc0.9 |
| Recording → upload | Production recording.prepare/start/stop/saveCopy/upload; visible private review | Saved MP4s decoded by the suite motion evaluator: 8 samples, ≥6 comparisons,4–30s; frozen score≤1 and motion>control+1; uploaded MP4 independently fetched/hashed and decoded again |
| Edit → upload | Production editor.open/apply; QEMU Ctrl+Enter, with editor.submit fallback if still editing | Uploaded PNG decoded: solid redaction, arrow changes pixels, original pixels unchanged outside marks; independent HTTP hash. The submit fallback branch was not separately logged |
| Link → browser | Production history.openLink to temporary real default Firefox | Independent Gecko URL/content/paint checks, full browser screenshot, HTTP object hash |
| History delete | Production delete.prepare/confirm for exact newly owned History ID | HTTP object404 after removal; removal row observed; final History cleanup |
| Auto-copy | Fresh QEMU region capture; no Copy action | wl-paste bytes equal exact uploaded URL |
| Upload clipboard | Native wl-copy image/text and URI-list sources; production action.invoke clipboard | Image RGBA preserved; text bytes and binary-file bytes preserved by independent object GET |
| Copy image | Production history.copyImage | Independent wl-paste PNG decoded to exact saved original RGBA |
| Survives exit | Production ui.quit and restart; owned distro clipboard manager for this cell | Resident PID/socket gone; exact native clipboard URL after2s and restart; stock owner-exit controls retained |
| Right-click upload | Real QEMU right-click and menu click: Dolphin on Fedora, Nemo on Ubuntu, Nautilus on Omarchy; AppImage uses Nautilus→Scripts | Exact clicked filename, one real History row, independent uploaded object bytes/SHA-256 |
| Live S3 | Key-set2 stdin bridge; QEMU region; production History Open link and exact prepared deletion | Authenticated S3 HEAD/GET hash and length; prefix listing exactly one object then zero; real default Firefox and public-object hash; origin absence after delete |
| Live Proton | Existing Proton lend; QEMU region; production History Copy link; real focus click and QEMU Ctrl+L/Ctrl+V/Enter with settling; production revoke | Real Firefox decrypts preview and downloads original PNG with exact SHA-256; fresh post-revocation browser navigation reports unavailable; borrowed keychain copy returned/erased |

The first eleven flows use the suite’s isolated loopback S3 fixture, with real desktop/app behavior; the final two use live S3 and Proton. Recording and editor controls used session methods rather than unproven surface coordinates. The editor checks here exercise an arrow and redaction; this pass does not claim every Tier1 driver assertion or every editor mark type. Notifications were disabled for the deterministic local fixture; right-click proof uses the real menu, object bytes and History rather than a banner-count assertion.

Corrected scripts and VM gaps

- The initial auto-copy assertion compared an older region URL after later captures replaced it; a new region immediately before the clipboard read fixed the script.
- Recording output is a text motion report, and the upload revision is `inspect.edit.revision`; the script parsing/schema mistakes were corrected and recordings rerun.
- Omarchy desktop-specific http/https MIME defaults overrode the temporary browser handler. Only those override rows were temporarily removed in the disposable guest; original bytes were restored. Copy→paste follows the suite’s existing recipient route. Explicit native focus and compositor settling fixed early blank-browser trials.
- A Quit assertion originally raised before restarting the resident and blocked local finalizers. The script now restarts in finally; the two retained local-only roots were explicitly recovered. Guest cleanup and guarded retirement verified no app roots/processes remained.
- Stock Wayland clipboard owner-exit loss is reproduced outside put.gd. Distro clipboard persistence was installed only in disposable overlays and owned during the exit cell; original stock failures remain in the record.
- Workstation port6043 was claimed by the GNOME worker during launch. Our attempted tunnel failed closed; Ubuntu’s tile was immediately registered on free6045. No input or lifecycle operation targeted the GNOME worker’s VM.
- A later artifact-review check initially used RGBA difference bbox, which ignores RGB-only changes when difference alpha is zero. The independent check was corrected to RGB and passed on all five saved edited PNGs.

All first useful errors and successful reruns are preserved, not relabelled. No GitHub issue was filed; no product bug was established by the final outcome checks. Draft [#1314](https://github.com/patrick-hudson/put.gd-desktop/pull/1314) was left unchanged, open/draft, CI success, no reviews.

Live cleanup and retained Proton files

**Five live S3 capture objects were removed.** Each live cell checked its isolated prefix listing empty and authenticated origin absence after exact History deletion. All test app histories/profiles/cache and bridged guest keychain items were cleaned; Proton lending receipts record carry-back/guest cleanup. Temporary browser handlers were restored. Native test clipboard/browser state was disposed with the retired overlays.

**Ten synthetic Proton files were retained privately in ten isolated suite folders; all ten share links were revoked.** This is the explicitly approved existing revoke-only cleanup; no unsafe file-deletion path was added. The prior Tier1 campaign retained three additional files, for **13 files retained by both campaigns combined**. This record’s ten paths are:

- `putgd-tier1-68ceb9ed55ce49f3a729c353f1483925/Screen-Capture-2026-11-08-20-09-44.png` (sp1, share revoked).
- `putgd-tier1-43d0085cffd2498f8875a4caa4941624/Screen-Capture-2026-11-08-20-14-54.png` (sp1, share revoked).
- `putgd-tier1-11935356c4724af390bfb733cb34b3ea/Screen-Capture-2026-11-08-20-03-48.png` (sp1, share revoked).
- `putgd-tier1-20493d5e26e04278a7cdfd2827b7db9c/Screen-Capture-2026-11-08-20-24-48.png` (sp3, share revoked).
- `putgd-tier1-827f382ecd3b4231b342b1863ff6ff83/Screen-Capture-2026-11-08-20-22-39.png` (sp4, share revoked).
- `putgd-tier1-d24c71821b684b7a8e565ebcf8ab15c1/Screen-Capture-2026-11-08-14-09-40.png` (sp2, share revoked).
- `putgd-tier1-4d825ae263154ca891e4b952acf4582f/Screen-Capture-2026-11-08-14-15-04.png` (sp2, share revoked).
- `putgd-tier1-69c3229ef4fd458c963c9ab3e52a9df4/Screen-Capture-2026-11-08-14-20-16.png` (sp2, share revoked).
- `putgd-tier1-74a4cb8f01a44e6a8c7a4c2bddd1a9fa/Screen-Capture-2026-11-08-14-03-41.png` (sp2, share revoked).
- `putgd-tier1-27880b76a7754ebf9aa7e89eaf5452c8/Screen-Capture-2026-11-08-14-28-51.png` (sp5, share revoked).

The earlier three files are listed in the [prior driver-campaign evidence](https://github.com/patrick-hudson/put.gd-evidence/blob/23eda7fc59ffea6b545498703035d66a737e523e/records/2026-11-08-budgie-omarchy-nightly-4234/README.md). Full new ledger: [proton-retained.json](proton-retained.json).

Saved browser evidence

These are real default-Firefox screenshots of live uploaded objects. Kiosk mode keeps share tokens out of the pictures; hashes and identities accompany every frame in [browser-visuals.json](browser-visuals.json).

| Run | Live S3 | Live Proton |
|---|---|---|
| sp1 | [browser PNG](rows/sp1/attempts/sp1-s3b/browser-content-1794168141613593338.png) | [decrypted preview PNG](rows/sp1/attempts/sp1-proton3/browser-content-1794168930492633354.png) |
| sp3 | [browser PNG](rows/sp3/attempts/sp3-s3/browser-content-1794169401904772757.png) | [decrypted preview PNG](rows/sp3/attempts/sp3-proton/browser-content-1794169527886617722.png) |
| sp4 | [browser PNG](rows/sp4/attempts/sp4-s3/browser-content-1794169294646032751.png) | [decrypted preview PNG](rows/sp4/attempts/sp4-proton/browser-content-1794169395252561890.png) |
| sp2 | [browser PNG](rows/sp2/attempts/sp2-s3b/browser-content-1794168142598072188.png) | [decrypted preview PNG](rows/sp2/attempts/sp2-proton4/browser-content-1794169259111338560.png) |
| sp5 | [browser PNG](rows/sp5/attempts/sp5-s3/browser-content-1794169661016745680.png) | [decrypted preview PNG](rows/sp5/attempts/sp5-proton/browser-content-1794169767536618002.png) |

Sources and retirement

Reused acceptance sources: B’s [Budgie report](https://github.com/patrick-hudson/put.gd-evidence/tree/977e3f9490c775bc7fde2789a706d522022885a2/records/2026-11-08-budgie-acceptance-round4-1275), D’s [Hyprland report](https://github.com/patrick-hudson/put.gd-evidence/tree/c9a112da7d03c36c899182c4c65308fd3709b88f/records/2026-11-08-hyprland-omarchy-1275). Their copied scripts and the exact private glue are under [sources](sources). None extends the frozen native window witness or publishes a nightly chart.

Workstation exports were verified against every archive-member SHA-256 before retirement. Guarded overlay cleanup receipts live in each row folder; [cleanup](cleanup) verifies no campaign QEMU/app process, overlay, guest slot, Proton lease, wall entry or tunnel remained. Other workers’ VMs/wall entries were preserved. Full originals remain on builders and verified workstation archives, indexed in [archive-index.json](archive-index.json); no golden copy was removed.

**Nothing was posted to or changed on issue#1003. No row was added to the nightly chart. No builder nightly config, d69 timer, ~/nd or ~/ne/results was edited. No physical desktop lock, EC2 resource, workflow dispatch, source push or merge was used in this scripted pass.**
