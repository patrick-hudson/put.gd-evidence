# Native window recording on KDE and GNOME Wayland (#1278)

Acceptance for [PR #1282](https://github.com/patrick-hudson/put.gd-desktop/pull/1282):
a `window` recording on Plasma and GNOME Wayland without the portal picker.
The run date is 2026-11-08 (UTC).

## Build under test

All five desktops ran packages from PR CI run `42438186700` (head `04fe630aa`,
package version `26.1108.4121~dev+g4f96cf988233`). The PR's later commits move a
header into `core` and change test macros only; the shipped code is the same.

| Package | SHA-256 |
| --- | --- |
| `putgd_26.1108.4121~dev+g4f96cf988233_amd64.deb` (ubuntu26.04) | `f5c3f12b5c8ed69b8b5ee75caff3a6dacb8c5c3f0afc1f2cf3094a3071cf8eed` |
| `putgd_26.1108.4121~dev+g4f96cf988233_amd64.deb` (debian13) | `483ee887d02c698591a2dd4d7ac3cf0fecad65afa70db3dd7ecab09657c56687` |
| `putgd-26.1108.4121~dev+g4f96cf988233-1.fc44.x86_64.rpm` | `0620756bcd5415c2f035c5bdcdac126a30034f99f70a719205a393cc950223e9` |
| `putgd-26.1108.4121-dev+g4f96cf988233-x86_64.AppImage` | `d12386dc083a53d914f1df454af14561125ad10983c80531221a0af4e7b13f5c` |

k72, d69 and f44 ran the native package, Aurora ran the AppImage, and the
Ubuntu GNOME VM (golden `transfer-0d2922e34f4b`, run `g1278b`) ran the Ubuntu
26.04 package installed with `lab.py install`. Every run used a private put.gd
profile. Packages and the input agent were removed afterwards and each desktop
lock was released with `--verified-clean`.

## How the runs work

`driver/window_accept.py` opens GTK test windows (`driver/win1278.py`): a
bouncing ball on a grid, and a still one as the control. It then drives the
production CLI.

1. **churn**: records the moving window by the identity from
   `recording.windows`. During the clip the window is moved, resized, has the
   pointer swept across it (through the uinput/QMP input agent), is covered by
   another window, and is minimized; on KDE it is then restored.
   - KDE moves and resizes go through a KWin script.
   - GNOME uses maximize and unmaximize, a resize by the app, and Super+Left.
     A GNOME client cannot unminimize itself, so the window stays minimized
     there.
2. **still-control**: records the still window. Its motion score is the floor.
3. **target-closed**: closes the recorded window three seconds into the clip.
   The session must reach review on its own.
4. **active-window**: a target with no identity must resolve to the focused
   window.
5. **monitor** and **region**: regression checks with the moving window in view.
   On GNOME these come from the `--short` run, which first focuses the moving
   window by a click, because the full run leaves it minimized.

Motion is `putgd-record --motion` (12 samples) on the saved MP4 copy. `prepare`
is the time from `recording.prepare` to `ready`. A picker would hold the session
in `preparing`, and none appeared.

## Results

| Desktop | Path | Slowest `prepare` → ready | Churn motion | Still control | Window closed | Active window resolved | Monitor / region motion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kubuntu 26.04 (k72), KWin 6.6.6, PipeWire 1.6.2 | kde-screencast | 0.41 s | 7.35 | 0.001 | target_closed in 0.16 s | yes | 0.89 / 2.38 |
| Debian 13 (d69), KWin 6.3.6, PipeWire 1.4.2 | kde-screencast | 0.60 s | 6.06 | 0.008 | target_closed in 0.19 s | yes | 0.89 / 2.68 |
| Aurora testing-45.20261107.1 (aurora-amd), KWin 6.8.2, PipeWire 1.6.11 | kde-screencast | 0.23 s | 6.23 | 0.035 | target_closed in 0.12 s | yes | 0.95 / 2.37 |
| Fedora 44 (f44), GNOME 50.6, PipeWire 1.6.9 | mutter-screencast | 0.54 s | 10.84 | 0.035 | target_closed in 0.17 s | yes | 0.90 / 2.76 |
| Ubuntu 26.04 GNOME 50.1 (VM on d69) | mutter-screencast | 0.70 s | 10.38 | 0.043 | target_closed in 0.24 s | yes | 0.89 / 2.70 |

"Window closed" is the time from closing the window to the session reaching
`reviewing` with `stopReason: target_closed` and a reviewable clip.

## What the frames show

Each `<case>.png` is six evenly spaced frames from that saved copy.

- **Resize.** After a resize every desktop letterboxes the window into the
  canvas taken at `prepare`. On Debian 13, `pipewiresrc` 1.4.2 fails KWin's
  renegotiation with `unhandled format`, and the helper reopens the source on
  the same node within 0.5 s (`source reopened … 1 times` in
  `record-debug.log`). On Mutter the window moves inside a fixed buffer, and the
  crop region was followed 9 times during the f44 churn.
- **Covered.** The window keeps recording its own live content on all five
  desktops.
- **Minimized.** The window keeps recording its own live content on all five:
  KWin 6.3, 6.6 and 6.8, and Mutter on GNOME 50.
- **Cursor.** The pointer is embedded: it is visible in frames after the sweep.
- **Decorations.** KWin 6.6 and 6.8 include the server-side title bar in a window
  stream; KWin 6.3 does not. GTK's client-side decoration is part of the window
  on GNOME.

## GNOME extension version gate

The PR moves the extension to version 19 (recording protocol 2).

- **f44**:
  - Before re-login (`fedora-f44/f44-gate-before/gate.json`): installing the
    RPM put v19 on disk while v18 stayed loaded. `capabilities` reported
    `outdated: true` with loaded 18 and packaged 19. `recording.windows` and a
    window `prepare` both failed `helper_outdated` ("log out and back in").
  - After re-login (`systemctl restart gdm`, `fedora-f44/f44-gate-after/gate.json`):
    the extension reported 19 with `recordingVersion: 2`, and
    `recording.windows` answered.
  - In the same check, a window `prepare` was refused `recording_target` with
    `reason: own_window`, because put.gd's first-run dashboard had focus. That
    is the own-window rule on a real session.
- **Ubuntu GNOME VM**: the golden had extension version 1 loaded. After the
  package install it failed the same way (`ubuntu-gnome-vm/gate-before/gate.json`).
  After `sync` and a QMP `system_reset` the extension reported 19 and the full
  run passed.

## Probes before the build

Before any code was written, small probes showed on real sessions that both
compositor routes work:

- KWin `zkde_screencast_unstable_v1.stream_window` on d69 and k72.
- Mutter `RecordWindow` with a session client on f44. Its `Closed` signal came
  66 ms after the window closed; KWin's stream `closed` event came 7 ms after.
- The `pipewiresrc` 1.4 renegotiation failure, which upstream 1.5.81+ fixes by
  keeping the possible caps.

They are described in the PR.

## Files

Each desktop folder holds, per run:

- `results.json`: capabilities, the listed windows, and per-case timings,
  events and motion.
- `gate.json`: the GNOME gate runs.
- `record-debug.log`: the helper's log without its per-second rate lines.
- `<case>.png`: the frame strips described above.

Saved clips and working clips stay on the builders under
`~/work/b1278/runs/`.
