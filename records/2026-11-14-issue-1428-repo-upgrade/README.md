# Issue 1428: signed repository upgrade row completed

Part of #1428. Build 26.1114.5000-nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885. Tested 2026-11-14. The user identified the Arch/OpenSSL ABI mismatch as pre-existing and separate from text recognition, and explicitly requested the non-CLI hotkey test in pass four. No package or system-library workaround was made.

| Cell | System | Previous → upgraded package | Newly installed dependencies in upgrade | Copy text | Row result |
| --- | --- | --- | --- | --- | --- |
| apt, retained first pass | d69 Debian 13 / Plasma Wayland, physical | 26.1113.4757~nightly → 26.1114.5000~nightly | tesseract-ocr-eng 1:4.1.0-2; tesseract-ocr 5.5.0-1+b1 | Independent wl-paste exact 62-character match | met |
| dnf, retained second pass | f44 Fedora 44 / GNOME 50.6 Wayland, physical | 26.1113.4757~nightly-1.fc44 → 26.1114.5000~nightly-1.fc44 | None; English data arrived with the old package via FFmpeg | Expected helper_outdated before login; extension 23 active after login; independent clipboard exact match | met |
| pacman, fourth pass | fresh Omarchy 4.5.0 / Arch Hyprland guest on d69 | 26.1113.4757nightly-1 → 26.1114.5000nightly-1, through omarchy update | tesseract 5.5.3-1; tesseract-data-eng and tesseract-data-afr both 2:4.1.0-5. zxing-cpp 3.1.1-1 already present from old-package GStreamer | One real Copy text hotkey and region selection; independent wl-paste exact 62-character match | met for repository upgrade/dependencies/helper/Copy text; separate CLI/S3 ABI finding remains |

## Pass four: package setup and full ELF audit

Fresh overlay run 17c58d2d-b3c7-45c8-b46e-cb1d8a9860fd, /home/patrick/work/r1428p4/work/lab-runs/a1, made by lab.py from the immutable omarchy-hyprland-20261108 golden. It ran on d69 with its own loopback VNC tunnel and wall tile. No physical desktop was used or locked in this pass.

Setup follows pass three: normally removed the disposable guest's omasnap/LibreOffice and OCR dependencies, verified absence, installed the previous release asset with pacman -U, checked the complete nightly key fingerprint, imported and locally signed it, installed the package-shipped source and Include with PackageRequired DatabaseRequired unchanged. A full transaction preview was reviewed and declined before confirming the native Omarchy updater. p4-prepare-old.txt, p4-old-install.txt, p4-repository-config.txt and p4-transaction-preview.txt retain these receipts.

p4-omarchy-update.ansi and its readable p4-omarchy-update.txt retain the entire native updater transcript. It exited 0, selected default tessdata provider 1 (Afrikaans) automatically through its own --noconfirm, and separately installed hard-required English. It updated the same 14-package set as pass three and performed its normal orphan cleanup and shell restart. Hyprland 0.56.2-4 and quickshell 0.3.2.r7.g2b4501a-1 were unchanged, OpenSSL remained 3.6.5-1, and no reboot was requested. No OMARCHY_ALLOW_DIRECT_PACMAN, added OpenSSL, LD_LIBRARY_PATH, compatibility symlink, package rebuild or binary modification was used.

[p4-elf-audit.md](p4-elf-audit.md) lists **every** package-owned ELF path, including plugins, helper libraries and symlink names under /usr/lib. [p4-elf-audit.json](p4-elf-audit.json) retains full ldd and readelf -d output, return codes, all missing lines and all relevant NEEDED entries per path, plus version checks. There are 54 ELF paths and 30 distinct resolved files. Missing dependencies occur on 29 paths resolving to 13 files. Every missing name is libcrypto.so.4, directly NEEDED in each affected ELF. No package ELF has a libssl.so.4 NEEDED entry.

Affected distinct files:

