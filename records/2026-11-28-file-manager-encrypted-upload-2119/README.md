# File manager "Upload encrypted with put.gd" (#2119, PR #2122) on six desktops

Lab acceptance of the new right-click entry "Upload encrypted with put.gd" beside "Upload with put.gd".
It runs `putgd --upload --encrypt -- <paths>`, which sends `upload.files` with `encrypt {enabled:true}`.
Tested 2026-11-28 02:23Z to 03:42Z (2026-11-27 20:23 to 21:42 CST) by a Sonnet 5.5 lab worker for the
Opus implementer thread, under desktop lease owner `feat-2119` (session = the worker's T3 delegated-task thread id).

## Build under test

- CI run 46096285139 on PR #2122 head e3354f081ea5db6671d48bcfb0bae820e5079372, tree a519421d1b96263a8fd73606b229395820433fb2.
  `putgd-cli diagnostics` build.gitTree a519421d1b96 on every desktop below; build.gitCommit shows the CI merge
  commit 39e717fcc8bd, version 26.1128.7278-dev+g39e717fcc8bd.
- Packages: release-native-fedora44 (f44 RPM), release-native-debian13 (d69 DEB), release-native-ubuntu26.04
  (k72 and the Ubuntu guest DEB), release-native-ubuntu24.04 (m74 DEB), release-appimage (aurora-amd).
- F1 re-check only: CI run 46101076903 (PR head 38c429032, tree 36aa9e9e2b38e3d27de2c859446ed0155a2e4f9c),
  release-native-ubuntu26.04 DEB 26.1128.7291-dev+gfcbe9d41e99f, installed on k72.

## Method

Real desktop sessions, shown on the display wall (RFB on the wall tunnels: input and frames; raw frames in `raw/`,
annotated pictures at the top level). Destination A: a real Amazon S3 destination (bucket put.gd, https://put.gd links,
a new `acceptance/tier1-live/<random>/` prefix per host), credentials lent to the desktop keychain through the lab secret
bridge (never printed); Settings → Destinations Test upload and link run until it passed (via `setup.testDestination`,
the same call the button makes). Encrypted links stayed Off except in item 2e. Destination B: a second profile, same bucket,
different prefix, never tested. Links were opened in the desktop's real default browser (Firefox on all six; on d69 the
default per `xdg-mime` is firefox-esr, see F3) and decrypted bytes were compared with `putgd-cli open` (sha256 equals the
source file). Objects and keychain items, local copies and config were removed afterwards.

## Results

| Item | f44 GNOME (Files, RPM) | aurora KDE (Dolphin, AppImage) | k72 KDE (Dolphin, DEB) | m74 Cinnamon X11 (Nemo, DEB) | d69 KDE (Dolphin, DEB) | Ubuntu GNOME guest on d69 (Files, DEB) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 both entries adjacent | pass (plain, encrypted) | pass (plain, encrypted) | pass after F1 (plain, encrypted) | pass (plain, encrypted) | pass after F1 (encrypted, plain: F2) | pass (plain, encrypted) |
| 2a one file: "Encrypted link copied", `#v1.`, encrypt.requested true, item `encrypted`, bucket holds only a random .html | pass | pass | pass | pass | pass | pass |
| 2b opens and decrypts in the default browser | pass | pass (notice click) | pass (notice click, and Firefox launched) | pass (Firefox launched; notice click timed out) | pass with firefox-esr (F3) | pass |
| 2c folder as .zip: one link, zip contents equal | pass (also browser Download) | pass | pass | pass | pass | pass |
| 2d each file: three encrypted links, one opened | pass | pass | pass | pass | pass | pass |
| 2e passphrase destination: link asks, opens with it | not run | not run | pass | not run | not run | not run |
| 2f plain entry: ordinary link, no `#` | pass | pass | pass | pass | pass | pass |
| 3 untested destination B: no object, History unchanged, refusal notice, Settings on B, Test then encrypted upload | pass | pass | pass | pass | pass | pass (notice not captured in a frame; no object, History unchanged, Settings on B) |
| 4 old client exits 2, old resident gives "put.gd was updated" notice, nothing uploaded | n/a | n/a | pass | n/a | n/a | n/a |
| 5 AppImage menu toggle removes and restores both entries | n/a | pass | n/a | n/a | n/a | n/a |

