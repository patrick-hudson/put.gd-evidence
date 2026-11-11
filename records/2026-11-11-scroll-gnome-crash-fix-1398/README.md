# FIX-5: the GNOME Shell crash after prepare, cancel, quit (PR #1398)

Session `fx5-0ade2c2b`, 2026-11-11 from 08:02 UTC. Host f44 (Fedora 44, GNOME Shell 50.6,
Mutter 50.6, Wayland), desktop lock `scroll-fix5`. Harness and raw output: `f44:~/work/fx5`
(`fx5.py` driver, `tally.py`, `relogin.sh`, one directory per run with `loop.jsonl` and `rpc.jsonl`).

## Cause (proved from the core of 07:39:35 UTC, `coredumpctl debug 3594190` with debuginfod symbols)

put.gd's Shell extension moved a window that Mutter had already unmanaged.

```
#0 meta_window_update_monitor (window=0x0, flags=USER_OP)            src/core/window.c:4168
#1 meta_window_wayland_update_main_monitor (window=0x55d13cb6ed30)   src/wayland/meta-window-wayland.c:728
#2 meta_window_update_monitor
#3 meta_window_move_resize_internal (window=0x55d13cb6ed30 [MetaWindowWayland],
       flags=META_MOVE_RESIZE_USER_ACTION | MOVE_ACTION | CONSTRAIN)  src/core/window.c:4464
#4.. ffi_call, Gjs::Function::invoke, an async function resumed from a promise job
```

In frame 3: `window->title` = `"put.gd recording controls"` (the helper's bar),
`window->unmanaging` = 1, `window->monitor` = NULL, client type Wayland, rect 737,530 447x52 (the
bar where the helper first showed it, before any placement). The flags are those of
`meta_window_move_frame(window, user_op=TRUE, x, y)`. Frame 1 line 728 is
`meta_window_update_monitor (toplevel_window, flags)` with `toplevel_window` NULL: the surface of
an unmanaged window has no toplevel window, and Mutter reads through it. (`gdb.out`, `gdb3.out`.)

The caller is `_placeRecordingBar` in `integrations/gnome/extension.js`, the only async code that
calls `move_frame`. It waits up to 2 s for the bar's window, up to 1 s for it to be shown, then
moves it and waits 100 ms, up to five times. Nothing ended those waits when the frame was hidden
or the window went away. The 1x1 heartbeat widget is not involved: it is a Shell actor, not a
window, and the crash is in a window call.

Two parts, then:

- **Ours:** the extension calls a `Meta.Window` method on a window it can know is gone.
- **Mutter's:** `meta_window_move_frame()` on an unmanaged Wayland window dereferences NULL instead
  of returning. Any extension that keeps a window across an await can reach it.

A second effect seen in every crash: gnome-session sets
`org.gnome.shell disable-user-extensions true` after the Shell dies, so after the next login
every user extension is off, put.gd's included, until the user turns them back on.

## Does this branch cause it?

`_placeRecordingBar`, `_followRecordingBar` and `_replaceRecordingBar` are byte-for-byte the same
on `origin/nightly` (the branch's diff of `extension.js` touches only the `beat` pixel, the
`scroll` action and the `beat` field check). The faulty call predates the branch.

What the branch adds is the timing that reaches it: `ScrollCaptureService` answers `ready` while
the Shell still places the bar (`placeShellBar`, `shellPlacing_`), so a cancel right after
`scroll.prepare` lands inside the placement's waits. `RecordingService` answers `ready` only after
`ShowRecordingFrame` has replied. Measured below.

## Reproduction, branch head (CI RPM of eaa1ba198, run 42975726725, sha256 758d4818…, extension 22)

f44 08:07 to 08:19 UTC, nothing of Patrick's open (session restarted at 07:41 by the confirmation
pass; only the wall VNC unit and session services running). Each loop step: private resident
(`XDG_*` under `~/work/fx5/<run>`), `putgd-cli` over its socket, region `[100,200,960,600]`.
`delay` is the sleep between `scroll.prepare` returning and the next call (the CLI's own start
adds about 50 ms). A crash is a changed or missing `gnome-shell` pid; after each one the driver
turned user extensions back on, restarted GDM, left the overview, restarted
`putgd-gnome-vnc.service` and required the extension `ACTIVE` before going on.