- /usr/bin/putgd-cli.
- /usr/lib/putgd/libaws-c-auth.so.1.0.0, libaws-c-cal.so.1.0.0, libaws-c-event-stream.so.1.0.0, libaws-c-http.so.1.1.0, libaws-c-io.so.1.1.0, libaws-c-mqtt.so.1.1.2 and libaws-c-s3.so.1.3.1, including their packaged symlink aliases.
- /usr/lib/putgd/libaws-cpp-sdk-core.so, libaws-cpp-sdk-s3.so, libaws-crt-cpp.so, libputgd-s3.so and libs2n.so.1.0.0 (including libs2n aliases).

The resident has no missing ldd dependency and stayed running through the real graphical job. putgd-ocr, putgd-ui, putgd-region and putgd-record each have no missing ldd dependency and each successfully returned --version-json with version 26.1114.5000-nightly / commit df229be2990554bb9c4dff5a020e1407e4eb1885, schema 1 and dirty false. CLI --version-json exits 127 with the known loader error. All other package ELFs had no not-found line, including the Caja/Nautilus plugins and worker executables. Worker executables passing ldd does not establish that their dynamically loaded S3 plugin works: libputgd-s3.so and its AWS dependency chain remain affected. No upload, recording or file-manager functional acceptance is claimed here.

## One Copy text job through the user hotkey

The test used the actual Hyprland session runtime and new private config/data/cache/state directories. Before starting the resident, all resolved socket paths were checked: putgd session.sock 33 bytes, Wayland socket 24, Hyprland command socket 95 and event socket 96; all below 107. The synthetic config has no destinations or credentials and assigns Copy text Ctrl+Shift+9. This is normal app hotkey configuration; the installed resident wrote the runtime Lua binding described in docs/desktops/hyprland.md. No Hyprland configuration file was edited and no direct action dispatch, CLI session call or replacement OCR path was used.

The first binding precheck incorrectly looked for the global action string in hyprctl's JSON. The actual Hyprland binding was present with the correct description, while its dispatcher was __lua with a numeric argument. The driver check was corrected to match `put.gd: Copy text from region` as documented; no key or recognition job had been sent before that correction. The original precheck error, resident log and binding snapshot remain alongside the corrected driver.

p4-hotkey-copy-corrected.txt records resident PID 6079 alive after 5 seconds and still alive after the job; p4-resident-maps.txt preserves its process mapping witness. It confirms the Ctrl+Shift+9 binding. A normal GTK window rendered the three dark-on-white fixture lines at 24 px. Through guest VNC, one physical Ctrl+Shift+9 was sent and one drag selected (110,130)–(650,300). p4-selector.png records the real selector. The independent wl-paste --no-newline readback is exactly:

```text
Repository upgrade test
English text is ready
Copy this region
```

62 characters, with no final newline. p4-fixture.txt and p4-clipboard.txt are byte-identical. p4-result.png shows the fixture and the product notification `Copy text — Copied 62 characters`. The installed helper and selector performed the job; no CLI was used by this driver. No operation ID was requested because the job was triggered by real user input. Exactly one recognition job was run. The fixture and resident were terminated by their owned PIDs afterward.

## Earlier passes and cleanup

[first-attempt.md](first-attempt.md), [second-attempt.md](second-attempt.md) and [third-attempt.md](third-attempt.md) retain all earlier summaries and their then-current limits. All old receipts are kept unchanged. Pass four completes the OCR row via the user-authorized UI route; it does not erase or fix the pre-existing CLI/AWS/S3 compatibility finding.

The fourth guest was stopped and its exact overlay retired through guarded cleanup. p4-retire preserves the completion manifest and p4-retired-run preserves final state, QEMU log and retirement receipt. Its immutable golden was preserved. The temporary tunnel and wall tile were removed. Complete acceptance and audit evidence is being published before exact-file removal of d69's owned ~/repo1428p4 and ~/work/r1428p4 scratch. A subsequent receipt will record completed host scratch cleanup. No physical package state changed in passes three or four; the earlier apt/dnf cleanup state remains documented in the prior summaries. No source edits or release workflows.
