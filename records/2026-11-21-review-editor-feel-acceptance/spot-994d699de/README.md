# PR #1791 spot checks on 994d699de

Manual CI run [44953233048](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44953233048) ended cancelled. Its uploaded AppImage, Ubuntu 24.04 DEB, and Fedora 44 RPM were used here. Each live resident and package reported version 26.1121.6128-dev+g994d699debef, commit 994d699debef2d645413f141c8374154353ceda7 and tree 5cc0a195f8544926279454675e9b841a365f99b6. Each package's SHA-256 matched the CI download.

| Desktop | Package | Identity | D · Typed cut snaps back | H · Save already pending |
| --- | --- | --- | --- | --- |
| Aurora Plasma Wayland | AppImage | [Verified](measurements/plasma-identity.json) | [Pass](measurements/plasma-cut-snapback.json) | [Pass](measurements/plasma-agent-save-wait.json) |
| Mint Cinnamon X11 | Ubuntu 24.04 DEB | [Verified](measurements/cinnamon-identity.json) | [Pass](measurements/cinnamon-cut-snapback.json) | [Pass](measurements/cinnamon-agent-save-wait.json) |
| Fedora 44 GNOME Wayland | Fedora 44 RPM | [Verified](measurements/gnome-identity.json) | — | — |
| Fedora 44 Budgie labwc Wayland guest | AppImage | [Verified](measurements/budgie-identity.json) | — | — |
| Omarchy Hyprland Wayland guest | AppImage | [Verified](measurements/omarchy-identity.json) | — | — |

- **D.** Selected a 3–5 s cut at 30 fps, typed 3.01 into Cut Starts, and pressed Enter with real desktop input. On both desktops the resident accepted a new revision with the start still at 3,000,000 µs and the field refreshed to 0:03.0. [Plasma before Enter](pictures/plasma-cut-before-commit.png) · [Plasma after](pictures/plasma-cut-after-snapback.png) · [Cinnamon before Enter](pictures/cinnamon-cut-before-commit.png) · [Cinnamon after](pictures/cinnamon-cut-after-snapback.png).
- **H.** Typed a second cut start at 2.50 s and chose a fresh local Save a copy filename. A fixture on the private control pipe temporarily held the genuine resident edit acknowledgement while the packaged binaries ran. After the file chooser closed, the production CLI's recording.review saveCopyDialog replied recording_state with “A chosen copy is waiting for your last change to be saved”. Both desktops wrote the chosen copy after delivery of the delayed answer, with the new cut start applied. [Plasma saved copy](pictures/plasma-saved-after-answer.png) · [Cinnamon saved copy](pictures/cinnamon-saved-after-answer.png).

The broader acceptance campaign is recorded for [5f2f799ac](../fixed-5f2f799ac/README.md) and [799e392e2](../README.md). The earlier refused-edit Save finding was outside these spot checks.

## Lab cleanup

The three physical leases were released after their cleanup checks. The scoped f44 DNF transaction invalidated a queued offline update. Budgie b3 timed out because the lab invocation used the wrong bootstrap key path. A fresh b4 with the correct path supplied the identity proof. Both Budgie overlays and Omarchy o4 were retired after evidence verification, and their VNC wall entries and tunnels were removed. [Cleanup receipts](measurements/lab-cleanup.json).
