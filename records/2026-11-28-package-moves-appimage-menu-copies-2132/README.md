# The package moves an AppImage's file manager menu copies aside (#2132, PR #2137) on d69 and k72

Lab acceptance of PR #2137: an AppImage writes per-user file manager menu files named like the package's, a user file
shadows the system one, so after installing the DEB, Dolphin showed only "Upload with put.gd". With the PR, every start of
the DEB's resident moves exact AppImage copies (only where the package has its own copy) to
`~/.local/state/putgd/file-manager-replaced/<UTC time>/{data,config,home}/<path>`, keeping their mode, and logs one line per
file, "Moved aside an AppImage file manager entry that the installed package replaces". Edited copies are never moved.

Tested 2026-11-28 05:43Z to 05:56Z (2026-11-27 23:43 to 23:56 CST) by a Sonnet 5.5 lab worker for the Opus implementer
thread, under desktop lease owner `feat-2132` (session = the worker's T3 delegated-task thread id), on the real Plasma
Wayland sessions of the builders, shown on the display wall (frames and input over the wall's RFB tunnel).

## Build under test

- CI run 46112258064 (event pull_request, conclusion success) on PR #2137, head 1a265f377748e66ba864a0609fe2bf868808e13a.
  CI builds the merge commit cd9ca435918a4a92028964b794513f3451669444 (parents: nightly e50502973236 and the PR head), tree
  e360c8cd1607bd17a918ca161430a1343c9b0106. So `build.gitTree` is the tree of nightly + PR head, not the tree of the head alone
  (0e3b1181bec0f6ecf16100be2757da256e7bc663); the PR's changes are in it.
- `putgd-cli diagnostics` build on both hosts: version 26.1128.7345-dev+gcd9ca435918a, gitCommit cd9ca435918a, gitTree e360c8cd1607, dirty false.
- Packages: artifact release-native-debian13 (d69) and release-native-ubuntu26.04 (k72), both
  `putgd_26.1128.7345~dev+gcd9ca435918a_amd64.deb`, sha256 1f4c5f10...46a2 (debian13) and 8e5d607e...736b (ubuntu26.04).
- Old AppImage for k72: release v26.1105.3906, `putgd-26.1105.3906-x86_64.AppImage`, sha256 2efb3e87374371666c6f3be22aa13b077b89d7b4020f42a428c72b428a3c6077.

## Results

| # | Check | d69 (Debian 13 Plasma, real Nov 1 stale files) | k72 (Kubuntu 26.04 Plasma, a fresh run of the old AppImage) |
| --- | --- | --- | --- |
| 1 | Start state | pass: six stale files byte- and stat-identical to the Nov 1 originals (538/431/550/470/461/2902 bytes, 2026-11-01 23:31:22 -0600, KIO and the Nautilus script 755) | pass: AppImage 26.1105.3906 wrote the KIO file (only putgdUpload), Nemo, Thunar, FileManager-Actions, Contractor, the Nautilus script, a Caja script, and putgd/file-manager/{putgd-upload (755, 12477 bytes, no `remove_exact`), appimage.owned, appimage.stamp, putgd.svg} |
| 2 | Edited Nemo copy (`Quote=single` appended) | sha 7e0e97af...b260, 444 bytes | same sha 7e0e97af...b260, 444 bytes |
| 3 | DEB installed, put.gd started in the session, ~12 s | pass | pass |
| 4a | KIO, Thunar, FileManager-Actions, Contractor (and on k72 the Caja script) gone from the user folder, present under `file-manager-replaced/<stamp>/...` with the same sha256, mode and mtime | pass (4 files) | pass (5 files: `data/` x4 + `config/caja/scripts`) |
| 4b | Edited Nemo file untouched | pass (7e0e97af..., 644, 444, same mtime) | pass |
| 4c | Nautilus script | **moved** (brief expected it to stay): see F1 | moved (same, by design) |
| 4d | One "Moved aside..." log line per moved file | pass: 5 lines for 5 files | pass: 6 lines for 6 files |
| 4e | Launcher `putgd/file-manager/putgd-upload` upgraded, mode unchanged | n/a (d69 had no AppImage launcher) | pass: log "Updated the AppImage's file manager launcher so its removal keeps edited entries"; now contains `remove_exact` (2), 13187 bytes, mode 755 as before |
| 4f | `appimage.owned` lists no moved file; `hash ` lines for exact entries that remain | n/a | partly: no moved file listed (only the launcher, the icon and the edited Nemo file remain). No `hash ` line, because no exact entry remains (the one left is the edited Nemo copy, correctly without a hash). Not provable on this host: the package has a copy of every entry |
| 5 | Dolphin right-click shows both "Upload with put.gd" and "Upload encrypted with put.gd" | pass (picture below) | pass (picture below) |
| 6 | Restorable: KIO backup moved back, sha256 and mode equal the original | pass: d5591653..., 755, 538 bytes, mtime 2026-11-01 23:31:22.557 -0600 | pass: d5591653..., 755, 538 bytes, mtime equal |
| 7 | Host restored | pass: all six files restored byte- and stat-identical (Nemo from the original bytes), DEB and the 9 pulled-in packs removed (putgd "rc" as before), data this run created removed | pass: #2137 DEB and the 9 packs removed, nightly 26.1125.7045 reinstalled, AppImage and every per-user file this run created removed |

Pictures (annotated, file names and menus only):

- d69: `d69-01-both-entries.png` (raw: `raw/d69-01-menu-raw.png`). Dolphin 24.12 sorts the KIO actions alphabetically, so the encrypted entry is above the plain one.
- k72: `k72-01-both-entries.png` (raw: `raw/k72-01-menu-raw.png`). Plain entry above the encrypted one.

## sha256 and stat listings

- `listings/d69-listings.txt`: d69 before, after the edit, after the start, the restore of the KIO file, and the final restore.
- `listings/k72-01-appimage-written.txt`: k72 after the AppImage's run (sha256 and stat of every file it wrote, its appimage.owned, the KIO file's content).
- `listings/k72-02-after-deb-start.txt`: k72 after the DEB's first start: the resident log lines, the moved files with sha256 and mode, the files left, the launcher, appimage.owned, diagnostics.
- `logs/d69-resident-log.jsonl`, `logs/k72-resident-log.jsonl`: the resident logs of the DEB's start (lines of the "Moved aside..." kind).

The AppImage on k72 wrote the same bytes as the Nov 1 run on d69 (the same sha256 for the KIO, Nemo, Thunar, FileManager-Actions, Contractor and Nautilus files), so the d69 files are real exact copies of what this AppImage writes.

## Findings

- **F1 (brief vs behavior, not a bug in the code).** The Nautilus script `~/.local/share/nautilus/scripts/Upload with put.gd` was moved on d69, though the brief expected it to stay because d69 has no Files plugin. The code (`moveAsideAppImageCopies`, src/app/FileManagerIntegration.cpp) adds the script when the package's Nautilus plugin file `libputgd-nautilus.so` exists (`systemPlugin(c,"nautilus/extensions-4")`); the DEB ships that file even where Nautilus (Files) is not installed. So it is moved on every host with the DEB, installed Files or not.
- **Note (hash lines).** Nothing on k72 could show "`hash ` lines for exact entries that remain": every entry the AppImage wrote has a package copy and was moved, and the one left was edited. A host where the package lacks a copy of a format would be needed.
- **Note (lab).** The apt repo pkg.put.gd/apt/ubuntu26.04 no longer holds nightly 26.1125.7045 (only 26.1126.7171). k72 was restored from the GitHub release asset `putgd-26.1125.7045-nightly-ubuntu26.04-x86_64.deb` (v26.1125.7045-nightly, sha256 33a44c8eb74198daf9ef33b87c7a72a443ce24a317694c1d1b1fb56564b78cd7) with `apt-get install --no-install-recommends --allow-downgrades`; `apt-cache policy putgd` now shows 26.1126.7171 as the candidate.
- **Note (lab).** The DEB install pulls in nine tesseract-ocr-* language packs (Recommends) on both hosts; they were removed again with the DEB.

## Method

Resident started from the Plasma session's environment (WAYLAND_DISPLAY and XDG_RUNTIME_DIR read from plasmashell's environment), not a bare systemd-run. Dolphin was opened on `~/work/p2137/files` (two small text files made for the test); the right-click was a real pointer event over the wall's RFB tunnel. Backups of the originals were taken with `cp -p` into the scratch folder before the Nemo edit, and the restore compared them with `cmp` and `stat`. The deletions of this run's files were done by exact path; the scratch folders on both builders were emptied by exact path. Resident logs on the builders were left.