| Loop | Iterations | Shell crashes | By delay |
|---|---:|---:|---|
| prepare, cancel, `ui.quit` (`b2-pcq`) | 16 | 4 | 0 s 4/8, 0.05 s 0/3, 0.1 s 0/5 |
| prepare, cancel (`b-pc`) | 17 | 3 | 0 s 3/5, 0.05 s 0/2, 0.1 s 0/5, 0.2 s 0/5 |
| prepare, kill the helper (`b-pk`) | 16 | 4 | 0 s 4/5, 0.05 s 0/1, 0.1 s 0/5, 0.2 s 0/5 |
| start, cancel within 0 to 200 ms (`b-sc`) | 20 | 0 | |
| start, `ui.quit` mid-capture (`b-sq`) | 20 | 0 | |

Two earlier short runs with a first version of the driver add 2 crashes in 5 prepare, cancel, quit
steps (`a`, `b-pcq`). All 22 Shell cores of the day on f44 (the confirmation pass's, 13 from these
loops, 8 from the nightly loops below) have the same four top frames, `meta_window_update_monitor`,
`meta_window_wayland_update_main_monitor` (17 of them in its `.cold` part, the window has no
surface left), `meta_window_update_monitor`, `meta_window_move_resize_internal`, under `ffi_call`
(`cores.txt`). So: a cancel or a dead helper
within about 50 ms of `ready` takes the Shell down a little more than half the time (11 of 18);
100 ms later the placement's first move is over and nothing crashes. Quit is not needed. Once
`scroll.start` has been accepted the placement is finished (start waits for it), which is why the
start loops are clean.

**Second fault, same code:** a `HideRecordingFrame` that overtakes a waiting `ShowRecordingFrame`
is undone when the placement returns. `stale.py`: prepare, cancel 0.1 s later, resident left
running, wall screenshot 4 s after: the white ring is still on the desktop (`stale-head-0.1.png`).
With the cancel 0.3 s after prepare the placement had finished and the ring was gone
(`stale-head-0.3.png`). By the code the leftover frame also keeps the scroll frame's 40 ms beat
timer; I did not measure that. It stays until the next frame is hidden or the resident leaves the
bus.

## Published nightly, recording path (v26.1110.4591-nightly RPM, sha256 b76afef5…, extension 21)

`recording.prepare` answers `preparing` after 0.07 s and reaches `ready` at 0.69 s (3 probes); the
Shell's placement runs in the last part of that. Delays are counted from `prepare` returning.

| Loop (published nightly, recording a region) | Iterations | Shell crashes | By delay |
|---|---:|---:|---|
| prepare, cancel, `ui.quit` (`n-rpcq`) | 28 | 2 | 0.35 s 2/4, the other six delays 0/4 each |
| prepare, cancel (`n-rpc`) | 28 | 2 | 0.35 s 1/4, 0.40 s 1/4, others 0/4 |
| prepare, kill the helper (`n-rpk`) | 28 | 4 | 0.40 s 4/4, others 0/4 |
| ready, start, cancel within 0 to 100 ms (`n-rsc`) | 21 | 0 | |
| ready, start, `ui.quit` (`n-rsq`) | 4 | 0 | driver stopped at 4: the restarted resident answered `initializing` while it recovered its journal |

Core of 08:22:17 (pid 3659691, nightly installed): `meta_window_update_monitor`,
`meta_window_wayland_update_main_monitor.cold`, `meta_window_update_monitor`,
`meta_window_move_resize_internal`, `ffi_call`: the same call, entered through the branch where the
window has no surface left.

