# Destination status acceptance on Aurora

**Blocked at the storage preflight on 2026-11-19.** The target was the physical
Aurora Fedora 45 builder (aurora-amd), image `testing-45.20261101.2`, with an
active, unlocked Wayland session and Plasma and KWin 6.8.2. See
[issue #1692](https://github.com/patrick-hudson/put.gd-desktop/issues/1692) and
[PR #1695](https://github.com/patrick-hudson/put.gd-desktop/pull/1695).

The read-only preflight measured 10,079,412,224 available bytes (9.39 GiB)
and 29,386,103 available inodes on the host filesystem containing
`/var/home/patrick`. The lab requires at least 10 GiB (10,737,418,240 bytes)
before a graphical campaign. A second reading returned the same values.
The desktop lock was free. The campaign stopped before lock acquisition, app
launch, desktop interaction or credential access.

## Target build

The lab tools came from `origin/nightly` at `ead0376f3` in the assigned test
worktree. The AppImage was downloaded locally from the `release-appimage`
artifact of [CI run 44477653690](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44477653690).
The run's PR head was `a86fbe882f94f8eb271b4b2b8b9e3a0f8824e6d5`. The
artifact's build metadata lists version `26.1119.5622-dev+g860a6b5b9458`,
commit `860a6b5b9458746990780bc8d5fef08b51c5675c`, and tree
`d9a194de6ac3243306fd4f2bb8fdf6cc4f29413b`, which matches the PR head's tree.
The AppImage SHA-256 was
`b572c7aa16bc11cd5f5d44e6c79d6706ffb3b949a45cd9edd2c9bd636f188af6`.
Running-build diagnostics were unavailable because the AppImage was never started.

## Checklist

| Step | Expected | Observed |
| --- | --- | --- |
| 1. Add destination and test | Connected. `destinationStatus` is `passed`, source `test`. | Blocked before execution |
| 2. Close all windows and reopen Settings | Connected | Blocked before execution |
| 3. Rename destination | Connected | Blocked before execution |
| 4. Restart put.gd | Connected with the same status record | Blocked before execution |
| 5. Upload a screenshot | Upload succeeds and row stays Connected | Blocked before execution |
| 6. Change and restore bucket | Ready to test, then Connected | Blocked before execution |
| 7. Store wrong secret, test and upload | Ready to test, then Test failed. Upload fails with an error code. | Blocked before execution |
| 8. Restore correct keys and test | Connected | Blocked before execution |

The checklist produced no screenshots, status readings or product failures for
nightly comparison. The preflight created no desktop processes, destinations or
bucket objects, and took no lock.
