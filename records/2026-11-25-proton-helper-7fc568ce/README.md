# Proton helper 7fc568ce: desktop/resource and installer acceptance (P6, #2025)

Repeat of the P6 desktop/resource acceptance (method of record `2026-11-14-proton-helper-34dda9fa`) for the
Bun 1.4.5 Proton helper, SHA-256 `7fc568ce70eeb6bbebe7e1fe676419b258e6b5f371b6daa538b6e300abef9fd0`.

**Packages:** published nightly `v26.1125.7045-nightly`, commit `9d9f65eb8f7c4e9a7eddaf8b0c7938b95e805d40`
(contains #2021, merge `6ef035770`), assets checked against its `SHA256SUMS`.

**Desktops (physical builders, installed package, private profile, Proton lab account under each builder's Proton lock,
quiet lease and desktop lock):**

| Host | Desktop | Package | Functional | Idle window 1 / 2 (RSS, CPU one core) | Active |
| --- | --- | --- | --- | --- | --- |
| m74 | Mint 22.3 Cinnamon 6.6.9 X11, Qt 6.4.2 | ubuntu24.04 deb | 26/26 | 11.5 MiB 0.007% / 11.5 MiB 0.003% | 4/4 |
| f44 | Fedora 44 GNOME 50.6 Wayland, Qt 6.11.2, AppIndicator tray active, putgd@put.gd ACTIVE | fedora44 rpm | 22/22 | 12.6 MiB 0.000% / 12.6 MiB 0.003% | 4/4 |
| k72 | Kubuntu 26.04 Plasma 6.6.6 Wayland, Qt 6.10.2 | ubuntu26.04 deb | 26/26 | 11.7 MiB 0.010% / 11.7 MiB 0.010% | 4/4 |

Each host: installed helper hash checked before measuring (Bun 1.4.5), Proton upload, share, inspect and revoke of every
link, region-helper lifetime, normal UI exit (code 0), 180 s settle, then two quiet windows of at least 300 s with no
swap, no helper process and host load below 1. No helper left at the end.

**Installers:** `tools/releases/audit_assets.py --proton-ci` at the tested commit on d69 over all seven assets
(three DEBs, two RPMs, Arch, AppImage): every package carries helper `7fc568ce…` with Bun 1.4.5 and the
release-time catalog; no official Bun advisory applies. The advisory snapshot was fetched on the workstation and
served by the exact-argument wrapper in `installers/`.

**Files:** `<host>-numeric.tar.gz` (numeric samples, results, events, drivers; no profiles, credentials, links or
payloads), `<host>-history.png` (History at the end of each run, every link revoked), `installers/audit.json`,
`drivers/` (the scripts used).
