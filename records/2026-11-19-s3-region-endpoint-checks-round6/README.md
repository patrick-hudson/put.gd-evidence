# S3 Region and Endpoint checks, review round 6 (#1675, #1676)

One picture for the last Sol round's conflict case on #1688. This record continues
`2026-11-19-s3-region-endpoint-checks-round5`.

## Build

put.gd-desktop `fix/s3-endpoint-path-1676` at `c3d5a417b`, stacked on
`fix/s3-region-name-1675` at `545392f39` (on nightly `f3f67d5df`). Dev build (AWS SDK
1.11.924) synced without `.git`, so the footer reads `0.0.0-dev.unknown`.

## Picture (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

`01-conflict-and-refused-file-both-shown.png`: a private resident shows an "Other
S3-compatible" destination. "pending-folder" is typed into Folder in bucket and not yet
saved. Then the configuration file is edited outside put.gd so the destination's Region is
blank, and the resident refuses the reload. The conflict banner ("Settings changed
elsewhere…") and the line "The configuration file wasn't loaded: …" are both shown. The
pending edit stays in the field. Before this round the conflict hid the file line.
