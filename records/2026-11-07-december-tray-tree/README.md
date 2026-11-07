# December tray tree redesign

The approved December icon is a broad three-tier fir with a separate five-point
star and a shallow tray-shaped stand. The normal mark and November turkey are
unchanged. Its progress fill and error/recording badge fallback still use the
shared renderer.

Implementation commit: `3f1e9e3146f184f2a17dcb5079cf994cc672021e`, based on nightly
`1dd816af3`. The production `src/ui/IconArt.cpp` is byte-identical to the renderer
used for the native Aurora sample. The header and existing shape assertions were
updated for the new geometry.

## Native Aurora sample

Patrick viewed and approved the live sample on Aurora's physical Plasma 6.8.2
Wayland desktop on 2026-11-07. The booted image was
`testing-45.20261101.2`; distro Qt was 6.11.2. The sample compiled with C++20,
CMake and Ninja inside the existing Fedora 45 `putgd-build` Toolbx. It ran
natively in the physical desktop session and stayed visible on the display wall.

The sample links the production `NativeTray.cpp` and the approved `IconArt.cpp`
with a small driver. Idle, 50% progress and complete are controlled demonstration
states. This proves how the proposed pixels appear in the real Plasma tray;
it is **not** a full application build, upload test, cross-desktop acceptance,
memory gate or release acceptance. No provider credentials or uploads were used.

- [Native tooltip and desktop](aurora/idle-tooltip.png)
- [Idle tray crop](aurora/idle-panel.png)
- [50% demonstration crop](aurora/half-panel.png)
- [Complete demonstration crop](aurora/done-panel.png)
- [Exact running identity](aurora/launch.json)
- [Host/session identity](aurora/host-identity.json)
- [Desktop cleanup receipt](aurora/cleanup-receipt.json)

The native sample was stopped normally and the desktop lease released after its
cleanup check passed. No installed app, desktop entries or user preferences were
changed. The retained host source/build and original captures are under
`/var/home/patrick/work/tree07/`; workstation originals are under
`/home/patrick/work/put.gd/work/december-tree-20261107/aurora/`.
The native executable SHA-256 is recorded in `aurora/launch.json`.

## Targeted regression tests

The repository's complete `tests/gui/test_tray_season.cpp` suite, including the
updated geometry assertions, ran through `ctest --preset dev -V` in a focused
CMake target linked to the production Ui, IconArt, Theme, WindowButtons and
TrayCalendar sources. The small target and presets are retained here. This is
not a full product build; the PR's ordinary CI runs the full selected suites.

Both runs were isolated, headless, network-disabled Ubuntu containers on Aurora,
using distro packages and dynamically linked Qt. The test source and changed
renderer match implementation commit `3f1e9e3146f184f2a17dcb5079cf994cc672021e`.

| Environment | Result | Log |
| --- | --- | --- |
| Ubuntu 24.04 / Qt 6.4.2 / GCC 13.2.0 | 36 passed, 0 failed, 0 skipped | [u24.log](tests/u24.log) |
| Ubuntu 26.04 / Qt 6.10.2 / GCC 15.2.0 | 36 passed, 0 failed, 0 skipped | [u26.log](tests/u26.log) |

The tests cover month boundaries, resume/clock behavior, full and partial fills,
transparent gaps, branch tiers, badge fallback and Qt tray raster parity. Socket
paths were checked against the 107-byte limit. Both owned test containers exited
zero and were removed; their sources, logs and build directories remain under
`/var/home/patrick/work/tree-tests07/`.

The Ubuntu 26.04 CI catalog render will supply the changed dark and light
`settings-tray-seasons.png` references. Full CI and those reference checks were
pending when this preview record was published. No broader desktop or release
gate is claimed by this record.
