# Issue 1428: repository upgrades, final Omarchy updater pass

Part of #1428. Tested build 26.1114.5000-nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885. Date 2026-11-14. No source changes, new repository tests, subordinate agents or release workflows.

| Cell | System | Old → new | Dependencies installed by upgrade | Copy text | Final acceptance |
| --- | --- | --- | --- | --- | --- |
| apt, first pass retained | d69 Debian 13 / Plasma Wayland, physical | 26.1113.4757~nightly → 26.1114.5000~nightly | tesseract-ocr-eng 1:4.1.0-2; tesseract-ocr 5.5.0-1+b1 | Independent wl-paste exact 62-character match | met |
| dnf, second pass retained | f44 Fedora 44 / GNOME 50.6 Wayland, physical | 26.1113.4757~nightly-1.fc44 → 26.1114.5000~nightly-1.fc44 | None; English data arrived with the old package through FFmpeg | Extension 22 active before upgrade; expected helper_outdated before login; extension 23 active after login and independent wl-paste exact match | met |
| pacman, third pass through omarchy update | fresh Omarchy 4.5.0 / Arch Hyprland guest on d69 | 26.1113.4757nightly-1 → 26.1114.5000nightly-1 | tesseract 5.5.3-1, tesseract-data-eng and tesseract-data-afr both 2:4.1.0-5. zxing-cpp 3.1.1-1 was already present from the old-package GStreamer dependencies | Not run: packaged CLI cannot load libcrypto.so.4, so no recognition request or clipboard comparison was submitted | not met: product CLI runtime failure blocks acceptance |

## Third pass: normal Omarchy updater

Fresh overlay /home/patrick/work/r1428p3/work/lab-runs/a1, run 140e9059-416e-4de5-a85e-4ea32fd16b9c, created by lab.py on d69 from the immutable omarchy-hyprland-20261108 golden. The runner checked resolved socket lengths before boot; the isolated app socket was 41 UTF-8 bytes. Its separate loopback VNC tunnel and wall tile remained active throughout graphical work. No physical builder desktop was used or locked in this pass.

As in earlier passes, normally removed omasnap, LibreOffice and their English/Tesseract/ZXing dependencies in the disposable overlay to establish absence before the old install. The old 26.1113.4757 release asset was installed with pacman -U after syncing the golden's initially missing package databases. Old install brought back zxing-cpp via gst-plugins-bad, but did not install Tesseract or language data. p3-old-prepare.txt and p3-old-install.txt retain the transactions and installed states.

p3-arch-config.sh uses only the old package's shipped key/source files. It checks the full nightly fingerprint 4032E28D893BAF66F4AC23D9A11D38D55536B371, runs pacman-key --add and --lsign-key, copies the .conf at public mode 0644 and adds its Include. SigLevel remains PackageRequired DatabaseRequired. No verification check was disabled. p3-repository-config.txt records the actual matching fingerprint and signing.

A read-only/declined transaction preview (p3-transaction-preview.txt) was inspected before confirming Omarchy's update. It synchronized the signed repository, selected the default tessdata provider and declined package installation. The real update was then run as `omarchy update` in an interactive SSH terminal with the guest's actual Hyprland/quickshell environment. The initial SSH-only launch lacked OMARCHY_PATH and was cancelled at the confirmation screen before an update began; p3-environment-precheck.ansi/.txt preserves that setup error. p3-update-session.py supplies the documented session environment. No updater source, hooks, package requirements or signature policy were changed.

The normal updater's start confirmation was answered Yes. Sudo used the approved shared guest login only in memory through its masked prompt; neither the value nor any private key is in these receipts. The whole updater terminal output is p3-omarchy-update.ansi, with ANSI-stripped readable companion p3-omarchy-update.txt. The updater completed with OMARCHY_EXIT=0. It created a system snapshot, verified signing keys, upgraded its 14-package system transaction, cleaned 33 orphan packages, restarted its shell, checked mise and finished normally. No retry of the actual updater was required.

The updater printed a tessdata provider list and `Enter a number (default=1)`, but its own pacman --noconfirm selected provider 1 (Afrikaans) without waiting for user input. English was separately a hard dependency and arrived too. No manual language package was installed. The recorded package metadata says `Validated By: SHA-256 Sum Signature`. All package keyring/integrity checks passed. OMARCHY_ALLOW_DIRECT_PACMAN was never set; the native updater satisfied its own update guard.

