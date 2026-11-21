# AppImage updates with put.gd's own zsync client (#1766)

What was checked: the `--install-update` child's built-in zsync client
updating real published nightlies from `pkg.put.gd`, and the Settings rows that
show it.

- Source: put.gd-desktop branch `feat/appimage-builtin-zsync`, commit
  `c680b1ac7` (rebased on nightly `0d0dba47f`, which includes #1765).
- Host: d69, Debian 13, Qt 6.8.2, `dev` preset (Debug), 2026-11-21.
- Target: nightly `v26.1120.5875-nightly`
  (`putgd-26.1120.5875-nightly-x86_64.AppImage`, 165,861,880 bytes, SHA-256
  `cb442a6b49ba4a47e2dc55c21e0feaf4ea2bebea506fb6a49c45836563312445`).

## Real updates against pkg.put.gd

A dev build has no release channel, so `putgd-cli --install-update` refuses it
(`update_install_unavailable`, `no_package`). The runs used `realrun.cpp.txt`, a
throwaway driver linked against the same objects as the test binary
(`UpdateCheck.cpp`, `UpdateInstall.cpp`, `Zsync.cpp`). It calls `installUpdate`
exactly as `runInstallMode` does, with one difference: the build identity is the
seed's published version instead of the dev build's. The feed, the
`SHA256SUMS` signature checked with the compiled nightly release key, the
`.zsync`, the Range requests to CloudFront and the swap are the product code.
`APPIMAGE` pointed at a copy of an older published nightly in a scratch folder.

| Seed (running image) | Method | Reused | Downloaded (.zsync + ranges) | Runs / requests | Install time | Peak RSS |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| 26.1120.5780 (previous nightly) | zsync | 153,243,648 B (92.4 %) | 12,901,996 B | 15 / 1 | 6.6 s | 38 MB |
| 26.1118.5367 (two back, from the GitHub release) | zsync | 143,056,896 B (86.3 %) | 23,088,748 B | 59 / 2 | 7.1 s | 38 MB |
| 26.1120.5780 | download (pkg.put.gd) | 0 | 165,861,880 B | - | 7.1 s | 61 MB |

Each install ended with the image at the same path, SHA-256 equal to the
signed `SHA256SUMS` line, and the old image kept as the hidden backup.
Debian's reference zsync 0.6.2 client, reading the same seeds against the same
`.zsync`, reports "Target 92.4% complete" and "Target 86.2% complete", so the
parser and block matching agree with zsync's own.

d69's LAN downloads the whole image in about 5 s, so zsync does not save time
there; it saves 92 % of the bytes. Most of its local time is reading the seed
(about 1.5 s for 158 MB) and the SHA-1 and SHA-256 checks of the result. At the
7 MB/s measured on the workstation in #1766 the whole file takes about 24 s and
the 12.9 MB about 2 s (an estimate from these byte counts, not a timed run).

Receipts: `final-5780.jsonl`, `final-5367.jsonl`, `final-download.jsonl` (the
child's progress lines and result), `*.time.txt` (`/usr/bin/time -v`).

## Settings

Rendered offscreen by `putgd-ui-catalog` (dark) on d69 from the same commit,
with four synthetic `update.status` states added to a local copy of
`tests/gui/ui_catalog.cpp` (not committed). The red boxes mark the changed text.

- `zsync-1766-1-reading.png`: "Finding the parts this version already has".
- `zsync-1766-2-fetching.png`: "Downloading only what changed ... (… reused
  from this version)".
- `zsync-1766-3-restart.png`: "with a zsync update that downloaded 12.3 MB".
- `zsync-1766-4-updated.png`: the same after the restart.

Sizes use 1024 math: 12,618,232 bytes shows as 12.03 MB and 153,243,648 bytes
as 146.14 MB.
