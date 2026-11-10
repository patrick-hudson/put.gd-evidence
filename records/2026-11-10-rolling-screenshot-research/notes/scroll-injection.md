# Scroll-injection mechanisms on five Linux desktops, and ShareX scrolling-capture stitching (as of 2026-11-09)

Legend: [V] = verified by reading source fetched this session (master/main on 2026-11-09). [I] = inferred or from background knowledge, not re-read this session. [U] = untested code. Budget was ~15 tool calls, so several items are [I] or Gaps; they are listed explicitly.

Versions read: KWin master (`src/backends/fakeinput/fakeinputbackend.cpp`, `src/wayland_server.cpp`, `src/wayland/clientconnection.cpp`), plasma-wayland-protocols fake-input.xml (interface version 6), mutter main (`data/dbus-interfaces/org.gnome.Mutter.RemoteDesktop.xml`, `clutter/clutter/clutter-virtual-input-device.h`), wlr-protocols `wlr-virtual-pointer-unstable-v1` (via swaywm mirror, interface version 2), Hyprland main (`src/protocols/VirtualPointer.cpp`, `ProtocolManager.cpp`), labwc master (`src/seat.c`, meson requires `wlroots-0.20`), kdeconnect-kde master (`plugins/mousepad/waylandremoteinput.cpp`), ShareX master (copyright 2007-2026; `ShareX.ScreenCaptureLib/ScrollingCaptureManager.cs`, `ScrollingCaptureOptions.cs`).

---

## 1. X11 / Cinnamon: XTest via xcb

### Takeaway
Use XTEST (`xcb_test_fake_input`, button 5 = wheel down, 4 = up): press then release per notch. It is delivered to the window under the real pointer, so warp the pointer into the region first and restore it afterwards. [I] throughout this section (not re-read this session; this is long-stable X11 behaviour).

### Findings
- Header/lib: `#include <xcb/xtest.h>`, link `xcb-xtest`. Packages: Debian/Ubuntu/Mint `libxcb-xtest0` (runtime), `libxcb-xtest0-dev` (dev); Fedora `libxcb` provides libxcb-xtest.so.0 and `libxcb-devel` the headers. [I] Qt's own xcb plugin already pulls libxcb; check that `libxcb-xtest.so.0` is present on all targets before choosing to dlopen vs link.
- Signature (xcb/xtest.h) [I]:
  `xcb_void_cookie_t xcb_test_fake_input(xcb_connection_t *c, uint8_t type, uint8_t detail, uint32_t time, xcb_window_t root, int16_t rootX, int16_t rootY, uint8_t deviceid);`
  `type` = XCB_BUTTON_PRESS (4) / XCB_BUTTON_RELEASE (5); `detail` = button number; `time` = 0 (CurrentTime) or ms delay; `root` = XCB_NONE for buttons; deviceid 0.
- Extension check: `xcb_get_extension_data(c, &xcb_test_id)->present`, or `xcb_test_get_version_unchecked/ xcb_test_get_version_reply` (request 2.2). [I]
- Routing: XTEST events are processed as if from the core pointer device, so they go to the window under the *current pointer position* (with the normal grab/propagation rules). No target window can be specified. Therefore: `xcb_warp_pointer(c, XCB_NONE, root, 0,0,0,0, x, y)` (or `xcb_test_fake_input(MotionNotify=6, detail=0 (absolute), root, x, y)`), then buttons. Save the original position first with `xcb_query_pointer` and warp back after the capture. [I]
- XI2 toolkits: Under XInput2, GTK3/4, Qt 6, Chromium, Firefox receive XI_ButtonPress for buttons 4-7 on the master pointer **and** emit/derive scroll from XI2 valuators (smooth scroll) only for devices that have scroll valuators. XTEST button 4/5 clicks go through the "Virtual core XTEST pointer" slave device, which has no scroll valuators, so servers emit legacy button 4/5 press/release; toolkits treat one 4/5 click as one discrete step (GTK: one GDK_SCROLL_UP/DOWN; Qt: angleDelta 120; Chromium/Firefox: one wheel tick). [I; widely observed with xdotool click 5, and what xdotool does]
- Why not `XSendEvent`: events are flagged `send_event=True`; GTK, Qt and Chromium ignore or mis-handle them (and XI2 events cannot be sent that way at all). [I]
- Overlay caveat: if put.gd's own overlay window is above the region and receives the pointer, the wheel goes to it. Use an input-transparent overlay (XShape empty input region: `xcb_shape_rectangles` on ShapeInput with 0 rects) or hide it during scrolling. [I]

