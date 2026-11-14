# Issue 1428: signed repository upgrade, 2026-11-14

Part of #1428. One scoped acceptance run, no source changes, no release workflows.
Worktree was fetched and detached at origin/nightly df229be2990554bb9c4dff5a020e1407e4eb1885, in /home/patrick/.t3/worktrees/put.gd/t3-1a9774c3-82713d5e40a2c7a7. Published build: 26.1114.5000-nightly, same commit.

| Cell | System | Version before → after | New packages in upgrade | Copy text | Result |
| --- | --- | --- | --- | --- | --- |
| apt | d69, Debian 13, Plasma Wayland, physical | 26.1113.4757~nightly → 26.1114.5000~nightly | tesseract-ocr-eng 1:4.1.0-2, tesseract-ocr 5.5.0-1+b1 | One region job; independent wl-paste exact 62-character match | met |
| dnf | f44, Fedora 44, GNOME 50.6 Wayland, physical | 26.1113.4757~nightly-1.fc44 → 26.1114.5000~nightly-1.fc44 | None; the old install already pulled tesseract-langpack-eng 4.1.0-12.fc44, tesseract-common and tesseract-libs 5.5.4-1.fc44 through FFmpeg | One region request rejected with gnome_login_required; no OCR or clipboard match | not met |
| pacman | fresh Omarchy 4.5.0 / Arch Hyprland overlay on d69 | 26.1113.4757nightly-1 → unchanged | None; upgrade failed target not found; old install pulled zxing-cpp 3.1.1-1 through gst-plugins-bad | Not run: old build has no helper | not met |

## Receipts and limits

The apt receipts contain the removal, old asset install, shipped inline-key nightly source, apt update, reviewed simulation, complete actual transaction, helper identity and graphical operation. apt accepted the nightly InRelease and package hashes with its normal signature policy. No checks were disabled. The helper is /usr/bin/putgd-ocr, located from dpkg -L.

The dnf receipts contain the reviewed removals (--noautoremove), old install, shipped repo file, reviewed upgrade and complete actual transaction. Its shipped configuration is gpgcheck=1 and repo_gpgcheck=0. The signed RPM passed Verify package files with no override. The local GitHub old RPM used the default local-file policy (dnf explicitly reported skipping OpenPGP for @commandline); this is distinct from the signed repository upgrade. No check was disabled by the run. rpm -V putgd was clean after upgrade. The helper is /usr/bin/putgd-ocr, located from rpm -ql.

Both successful helper --version-json invocations returned schema 1, version 26.1114.5000-nightly, packageVersion 26.1114.5000~nightly, commit df229be2990554bb9c4dff5a020e1407e4eb1885, tree 72e44106c147d2c855ff55044f59c85ce0b1b113, count 5000, dirty false and sourceProvenance git. Contrary to the brief, this command does not print engine versions. capabilities also returned an empty engines object. No engine version is inferred from that output.

Fedora started with no putgd and had English data removed (including its reverse dependencies) before the old install. That old install reintroduced English data. The post-upgrade GNOME session reported installed extension 23, loaded 0 and gnome_login_required. This was a newly installed old package without an intervening login, not evidence of a regression from loaded extension 22. No logout or extension workaround was used to turn the result into a pass. The fixture frame was saved; the failed request had no operation ID. Clipboard readback was not performed after rejection, to avoid reading unrelated pre-existing desktop content. Thus the requested Fedora exact-match witness is absent.

Omarchy initially had English data, Tesseract and ZXing. Removed omasnap, libreoffice-fresh and those dependencies normally, without --nodeps, in the disposable overlay; recorded their absence before installing the old package. The old asset installed normally after syncing the golden's initially missing package databases. It ships /usr/share/putgd/repo/putgd-nightly.conf (PackageRequired DatabaseRequired), but does not activate /etc/pacman.d/putgd.conf, add its Include or import its key. The literal requested pacman -Sy putgd then returned `error: target not found: putgd`. No active put.gd repository was added afterward. This is the direct release-asset installation route; the documented web installer separately configures the repository, and that route was not tested. No signed pacman repository verification or new helper/OCR claim is made.

## Fixture and graphical evidence

The normal fullscreen GTK fixture rendered DejaVu Sans at 24 px, dark on white:

```text
Repository upgrade test
English text is ready
Copy this region
```

apt text.recognize source=region, copy=true used the real selector, driven with RFB pointer events at (110,130)–(650,300). Operation aeae6802-7cc5-4eb7-9df1-7a72425348ec completed, copyStatus copied, English, 62 characters; wl-paste --no-newline returned exactly the fixture (no final newline). No upload or destination configuration. Only one recognition job was submitted per physical cell; prior attempts failed fixture/environment prechecks before submission. Fedora's one submitted request was rejected immediately. Frames are fixture-only crops made on the hosts, after checking that the crop was at least 90% white. Failed prechecks wrote no desktop frame. The Arch frame shows the disposable guest, not OCR evidence.

## Lab setup corrections

Original failures are retained. Debian's old gh download lacked authentication; public curl succeeded. The stale d69 runner lacked the Omarchy profile, so current tools were copied into isolated ~/work/r1428. Its first launch refused because the copied tools lacked the socket-check utility; copying that utility allowed the corrected a2 launch. No overlong socket was bypassed; physical runtime sockets were 41 UTF-8 bytes and the VM runner checked all its paths before boot. An absent rfb module in the first graphical attempt left two owned processes; their exact PIDs were stopped. Absolute Wayland display paths fixed private-runtime connectivity. Stale VNC streams on both physical desktops were restarted through their existing user services. No compositor/session restart occurred.

One third-party COPR refresh error contained an expiring presigned mirror URL. The URL is redacted in the receipt; the error text and complete package transactions are otherwise retained. No credentials, package payloads, VM disks or keys are included.

## Cleanup and retained changes

Both desktop locks were released before 12:15 UTC; no test resident, UI or fixture remains. The lock guard treats a newly installed putgd package as leftover, so putgd was removed from both hosts after testing (both had no installed package at the start). Debian retains English data and tesseract-ocr, and the residual nightly apt conffile/key. Fedora's removed FFmpeg/Tesseract development packages were restored; dependency resolution advanced FFmpeg packages from 8.1.3-1 to 8.1.3-2.fc44 and gstreamer1-plugin-libav from 1.28.8 to 1.28.9. No compositor or desktop package changed. dnf invalidated a pending lab offline transaction, as its receipts state; no full update was run.

The sole booted guest (run 6635f2d3-a34c-4f87-a841-01e08c28e38d) was stopped and its exact overlay retired by guarded cleanup with a completion evidence manifest. First cleanup refused the external golden root; corrected --images-root succeeded. Its golden was preserved. The temporary VM tunnel and wall tile were removed. Private raw receipts, drivers, downloaded old assets and isolated profile directories remain under ~/repo1428 and /tmp/r1428-* on their respective hosts; isolated runner metadata remains under d69 ~/work/r1428. No idle guest or forwarding process remains. No source edits, commits or PRs in put.gd-desktop.
