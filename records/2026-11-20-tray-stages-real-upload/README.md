# Physical tray activity with live S3 uploads

PR #1755 candidate `a6e5399f2ac8db293d329ee43cfa2051ac39257d`, tree `75d0000c0a253bcc5be8b553f4f6fdc1f06aa098`. The manual CI run passed and supplied the native DEBs and RPM. Each physical resident reported the exact commit and tree through `putgd-cli ui.snapshot`. The local date was November 20 on every host, with the calendar-selected turkey and the dark-panel tint set. Timestamps in diagnostic receipts are UTC. [Candidate PR](https://github.com/patrick-hudson/put.gd-desktop/pull/1755) · [Manual CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44847506375)

| Host | Active native session | Package SHA-256 | Running build |
| --- | --- | --- | --- |
| k72, Kubuntu 26.04.1 | Plasma 6.6.6, Wayland, seat0 session 509 | `57bff12a37dd4fca2d3d9f0d27bf1bd54ee5a0cb05b0ca5acb5ed4ac72f9cfd9` | [Diagnostics](k72/build.json) |
| m74, Linux Mint 22.3 | Cinnamon 6.6.9, X11, seat0 session c89 | `cdee62d21584326fa1e03e8c993b79b05c407803c3ca2e96b88abb8e6f73315d` | [Diagnostics](m74/build.json) |
| f44, Fedora 44 | GNOME Shell 50.6, Wayland, seat0 session 21444 | `50eac340497261e2614a29405e2e172678afdb46d30adb0e4da2ba82ee6b5ab5` | [Diagnostics](f44/build.json) |

## Results

| Requested scenario | k72 Plasma Wayland | m74 Cinnamon X11 | f44 GNOME Wayland |
| --- | --- | --- | --- |
| 1. Region hotkey, small real S3 upload | PASS · five stages, checked turkey | PASS · five stages, checked turkey | PASS · five stages, checked turkey |
| 2. Larger real S3 upload | PASS · 6 MiB retry, fill rises visibly | PASS · 24 MiB, fill rises visibly | PASS · 24 MiB, fill rises visibly |
| 3. Failed upload, expiry, attention row, recovery | FAIL · stuck blue after terminal failure, recovered on new upload | FAIL · stuck blue after terminal failure, recovered on new upload | FAIL · stuck blue after terminal failure, recovered on new upload |
| 4. Local-only save | FAIL · Saved and check appeared, Processing skipped | FAIL · Saved and check appeared, Processing skipped | FAIL · Saved and check appeared, Processing skipped |

The region test used Ctrl+Shift+1 through each builder's native RFB input and dragged over the maximized synthetic fixture. Tray diagnostics recorded Capturing → Processing → Uploading → Complete → Idle. The actual StatusNotifier item reported “Upload complete” and the turkey stayed visible with a lower-right check for 1.501 seconds. An authenticated S3 GET matched the local PNG's SHA-256. Fast stages on Plasma and GNOME were also sampled through a dedicated continuous RFB connection to distinguish the upload frame from the later check. [Kubuntu capture](k72/region-tray-history.json) · [Mint capture](m74/region-tray-history.json) · [Fedora capture](f44/region-tray-history.json)

Early and late physical frames show the green fill climbing. The comparison counts, using a six-unit RGB tolerance around the selected palette colour, were 72 → 100 green pixels on Plasma, 15 → 127 on Cinnamon, and 4 → 59 on GNOME. The real StatusNotifier pixmaps and tooltip progress are in each host's large-upload tray history. Each completed larger object was independently retrieved from S3 and matched the synthetic file byte for byte. [Kubuntu progress](k72/large-upload-tray-history.json) · [Mint progress](m74/large-upload-tray-history.json) · [Fedora progress](f44/large-upload-tray-history.json)

## Failed upload left Processing on screen

Each isolated failure used a second S3 profile with a loopback endpoint whose port refused the connection. Each operation finished `partial`, with a saved local copy and an upload marked `failed` with `s3_transport_unknown`. No other upload was active. The tray history stopped at Capturing → Processing. The blue turkey and “Processing” tooltip persisted through the last observation 16.2–16.4 seconds after the Processing transition on each desktop. The failure badge and the expected timed transition to idle were absent.

| Host | Capturing timestamp | Processing timestamp | Last observed still Processing | Menu attention row |
| --- | --- | --- | --- | --- |
| k72 | `01:23:08.230Z` | `01:23:08.481Z` | `01:23:24.754Z` | Failed uploads (4) |
| m74 | `01:23:14.070Z` | `01:23:14.321Z` | `01:23:30.478Z` | Failed uploads (4) |
| f44 | `01:21:44.015Z` | `01:21:44.266Z` | `01:22:00.658Z` | Failed uploads (3) |

Menu request counts stayed unchanged throughout the wait. The failure row remained visible in the menu served by every resident and was photographed in the Cinnamon and GNOME menus. A new file upload replaced the stalled indicator, showed all five stages, and was verified by authenticated S3 GET on all three hosts. [Kubuntu failure and tooltip](k72/failure-timing-and-menu.json) · [Mint failure and tooltip](m74/failure-timing-and-menu.json) · [Fedora failure and tooltip](f44/failure-timing-and-menu.json)

## Local-only save skipped Processing

We removed all destinations and kept local copies on. The two hotkey saves per desktop ended `completed`, with `uploadStatus: local_only` and a `saved` local result. Each tray history showed Capturing → Complete → Idle. The complete stage displayed “Saved” with a green turkey and a lower-right check for about 1.5 seconds. There was no Processing transition in either attempt on any desktop. The table records a failure because the stage contract calls for Processing while saving the local copy, even though the completion state was correct. [Kubuntu history](k72/local-save-tray-history.json) · [Mint history](m74/local-save-tray-history.json) · [Fedora history](f44/local-save-tray-history.json)

## Campaign conditions

The completed live uploads used unique prefixes and expiring S3 links. The first setup attempt used private-publication mode, which this S3 provider refuses during admission. That setup mistake was corrected before the scored live runs. All three desktops rendered the same dark-panel palette. The acceptance run covers the requested tray scenarios on physical sessions, including the optional GNOME desktop.

## Kubuntu transport comparison

The initial candidate 24 MiB transfer ended `partial` with `uploadStatus: unknown` and `publication_unknown`. A 6 MiB candidate retry showed visible progress and verified at S3. A separate candidate run then completed the original 24 MiB payload and independently verified it at S3. The same 24 MiB payload on the published nightly reproduced `partial`, `unknown`, and `publication_unknown`. The comparison ran the uploads serially on the same Plasma desktop, with a fresh S3 prefix for the nightly. The nightly build came from the published native Kubuntu DEB and its SHA-256 matched the release's manifest. [Published nightly](https://github.com/patrick-hudson/put.gd-desktop/releases/tag/v26.1120.5875-nightly) · [Comparison receipts](k72/transport-comparison/)

## Cleanup

The campaign removed 17 test objects and verified every test prefix and multipart listing was empty. The nightly comparison prefix was empty on inspection. We deleted the exact temporary keychain references, private profiles, runtime sockets, and synthetic payload files. Candidate packages were removed, and Fedora's AppIndicator settings were restored. All desktop leases passed the cleanup check before release. [Cleanup receipts](cleanup.json)
