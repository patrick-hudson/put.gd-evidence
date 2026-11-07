# #1187: GNOME helper discovery without a 3 s probe (A/B on f44)

What was tested: why the put.gd resident idles about 2.6 MiB larger on GNOME while the Shell extension is
unavailable, and whether put.gd-desktop PR #1269 removes the difference without losing the extension when it is
enabled later.

## Builds

All builds are CI `release-appimage` artifacts, extracted and run through `AppRun`. SHA-256 are in `appimage-sha256.txt`.

- base `775f878b2b29`, nightly and the PR's base, CI run 42412781803
- fix v1 `b121a7796114`, event-driven discovery with a backoff probe, CI run 42412919815
- fix v2 `d6bb98dc4653`, as v1, plus each retry asks for a heap reclamation. CI run 42415727402.
- fix v3 `0022e9afac4b`, the PR head: each retry asks only for a page release that never postpones one already due.
  CI run 42418438878.

## How

The tools are in `tools/`.

- **Host and session.** f44 (Fedora 44, GNOME 50 Wayland, the builder's real session) under the f44 desktop lock, on a
  quiet host. The resident ran with private XDG roots under `/tmp/i1187/NAME`, on the session's own bus and
  Wayland display, as a GNOME core resident.
- **Extension states.** `putgd@put.gd` (v18, `/usr/share`) was set with `gnome-extensions disable` for
  "absent" and `enable` for "enabled", and enabled again after every sequence. The appindicator extension stayed on.
- **Sequence.** Start the resident and sample `smaps_rollup` every 5 s for 240 or 300 s. Full `smaps` was saved
  at 180 s. The page-release counters were read from `diagnostics` only at the end, so the idle window is never
  touched. Base and fix ran alternately with the same sequence.
- **Two conditions.**
  - `f44-real-noui/` matches the issue: a saved configuration, so no UI process. The `children` field shows none.
  - `f44-real/`: a fresh configuration, so the first-run Settings window (putgd-ui) was open for the whole run.
- **"Late" runs.** The extension starts disabled and is enabled at 150 s while the resident is idle. Then
  `capabilities` is polled for the helper. In `v3-fix-late`, one desktop capture through the extension to a private
  local destination follows.

## Result: no UI open (the issue's condition)

Median RSS / file-backed MiB of the resident over each idle window. Two page releases are the startup one and the
one after the 60 s cleanup pass. The fix adds one after each discovery retry that lands after them:

| Run | Build | Extension | 100-185 s RSS / file | 190-240 s RSS / file | 245-300 s RSS / file | Page releases | Helper at end |
|---|---|---|---|---|---|---|---|
| nu-base-absent-b1 | `775f878b2b29` | absent | 11.61 / 8.41 | 11.61 / 8.41 | 11.61 / 8.41 | 2 | False |
| nu-base-absent-b2 | `775f878b2b29` | absent | 11.58 / 8.38 | 11.58 / 8.38 | 11.58 / 8.38 | 2 | False |
| nu-base-enabled | `775f878b2b29` | enabled | 9.02 / 5.82 | 9.02 / 5.82 |  | 2 | True |
| nu-fix-absent-b1 | `0022e9afac4b` | absent | 9.12 / 5.89 | 11.94 / 8.71 | 9.12 / 5.89 | 4 | False |
| nu-fix-absent-b2 | `0022e9afac4b` | absent | 9.16 / 5.95 | 11.87 / 8.66 | 9.16 / 5.95 | 4 | False |
| nu-fix-enabled | `0022e9afac4b` | enabled | 9.07 / 5.86 | 9.07 / 5.86 |  | 2 | True |

- **Root cause confirmed.** On the base, the extension being absent costs 2.6 MiB at idle (11.6 against 9.0), the
  issue's number. `smapsdiff-base-enabled-vs-absent-180s.txt` shows where: libQt6Core +1160 KiB, libQt6DBus +552,
  putgd +500, libdbus +252, libstdc++ +128. That is the code the 3 s `Hello` retry runs: D-Bus send and receive, the
  error reply, and the adapter's capability JSON. It faults those pages back in after every page release.
- **Between probes, the fix matches enabled.** With the extension absent, the fix idles at 9.1 MiB, the enabled
  size. `smapsdiff-base-absent-vs-fix-absent-180s.txt` is the same list reversed.
- **After each retry.** The resident is back at the base's size for about 32 s, until the release that follows it.
  The retry backs off from 3 s to one probe every 15 minutes (3, 9, 21, 45, 93, 189 s, …), so at the cap that is
  about 32 s in every 900 s. `series-file-mib.txt` shows the pattern.

## Result: first-run Settings window open

| Run | Build | Extension | 100-185 s RSS / file | 190-240 s RSS / file | 245-300 s RSS / file | Page releases | Helper at end |
|---|---|---|---|---|---|---|---|
| real-base-absent | `775f878b2b29` | absent | 12.39 / 9.09 | 12.39 / 9.09 |  | 2 | False |
| real-base-enabled | `775f878b2b29` | enabled | 10.79 / 7.48 | 10.79 / 7.48 |  | 2 | True |
| real-base-late | `775f878b2b29` | absent | 12.02 / 8.69 | 10.57 / 7.23 |  | 3 | True |
| real-fix-absent | `b121a7796114` | absent | 12.10 / 8.77 | 12.10 / 8.77 |  | 2 | False |
| real-fix-enabled | `b121a7796114` | enabled | 10.14 / 6.82 | 10.14 / 6.82 |  | 2 | True |
| real-fix-late | `b121a7796114` | absent | 12.06 / 8.77 | 10.56 / 7.25 |  | 3 | True |
| v2-base-absent-b1 | `775f878b2b29` | absent | 11.94 / 8.62 | 11.94 / 8.62 | 11.94 / 8.62 | 2 | False |
| v2-base-absent-b2 | `775f878b2b29` | absent | 12.01 / 8.69 | 12.01 / 8.69 | 12.01 / 8.69 | 2 | False |
| v2-fix-absent-b1 | `d6bb98dc4653` | absent | 10.68 / 7.38 | 12.25 / 8.95 | 10.68 / 7.38 | 3 | False |
| v2-fix-absent-b2 | `d6bb98dc4653` | absent | 10.79 / 7.48 | 12.43 / 9.12 | 10.79 / 7.48 | 3 | False |
| v2-fix-enabled | `d6bb98dc4653` | enabled | 10.73 / 7.41 | 10.73 / 7.41 |  | 2 | True |
| v2-fix-late | `d6bb98dc4653` | absent | 12.33 / 9.02 | 10.68 / 7.36 |  | 3 | True |
| v3-base-absent-b1 | `775f878b2b29` | absent | 12.04 / 8.73 | 12.04 / 8.73 | 12.04 / 8.73 | 2 | False |
| v3-base-absent-b2 | `775f878b2b29` | absent | 11.98 / 8.68 | 11.98 / 8.68 | 11.98 / 8.68 | 2 | False |
| v3-fix-absent-b1 | `0022e9afac4b` | absent | 10.71 / 7.39 | 12.44 / 9.12 | 10.71 / 7.39 | 4 | False |
| v3-fix-absent-b2 | `0022e9afac4b` | absent | 10.62 / 7.32 | 12.29 / 8.98 | 10.62 / 7.32 | 4 | False |
| v3-fix-enabled | `0022e9afac4b` | enabled | 10.63 / 7.31 | 10.63 / 7.31 |  | 2 | True |
| v3-fix-late | `0022e9afac4b` | absent | 12.28 / 8.95 | 10.62 / 7.28 |  | 4 | True |

- The UI-open condition gives the same picture with a smaller gap: base absent 12.0 to 12.4 MiB against enabled 10.8.
- v1 shows why a plain slow probe is not enough. After the release, a backoff retry maps the D-Bus pages again, and
  nothing releases them until the next interaction (v1 absent 12.1).
- v2 releases after each retry. But the backoff's first steps restarted the release timer, so the startup release
  slipped from about 35 s to 95 s (`v2-fix-absent-*` series: 30.7 MiB file-backed until 95 s).
- v3 keeps the startup release on time (7.39 MiB at 40 s against the base's 8.73) and releases after each retry.

## Enabling the extension later still works

- `real-fix-late` (v1) and `v3-fix-late` (v3): the extension was enabled 150 s into an idle run, with no retry
  due. The resident had the helper 0.02 s later, through the extension's `CapabilitiesChanged`. The base took
  0.06 s.
- In `v3-fix-late` a desktop capture through the extension then completed:
  `f44-real/v3-fix-late/capture-after-enable.png`. It shows the f44 session at 4:46 PM local, with the v3 build's
  Settings window and version string visible. `f44-after-enable.png` is the wall frame at 4:44 PM, after the enable.
- A missed signal is covered by the backoff probe. CI's `gnome_core_transport_integration` proves it with
  `lostEnableSignalRecoversThroughTheSafetyProbe`, plus `extensionSignalsDiscoverWithoutWaitingForTheProbe`
  and `missingExtensionBacksOffToTheSafetyProbe`.

## Headless stand-ins (not representative)

`f44-standin/` and `m74-standin/`: `fake_shell.py` owns `org.gnome.Shell` on a private
`dbus-run-session` bus. Nightly `1dd816af3101` showed only 0.23 MiB between absent and enabled, because the private
bus kept the D-Bus pages hot in both states (libQt6DBus 620 KiB either way). The m74 runs add forced cgroup reclaim.
These runs are why the real-session condition is the measurement of record.
