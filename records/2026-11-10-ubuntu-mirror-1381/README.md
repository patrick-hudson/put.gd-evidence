# Ubuntu container mirror throughput (#1381)

Repository: patrick-hudson/put.gd-desktop. PR https://github.com/patrick-hudson/put.gd-desktop/pull/1382, final source head 1fb7616007565d91d99f2acac3d70ab1e1385bdc. Final CI: https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42748578866.

The four bare-container probes each GET at most 2 MiB from Ubuntu's base noble `pool/main/g/glibc/libc6_2.39-0ubuntu8_amd64.deb`, with a three-second timeout and 0.2-second kill grace. The package is still referenced by noble/main; its availability and actual 2 MiB transfers were verified on d69. Sequential worst-case probing is approximately 13 seconds and 8 MiB of response bodies. At the 1 MiB/s floor, a 483 MiB dependency download takes approximately eight minutes, leaving room in the existing 20-minute install step. Partial bodies count toward measured throughput; HTTP errors and zero-byte/stalled responses rank last. All candidates remain in the explicitly prioritized mirror+file list, including an all-slow set. APT still verifies all metadata/packages with Ubuntu's keyring; samples are ranking hints only.

## Focused regression on d69

Host: Debian 13 builder patrick@192.168.68.69, SSH only, no desktop use or lock. Scratch directory: ~/work/ubuntu-mirror-1381. Python 3.13, distro bash/coreutils. No workstation build, packaging, ctest or VM work. These tests use TCP HTTP fixtures only, with no app launch or Unix sockets.

`python3 -m unittest discover -s tests/ci -p test_ubuntu_mirrors.py -v`: six pass in 11.571 seconds (`focused-tests-payload.log`). HTTP fixtures answer HEAD 200 and serve fast indexes even when package payloads are throttled. The test script substitutes loopback endpoints/ports into the old and new snippets, avoiding external network access in the regression.

The three new tests replayed against origin/nightly cdac6e4b3174b59e0292b2a16af9abdd110e7514 all fail (`baseline-final.log`): slow-first ordering, missing dead-mirror speed diagnostic, and all-slow ordering. The fast-index/slow-payload case also fails against the first implementation (`metadata-regression.log`). Initial fixture results and an intermediate fixture typo are retained in the source history/run context; the typo was corrected before final validation.

## Failure that improved this fix

The original run 42737959530 attempt 1 selected us.archive after HEAD 200; sanitizers fetched metadata at 71.1 kB/s and then requested 514 MB. See `incident-attempt-1.log`.

The original us.archive incident was not reproduced live. However, the first PR implementation sampled Packages.xz, and run 42745955621 at 010480922e7e5c1b8ffd029a68b573a319cee836 exposed another live failure: Azure served that metadata sample at 35,029,000 B/s, then the linux24 package transfer crawled until the 20-minute step timeout. Its full failed job log is preserved in `metadata-probe-linux24-timeout.log`. Other `metadata-probe-*.log` files belong to that superseded implementation, not final acceptance. That run's remaining work was cancelled after the failure, and final acceptance uses the new full run above.

This is why the final probe downloads a package payload instead of an index. Ranking remains a bounded point-in-time hint, not a guarantee against later changes or per-object variability.

## Scope and cleanup

Snapshot sharing was assessed, deferred: linux/sanitizers install before checkout and use different dependency sets. Reuse requires changing bootstrap order and snapshot retention, plus cache compression/path handling, rather than simply adding a restore step. The hosted helper uses fixed archive preference without measuring throughput, so it shares that weakness; it remains unchanged with bounded package attempts and existing snapshot fallback.

No product behavior or desktop surfaces changed; graphical acceptance was not run. No docs changed. Issue closure/merge belongs to the coordinator. Final run results and cleanup receipt follow below.


## Final-head measurements

| Job | APT package fetch | Context |
| --- | --- | --- |
| linux (24.04) | 483 MB in 47 s (10.3 MB/s) | cold install |
| linux (26.04) | 529 MB in 43 s (12.4 MB/s) | cold install |
| sanitizers | 514 MB in 29 s (18.0 MB/s) | cold install |
| package Ubuntu 26.04 bootstrap | 25.0 MB in 2 s (12.7 MB/s) | bootstrap before checkout |
| package Ubuntu 26.04 dependencies | 1002 kB in 0 s (2746 kB/s) | warm snapshot, 1002 kB/560 MB; APT rounds seconds |

The annotated PNG is a rendering of the exact retained log lines with labeled before, intermediate failure and after panels. It was rendered on d69 with distro Pillow, then visually inspected on the workstation. The plain-text log excerpts retain timestamps. The package cache hit is explicitly identified rather than counted as a cold throughput benchmark.

Source export `d69-test-source.tar` has SHA-256 `5efb05bee4a374bc59b4572684344b3a258732f2302b19e4a1a2bc9c2424cf93`; `d69-test-source.index` lists its paths. Restore in a new empty directory with `tar -xf /path/to/d69-test-source.tar`. `baseline-replay.py` and `metadata-replay.py` reproduce the regression checks from that tree. `cleanup.txt` records exact-file cleanup after the same archive checksum was verified on both d69 and the workstation. No lab resources remain.


Final full CI and the required CI summary passed at source head 1fb7616007565d91d99f2acac3d70ab1e1385bdc; every selected job succeeded (release-only collect was not selected). The blocking `gh run watch 42748578866 --exit-status` returned 0. CodeRabbit review 5836326579 covers this head: no code findings or Outside diff range comments; generic docstring-coverage advisory only. Review-thread snapshot has zero threads.