### Minimal code [U]
```cpp
#include <xcb/xcb.h>
#include <xcb/xtest.h>
bool wheel(xcb_connection_t* c, xcb_window_t root, int x, int y, int notches /*+down,-up*/) {
  auto ext = xcb_get_extension_data(c, &xcb_test_id);
  if (!ext || !ext->present) return false;
  auto q = xcb_query_pointer_reply(c, xcb_query_pointer(c, root), nullptr);
  int ox = q ? q->root_x : x, oy = q ? q->root_y : y; free(q);
  xcb_warp_pointer(c, XCB_NONE, root, 0,0,0,0, x, y);
  uint8_t b = notches > 0 ? 5 : 4;
  for (int i = 0; i < abs(notches); ++i) {
    xcb_test_fake_input(c, XCB_BUTTON_PRESS,   b, 0, XCB_NONE, 0, 0, 0);
    xcb_test_fake_input(c, XCB_BUTTON_RELEASE, b, 0, XCB_NONE, 0, 0, 0);
  }
  xcb_flush(c);
  xcb_warp_pointer(c, XCB_NONE, root, 0,0,0,0, ox, oy); xcb_flush(c);
  return true;
}
```
Use put.gd's own xcb connection (`QX11Application` native interface), not Qt's.

### Added verification
- xdotool [V: jordansissel/xdotool `xdo.c`]: `xdo_click_window(xdo, window, button)` = `xdo_mouse_down(...)`, `usleep(DEFAULT_DELAY)`, `xdo_mouse_up(...)`; the press path calls `XTestFakeButtonEvent(xdo->xdpy, button, is_press, CurrentTime)` (line ~834). `xdotool click 5` is therefore exactly one press+release of button 5 through XTEST, which toolkits take as one wheel notch.
- Packages [V]: Debian 13 (trixie) and Ubuntu 24.04 (noble) `libxcb-xtest0` ships `/usr/lib/x86_64-linux-gnu/libxcb-xtest.so.0(.0.0)`; `libxcb-xtest0-dev` ships `/usr/include/xcb/xtest.h`, `libxcb-xtest.so`, `.a` and `xcb-xtest.pc` (packages.debian.org / packages.ubuntu.com file lists). Mint 22 is Ubuntu 24.04-based (same names) [I].
- Fedora (`libxcb`, `libxcb-devel`) and Arch (`libxcb`) [I]: both distros ship all xcb extension libraries, including xtest, in the single `libxcb` package; the Fedora and Arch package pages were JS-rendered and could not be read.

### Gaps
- Fedora 44 and Arch package contents not confirmed from a file list.

---

## 2. GNOME / Mutter

### Takeaway
Both paths work for an ordinary unsandboxed process. Recommended: (b) the put.gd GNOME Shell extension drives a Clutter virtual pointer (no indicator, no dialog, no D-Bus peer rules, and it can warp the real cursor). (a) RemoteDesktop D-Bus is a verified fallback with only one catch: an active session makes GNOME Shell show the "Stop Screen Sharing" indicator.