**Verdict.** Pre-existing: the published nightly's recording path takes the Shell down through the
same extension call, 8 times in 84 prepare loops, when a cancel, a quit or a dead helper lands in
the roughly 100 ms in which the Shell places the bar. Underneath is a Mutter bug (NULL dereference
in `meta_window_move_frame` for an unmanaged Wayland window). This branch does not introduce the
fault; it widens the window, because a scroll capture is `ready` and cancellable while the
placement is still running (11 crashes in 18 with the cancel at once, against 8 in 84 aimed
attempts for a recording), and the confirmation pass's clean-up happened to do exactly that.

## Fix (3b9701cb3, `integrations/gnome/extension.js`, extension stays at version 22)

- `BarWindow`: the bar is watched from the moment the lookup finds it, before the first wait. On
  Mutter's `unmanaging` or `unmanaged` it is no longer live; the placement returns
  `{placed: false, outside: false}` and the size-change follower drops it. No `Meta.Window` method
  is called on a bar that is not live. Handlers are disconnected when the placement ends without
  following the bar, when the frame is hidden, and so on `disable()`.
- `_recordingBar` skips windows whose actor `is_destroyed()`: the actor of an unmanaged window stays
  in `global.get_window_actors()` while it fades out.
- `_hideRecordingFrame` (the bridge call, a lock, the resident leaving the bus, `disable()`) bumps
  an epoch. A placement that is waiting checks it after every wait and ends `cancelled`: it moves
  nothing, and the frame and its beat are not shown again after the hide.
- The resident's order is not changed. With the extension safe against a window that goes away at
  any moment, the order no longer matters, and it could not be the fix: a helper that is killed
  gives the resident nothing to order (`pk` loops), and a resident that is killed sends no hide at
  all. The resident refuses an extension older than the packaged version, and the version this
  branch ships (22) has never been published, so no user runs the new resident against the
  unfixed code.
- Test (`tests/desktop/test_gnome_ownership.mjs`, `gnome_ui_ownership_contract`): a bar unmanaged
  while the placement waits for it to be shown, and between two moves, gets no further method
  call; a window whose actor is destroyed is not looked at; a hide (bridge call and
  `_hideRecordingFrame`) during each wait ends the placement `cancelled` with no beat timer, no
  actor and no handler left; an unmanaged followed bar is dropped and a late size change moves
  nothing. The new cases fail against the extension of eaa1ba198.

## Whole suites, d69 (`~/work/s1376/src`, tree = 3b9701cb3 by `rsync -n --checksum`)

- `ctest --preset dev --parallel 3`: **154 of 154 passed**, 415 s (`ctest-fix5.log`).
- `python3 -m pytest tests/desktop/test_surface*.py tests/desktop/test_review_adversarial.py`: 431
  passed, 5 skipped, 7 failed, the same seven d69-only failures as fix rounds 2 to 4 (4
  `AimedRelease`, 3 `test_lost_session_*`; `pytest-fix5.log`, compared name by name with
  `pytest-fix4.log`). CI's contracts job runs that step and passed.
- `tests/integration/test_mcp.py` was not run: nothing it covers changed.

## Result with the fix (CI RPM of 3b9701cb3: run 42985758991, `putgd-26.1111.4668~dev+g242e70396cd5-1.fc44`, sha256 2f76c5f2…)

The package is CI's merge build 242e70396cd5, second parent 3b9701cb3; the installed
`extension.js` has the same sha256 as the source file (2dba612d…). f44 re-logged in at 08:29, one
Shell (pid 3680602) for everything below, 08:29:39 to 08:46 UTC.

