# Use a custom endpoint help leaves blank space around its text

In Settings → Destinations → an S3 destination → Advanced connection settings, clicking the
help button next to **Use a custom endpoint** shows the explanation under the row. But a band of
empty space, about 35–45 px, sits between the checkbox and the text, and another, about 50 px,
sits between the text and Storage class. Every other setting's help in that panel sits right
under its row with no gap.

Seen on 2026-11-21 while accepting PR #1789 (#1787):

- k72: Kubuntu 26.04, Plasma 6.6 on Wayland.
- f44: Fedora 44, GNOME on Wayland.

Both ran packages from `52bcb0dca8bf105c50dbe5d35c8fe5acb84adb1a` (26.1121.6098-dev+g52bcb0dca8bf,
CI run 44933380085) as a private resident with one synthetic S3 destination.

That row is built by `Ui::settingRow` (`src/ui/Ui.cpp`). Its help note is placed through the
`inlineHelpRow` branch of `Ui::helpButton`, which #1789 did not change, so nightly 26.1121.6060
lays it out the same way.

Files: `k72-custom-endpoint-help.png` and `f44-custom-endpoint-help.png`. Each is the put.gd
window with the help open and the two blank bands boxed.
