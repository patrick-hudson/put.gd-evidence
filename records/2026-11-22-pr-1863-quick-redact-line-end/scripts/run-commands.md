# Builder commands

Use the workstation checkout's `tools/lab/desktop_lock.py` for lease acquisition, heartbeat, guard and the two-step clean release.
Use `remote.sh` for the pinned, non-interactive SSH transport.
Stage `desktop.py`, the matching `crops-HOST.json`, and the test DEBs under the private `/tmp/qr1863` directory on the builder.

Read `apt-get -s --no-install-recommends` for each putgd install or removal before the actual transaction. Mint nightly came from the pinned publication in APT, version `26.1121.6060~nightly`. Kubuntu nightly came from the native ubuntu26.04 asset in the same published tag. The candidate DEBs were downloaded from run 44992999617 with `gh run download 44992999617 -p 'release-native-ubuntu*'`.

For each run, put the guard before the remote driver. For example:

```sh
python3 tools/lab/desktop_lock.py guard k72 --session codex-qr1863 &&
  ./remote.sh k72 'umask 077; python3 /tmp/qr1863/desktop.py k72 nightly-clean 1 2 3 4 5-jwt 5-jwt-labeled 5-hex 5-hex-three 6'
```

The driver creates a fresh private runtime directory and checks its exact UTF-8 socket pathname before starting the resident. It invokes `diagnostics` and retains its `build` member, then takes each desktop capture with the private resident and the installed production CLI. The saved images use the explicit crop rectangles in `crops-*.json`. Run `verify.py RUN_DIRECTORY scripts/regions-HOST.json` against each evidence directory. The verifier uses reference rectangles in desktop coordinates registered against the visible fixture in the source captures.

On Mint, initial fixture probes found a missing local output setting, then an absent settings revision on clean start, then a missing `publicationMode` in the proposed default output. The driver now enables local-only output under its private root with complete settings before capture. The next probe showed that xed opened narrower than the requested width and Firefox needed a readiness check, which were fixed by the owned-window geometry and activation commands in the driver.

On Kubuntu, the first fixture probe found that Kate detached and the KWin script's Qt rectangle constructor was unavailable. The corrected driver adopts the exact Kate child and uses KWin's rectangle object assignment. Another session used the desktop during the first nightly run, including changing the installed package during case 6. The verification run repeated the full matrix after that session left and the published native nightly was reinstalled. The interrupted case metadata was kept for audit outside the reported matrix.