### (a) org.gnome.Mutter.RemoteDesktop (bus name `org.gnome.Mutter.RemoteDesktop`, path `/org/gnome/Mutter/RemoteDesktop`, session bus)
- Signatures [V: mutter main `data/dbus-interfaces/org.gnome.Mutter.RemoteDesktop.xml`]: `CreateSession() -> (o session_path)`; Session: `Start()`, `Stop()`, `NotifyPointerAxis(d dx, d dy, u flags)` (pixels of a standardized mouse; base discrete step 10.0; flags 1 finish, 2 wheel, 4 finger, 8 continuous; none = finger), `NotifyPointerAxisDiscrete(u axis, i steps)`, `NotifyPointerMotionRelative(d dx, d dy)`, `NotifyPointerMotionAbsolute(s stream, d x, d y)`, `NotifyPointerButton(i button, b state)`. The interface doc says it is private, with no compatibility promised.
- `NotifyPointerAxisDiscrete` semantics [V: `src/backends/meta-remote-desktop-session.c`]: `axis > 1` -> error "Invalid axis value"; `steps == 0` -> error "Invalid axis steps value"; mapping `discrete_steps_to_scroll_direction`: axis 0 with steps < 0 = CLUTTER_SCROLL_UP, axis 0 with steps > 0 = DOWN, axis 1 steps < 0 = LEFT, > 0 = RIGHT. It then calls `clutter_virtual_input_device_notify_discrete_scroll(session->virtual_pointer, CLUTTER_CURRENT_TIME, direction, ...)` once per `abs(steps)` (source pretended to be the wheel, per code comment). So one notch down = `NotifyPointerAxisDiscrete(0, +1)`. A virtual pointer is created lazily (`ensure_virtual_device(session, CLUTTER_POINTER_DEVICE)`).
- Scroll-only without ScreenCast [V]: `handle_start` runs `meta_remote_desktop_session_start`, which starts the ScreenCast session only `if (session->screen_cast_session)`; so a bare RemoteDesktop session works; no stream is needed for axis/relative/button. `NotifyPointerMotionAbsolute` takes a `stream` path so absolute motion needs a linked ScreenCast stream [V by signature]; without one, you cannot place the cursor (use relative motion, or the extension path).
- Caller restriction [V: `meta-remote-desktop.c` `handle_create_session`, `meta-dbus-session-manager.c`, `meta-remote-desktop-session.c`]: no sandbox/uid/executable check. `CreateSession` only fails if session creation is inhibited (`inhibit_count > 0`). The session records `peer-name = g_dbus_method_invocation_get_sender()`, and `check_permission` returns `g_strcmp0(session->peer_name, sender) == 0` for Start, Stop and every Notify: only the **same D-Bus connection** that created the session may use it (GNOME 50 main; earlier versions: I). Keep one `QDBusConnection` for create/start/notify (not `sessionBus()` clones with a different unique name). Session.Start returns ACCESS_DENIED "Permission denied" if called from another connection.
- Real client [V: GSConnect `src/service/components/input.js`]: `connection.call('org.gnome.Mutter.RemoteDesktop','/org/gnome/Mutter/RemoteDesktop','org.gnome.Mutter.RemoteDesktop','CreateSession', null, null, Gio.DBusCallFlags.NONE, -1, null)` -> `reply.deepUnpack()[0]` is the object path; then a `Gio.DBusProxy` (bus SESSION, name `org.gnome.Mutter.RemoteDesktop`, iface `...Session`) `init_async`, `call('Start', null, NONE, -1, null)`; scroll is `call('NotifyPointerAxisDiscrete', GLib.Variant.new('(ui)', [axis, steps]))` (GSConnect passes Gdk.ScrollDirection.UP = 0 as axis and +/-1 steps); `Stop` ends it; it listens for the session's `Closed` signal. No dialog is involved. GSConnect runs as an ordinary user service (not in the Shell), confirming ordinary-session-process access.
- Indicator [V: gnome-shell `js/ui/status/remoteAccess.js`, mutter `meta-remote-desktop-session.c`]: `meta_remote_desktop_session_start` always calls `init_remote_access_handle`, which creates a MetaRemoteAccessHandle and emits `new-handle` on the controller, even with no ScreenCast. The RemoteDesktop handle does not set `is-recording` (grep of the session source found none; the ScreenCast session sets it from a property, default FALSE). Shell has two indicators: `RemoteAccessApplet` (red `media-record-symbolic` privacy dot) only for handles with `is_recording`; `ScreenSharingIndicator` (`screen-shared-symbolic` + `screencast-stop-symbolic`, a clickable panel button, accessible name "Stop Screen Sharing", click stops all handles; kept visible at least 5 s, `MIN_SHARED_INDICATOR_VISIBLE_TIME_US`) for handles with `!isRecording`. So a bare RemoteDesktop session shows the screen-sharing stop button for as long as it is started [V by code reading; not observed on screen]. Mitigation: Start the session just before the capture burst and Stop right after; or use (b).

### (b) Extension with Clutter virtual device
- C signatures [V: mutter tags 46.0, 48.0 and 50.0, `clutter/clutter/clutter-virtual-input-device.h`; identical in all three, unchanged]:
```
void clutter_virtual_input_device_notify_discrete_scroll (ClutterVirtualInputDevice *vd, uint64_t time_us, ClutterScrollDirection direction, ClutterScrollSource scroll_source);
void clutter_virtual_input_device_notify_scroll_continuous (ClutterVirtualInputDevice *vd, uint64_t time_us, double dx, double dy, ClutterScrollSource scroll_source, ClutterScrollFinishFlags finish_flags);
void clutter_virtual_input_device_notify_absolute_motion (vd, uint64_t time_us, double x, double y);
```
  Enums [V]: ScrollDirection UP, DOWN, LEFT, RIGHT, SMOOTH; ScrollSource UNKNOWN, WHEEL, FINGER, CONTINUOUS; finish flags NONE, HORIZONTAL, VERTICAL. Time = microseconds. (Earlier "arity risk" note withdrawn: no change between 46 and 50.)
- Seat acquisition differs by pattern [V]: gnome-shell's own `js/ui/keyboard.js` (main) uses `global.stage.context.get_backend().get_default_seat()` and `seat.create_virtual_device(Clutter.InputDeviceType.KEYBOARD_DEVICE)`, and passes `Clutter.get_current_event_time() * 1000` (ms -> us) to `notify_keyval`. Real extensions use `Clutter.get_default_backend().get_default_seat()` (older style, still working in the examples below; prefer the `global.stage.context` form on 48+ [I]).
- Real GJS examples [V: GitHub raw files]:
  - TheBlackPrism/surface-dial-evolved `extension/lib/actions.js`: `const seat = Clutter.get_default_backend().get_default_seat(); this._pointer = seat.create_virtual_device(Clutter.InputDeviceType.POINTER_DEVICE);` ... `this._pointer.notify_discrete_scroll(GLib.get_monotonic_time(), direction, Clutter.ScrollSource.WHEEL)` with `Clutter.ScrollDirection.DOWN/UP`, looped once per step.
  - IAmYetiish/couchpad `couchpad/lib/actions/virtualInput.js`: same construction, `this._pointer.notify_discrete_scroll(eventTime(), direction, Clutter.ScrollSource.WHEEL)`.
