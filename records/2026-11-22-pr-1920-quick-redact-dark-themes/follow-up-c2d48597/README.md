# PR #1920 #1912 file-control follow-up

The ten file controls were rerun on m74, Linux Mint 22.3, using an offscreen editor with a private session socket and D-Bus. Both builds used the original PNG fixtures from the first run. The original pixels matched in every build pair. All whole images are 3840×2160. Each crop is the same window from its paired whole image. Each row has one trailing synthetic token and zero decoys in both sizes.

## Coverage

| Fixture | Crop | Nightly whole / crop | Candidate whole / crop | Whole PNGs | Crop PNGs |
| --- | --- | --- | --- | --- | --- |
| Initial | 1790×1100 | Missed / Missed | Full / Full | [Nightly](pictures/file-whole-nightly.png) · [Candidate](pictures/file-whole-candidate.png) | [Nightly](pictures/file-crop-nightly.png) · [Candidate](pictures/file-crop-candidate.png) |
| V3 | 1790×466 | Missed / Missed | Full / Full | [Nightly](pictures/file-whole-v3-nightly.png) · [Candidate](pictures/file-whole-v3-candidate.png) | [Nightly](pictures/file-crop-v3-nightly.png) · [Candidate](pictures/file-crop-v3-candidate.png) |
| V8 | 1790×488 | Missed / Full | Missed / Full | [Nightly](pictures/file-whole-v8-nightly.png) · [Candidate](pictures/file-whole-v8-candidate.png) | [Nightly](pictures/file-crop-v8-nightly.png) · [Candidate](pictures/file-crop-v8-candidate.png) |
| V9 | 1790×488 | Missed / Full | Missed / Full | [Nightly](pictures/file-whole-v9-nightly.png) · [Candidate](pictures/file-whole-v9-candidate.png) | [Nightly](pictures/file-crop-v9-nightly.png) · [Candidate](pictures/file-crop-v9-candidate.png) |
| V10 | 1790×488 | Missed / Full | Missed / Full | [Nightly](pictures/file-whole-v10-nightly.png) · [Candidate](pictures/file-whole-v10-candidate.png) | [Nightly](pictures/file-crop-v10-nightly.png) · [Candidate](pictures/file-crop-v10-candidate.png) |

The ordered recognized word lists from separate Copy text operations matched in 10 of 10 checks. The record includes both SHA-256 values, word counts, and truncation flags. [Copy text hash check](copy-text-hashes.json) · [Source-pixel comparison](comparison.json)

## Builds

| Build | CLI version | DEB version | Git commit | Git tree |
| --- | --- | --- | --- | --- |
| Nightly | `putgd 26.1122.6439-nightly` | `26.1122.6439~nightly` | `28e9f91060cd10a69921268eefc89e2b6fe4a50e` | `65df546861260bcb92f41ce3f24d3130e90e0c11` |
| Candidate | `putgd 26.1122.6637-dev+gc2d48597a77a` | `26.1122.6637~dev+gc2d48597a77a` | `c2d48597a77a7f604099ea2c6941d5ae5673f1b9` | `e44b87ecf71bccffbcea4e952a8860cf9c8a97a0` |

The candidate came from the Ubuntu 24.04 DEB in [CI run 45081814974](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45081814974). Its SHA-256 is `449ecd3b068ca3139b75c105b0577498ceaf70703fc1b26526d3c13835c60eda`. The live candidate returned the Git tree above through `putgd-cli diagnostics`, matching `git rev-parse c2d48597a77a7f604099ea2c6941d5ae5673f1b9^{tree}`.

## Reproduction and cleanup

Reuse the source PNGs from the [original evidence record](../README.md) or generate them with its scripts and seed. Put the original named fixture PNGs and box manifest in `fixture/` under a short private builder directory. Check the source hashes in [fixture-sha256.txt](fixture-sha256.txt). With the matching package, invoke the original offscreen driver with the follow-up Git tree and the ten scenario names. Use the same editor method for the pixel check and the annotations. The original driver rejects overlong session sockets before launching the app.

```bash
dbus-run-session -- python3 scripts/headless.py "$PWD" BUILD controls \
  file-whole file-crop file-whole-v3 file-crop-v3 file-whole-v8 file-crop-v8 \
  file-whole-v9 file-crop-v9 file-whole-v10 file-crop-v10
dbus-run-session -- python3 scripts/headless.py "$PWD" candidate annotate
```

Both apt transactions were simulated before confirmation and scoped to putgd. m74 was restored to the published nightly, verified by version and source tree, and the desktop lock was released after its cleanup check. [Cleanup receipt](cleanup.txt)
