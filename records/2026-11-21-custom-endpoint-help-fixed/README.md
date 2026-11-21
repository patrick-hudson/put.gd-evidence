# Use a custom endpoint help opens without blank space (#1793, PR #1794)

In Settings → Destinations → an S3 destination → Advanced connection settings, the help for
**Use a custom endpoint** opened with about 35–45 px of blank space above its text and about 50 px
below it. The before pictures are in
[2026-11-21-custom-endpoint-help-spacing](https://github.com/patrick-hudson/put.gd-evidence/tree/2c99624c0fd8de586654b21534ef474f68266d24/records/2026-11-21-custom-endpoint-help-spacing).

The cause is how Qt's QFormLayout handles a row that has a field but no label: the row never gets
shorter than its item's size hint. The row widget built by `Ui::settingRow` reported, as its size
hint, the height its wrapped help needs at the row's narrow 233 px hint width (171 px). At the
real 760 px width it only needs 86 px, and the extra height went to the help label, which centers
its text. PR #1794 makes the `settingRow` widget and the help note `Ui::helpButton` creates report
the height for their current width.

## Build

PR head `a4bfd6a2d3f7f9f3c510315630dcdd50a6327233`, packages from manual CI run 44939192732, shown in
the app as 26.1121.6101-dev+ga4bfd6a2d3f7.

- k72: `putgd_26.1121.6101~dev+ga4bfd6a2d3f7_amd64.deb`, SHA-256
  `f13fc4f7527cc11397090ce535659d1aa5ad747966704dbe068220da9cffb0aa`.
- f44: `putgd-26.1121.6101~dev+ga4bfd6a2d3f7-1.fc44.x86_64.rpm`, SHA-256
  `167245063664f56fe10666f69d25ae494d7a5f855192531a03be5188c7bf06ad`.

Each package was unpacked into a private folder and run as a private resident with its own `XDG_*`
folders and runtime directory on the real desktop session. It had one synthetic S3 destination
and no stored credentials. Clicks went through the wall VNC.

## Hosts

- k72: Kubuntu 26.04, Plasma 6.6 on Wayland, under desktop lock session `e1793-k72`.
- f44: Fedora 44, GNOME on Wayland, under desktop lock session `e1793-f44`.

## Result

| Desktop | Use a custom endpoint help | Storage class help (another help in the same panel) |
|---|---|---|
| k72, PR head | Right under its row, no blank space above or below; Storage class follows directly | Under its field, as before |
| f44, PR head | Right under its row, no blank space above or below; Storage class follows directly | Under its field, as before |

`Ui::settingRow` has one caller (Use a custom endpoint), so Storage class is the other help shown.
It goes through the same `Ui::helpButton` note path that this change also touches.

## Files

- `after-k72-custom-endpoint-help.png`: k72, full screen without the taskbar, both helps open, boxed.
- `after-f44-custom-endpoint-help.png`: f44, the put.gd window, both helps open, boxed.

Offscreen checks on aurora-amd (Fedora 45, Qt 6.11.2): the GUI test `helpOpensUnderItsOwnField`
now fails if an open help note is a text line or more taller than its text. With nightly's
`Ui.cpp` it fails (`customEndpoint` 85 px, `customFileNamePatternToggle` 17 px), and with the
fix it passes. All 19 `gui_` and `ui_` ctest suites pass, including `ui_catalog_render`.
