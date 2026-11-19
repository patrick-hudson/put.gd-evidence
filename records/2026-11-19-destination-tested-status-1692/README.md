# Destination "Connected" status kept after closing Settings and renaming (#1692)

Before and after pictures for issue #1692 and its fix on branch
`fix/destination-tested-status` (commit `dd5e29759`).

**Setup.** d69 (Debian 13), a private Xvfb display (`:92`, no window manager) under
`dbus-run-session`, private `XDG_*` folders, and the loopback S3 fixture
`tests/fixtures/s3_server.py` with its synthetic session keys. One S3 destination,
"Team bucket", is the capture default. The script stores the synthetic keys for this
session, opens Settings → Destinations and presses **Test upload and link** in the
window with a real pointer click. It then closes the window with `WM_DELETE_WINDOW`,
as a window manager's close button does (the `putgd-ui` helper exited: its PID went to
0), opens Destinations again, and renames the destination through `settings.save`.

**Builds.**

- Before: the published nightly `26.1118.5367` Debian 13 DEB, extracted privately.
- After: a dev build of `dd5e29759` (the fix) on d69.

**Result.**

| Step | Before (nightly) | After (fix) |
| --- | --- | --- |
| Before Test | Ready to test | Ready to test |
| Test passed | Connected | Connected |
| Settings closed and opened again | Ready to test | Connected |
| Destination renamed | Ready to test | Connected |

With the fix, `settings.get` reported `destinationStatus.fixture.state = "passed"`
(`source: "test"`) after each of the last three steps.

**Files.**

- `destination-status-before-after.png`: the four steps side by side, cropped to the
  destination row and title, with the changed states boxed in red.
- `before-after-reopen-full.png`, `after-after-reopen-full.png`: the whole window after
  closing and reopening.
- `before-after-rename-full.png`, `after-after-rename-full.png`: the whole window after
  the rename.