Hyprland 0.56.2-4, quickshell 0.3.2.r7.g2b4501a-1, Omarchy 4.5.0-3, Qt base 6.12.0-3 and xdg-desktop-portal-hyprland 1.4.1-2 remained unchanged. The transaction updated putgd, cliamp, gliff, herdr, mise-bin, owe, superwhisper-bin and yt-dlp, and installed ada/nodejs/simdjson plus OCR/data packages. It requested no reboot; the live Hyprland session survived. Its normal shell restart was recorded. Full package activity, including orphan removals, is retained in the transcript and p3-loader-finding.txt's pacman journal.

## Product finding after successful update

/usr/bin/putgd-ocr --version-json succeeds and reports schema 1, version 26.1114.5000-nightly, packageVersion 26.1114.5000~nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885, tree 72e44106c147d2c855ff55044f59c85ce0b1b113, count 5000, dirty false and sourceProvenance git. Its installed location was obtained from pacman -Ql.

The single planned region-job driver started the installed resident with a fresh private profile. Before submitting a job, its capabilities inspection invoked the installed CLI and received no JSON because the dynamic loader refused the CLI. Subsequent direct read-only commands made the error explicit:

```text
$ /usr/bin/putgd-cli --version-json
/usr/bin/putgd-cli: error while loading shared libraries: libcrypto.so.4: cannot open shared object file: No such file or directory
$ /usr/bin/putgd-cli capabilities
/usr/bin/putgd-cli: error while loading shared libraries: libcrypto.so.4: cannot open shared object file: No such file or directory
```

p3-copy.txt retains the driver error; p3-copy-error.txt records these commands and ldd. p3-loader-finding.txt records that readelf -d lists a direct NEEDED entry for libcrypto.so.4, while the installed system has openssl 3.6.5-1. The putgd package declares an unversioned openssl dependency, satisfied by that package. This is a packaged-runtime compatibility finding; the signed repository upgrade and OCR dependency arrival succeeded.

Stopped at that finding: no manual library installation, symlink, alternate library path, rebuild, alternate updater, ABI bypass or switch to a GUI/hotkey path to make acceptance pass. No recognition operation ID exists and no clipboard readback was taken. Consequently this does **not** establish that the GUI's Copy text action itself fails, nor does it establish a successful OCR/clipboard result on Arch. The row remains not met because the production CLI needed to run the requested acceptance job is unusable.

p3-loader-result.png shows the actual loader error rendered by `/usr/bin/foot --hold /usr/bin/putgd-cli --version-json` in the guest session. It is a failure frame, not a fabricated OCR result. The terminal and resident were stopped by their exact owned PIDs. The driver's secondary None PID reporting error happened during its finally block after stopping the resident; pgrep confirmed no putgd process remained.

## Prior attempts and cleanup

[first-attempt.md](first-attempt.md) preserves the initial pass, including apt's accepted result. [second-attempt.md](second-attempt.md) preserves the corrected Fedora pass and the direct pacman command rejected by Omarchy's own hook. All their receipts remain unchanged. That direct-command failure was a route mismatch, not a putgd failure. This third pass uses the native updater and exposes the separate CLI loader finding above.

The new guest was stopped and its exact overlay retired through guarded cleanup. p3-retired-run retains final state, qemu log and retirement receipt; p3-retire retains the completion evidence manifest. A collection/retirement sequencing error stopped the guest before the final app-log transfer finished: the driver log itself had already been read into p3-copy-error.txt, the failure frame was transferred, and the host-side state was then exported directly. The first guarded retirement refused the not-yet-created manifest; p3-retirement-corrected.txt records the successful corrected cleanup. No failed product operation was retried and no source golden was modified.

The temporary wall tile/tunnel is removed. No physical package state changed in this pass; apt/dnf retain their previously documented cleanup state. The complete new receipts and retirement evidence were published before exact-file removal of d69's owned ~/repo1428p3 and ~/work/r1428p3 scratch. p3-host-scratch-cleanup.txt records the find manifests passed to xargs -0 rm -f and removal of emptied directories; p3-final-state.txt confirms those directories absent and no remaining QEMU process. The isolated guest profile disappeared with its retired overlay. No desktop locks were acquired in this guest-only pass.