- GJS [U] for put.gd:
```js
const seat = global.stage.context.get_backend().get_default_seat();
const ptr = seat.create_virtual_device(Clutter.InputDeviceType.POINTER_DEVICE);
ptr.notify_absolute_motion(GLib.get_monotonic_time(), x, y);   // stage (logical) px; moves the real cursor [I]
ptr.notify_discrete_scroll(GLib.get_monotonic_time(), Clutter.ScrollDirection.DOWN, Clutter.ScrollSource.WHEEL);
// keep ptr alive during the capture; destroy it afterwards
```
  Expose `ScrollAt(x, y, steps)` on the extension's existing D-Bus interface. Whether the virtual pointer event is routed to the surface under the pointer is standard Mutter input handling [I].

### Which
(b): no indicator, no peer-name constraint, absolute positioning without ScreenCast; costs: extension must be enabled (GNOME 50 extensions still load; put.gd already ships one).

### Gaps
- Visual appearance of the indicator was not observed, only derived from code.
- Whether the `RemoteAccessApplet` also shows for RemoteDesktop handles on older versions (46-48): remoteAccess.js read only on main.
- `notify_absolute_motion` warping behaviour under X11-on-GNOME not relevant; not checked.

---

## 3. KDE / KWin: org_kde_kwin_fake_input

### Takeaway
Gating depends on the Plasma release. Released Plasma up to and including 6.7.x (tag v6.7.6 has no sandbox code): the global is in a blacklist and is only advertised to clients whose executable is the first `Exec=` token of a desktop file that lists `X-KDE-Wayland-Interfaces=org_kde_kwin_fake_input` (or, for security-context clients, whose app id maps to such a desktop file). From Plasma 6.8 (tag v6.7.90 onward): the global is hidden only from Flatpak/Snap clients; any other client gets it. `authenticate` is a no-op everywhere. Ship the desktop-file key so it works on 6.3 (Debian 13, tag v6.3.6) through 6.7.

### Released-tag gating [V: `src/wayland_server.cpp`, `src/utils/serviceutils.h`, `src/wayland/clientconnection.cpp`]
- v6.3.6, v6.5.0, v6.6.0 (same logic; 6.6 drops `org_kde_kwin_keystate` from the list and moves some lines). Decisive code at v6.3.6:
```cpp
QStringList fetchRequestedInterfaces(ClientConnection *client) const {
    if (!client->securityContextAppId().isEmpty())
        return KWin::fetchRequestedInterfacesForDesktopId(client->securityContextAppId());
    return KWin::fetchRequestedInterfaces(client->executablePath());
}
const QSet<QByteArray> interfacesBlackList = { "org_kde_plasma_window_management", "org_kde_kwin_fake_input",
   "org_kde_kwin_keystate", "zkde_screencast_unstable_v1", "org_kde_plasma_activation_feedback", "kde_lockscreen_overlay_v1" };
bool allowInterface(ClientConnection *client, const QByteArray &interfaceName) override {
    ...
    if (client->processId() == getpid()) return true;
    ...
    if (!interfacesBlackList.contains(interfaceName)) return true;
    static bool permissionCheckDisabled = qEnvironmentVariableIntValue("KWIN_WAYLAND_NO_PERMISSION_CHECKS") == 1;
    if (!permissionCheckDisabled) {
        if (client->executablePath().isEmpty()) { /* "Could not identify process" */ return false; }
        auto requestedInterfaces = client->property("requestedInterfaces");  // cached per connection
        if (requestedInterfaces.isNull()) { requestedInterfaces = fetchRequestedInterfaces(client); client->setProperty(...); }
        if (!requestedInterfaces.toStringList().contains(QString::fromUtf8(interfaceName))) return false;
    }
    return true;
}
```
- Desktop-file mapping [V: `serviceutils.h` v6.6.0]: `fetchProcessServiceField` runs `KApplicationTrader::query` over all services and keeps those where `QFileInfo(QProcess::splitCommand(service->exec()).first()).canonicalFilePath() == executablePath`; takes `servicesFound.first()` and reads `X-KDE-Wayland-Interfaces`. `executablePath` = `executablePathFromPid(pid)` (`/proc/<pid>/exe`-based, `src/utils/executable_path_proc.cpp`) [I for /proc]. Consequences: (1) the process's real executable must equal the canonical first token of `Exec=` (symlinks resolved): an AppImage runtime is `/proc/pid/exe` = the mounted `/tmp/.mount_XXXX/usr/bin/putgd` (random mount point) or the AppImage file itself (type-2 runtime exec'd, then the payload is run from the FUSE mount), so the desktop `Exec=` will not match a path that changes per launch: **the dbus-free X-KDE-Wayland-Interfaces route is effectively unusable from an AppImage unless the Wayland connection is made by a helper binary at a stable path** [I, inferred from the mapping rule]. (2) A helper with a different executable needs its own desktop file with `Exec=/usr/bin/putgd-helper` and the key; the desktop file may be `NoDisplay=true` (`KApplicationTrader` includes hidden entries? not verified). (3) The Wayland connection that matters is the process that owns the `wl_display`, i.e. use a private connection from the helper, not Qt's.
- No `isTrustedOrigin`-style ownership/writability check on the executable exists in the code read at v6.3.6/v6.6.0 [V by absence in these three files; the `Exec` match is the only check]. Under `$HOME` is therefore fine as long as the path matches (and the commit message below calls this "pseudo-security").
- Sandbox-only rule [V]: commits on `src/wayland_server.cpp` and `clientconnection.cpp` dated **2026-06-18** ("Skip announcing restricted interfaces only to sandboxed clients"; "Determine whether a client is sandboxed depending on cgroup"). Commit message: the desktop-file approach "provides pseudo-security. The desktop files can be changed or overriden by the user"; it costs overhead; "a better approach to restrict privileged interfaces is to use the security context protocol". Tag check: `isSandboxed` absent in v6.3.6, v6.5.0, v6.6.0, v6.6.5, v6.7.0, v6.7.5, v6.7.6; present in v6.7.90, v6.7.91, v6.8.2 (so Plasma 6.8; 6.8.2 is the newest 6.x tag found) and master. In 6.8 `allowInterface` is: `if (client->isSandboxed()) return !restrictedInterfaces.contains(interfaceName); return true;`, restricted set = window_management, fake_input, screencast, activation_feedback, lockscreen_overlay, security_context_manager, ext_data_control_manager. `isSandboxed(pid)`: `sd_pid_get_user_slice` must be `app.slice` and `sd_pid_get_user_unit` must start with `app-flatpak-` or `snap.`; on failure returns false (unsandboxed). Unsandboxed AppImage/native: allowed.

