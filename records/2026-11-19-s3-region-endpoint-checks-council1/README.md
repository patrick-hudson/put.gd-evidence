# S3 Region and Endpoint checks, council round 1 (#1675, #1676)

One picture for council round 1 on #1688 (C7). This record continues
`2026-11-19-s3-region-endpoint-checks-round6`.

## Build

put.gd-desktop `fix/s3-endpoint-path-1676` at `205ac89e039f5baf8f56e28b09be1a5b4aff8f82`, stacked on
`fix/s3-region-name-1675` at `b5fde0eedb1273175dde004f1ea7f52bbad2a9b7` (on nightly `f3f67d5df`). Dev build (AWS SDK 1.11.924)
synced without `.git`, so the footer reads `0.0.0-dev.unknown`.

## Picture (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

`01-settings-opened-with-refused-file.png`: with put.gd closed, the configuration file was
edited so the only destination's Region was blank, and then put.gd was started. The
resident refused the file. The Settings page shows "The configuration file wasn't loaded: …"
in its footer from the moment it opens.

On the Destinations page, with no accepted destination, the existing empty-state page ("No
destinations yet") replaces the destination content and its footer, so the line isn't shown
there. That layout predates this change and wasn't altered.