| Loop | Iterations | Shell crashes | Delays |
|---|---:|---:|---|
| prepare, cancel, `ui.quit` (`f-pcq`) | 32 | 0 | 0 s x16, 0.02 s x8, 0.05 s x8 |
| prepare, cancel (`f-pc`) | 32 | 0 | same |
| prepare, kill the helper (`f-pk`) | 32 | 0 | same |
| start, cancel within 100 ms (`f-sc`) | 30 | 0 | 0, 0.05, 0.1 s x10 each |
| start, `ui.quit` mid-capture (`f-sq`) | 30 | 0 | 0.2, 0.5, 1 s x10 each |
| recording: prepare, cancel, `ui.quit` (`f-rpcq`) | 28 | 0 | 0.30 to 0.60 s, x4 each |
| recording: prepare, cancel (`f-rpc`) | 28 | 0 | same |
| recording: prepare, kill the helper (`f-rpk`) | 28 | 0 | same |
| recording: ready, start, cancel (`f-rsc`) | 21 | 0 | 0, 0.05, 0.1 s x7 each |

259 iterations, 0 Shell crashes. `coredumpctl list --since 02:29:39`: nothing, of any program.
The Shell's journal for the window (`journal-fixed-shell.txt`, 65 lines): no `JS ERROR`, no line
from the extension; 57 x "D-Bus client with active sessions vanished" (Mutter, a helper that ended
with its screencast session open) and 8 x "Can't update stage views actor". Every reply was the
expected one (`ready`/`cancelled`/`quitting`, `failed` after a killed helper). The recording
build reaches `ready` 0.54 to 0.65 s after prepare here (`f-probe`), so the 0.30 to 0.60 s delays
cover the placement as they did on nightly. `stale.py` and `stalekill.py`: no ring 4 s after a
cancel 0.1 s after prepare, nor 4 s after the helper was killed, resident alive
(`stale-fix-0.1.png`, `stale-fix-kill.png`).

GNOME rows, same session, private profile `rows/` (the confirmation pass's `pass2.capture` and
verifiers):

| Row | Result |
|---|---|
| Qt ruler, from top, x3 (`plain-0..2`) | 3 exact, 960x2400, 0 unexpected pixels |
| 24,000 px ruler opened at its end, fromTop on, x3 (`long-bottom-0..2`) | 3 exact, 960x24000, `end_of_content`, top proved; way up 5.7 / 5.6 / 5.7 s |
| 125%, x1 (`scaled-00`) | exact, 1200x3000, 0 bad scanlines; scale back to 1.0, wall 1920x1080 |
| User-style, x1 (`user`): Ctrl+Shift+F7 and a selector drag through the wall VNC | 1 new history record, image exact |
| Recording start and stop, x1 (`record`) | `ready` (bar outside), `recording`, stop after 4.70 s, saved copy h264 960x600, 141 frames, three sampled frames differ; `recording.png` shows ring, dim strips and the widened bar below the area |

The user-style row needed a key and a pointer drag, which BUILD.md's input rule does not allow;
the task asked for the row and the earlier physical passes ran it the same way, on a locked
desktop over a fixture this run opened. Everything else used RPC only.

CI on 3b9701cb3: run 42985758991, all 16 jobs and the `CI` summary pass (collect, pipewire, prune
caches and CodeRabbit skipped as before).

## f44 afterwards (08:47 to 08:49 UTC)

`dnf remove --noautoremove putgd libmng jasper-libs qt6-qtimageformats`: the package list is
identical to the one taken before the first install (`packages-before.txt`, `packages-final.txt`).
`enabled-extensions` and `disabled-extensions` are back to what they were at 08:05
(`['background-logo@fedorahosted.org']`; `hkwitness@lab`, `appindicatorsupport@rgcjonas.gmail.com`
and `putgd@put.gd` disabled), `disable-user-extensions` is false. GDM restarted, overview closed,
`putgd-gnome-vnc.service` restarted: two wall frames 62 s apart differ in the clock, 1920x1080, tty2,
no put.gd process. Lock released 08:49:24 UTC with `--verified-clean`.

Left on f44: `~/work/fx5` (458 MB with the three RPMs) and the 22 Shell cores of today in
`/var/lib/systemd/coredump` (about 30 MB each), which systemd removes by age. A copy of the run
records without packages, profiles and per-second frames is in `acceptance/fix5/`.

Not done: no upstream Mutter report was filed for the NULL dereference; the AppIndicator extension
was already disabled on f44 before this session and was left so.