### Protocol and handler [V]
- plasma-wayland-protocols `fake-input.xml` interface version 6 (requests as before: authenticate, pointer_motion, button, axis, touch_*, pointer_motion_absolute v3, keyboard_key v4, destroy v5, keyboard_keysym v6). KWin `s_version = 6`.
- `authenticate(application, reason)` [V v6.3.6 and master]: body is `device->setAuthenticated(true);` under `// TODO: make secure`. No UI, no prompt, application/reason are ignored. All other requests return early if not authenticated, so you must call it once after binding.
- `axis(axis, value)` [V v6.3.6 line 179 and master]: `axis` 0 vertical, 1 horizontal (other values ignored); handler calls `pointerAxisChanged(nativeAxis, wl_fixed_to_double(value), /*deltaV120*/0, PointerAxisSource::Unknown, ...)` then `pointerFrame`. `PointerInputRedirection::processAxis(axis, delta, deltaV120, ...)` (`src/pointer_input.cpp`) forwards to the Wayland seat. KWin treats `delta` as the continuous value and, for shortcut handling, `deltaV120 != 0 ? deltaV120/120.0 : delta/15.0` (`src/input.cpp` v6.6.0 line ~1018) [V]: KWin itself equates delta 15.0 with one notch.
- Value for one notch: send `wl_fixed_from_double(15.0)` on axis 0 (positive = down, as in wl_pointer) [I for client behaviour: libinput/KDE Connect/wayvnc convention is 15 per notch; clients receive axis value 15 with no discrete/v120 info, so GTK/Qt/Chromium treat it as a smooth-scroll delta of 15 px-equivalents rather than a hard "1 notch"; Qt and Chromium convert wl_pointer axis values to pixels/angle at roughly 1:1 with 15 = 1 notch when no v120/discrete is present; GTK may scroll by a different amount]. This is the weak point of fake_input: no discrete data. Calibrate by measuring the scroll in pixels and stitching from the measured overlap (which stitching does anyway).
- Fallback: RemoteDesktop portal + libei, see section 5. KDE Connect uses exactly that now (`plugins/mousepad/waylandremoteinput.cpp` [V]: `SelectDevices` with `types=7`, `persist_mode=2`, `ei_device_scroll_delta(m_pointer, dx, dy * -1)`). A host app cannot skip the first approval dialog; later runs skip it with a stored `restore_token`.
- Deprecation: none found. The 2026-06-18 change moves KDE toward security-context-based restriction, which Flatpak/Snap use.

### Minimal code [U]
```cpp
// client header from fake-input.xml via wayland-scanner; own wl_display connection
org_kde_kwin_fake_input* fi = (org_kde_kwin_fake_input*)wl_registry_bind(reg, name, &org_kde_kwin_fake_input_interface, std::min(ver, 6u));
org_kde_kwin_fake_input_authenticate(fi, "put.gd", "scrolling capture");
org_kde_kwin_fake_input_pointer_motion_absolute(fi, wl_fixed_from_double(x), wl_fixed_from_double(y)); // v>=3, global logical coords
org_kde_kwin_fake_input_axis(fi, WL_POINTER_AXIS_VERTICAL_SCROLL, wl_fixed_from_double(15.0));          // one notch (see above)
wl_display_roundtrip(dpy);
```
If the global is missing from the registry (pre-6.8 and no matching desktop file), fall back to the portal.