Refusal text seen on B (the #2118 wording): "a2119 B (untested) needs one passed Test upload and link before it can encrypt.
It checks that encrypted pages open over https. Select it in Settings → Destinations. Or upload it without encryption."

## Findings

- **F1 (fixed in 38c429032, re-checked).** A stale per-user service menu `~/.local/share/kio/servicemenus/putgd-upload.desktop`
  (X-putgd-Managed=true, one Action, written by an earlier AppImage run) shadows the DEB's `/usr/share/kio/servicemenus/` file of
  the same name, so Dolphin showed only "Upload with put.gd" on k72 and d69 (`k72-00-...`, `d69-00-...`). Re-check on k72 with
  the 7291 DEB from the stale state (`stale-per-user-files-k72-before-fix.txt`): after install the files were still there; after
  put.gd started all six (KIO, Nemo, Thunar, Contractor, FM-Actions, Nautilus script) were gone, the log had one "Removed an
  AppImage file manager entry that the installed package replaces" line per path, and Dolphin showed both entries (`k72-20-...`).
  Baseline: the shadowing needs the new entry to be visible; with the published nightly 7275 the single plain entry was identical,
  so this was never visible before #2119 (not run on 7275).
- **F2 (observation).** Dolphin 24.12 (d69) sorts the KIO actions alphabetically, so "Upload encrypted" appears above "Upload with
  put.gd"; Dolphin on k72 and aurora keeps the file's order. Always adjacent.
- **F3 (d69 lab note).** On d69 `kde-open` picks the installed ChatGPT app for https links although `xdg-mime query default
  x-scheme-handler/https` says firefox-esr.desktop, so a "Click to open in browser" there may open ChatGPT. Not tested through the
  notice (it timed out); the link was opened with firefox-esr. Not a PR issue.
- **Observation.** After B's refusal Settings opens on Destinations with B selected but at the top of the page; the Encrypted links
  card with Test upload and link is at the bottom (f44, aurora, m74, guest). On k72 the page was already scrolled there.
  GNOME opens that window behind the Files window.
- **Observation.** "Upload each file" copies only the last link to the clipboard for the plain and the encrypted entry alike (the
  notice says links copied; all links are in History). Pre-existing `uploadClipboardBehavior each_link`.

## Lab notes

- m74: my first resident, started with `systemd-run --user`, inherited the user manager's stale WAYLAND_DISPLAY and
  XDG_CURRENT_DESKTOP, so every upload said "Finished with errors: Uploaded. Couldn't copy the link." (copyStatus failed, also for
  the plain entry). Started from the Cinnamon session environment it copied the link ("Encrypted link copied"). Launch artifact, not a product result
  (`m74-02x-copy-failed-wrong-resident-env.png`). Cinnamon keeps error toasts on screen until dismissed.
- d69: the lab bridge wrote to Secret Service (gnome-keyring) while the KDE resident reads KWallet (`credential_store_unavailable`)
  until KDE_FULL_SESSION and KDE_SESSION_VERSION were passed to the bridge.
- d69: Plasma showed old "Yesterday" put.gd notifications from earlier work; they are not from this run.
- The Ubuntu GNOME guest: `gnome-wayland` profile, golden gnome-provisioned-20261016-trimmed-20261113, run a2119-ug, QEMU 10.0.13,
  wall tile `putgd-vm-a2119-ug` (workstation port 5980). Retired with `lab.py reset` and `lab.py cleanup --evidence-manifest`; the
  tunnel unit was stopped and its wall entry removed. wl-clipboard was installed in the guest to read the clipboard.
- Host state: each host's resident was stopped, config.json removed, keychain item and bucket prefixes deleted, local copies
  removed, packages put back to what was found (f44 nightly 7275 RPM, k72 and m74 nightly 7045 DEBs, d69 none, aurora none).
  The harness' removal check blocked the worker's deletion of put.gd's own app data directory on m74, d69 and k72
  (`~/.local/share/putgd`); the implementer removed those files by exact list and released the leases.
- One `rm -rf` of the worker's own scratch directory (`unz`, an unzip folder) happened early on f44 before the no-rm-rf rule was
  applied; nothing else was removed that way.
