# Issue 1428 packaging: integration build and package receipts

All five follow-through checks passed for integration commit **bcb868f9ac5b50967976656ed306858f5d8ae72f**, tree `4495eec58fce3a73e7b825d376a9aea9e68b1b57`, version `26.1113.4805-dev+gbcb868f9ac5b`, built by direct integration-branch [CI run 43380438975](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43380438975). This is the actual integration commit identity, rather than a synthetic pull-request merge. [PR 1438](https://github.com/patrick-hudson/put.gd-desktop/pull/1438) was already merged. No product files changed and no new pull request was needed for this follow-through.

The run completed successfully: all six package builds, SBOM, source collection, Arch install, AppImage PipeWire, contracts, both Linux builds, sanitizers and CI summary passed. Three jobs were intentionally unselected (`prune caches`, the independent `pipewire` path, and release `collect`). See [CI results](integration-ci-result.json) and [artifact identities](integration-artifacts.json). The application source was rebuilt on CI; containers, mounted-image checks and native measurements ran on k72; the independent STABLE scan ran on d69. No GUI, resident session or desktop acceptance was attempted here.

## 1. Whole-image and native sizes

| Whole AppImage | CI run | Commit | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Recorded nightly-head baseline | 43355658846 | 466449a4c69a07a1997668d1b70d637abac76a16 | 158030328 | 12d7dc466793ad7807b81788207c23d27cdf84ffeabb2e83043593a697b977f4 |
| Integration | 43380438975 | bcb868f9ac5b50967976656ed306858f5d8ae72f | 164518392 | bbf92855d0264ae60de22a9f8a2c7f68197c86079f5706666f9440d240f152d5 |

The **whole-image increase is 6488064 bytes (6.488064 MB), below the 12000000-byte target**. This includes all integration changes relative to nightly. It is not an estimate from the OCR library files. See [size and exact-package bindings](size-and-package-binding.json), [baseline receipt](nightly-head-baseline.json), and the chart in `sizes.html`.

A no-Recommends DEB comparison against that exact nightly-head installation adds **13220 KiB / 13537280 bytes**, including putgd's own 2388 KiB increase and the newly needed runtime dependencies. Recording Recommends are byte-for-byte unchanged: `gstreamer1.0-plugins-ugly, gstreamer1.0-libav, gstreamer1.0-vaapi, gvfs-fuse`. ZXing already belonged to the nightly install, so its cost is included separately in the clean-system figures below. [Native comparison](native-integration-size.json).

| Fresh install kind | Explicit OCR engine/data package payload bytes | Full putgd install added above the clean base, bytes |
| --- | ---: | ---: |
| Ubuntu 24.04 DEB | 11283456 | 1080402944 |
| Fedora 44 RPM | 12387251 | 1168289605 |
| Arch pacman, including ZXing's required zint | 35214737 | 1706267697 |

These are package-manager uncompressed installed-size metadata, excluding download caches; they are not physical filesystem allocation. The middle column is the named engine/data set, not its entire transitive dependency closure. On Ubuntu, adding libarchive13t64 and libgif7 brings that set to **12283904 bytes**. The final column includes putgd, its bundled Proton runtime and every newly required package. Raw before/after inventories and `*-all-installed-sizes.json` retain the basis.

Arch's English data package alone is **23466654 bytes**. Consequently the plan's provisional roughly-12-MB native package estimate does **not** hold on Arch. No package/data selection was changed to meet an estimate.

## 2. Mounted AppImage, empty helper environment

[Mounted-image receipt](mounted-appimage-receipt.json) and [replay script](mounted-audit.py). The exact integration CI AppImage above was mounted read-only through its real AppImage/FUSE runtime on k72, at a new `/tmp/.mount_...` path. Mounting used only `PATH=/usr/bin:/bin` to locate fusermount. The helper `--version-json`, ldd resolution and each engine's transitive resolution used **`env={}`**, without `LD_LIBRARY_PATH` or Qt overrides. The helper's identity matched the CI manifest and its own RUNPATH was `$ORIGIN/../lib`.

All engine paths resolved inside the mounted image: `libtesseract.so.5.5`, `libleptonica.so.6`, `libZXing.so.4`. The same existing whole-AppImage ownership policy was reused for the other mapped libraries. Base host libraries such as libc, libm, libstdc++, libgcc_s, libz, libpthread and libdl remained host provided. No engine, codec, network, archive or OpenMP library fell back to the host; the three minimal engine closures contain none of those forbidden additions. The receipt includes all 18 named helper resolutions, raw ldd output including the interpreter, engine hashes, complete notice/inventory audit, and English data SHA-256 `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2` at `usr/share/putgd/tessdata/eng.traineddata`.

The final receipt confirms **unmounted=true**. Harness failures and corrected commands are retained below; they did not require a product change.

## 3. Six SBOMs and STABLE rehearsal on d69

[Independent STABLE receipt](stable-integration-receipt.json), [summary](stable-policy-bcb/vulnerability-summary.md), [classified report](stable-policy-bcb/vulnerability-report.json), [six raw Grype results](stable-policy-bcb/), [six CycloneDX files and receipts](integration-sboms/). Every SBOM hash and installer hash was independently bound to the downloaded integration artifacts before scanning. The exact AppImage was also copied to d69 and its SHA-256 matched its SBOM.

Locked Grype **0.121.2**, Syft **1.57.0**; current listing refreshed during the rehearsal. Database schema v6.1.10, built **2026-11-12T06:20:58Z**, archive SHA-256 `c98bd6bd207590fa04c8e2fea3db1859f7f952b57400fc62e19f517f1b562f5e`. Policy SHA-256 `f759c346c86830bf44db9f93923525058a7fc7f33584b1f7df7c253a09b7ffc3` matches the integration checkout unchanged.

**Exit 0; STABLE blocking policy active; zero flagged/blocking findings.** The AppImage has 176 components and 163 findings (9 high, 138 medium, 16 low). Six existing findings retain their pre-existing scoped acceptances; the other high findings have no fix. Each of the five native package SBOMs has 25 bundled components and zero findings. No finding names Tesseract, Leptonica, ZXing, libzueci, tessdata_fast or qrcodegen. **No new policy acceptance was needed.** The native libraries belong to the distribution; these SBOMs/gates cover bundled code rather than the container's whole OS.

The AppImage SBOM includes Tesseract 5.5.4, Leptonica 1.87.0, ZXing-cpp 3.1.1, tessdata_fast 874164186573, embedded libzueci 1.0.1 and qrcodegen 1.8.0. Every native SBOM includes qrcodegen 1.8.0. The `--release-tag v26.1113.4805` argument selected STABLE policy for rehearsal only: no Git tag or release was created or published.

## 4. Actual rebuild of the extracted final source archive

[Source rebuild receipt](source-rebuild-receipt.json), [CI results](integration-ubuntu24.04/source-build-results.json), [parameters](integration-ubuntu24.04/source-build-parameters.json), [build log](integration-ubuntu24.04/source-build.log), [archive manifest](integration-ubuntu24.04/source-archive.json).

CI's final archive is `putgd-26.1113.4805-dev+gbcb868f9ac5b-source.tar.gz`, **24463898 bytes**, SHA-256 **af137bf6eed102f6094b5e7083b34867d72cdeb7edbc25e90f261978ed722c4c**. CI extracted it into a directory without `.git` and ran normal release configure/build with `PUTGD_OCR=ON`, bundled Proton and offline pinned Proton source inputs, using the provisioned official AWS SDK. This was a real compile/link, with the normal compiler cache, not the PR-only inputs/dry-run check.

The rebuild passed in **541.406889104 seconds**. All ten product programs, including putgd-ocr, returned the supplied archive identity at bcb868f9a/tree 4495eec5/count 4805. The rebuilt Proton helper matched the manifest and installed bundled hash. Every archive member was independently checked against the archive manifest afterward; the receipt explicitly lists the vendored QR files, dependency lock/verifier, OCR CMake file, pins, configure/provisioning tools, compliance templates and build instructions.

## 5. Clean installs with optional dependencies disabled

[Clean-install receipt](clean-install-receipt.json), replay scripts `pg1438-clean-install-{deb,rpm,arch}.sh`, logs `*-clean-install.log`, before/after inventories and dependency query outputs are retained here. Each base had none of Tesseract, Leptonica, ZXing or English data before the actual putgd installer was installed.

| Kind | Base image digest | Install | Required data |
| --- | --- | --- | --- |
| Ubuntu 24.04 DEB | sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55 | apt-get install --no-install-recommends | /usr/share/tesseract-ocr/5/tessdata/eng.traineddata |
| Fedora 44 RPM | sha256:43b29f65a41eb9c35e1cd5323e3bdf3b655c2357a9f4f1ff2f9c2798e5045d80 | dnf install --setopt=install_weak_deps=False | /usr/share/tesseract/tessdata/eng.traineddata |
| Arch pacman | sha256:823e937464d1528b306a8e1137ef406b9c56e5fee43c7a19e93684d554af74e1 | pacman -U, required dependencies only | /usr/share/tessdata/eng.traineddata |

Arch's disposable rolling base was updated before the recorded no-OCR pre-install snapshot; no host was upgraded. Package metadata proves the English hard dependencies (`tesseract-ocr-eng`, `tesseract-langpack-eng`, `tesseract-data-eng`) beside the generated library requirements. All three exact CI packages installed successfully, putgd-ocr answered with bcb868f9a under an empty environment, all its libraries resolved, and the English data file was readable and hashed. Nayuki's MIT notice was present (the Docker DEB base excludes standalone docs, but retains the full DEP-5 copyright notice).

The checks cover one fresh representative per native package kind. They do not claim graphical acceptance or signed-repository upgrade/publication. Full application processes were not started, so these probes did not create a putgd Unix session socket; helper version queries exit before confinement or descriptor handling.

## Harness corrections and cleanup

The first DEB preflight used an incorrectly quoted dpkg format (`Bad substitution`). `fresh-preflight.sh` records the corrected literal-format query and confirmed the base had no OCR packages before installation.

The first AppImage mount used env={} for the mount runtime too and failed `No suitable fusermount binary found on the $PATH`; its receipt/log/script are retained. The correction supplies only a system PATH to the mount runtime, keeping every helper and loader query empty. The first cleanup checked the mount before asynchronous FUSE exit; the next attempted unmount while the runtime still held it and got `Device or resource busy`. The exact owned runtime PID/start time was inspected and retired (`own-mount-retire.py`, `mount-cleanup-retry.json`). The final replay waits for runtime exit and FUSE completion; its receipt confirms the mount is gone. Earlier scripts and the completed measurement before the cleanup retry remain alongside it.

The first combined native size collector encountered Arch metapackages with an omitted SIZE field (`KeyError: SIZE`). The original collector and error log are retained; the corrected collector treats those empty metapackages as zero bytes. The actual OCR package sizes all have explicit SIZE values.

[Cleanup receipt](cleanup-receipt.json): only the four exact disposable packaging containers were stopped and removed after exporting evidence. No build server desktop, other project, shared image/cache, input package, source tree or raw scan was removed. No AppImage mount remains. Full installers, source inputs and private working records remain on k72 under `~/work/ocr-integration-bcb-artifacts`; scan inputs/tools/database and raw reports remain on d69 under `~/work/ocr-pkg-1438-scan`. Older compiled output was archived with verified restore indexes in the separate #1438 work directories.
