# Issue 1428: signed repository upgrade, final corrected pass

Part of #1428. Source/build commit df229be2990554bb9c4dff5a020e1407e4eb1885, version 26.1114.5000-nightly. Run date 2026-11-14. No source changes, release workflow dispatches, or subordinate agents.

| Cell | System | Old → new | Dependencies newly installed in upgrade | Copy text result | Acceptance |
| --- | --- | --- | --- | --- | --- |
| apt (first pass retained) | d69 Debian 13 / Plasma Wayland, physical | 26.1113.4757~nightly → 26.1114.5000~nightly | tesseract-ocr-eng 1:4.1.0-2; tesseract-ocr 5.5.0-1+b1 | Exact 62-character match through independent wl-paste | met |
| dnf (corrected pass) | f44 Fedora 44 / GNOME 50.6 Wayland, physical | 26.1113.4757~nightly-1.fc44 → 26.1114.5000~nightly-1.fc44 | None; English data 4.1.0-12.fc44 arrived with the old package via FFmpeg | Expected helper_outdated before re-login; after re-login extension 23 active and independent wl-paste exact 62-character match | met |
| pacman (corrected pass) | fresh Omarchy 4.5.0 Arch / Hyprland 0.56.2 guest on d69 | 26.1113.4757nightly-1 → unchanged | None committed. Planned: tesseract 5.5.3-1, tesseract-data-eng 2:4.1.0-5, also tesseract-data-afr 2:4.1.0-5. zxing-cpp 3.1.1-1 was already pulled by old-package GStreamer | Not run: upgrade aborted by Omarchy pre-transaction hook; old build has no helper | not met |

## Corrected Fedora pass

Receipts: p2-dnf-old-preview.txt, p2-dnf-old-relogin.txt, p2-dnf-upgrade-preview.txt, p2-dnf-old-enabled.txt, p2-dnf-new-relogin.txt, p2-dnf-copy-desktop.txt, p2-dnf-clipboard.txt, p2-dnf-fixture.txt, p2-dnf-fixture.png, p2-dnf-result.png and p2-dnf-lock-release.json.

The old GitHub release RPM was installed normally. After restarting GDM for an autologin, its version-22 system extension was initialized; explicitly enabling it gave Enabled Yes / State ACTIVE, independently recorded by gnome-extensions and org.gnome.Shell.Extensions.GetExtensionInfo. This establishes the requested old loaded state. The reviewed dnf upgrade changed only putgd. Signature verification remained enabled (gpgcheck=1, shipped repo_gpgcheck=0); Verify package files passed and the upgrade completed. No new dependency was needed. English data already present through the earlier FFmpeg dependency chain is retained as an accepted limitation of this distro's transaction.

Before the second login, action.invoke {action:text} returned helper_outdated, loaded 22 / packaged 23, with the documented logout/login message. No crash or silent success. After the second GDM restart/autologin, gnome-extensions reported version 23 active; production capabilities reported extensionVersion 23, outdated false and setup ready. One post-login text.recognize region job was submitted, operation b179d9f8-6c90-4c7d-b317-72abbd95e239, completed with copyStatus copied. wl-paste --no-newline independently returned exactly:

```text
Repository upgrade test
English text is ready
Copy this region
```

There is no final newline (62 characters). The normal GTK fixture uses 24 px dark text on white. RFB drag selected (110,130)–(650,300). Only fixture-only crops left the host, after the crop coverage check. A few post-login frame prechecks failed before any recognition request: GNOME's overview showed the fixture scaled, and the VNC service reconnected once. Esc dismissed the overview; the fullscreen fixture then covered 99.7% of the desktop in white and the single recognition job ran. These lab/precheck failures remain in the p2-dnf-* receipts; no product recognition failure was retried.

/usr/bin/putgd-ocr --version-json succeeded and returned build identity 26.1114.5000-nightly / df229be2990554bb9c4dff5a020e1407e4eb1885, dirty false, schema 1. Engine versions are not part of that command, as the user corrected; the first-pass expectation was mistaken.

