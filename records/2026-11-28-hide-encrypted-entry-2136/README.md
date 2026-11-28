# Upload encrypted with put.gd hides where the destination can't encrypt (#2136, PR #2139)

Live acceptance of put.gd-desktop PR #2139 on the lab builders, 2026-11-28 05:59–06:49 UTC, each row under
its desktop lock and on the wall. Packages are the PR's own CI artifacts: m74 from head c1a1d59bb (run
46112539391, build 26.1128.7347~dev+gc3f3058d6e2f); k72, d69, aurora and f44 from head 50cdea6b1 (run
46115653197, build 26.1128.7348~dev+gbbc2db7bbf73, diagnostics gitTree 252d1726…).

Each row added two lab destinations without secrets (a Proton Drive destination and an untested S3 one) and
switched the capture destination between them with `putgd-cli settings.patch`, with no file manager restart.
`capabilities.uploadFiles.encryptedEntry` and the marker `~/.local/share/putgd/file-manager/encrypted-entry-hidden`
followed each switch (`proton-drive` / absent).

| Host | File manager | Proton Drive routed | S3 routed | Notes |
|---|---|---|---|---|
| m74 Mint 22.3 (Ubuntu 24.04 DEB) | Nemo 6.6.3 | hidden | shown | `putgd-launcher --upload --encrypt` (Thunar's Send To command) refused: "Upload didn't start: Proton Drive already encrypts files end to end. Select Upload with put.gd instead." |
| k72 Kubuntu 26.04 DEB | Dolphin 25.12.3, KIO 6.24 | hidden | shown, from the putgd plugin | Service menu has only putgdUpload; plugin found by KIO without ServiceTypes; folder+file selection shows both; Plasma desktop icons hide/show too; choosing the entry ran the launcher through KIO and opened S3's Encrypted links card |
| d69 Debian 13 DEB | Dolphin 25.04.3, KIO 6.13 | hidden | shown, from the plugin | DEB Depends has no KDE package; folder+file selection shows both |
| aurora Fedora 45 RPM (Atomic, /usr overlay) | Dolphin 26.08.2, KIO 6.31 | hidden | shown | RPM requires no KF6 library |
| f44 Fedora 44 RPM, AppIndicator tray active | Files 50.4 | hidden | shown | Files asks the plugin again when the selection changes, not at each popup |

The package's #2132 migration moved the hosts' stale AppImage menu copies aside on d69, aurora and f44,
including aurora's pre-#2136 encrypted Nemo and FileManager-Actions copies (Sol R5-2). They were put back with
`mv` afterwards; the `*-restored.txt` listings give sha256, mode and mtime. Each host's earlier package state
was restored (m74 and k72: the repository's current nightly 26.1126.7275, the earlier one is gone from it;
f44: 26.1126.7275 from the release; d69 and aurora: no package, as before).

Files: annotated pictures (`<host>-<file manager>-<state>.png`), `*-discovery.txt` / `aurora-facts.txt` (installed
service menu, plugin file and owner package, dependencies), `*-restored.txt`, `d69-aside-before.txt`.