### Gaps
- `KApplicationTrader` treatment of `NoDisplay=true` desktop files: not verified.
- Exact per-toolkit result of a v120-less axis value 15 on Qt 6, GTK 4, Chromium: not read.
- `/proc/pid/exe` of a process inside a mounted AppImage: not run.
- kdotool/dotool sources: not read (dotool uses uinput).

---

## 4. wlroots: labwc and Hyprland (zwlr_virtual_pointer_v1)

### Takeaway
Both advertise `zwlr_virtual_pointer_manager_v1` to every client; no permission prompt in Hyprland's protocol code. Events go through the normal pointer pipeline so wheel reaches the surface under the real cursor. Use `motion_absolute` to put the cursor in the region first.

### Findings (protocol, [V] from wlr-virtual-pointer-unstable-v1.xml, manager v2)
- Manager: `create_virtual_pointer(wl_seat? seat, new_id zwlr_virtual_pointer_v1)`; `create_virtual_pointer_with_output` (since 2) adds `wl_output?`.
- Pointer requests (all `time` = uint ms): `motion(time, fixed dx, fixed dy)`; `motion_absolute(time, uint x, uint y, uint x_extent, uint y_extent)` ("x can range from 0 to x_extent"; pick extent = output logical size); `button(time, button, state)`; `axis(time, uint axis, fixed value)`; `frame()`; `axis_source(uint)`; `axis_stop(time, axis)`; `axis_discrete(time, uint axis, fixed value, int discrete)`; `destroy`.
- One wheel notch (conventional, mirrors libinput/wlroots; sequence I): `axis_source(WL_POINTER_AXIS_SOURCE_WHEEL=0)`; `axis_discrete(t, WL_POINTER_AXIS_VERTICAL_SCROLL=0, wl_fixed(15.0), +1)`; `frame()`. Positive = down. Value 15.0 per notch is the convention (wlrctl/ydotool style) [I]; Hyprland code maps `deltaDiscrete = discrete * 120` and `delta = wl_fixed_to_double(value)` [V in VirtualPointer.cpp lines ~94-110], so both fields must be sent. Axis > 1 raises `invalid_axis`. Events are queued until `frame`.
- Hyprland [V]: `ProtocolManager.cpp`: `PROTO::virtualPointer = makeUnique<CVirtualPointerProtocol>(&zwlr_virtual_pointer_manager_v1_interface, 2, "VirtualPointer");` and `bindManager` has no permission check (Hyprland's permission manager gates screencopy, virtual keyboard, plugins etc. per its wiki; I did not find pointer gating in the files read). Events are emitted as pointer axis/warp events into the normal input manager, hence delivered to the surface under the cursor.
- labwc [V]: `src/seat.c` creates `wlr_virtual_pointer_manager_v1_create` and `handle_new_virtual_pointer` adds it as a regular pointer with optional output mapping (labwc master builds against wlroots 0.20); axes go via `handle_axis` -> `wlr_seat_pointer_notify_axis`. No client filtering (no security-context check seen in the code read).
- Hyprland synthesized-scroll dispatcher/IPC: none found in this session. (`hyprctl dispatch` has no wheel dispatcher to my knowledge; `sendshortcut` is for keys/mouse buttons; unverified.)
- Overlay behaviour [I]: a put.gd overlay surface with empty input region (`wl_surface_set_input_region` with an empty region) does not take pointer focus; layer-shell surfaces with `keyboard_interactivity=none` and empty input region likewise. Do not leave a full-screen input-taking overlay up during scrolling.
- Moving pointer: `motion_absolute` with extents of the output the region is on; with multiple outputs pass `create_virtual_pointer_with_output` or global-layout extents [I].
- Reference clients: wlrctl, ydotool (uinput), dotool (uinput), wayvnc (uses zwlr_virtual_pointer), lan-mouse: not read; names from memory only.

### Minimal code [U]
```cpp
auto* vp = zwlr_virtual_pointer_manager_v1_create_virtual_pointer(mgr, seat, nullptr?);  // use _with_output if v>=2
uint32_t t = now_ms();
zwlr_virtual_pointer_v1_motion_absolute(vp, t, x, y, outW, outH);
zwlr_virtual_pointer_v1_frame(vp);
zwlr_virtual_pointer_v1_axis_source(vp, WL_POINTER_AXIS_SOURCE_WHEEL);
zwlr_virtual_pointer_v1_axis_discrete(vp, t, WL_POINTER_AXIS_VERTICAL_SCROLL, wl_fixed_from_double(15.0), 1);
zwlr_virtual_pointer_v1_frame(vp);
wl_display_roundtrip(dpy);
```
Fallback on these: RemoteDesktop portal is not implemented by xdg-desktop-portal-wlr (as far as I know, [I]), so the fallback is `/dev/uinput`-like or `ydotool`; both undesirable.

### Added verification (second pass)
- labwc [V: `src/seat.c` master]: `#include <wlr/types/wlr_virtual_pointer_v1.h>` line 15; `handle_new_virtual_pointer` line 626; `seat->virtual_pointer = wlr_virtual_pointer_manager_v1_create(` line 708 with `CONNECT_SIGNAL(seat->virtual_pointer, seat, new_virtual_pointer)` line 710; removed at line 740. No filtering by client.
- Hyprland permissions [V: wiki `content/configuring/core/advanced-configuration/permissions.md`, `src/managers/permissions/DynamicPermissionManager.hpp`]: enforced only if `ecosystem.enforce_permissions` is set (off by default; config is now Lua: `hl.permission({ binary, type, mode })`). Types in the enum: `SCREENCOPY`, `PLUGIN`, `KEYBOARD` (virtual/USB keyboard connection, default ALLOW), `CURSOR_POS`, `INPUT_CAPTURE`. **No virtual-pointer permission type exists**; `CVirtualPointerProtocol::bindManager` has no check [V]. Hyprland's tree has `src/protocols/VirtualPointer.cpp` and `VirtualKeyboard.cpp` only (no fake-input style protocol).
- Client sequences for one notch [V from source]:
  - wayvnc `src/pointer.c`: at init `zwlr_virtual_pointer_v1_axis_source(ptr, WL_POINTER_AXIS_SOURCE_WHEEL)` once; per notch `zwlr_virtual_pointer_v1_axis_discrete(ptr, t, WL_POINTER_AXIS_VERTICAL_SCROLL, wl_fixed_from_int(15), 1)` for down and `(-15, -1)` for up; comment: "I arrived at the magical value of 15 by connecting a mouse with a scroll wheel and viewing the output of wev."; a `frame` follows in the pointer-set path; `motion_absolute(t, x*INT32_MAX, y*INT32_MAX, INT32_MAX, INT32_MAX)` (normalised extents).
  - lan-mouse `input-emulation/src/wlroots.rs`: wheel: `pointer.axis_discrete(now, axis, value as f64 / 8., value / 120)` (so 120 -> 15.0, 1 step), then `axis_source(Wheel)`, `frame()`; continuous: `axis(now, axis, value)`, `axis_source(Continuous)`, `frame()`.
  - wlrctl `pointer/pointer.c` (sourcehut): smooth only: `axis_source(FINGER)`, `axis(timestamp(), axis, dx/dy)`, `frame()`, then `axis_source(FINGER)`, `axis_stop(...)`, `frame()`. It does not send `axis_discrete`, so clients see touchpad-style scrolling.
  - Therefore send 15.0 + discrete 1 with source WHEEL (wayvnc/lan-mouse), not wlrctl's pattern.

### Gaps
- Hyprland dispatcher/IPC for synthetic scroll: not searched this pass either (no `hyprctl` wheel command known).
- wlroots implementation of `axis_discrete` (how `discrete` maps to `value120`) in 0.18/0.20: not read; Hyprland's mapping is `discrete * 120`.

---

## 5. Cross-desktop fallbacks

- XDG RemoteDesktop portal + libei [I except KDE Connect usage V]: `CreateSession`, `SelectDevices(types, persist_mode, restore_token)`, `Start` (shows dialog, returns `devices` and `restore_token`), `ConnectToEIS` -> fd; `ei_new_sender`, `ei_setup_backend_fd`, bind caps, `ei_device_start_emulating`, `ei_device_scroll_discrete(dev, 0, 120)` (value is in 120ths: 120 = one notch), `ei_device_frame`. Implemented by xdg-desktop-portal-gnome (GNOME), -kde (Plasma). Not by -wlr/Hyprland (inferred). `persist_mode=2` = until revoked.
- `/dev/uinput`: default mode root:root 0600 (udev may add `uaccess` rules on some distros); needs a udev rule/group, injects at the kernel level and so is cross-desktop but cannot be shipped silently (permissions, security, and absolute positioning requires a calibrated abs device). Unsuitable for a packaged app. [I]

---

## 6. Wheel-notch settle times

Not researched in the second pass (budget). No per-toolkit pixel-per-notch or animation-duration constants were found in source, so none are claimed. The only sourced numbers: KWin treats 15.0 axis delta as one notch (`input.cpp`), wayvnc/lan-mouse use 15.0 per notch for wlroots, ShareX waits 300 ms (`ScrollDelay`). Plan on measuring: capture repeatedly after a notch until two consecutive frames are identical (or until a timeout), instead of a fixed delay. Chromium (~100-200 ms smooth scroll) and Firefox figures from memory are unverified [I].

## 7. ShareX stitching [V: ScrollingCaptureManager.cs and ScrollingCaptureOptions.cs, master]

### Options (defaults)
`StartDelay=300` ms, `AutoScrollTop=false`, `ScrollDelay=300` ms, `ScrollMethod=MouseWheel`, `ScrollAmount=2`, `AutoIgnoreBottomEdge=true`, `AutoUpload=false`, `ShowRegion=true`.

### Loop
Activate target window; `Task.Delay(StartDelay)`; optional Home/`SB_TOP`. Then until stop:
1. `lastScreenshot = CaptureRectangle(selectedRectangle)` (no cursor).
2. If `CompareLastTwoImages()` (last vs previous byte-equal via `SkiaImageHelpers.CompareImages`, not read) -> end of content, break.
3. Scroll: MouseWheel `SendMouseWheel(-120 * ScrollAmount)` (so 2 notches), or Down arrow xN, PageDown, or WM_VSCROLL SB_LINEDOWN xN.
4. `CombineImagesAsync(Result, lastScreenshot)` (runs while page animates); null -> break.
5. previous = last; `delay = ScrollDelay - elapsed`; sleep the remainder (so the settle wait is ScrollDelay minus stitch time, and the capture at the top of the loop happens after it).
Note capture happens after the delay and scroll is sent *after* the capture; first iteration captures initial view.

### CombineImages
- First frame: result = copy.
- Fail if width differs or `currentImage.Height > result.Height`.
- `matchLimit = currentImage.Height / 2`; `ignoreSideOffset = min(max(50, width/20), width/3)`; compared bytes per row = pixels from `ignoreSideOffset` to `width - ignoreSideOffset` (RGBA, 4 bytes), exact equality via `SequenceEqual`; result rows compared are the *last frame-height rows of the result* (`rect.Y = result.Height - currentImage.Height`... see code).
- Bottom edge: `ignoreBottomOffsetMax = height/3`; `ignoreBottomOffset = max(50, height/10)`; if AutoIgnoreBottomEdge, compare rows from the bottom of result and current upward; at the first differing row `i`, `ignoreBottomOffset += i`; then `max(..., bestIgnoreBottomOffset)`, then clamp to max. (Detects a sticky footer: rows identical in both frames at the bottom are excluded from matching and are cut from the result before appending.)
- Quoted matching loop:
```csharp
int rectBottom = rect.Bottom - ignoreBottomOffset - 1;
for (int currentImageY = currentImage.Height - 1; currentImageY >= 0 && matchCount < matchLimit; currentImageY--)
{
    int currentMatchCount = 0;
    for (int y = 0; currentImageY - y >= 0 && currentMatchCount < matchLimit; y++)
    {
        if (CompareRows(resultScan0 + ((rectBottom - y) * stride), currentImageScan0 + ((currentImageY - y) * stride), compareLength) == 0)
            currentMatchCount++;
        else break;
    }
    if (currentMatchCount > matchCount) { matchCount = currentMatchCount; matchIndex = currentImageY; }
}
```
  I.e. for each candidate row Y in the new frame (bottom up), count how many consecutive rows going upward equal the result's rows ending at `rectBottom` (bottom of result minus ignore offset); pick the longest run (cap = half height).
- Append: `matchHeight = currentImage.Height - matchIndex - 1`; new result height = `result.Height - ignoreBottomOffset + matchHeight`; draw result minus its bottom `ignoreBottomOffset` rows, then rows `matchIndex+1 ..` of the new frame.
- Fallback: if `matchCount == 0 && bestMatchCount > 0`, reuse the best previous `matchCount/matchIndex/ignoreBottomOffset` (the scroll step is assumed constant), status PartiallySuccessful. Else status Failed, returns null, capture ends (keeping what it has). Bug-for-bug notes: no fuzzy tolerance (exact equality, so subpixel/video/gradient content fails); `matchHeight <= 0` also fails.

### Complaints (ShareX issue tracker, read bodies only for three issues)
- #1275: capped at 100 scrolls; end detection impossible when video plays at the bottom (maintainer quote); no manual stop. [V]
- #7424: "you only scroll one step"; maintainer-side answer pointed to the docs section on static elements (sticky headers/footers) [V]
- #7334: after the v16 rewrite, auto-detect "tends to delete most of the screenshots"; users lack manual overlap adjustment; static content on sides/bottom (e.g. Discord message bar) breaks it [V]
- Duplicated chunks and smooth-scrolling problems are plausible consequences (exact equality + fixed delay) but I did not find dedicated issue text for them [I].

### Deepin / wayscrollshot
Not researched this session (Gap). Do not rely on any claim about them.

---

## Overall gaps (for the report writer)
- Closed in the second pass: KWin gating per release (6.3.6, 6.5.0, 6.6.0 desktop-file; 6.8 sandbox-only); `authenticate` is a no-op; GSConnect RemoteDesktop usage; mutter caller check (same D-Bus connection only); indicator logic; Clutter signatures unchanged 46 to 50; real GJS examples; wlroots client sequences; labwc lines; Hyprland permissions; xdotool; Debian/Ubuntu packages.
- Still open: observed look of the GNOME indicator; Plasma 6.8 `axis` behaviour in Qt/GTK/Chromium without v120; whether an AppImage can satisfy the pre-6.8 desktop-file match (inferred no); Hyprland scroll dispatcher; toolkit scroll constants; Deepin and wayscrollshot; `SkiaImageHelpers.CompareImages`; Fedora/Arch package file lists.