## Corrected pacman pass: real command failure

Fresh independent overlay a3, run ffd1c3c1-401f-4f01-9870-2dbb5448f31e. Its immutable Omarchy golden was not modified. As in the first pass, removed omasnap and LibreOffice and their OCR dependencies normally, verified no putgd, English data, Tesseract or ZXing, synced the golden's initially missing package databases and installed the old asset with pacman -U. That old install pulls ZXing via gst-plugins-bad.

No installer configure-only mode was used. arch-config.sh reproduces the repository setup using the old package's files: verified full fingerprint 4032E28D893BAF66F4AC23D9A11D38D55536B371, pacman-key --add, pacman-key --lsign-key, copied the nightly .conf, set public mode 0644 and added its Include. SigLevel stayed PackageRequired DatabaseRequired. The approved shared guest login was used only in memory over SSH stdin for sudo; no workstation private key was transferred. The source script contains no login value.

p2-arch-config-preview.txt records the fingerprint, local signing and successfully synchronized signed database. p2-arch-upgrade-preview.txt records the full transaction before confirmation; a provider prompt consumed the first scripted n as an invalid number, then EOF chose the default provider and declined the final transaction. No package was changed by that preview. The final pacman -Syu putgd --noconfirm used the same default provider and planned 14 packages, including Afrikaans and English data, with 315.75 MiB download. It planned no Hyprland, compositor, portal, kernel or desktop-package change. All package signatures passed `checking keyring` and `checking package integrity` before the pre-transaction hook failed.

Exact failure in p2-arch-upgrade.txt:

```text
(1/2) Checking Omarchy update entrypoint...

Woah partner...

This looks like a direct pacman system upgrade. Omarchy updates should normally
run through:

  omarchy update

That path handles the update transcript, snapshot, keyrings, package upgrade,
migrations, post-update hooks, shell update state, and restart checks together.

If you really meant to bypass Omarchy for this transaction, rerun pacman with:

  sudo env OMARCHY_ALLOW_DIRECT_PACMAN=1 pacman -Syu

error: command failed to execute correctly
error: failed to commit transaction (failed to run transaction hooks)
Errors occurred, no packages were upgraded.
```

Stopped here as requested: no bypass variable, no alternate updater, manual dependency install or disabled verification. putgd remained 26.1113.4757nightly-1, Tesseract/English data absent, ZXing 3.1.1-1 present. putgd-ocr was absent and Copy text was not run. This is a failure of the specified direct command on Omarchy, not evidence of broken OCR or invalid package signatures. The guest session survived because nothing was committed.

## First attempt and cleanup

[first-attempt.md](first-attempt.md) preserves the complete original summary and its superseded dnf/pacman verdicts. Original receipt filenames are unchanged. The two first-attempt gaps were corrected by the user's follow-up: Fedora needed the old extension loaded and two logins; Arch needed installer-equivalent repository configuration. apt's first-pass met verdict stands. All new receipts have p2- prefixes.

Fedora was returned to putgd uninstalled (the initial package state) and its lock released at 12:13:50 UTC, before 12:15. No test process or input helper remains. d69 was not relocked or driven on its physical desktop. The a3 guest was stopped and its overlay retired through guarded cleanup; p2-overlay-cleanup.json preserves its exact disk/run identity. Both a2 and a3 retirement manifests and state receipts are included. The temporary a3 wall tile/tunnel was removed. No golden changed.

First-pass retained package changes remain: Debian has tesseract-ocr and English data plus the residual nightly apt source; Fedora has restored FFmpeg/development packages advanced to 8.1.3-2.fc44 and gstreamer1-plugin-libav 1.28.9-1.fc44. No physical compositor/desktop package changed. dnf invalidated its pending lab offline transaction, as the receipts state. Host scratch removal is pending publication of these receipts; a subsequent add-only receipt will record exact-file cleanup. No removal of pre-existing host work is authorized or planned.
