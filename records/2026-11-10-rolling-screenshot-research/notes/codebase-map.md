# put.gd codebase map for "Auto-scroll rolling screenshot"

Source: nightly checkout a `nightly` checkout (HEAD `32a9a763e`, read-only).
All paths are relative to the repo root. Line numbers are from that HEAD. Source is written in a dense
one-statement-per-line style, so a "line" is often a whole function body. Statements marked
**(unverified)** rest on outside knowledge, not on anything in the repo.

Headline findings (details below):

1. **No input injection exists in the product** (Q4). Nothing under `src/` links or calls XTest, uinput, fake_input, virtual-pointer, RemoteDesktop, libei. Lab/test code has all of them.
2. **Every existing single-shot screenshot path already excludes the cursor; every recording path embeds it** (Q2). A step-wise design (scroll, settle, one still grab) is the cheapest fit. A streamed 10 to 30 fps design reuses `putgd-record` acquisition but needs the cursor mode flipped in five places.
3. **The editor refuses images over 24 megapixels** (`src/core/EditorJob.h:49`): at 1600 px wide that is 15,000 px tall, so a 1600 x 30000 image cannot be opened by "edit". The plain path has a different wall: `limits.pendingImageBytes` defaults to 64 MiB and a `kind=="image"` payload of 183 MiB fails `image_memory_limit` (`src/app/OperationService.cpp:434-439`).
4. **GNOME's extension has no region-capture or input method** (Q9); `Acquire` selects and captures whole monitors then ships base64 PNG over D-Bus in 64 KiB chunks. Any GNOME work needs an extension version bump (19 to 20) and a re-login.
5. **The KDE restricted-interface key for Wayland protocols is `X-KDE-Wayland-Interfaces`** (used today only for `zkde_screencast_unstable_v1` on `putgd-record`); ScreenShot2 uses the different key `X-KDE-DBUS-Restricted-Interfaces` (Q10).
6. **Layer rules** (`tools/ci/check_layers.py:30-55`) decide where the new interface may live: `app` may not include `platform/*`, so a `ScrollDriver`-style interface must be in `core/` (Q5, Q16).

---------------------------------------------------------------------------------------------------

## 1. Region capture flow today, end to end

### 1.1 Entry points (all converge on `OperationService::invoke`)

| Trigger | Code |
| --- | --- |
| Session method `action.invoke {action, source?, path?, mode?}` | `src/app/LocalServer.cpp:130-134` validates fields, then `operations_.invoke(p["action"], reply, options)` |
| `putgd-cli action.invoke '{"action":"region"}'` | `src/cli/main.cpp:26-55` is a generic forwarder: `parser.addPositionalArgument("method",...)`, builds `{schemaVersion:1, requestId, session, method, params}`. It knows no method names. |
| `editor.open {source?,path?}` | `src/app/LocalServer.cpp:143-146` -> `operations_.invoke("edit", reply, p)` |
| Tray click | `src/ui/TrayController.cpp:195` (native menu) -> `invokeAction(action)` (`:544-560`) -> `operations_.invoke(...)`; labels at `:223-224`; native tray table `src/ui/NativeTray.cpp:108-123` (`Entry{label,action,parent}`) |
| Global shortcut | per-adapter signal `actionRequested(action)` wired to the tray at `src/main.cpp:458-474` -> `TrayController::invokeShortcut` (`:538-543`) -> `invokeAction(action,true)` |
| Main window buttons | `putgd-ui` `src/ui/MainWindow.cpp:137-186`, sends `action.invoke` over the session socket |
| MCP `perform_action` | `tools/mcp/share_mcp/server.py:227-232` -> `adapter.call('action.invoke', {'action': action})` |

Actions are `Settings::actionNames()` = `region, window, desktop, clipboard, edit` (`src/core/Settings.cpp:54`) plus `record`
(`:56`); UI order `presentationOrder()` = `region, window, desktop, edit, record, clipboard` (`:58`).

### 1.2 `OperationService::invoke` (`src/app/OperationService.cpp:261-356`)

1. `:270-275`: `record` is special-cased first (`recording_->invoke(mode,reply)`), refuses with `editor_active` if an editor is open.
2. `:276`: `Settings::actionNames().contains(action)` else `invalid_action`.
3. `:279`: `source = action=="edit" ? options["source"] (default "region") : action`. Edit sources: `region|window|desktop|clipboard|file` (`:281`).
4. Exclusion errors: `editor_active` (`:282`), `recording_active` (`:283`), `queue_full` (`:285`), `busy_selecting` (`:286`, `selectingId_`), `output_required` (`:289`).
5. `:290-292`: builds an `Operation` (id, action, settings snapshot, destination from `snapshot.actions.value(action)`); `if(action=="edit"){editingId_=op.id;editor_=make_shared<EditorSession>();}`.
6. `:300-330`: `source_.setRegionScreenshotFirst(snapshot.regionSelectionMode=="screenshot_first")` then
   `acquisition = source_.prepareAcquisition(source, snapshot.limits, earlyTerminal, released)` (`SourceAdapter` API, `src/core/SourceAdapter.h:26-56`). Native target and layout are frozen here, and for live region selection the selector starts here, **before** the two journal saves. Geometry only; no pixels.
7. `:332-356`: journal save #1 (accepted), `reply({operationId,operation})`, journal save #2 (`state="acquiring"`), then `acquisition(limits, callback)`: only now are pixels read. The callback runs `startEditing` (action `edit`, `:354`) or `enqueue({op,payload,...})` (`:355`).

### 1.3 Plain region capture after pixels

- `enqueue` (`:428-443`): for `payload.kind=="image"` it charges `image.sizeInBytes()` against `limits.pendingImageBytes` and fails with `image_memory_limit` when over (`:434-441`). Default `pendingImageBytes = 67108864` (64 MiB) (`src/core/Settings.h:36`).
- `pump()` (`:544`) -> `run(Job)` (`:545`, on a worker via `background`): `ArtifactStore::commit` (spool file, SHA-256; `src/core/ArtifactStore.cpp:215-245`): `kind=="image"` is encoded to PNG **in memory** with `QImage::save(&buffer,"PNG")` (`:224`), `kind=="png"` is stored verbatim (`:225-227`), `kind=="files"` streamed (`:214-220`); then `LocalArchive` copy, `StorageProvider` upload, `HistoryStore` commit, link copy (`beginUploadCopies`/`uploadLinkReady`). Owners per `docs/design/overview.md:47-53`.
- Thumbnail: `ArtifactStore::preview` (`src/core/ArtifactStore.cpp:80-100`): `QImageReader` with `setScaledSize(256x256 keep ratio)` then `scaled()`; limit `maxPixels`. A 1600 x 30000 image becomes about 14 x 256 px.

### 1.4 "Capture region & edit" (`edit`) vs plain region

Same acquisition (`source=="region"`), different sink:

- `startEditing` (`OperationService.cpp:449-504`): payload must be `kind=="image"` or one file; `op.state="editing"`; `EditorJob(staging=<data>/editing, helper=putgd-ui).run(*image,destination,outputBytes,session)`.
- `EditorJob::run` (`src/core/EditorJob.cpp:98-106`): **rejects `w*h > EditorJob::admissionPixels = 24000000`** (`src/core/EditorJob.h:49`) -> `edit_input_too_large` (`EditorJob.cpp:57`); stages the QImage as PNG with `QImageWriter(&input,"png")`, `setQuality(80)` into a private 0700 `pge-XXXXXX/input.img` (0400, hashed), spawns `putgd-ui --edit-image` (private UiControl pipes, role `image-edit`; protocol in `docs/design/image-editor.md:190-217`).
- The editor returns sanitized PNG bytes; the resident re-enters the normal path as `ClipboardPayload{kind="png", bytes, mime="image/png"}` (`OperationService.cpp:487-495`), never re-encoded (`ArtifactStore.cpp:225`).
- `outputBytes = min(limits.maxFileBytes, 512 MiB)` (`:454`). File input (`runFile`) is separately capped at `min(maxFileBytes,256 MiB)` (`:469`).
- Output required unless keepUploads (`:455`).

### 1.5 Per desktop: who does selection, who reads pixels

| Desktop | Adapter (chosen in `src/main.cpp:244-282`) | Process: selection | Process: pixels | Frozen target / layout |
| --- | --- | --- | --- | --- |
| Cinnamon/X11 (Core route) | `X11CoreSourceAdapter` (`src/platform/x11/X11CoreSourceAdapter.*`) + `CaptureProcessController` | `putgd-capture` (`src/capture/main.cpp`) shows `NativeRegionOverlay` (xcb surfaces, pointer+keyboard grab: `src/platform/x11/NativeRegionOverlay.cpp:233-234`) | `putgd-capture`: `CinnamonRegionCapture` calls `org.Cinnamon.ScreenshotArea` per monitor (`CinnamonRegionCapture.cpp:99-100`) or `X11Capture::frames` root grab; `composeFrames` crop; PNG encode in a `QThread` with `BoundedFile` (`src/capture/main.cpp:162-170`); result.png in `/tmp/putgd-capture-XXXXXX/` (0700 dir, 0600 file) | resident freezes via `X11NativeSnapshot` before the helper starts (`X11CoreSourceAdapter.cpp:30-38`); helper re-checks `native.unchanged` |
| Cinnamon Core resident decode | resident worker `CaptureProcessController::decode` (`src/platform/x11/CaptureProcessController.cpp:213-236`) verifies size/hash/PNG header, decodes into a pre-allocated `QImage` (bypasses Qt's reader allocation guard), returns `PayloadResult{image}` | | | |
| GNOME/X11, Plasma/X11, other X11 (QApplication fallback) | `X11SourceAdapter` in the resident (`X11SourceAdapter.cpp:76-189`); selector `RegionOverlay` (`src/ui/RegionOverlay.cpp`) | resident | resident: `X11Capture::frames` -> `QScreen::grabWindow(0)` (`X11Capture.cpp:102`) after `X11CompositorSettle` (XDamage quiet) | `X11Capture::freeze` |
| GNOME Wayland | `GnomeAdapter` (`src/platform/gnome/GnomeAdapter.cpp:190-262`) | Shell extension: St `RegionSelector` actor, started by `Preview` (`:206`) | Shell extension: `Shell.Screenshot.screenshot_area(x,y,w,h,stream)` per monitor (`integrations/gnome/extension.js:1223`) or `composite_to_stream` from a frozen stage; resident pulls base64 chunks with `Read` (`GnomeAdapter.cpp:233-244`) and decodes in a worker (`gnome::decodeTransfer`, `GnomeProtocol.cpp`) | `Prepare` ticket, layout from Mutter DisplayConfig |
| KDE Plasma Wayland | `KdeSourceAdapter` (`src/platform/kde/KdeSourceAdapter.cpp:70-110`) | `putgd-region` (`src/platform/wayland/region_main.cpp:37`, `LayerShellRegionOverlay`) via `WaylandRegionProcess` (`RegionProcess.h:18`): geometry only, helper must exit 0 | **resident**: `KWinCapture::request("CaptureScreen", {screen}, ...)` per output (`KdeSourceAdapter.cpp:198`), compose in a worker (`:220`) | `layout()` frozen, `unchanged()` rechecked |
| Budgie 10.10 / labwc | `BudgieSourceAdapter` (`src/platform/budgie/BudgieSourceAdapter.cpp:82-194`) | `putgd-region` | **resident**: `ImageCopyCapture::captureOutput` (`src/platform/wayland/ImageCopyCapture.cpp:360`) + `composeOutputFrames` (`CaptureCompose.h:15`) | frozen layout |
| Hyprland | `HyprlandSourceAdapter` (`src/platform/hyprland/HyprlandSourceAdapter.cpp:202-325`) + `PressCatcher` (`:41`) | `putgd-region` | resident `ImageCopyCapture` | frozen layout, IPC `j/activewindow` for windows |

Route selection is environment-based (Q5.1). `regionSelectionMode` default `live`: pixels are acquired only after both journal checkpoints; `screenshot_first` is the opt-in frozen mode (`OperationService.cpp:329`, `docs/design/architecture.md:30-46`). Recording selection is always live (`schemas/config.schema.json:901-907`).

### 1.6 Details worth knowing

- Hotkey crosshair hold on Cinnamon: `X11CoreSourceAdapter.cpp:10-18` (press -> `holdCrosshair`, `activated` -> release); `crosshairHoldMs = 5000` (`CaptureProcessController.h`).
- `CaptureProcessController` helper protocol: bootstrap (nonce, generation, build, limits triple, path/device/inode, cursor, appearance), `ready`, `preview`, `begin`, `handoff_done`, `accept`; deadlines 10 s prepare / 120 s select (`src/capture/main.cpp:123,225,262`; `CaptureProcessController.cpp:100-105`). It is one-shot per capture and refuses a second (`busy_selecting`).
- Process-level checks everywhere: matching build manifest, nonce, generation, bounded frames, normal exit (`docs/design/architecture.md:46-47`).

---------------------------------------------------------------------------------------------------

## 2. Frame sources per desktop

Legend: SS = single still per call; STREAM = continuing frames. "Cursor" is what ships today.

| Source | File | Process | Shape | Pixel format | Region crop | Cursor today | Scale / multi-monitor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **X11Capture** (generic root grab) | `src/platform/x11/X11Capture.{h,cpp}`; `frames()` `:98-119` | `QGuiApplication` xcb process only (`X11Capture::X11Capture` returns without a connection unless platform is `xcb`, `:10-14`): QApplication resident or `putgd-capture` | SS, sync: `screen->grabWindow(0).toImage()` (`:102`) per RandR monitor | `QImage` (Qt root grab, DPR set to 1) | whole monitor, cropped later by `composeFrames`; `grabWindow(0,x,y,w,h)` supports a rect but is unused | **excluded** (comment `:99-101`) | `CaptureFrame{identity, logicalRect, nativeRect, density, rotation, pixels}` (`src/platform/Geometry.h`); RandR native vs Qt logical, scale mismatch >0.02 rejected (`:48-51`); multi-monitor = one frame per monitor |
| **CinnamonRegionCapture** | `src/platform/x11/CinnamonRegionCapture.{h,cpp}` | whichever process owns `X11SourceAdapter` (`putgd-capture` on Core route) | SS, async per monitor: D-Bus `org.Cinnamon.ScreenshotArea(false,x,y,w,h,false,path)` (`:99-100`) writes a PNG file; completion by inotify `IN_CLOSE_WRITE` (fallback poll for IEND, `:80-95,123-135`); decode in `QThread` (`:136-171`); deadline 10 s | PNG 8-bit, RGB(A) | the code passes the full monitor `nativeRect` (`:98`); the D-Bus call itself takes an area, so a region rect is possible but unused | first/sixth args `false` (include-cursor, flash per Cinnamon's signature **(unverified)**) | native coordinates; one call per monitor |
| **X11CompositorSettle** | `src/platform/x11/X11CompositorSettle.{h,cpp}` | same | event: XDamage on root, settles after `quietMs=100` of no repaints in the areas, limit 1000 ms (`.h:21-23`) | n/a | native areas | n/a | Directly reusable idea for "wait for a scroll step to finish painting" |
| **KWinCapture** (ScreenShot2) | `src/platform/kde/KWinCapture.{h,cpp}`, transfer `KWinTransfer.*` | **resident only** (desktop entry matches the resident exe, `KWinCapture.cpp:20-41`) | SS, async: `CaptureScreen(name,options,fd)`, `CaptureActiveWindow` (`KdeSourceAdapter.cpp:60,198`); raw image over a nonblocking pipe fd + metadata (`:50-80`); 10 s | raw `QImage::Format` named by metadata (validated, `KWinTransfer.cpp:14-15`) | options `include-cursor:false, native-resolution:true, include-decoration:true, include-shadow:false` (`KWinCapture.cpp:63`); **only whole screens and the active window are used**; ScreenShot2 also has an area request **(unverified here; see the Plasma 6.6 XML cited in `docs/desktops/kde.md:111`)** | **excluded** | metadata `scale`, `screen` checked against frozen output (`KdeSourceAdapter.cpp:202-205`) |
| **zkde-screencast** | `src/record/KdeScreencast.{h,cpp}` | `putgd-record` | STREAM: PipeWire node. `streamOutput/streamRegion/streamWindow` (`.h:30-35`) -> `zkde_screencast_unstable_v1_stream_region(x,y,w,h,scale,pointer)` (`KdeScreencast.cpp:147`); consumed by GStreamer `pipewiresrc` (`src/record/WaylandAcquisition.h`, `RecordingPipeline.cpp`) | GStreamer `video/x-raw` | logical rectangle done by KWin, even-size rounding | **embedded** (`POINTER_EMBEDDED`, `:136,147,158`); protocol enum has `hidden=1` (`src/platform/kde/protocols/zkde-screencast-unstable-v1.xml:16-21`) | no dialog, but KWin only offers it to an exe whose desktop entry lists `X-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1` (Q10); KWin >=6.6 omits the requester's own windows from the stream (`docs/desktops/kde.md:49-56`) |
| **MutterScreenCast** | `src/record/MutterScreenCast.{h,cpp}` | `putgd-record` | STREAM: `org.gnome.Mutter.ScreenCast` `RecordMonitor/RecordArea/RecordWindow` then PipeWire node (`:62,68,75`) | GStreamer | `RecordArea(x,y,w,h,{cursor-mode})` logical rect | **embedded**: `{"cursor-mode", uint(1)}` (`:62,68,75`); other modes hidden/metadata exist in Mutter **(unverified)** | no dialog on tested GNOME; Mutter has no per-window exclusion of the requester's own surfaces |
| **GNOME extension bridge** | `integrations/gnome/extension.js` (`Prepare/Preview/Acquire/Read/Release`, `:34-38`) + `src/platform/gnome/GnomeAdapter.cpp` | Shell (capture) + resident (bridge, decode) | SS: one `Acquire` = selection (region) + one PNG per monitor via `screenshot_area` (`extension.js:1223`) or `composite_to_stream` of a frozen stage texture (`:1186-1221`); transfer 64 KiB base64 `Read` chunks (`GnomeProtocol.h chunkBytes=65536`) | PNG | whole monitor frames, crop in the resident's `decodeTransfer`/`composeFrames` | **excluded** (`docs/desktops/gnome.md:7`) | layout from `org.gnome.Mutter.DisplayConfig`; fractional scale handled by resample (`extension.js:1140-1160`); frames reported with `density`, `native`, `logical` |
| **ImageCopyCapture** (ext-image-copy-capture) | `src/platform/wayland/ImageCopyCapture.{h,cpp}` | resident (Budgie, Hyprland; the KDE adapter does not use it) | SS, async: `captureOutput(name,limits,Reply)` / `captureToplevel(id,...)` (`.h`); each call creates a session and one frame (`ImageCopyCapture.cpp:255` `create_session(copy,source,0)`) and one `wl_shm` buffer | `wl_shm` format -> `QImage::Format` via `shmImageFormat`; rotated outputs turned upright; density 1 | whole output only | **excluded**: options argument `0` (`:255`); `paint_cursors` flag exists | own `wl_display` (Q11); one request per output |
| **ImageCopySource** (recording) | `src/record/ImageCopySource.{h,cpp}` | `putgd-record` | STREAM into GStreamer `appsrc` from a capture thread, 4 `wl_shm` ring, damage-driven, last frame resent each 1 s on a still screen (`.h:20-27`) | GStreamer caps from the shm format | whole output, cropped by `videocrop` in the pipeline | **painted**: `EXT_IMAGE_COPY_CAPTURE_MANAGER_V1_OPTIONS_PAINT_CURSORS` (`ImageCopySource.cpp:309`) | output-sized |
| **PortalScreenCast** | `src/record/PortalScreenCast.{h,cpp}` | `putgd-record` | STREAM via xdg-desktop-portal; `start(sourceTypes, restoreToken, Done)` | GStreamer | `videocrop` of a monitor share | `cursor_mode = Embedded if offered else Hidden` (`PortalScreenCast.cpp:104`) | picker once per target kind with a stored restore token (`docs/design/recording/wayland.md:41-49`); **never used on Budgie/Hyprland**; Plasma/GNOME only as fallback |
| **X11 recording** (`ximagesrc`) | `src/record/RecordingPipeline.cpp:369-370` | `putgd-record` | STREAM | GStreamer | `startx/starty/endx/endy` | **embedded** `show-pointer=true` | root pixels; it records every visible pixel in the area, so overlays are kept outside the area (Q3) |

### Can a caller get 10 to 30 fps for 30+ s without re-prompting, cursor excluded?

- **Streams already exist and run without re-prompting** on KDE (`kde-screencast`), GNOME (`mutter-screencast`), Budgie and Hyprland (`wlr-capture`, no portal), X11 (`ximagesrc`). Measured: KWin 6.7 59.7 to 59.9 distinct frames/s, 60 fps monitor recording (`docs/design/recording/wayland.md` "Timestamps and A/V sync"); `recordingFrameRate` 30 or 60 (`schemas/config.schema.json:909`), `AdaptiveRate` steps down under load.
- **They embed the cursor today.** To exclude it: X11 `show-pointer=false` (`RecordingPipeline.cpp:369-370`), Mutter `cursor-mode` 0 (`MutterScreenCast.cpp:62,68`), KWin `POINTER_HIDDEN` (`KdeScreencast.cpp:147`), portal `Hidden` (`PortalScreenCast.cpp:104`), ext-image-copy flags 0 (`ImageCopySource.cpp:309`). None of these hidden modes is exercised anywhere in this repo (except the portal fallback when Embedded is not offered), so each needs acceptance.
- **They are all inside `putgd-record`** (GStreamer + FFmpeg dev libraries required, optional build `PUTGD_RECORDING`, `cmake/Recording.cmake:5-9`). Nothing in the resident or `putgd-capture` consumes PipeWire (`grep pipewire cmake/*.cmake` finds no libpipewire link; only GStreamer).
- **Cheapest "pixels of rectangle R now" per desktop** (all cursor-free by default):
  - X11 generic: `QScreen::grabWindow(0,x,y,w,h)` or raw `xcb_get_image` on root (xcb already linked: `cmake/Platform.cmake:4`); wait with XDamage (`X11CompositorSettle`). Muffin composited desktops: the repo found a root read can precede presentation and used Cinnamon's `ScreenshotArea` instead (`X11SourceAdapter.cpp:117-120`). Unmeasured per-call latency.
  - Cinnamon: `ScreenshotArea` with a region rect (PNG encode + file + inotify per frame; unmeasured).
  - KDE: `KWinCapture` `CaptureScreen` (full output raw, in the resident only); area request not used today.
  - GNOME: needs a new extension method (e.g. `CaptureArea(x,y,w,h)`) because `Acquire` always selects and captures whole monitors, and returns through base64 D-Bus chunks.
  - Budgie/Hyprland: `ImageCopyCapture::captureOutput` (full output; session created per call).
- No existing source returns a rectangle directly with cursor control except the streams.

---------------------------------------------------------------------------------------------------

## 3. Recording's on-screen frame and controls (and how it stays out of the pixels)

Owner: `putgd-record`, `src/record/Overlays.{h,cpp}`; session `src/record/RecordSession.cpp`; resident drives GNOME's Shell-side parts through `RecordingShell`.

### 3.1 Pieces

- `SelectionOverlay` (`Overlays.h:30-60`, `.cpp:135`): drag surfaces on every screen for X11; on layer-shell desktops the helper instead reuses `LayerShellRegionOverlay` (`docs/design/recording/wayland.md` "Wayland selection").
- `BoundsOverlay` (`Overlays.h:75-95`, `.cpp:286-325`): ready ring 3 px white (`QColor(255,255,255,235)`) just **outside** the rectangle plus a 1 px dark hairline; while recording four dim strips cover everything outside (`dimColor{0,0,0,110}`). Strips are created clear with the ring so they map before the bar (`.cpp:286-300`, #127).
- `PassiveSurface` (`.cpp:246-266`) with `passiveFlags` (`.cpp:70`):
  `Qt::Tool | Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::X11BypassWindowManagerHint | Qt::WindowDoesNotAcceptFocus | Qt::WindowTransparentForInput`, attributes `WA_TranslucentBackground, WA_ShowWithoutActivating, WA_NoSystemBackground`. On X11 Qt turns `WindowTransparentForInput` into an empty input shape (the repo relies on exactly this in `NativeRegionOverlay.cpp:187`, "Qt's empty input shape lets early clicks reach the native parent"). Wayland: same flag; the doc states KDE ring/strips are "input-transparent overlay layer surfaces" (`docs/design/recording/wayland.md` "Wayland selection, bounds and bar"). How Qt maps the flag to a Wayland input region is **unverified in the repo**.
- Layer-shell mode (`Overlays.cpp:37-69`): `SurfaceMode surfaceMode()` returns `LayerShell` when the Qt platform is Wayland and `XDG_CURRENT_DESKTOP` has token KDE, Budgie or Hyprland, else `Compositor` (GNOME), `X11` for xcb (`:40-52`). `toLayer()` (`:57-68`): `LayerShellQt::Window::get`, scope `putgd-record`, `LayerOverlay`, anchors top-left, `setExclusiveZone(-1)`, keyboard `OnDemand` (bar) or `None` (passive), margins = logical offset on the output. Strips that cross an output seam are split per screen (`:268-282`).
- `ControlBar` (`Overlays.h:100-170`, `.cpp:329+`): `Qt::Tool | Frameless | StaysOnTop | X11BypassWindowManagerHint` (accepts focus/clicks); recording-specific widgets (format/audio/Record/Pause/Stop/Discard); placement in `src/record/BarPlacement.cpp` (shared with the layer-shell path): below the rect, else above, else another monitor, else inside the corner where it shrinks to an 88x35 px handle that **is in the clip**. `placeAround` (X11), `placeOnLayer` (`.cpp:587-627`), window title constant `controlBarTitle = "put.gd recording controls"` (`Overlays.h:27`).

### 3.2 Keeping it out of the capture, per desktop

| Desktop | Mechanism |
| --- | --- |
| X11 | `ximagesrc` records every visible pixel, so ring and strips are outside the rectangle by construction and the bar is placed outside (`docs/design/recording/overlay-and-review.md` "Overlay (X11)") |
| KDE | layer surfaces outside the rect; KWin >=6.6 also leaves the requester's windows out of its own stream (`kdeScreencast.hidesRequester`); 6.3 does not. A bar forced inside the rect collapses to the handle and appears in the clip |
| GNOME | the resident calls the extension's `ShowRecordingFrame {rect,kind,state,pid}` (`extension.js:44,1550`): `class RecordingFrame` (`:142-187`) draws the ring and dim strips as `St.Widget({reactive:false,can_focus:false,track_hover:false})` actors on `Main.uiGroup`, and moves the helper's bar window (matched by title `put.gd recording controls` and by being a direct child of the resident) out of the rectangle with `move_frame/make_above`. `HideRecordingFrame` (`:45,1590`) removes them. Resident side: `GnomeAdapter::showFrame/hideFrame` (`GnomeAdapter.cpp:287+`) |
| Budgie / Hyprland | layer surfaces as on KDE; a monitor recording includes the bar (`docs/desktops/budgie.md`, Recording) |
| Window recordings | stream carries only that window; `overlayExcluded=true`, no ring (`wayland.md`) |

`overlayPlacement` reports `outside | handle | hidden | compositor` (`docs/design/recording/wayland.md`, end).

### 3.3 What auto-scroll needs, and what is reusable

- A visible frame: `BoundsOverlay` as is (ring outside, strips optional). A scroll capture **injects wheel events into the area under the ring**, so every ring/strip surface must stay input-transparent. They already are on X11 (`WindowTransparentForInput` + bypass) and are documented click-through on layer shell. GNOME actors are `reactive:false`.
- A stop control that does not take wheel events and is not in frames: put the bar outside the rectangle (existing `BarPlacement`); the full-screen/handle fallback is a problem for a scrolling capture because the bar would be in the frame. Prefer a minimal bar (Stop + progress) and refuse or relocate if no outside spot exists.
- `ControlBar` is recording-specific (`Options{formats,codecs,audioSupported}`); a scroll session needs its own small bar class that reuses `BarPlacement`, the `toLayer` helper and `controlBarTitle`-style title matching for the GNOME extension (the extension currently accepts only the exact recording title; see `extension.js:1550+`).
- A stop key: on X11 the resident can see raw key events without a grab (XInput2 raw key press/release, `src/platform/x11/X11Shortcuts.cpp:22-27,142`; `X11CoreSourceAdapter.cpp:7-10` already turns Escape into `escapePressed` while a crosshair hold is active). On Wayland there is no passive Esc; options are the bar's Stop button, the global shortcut toggling (the `record` shortcut toggles Stop: `OperationService.cpp:270-275`, `TrayController.cpp:549`), or a layer surface with `KeyboardInteractivityOnDemand`.

---------------------------------------------------------------------------------------------------

## 4. Input injection / pointer control

### 4.1 Product: none (verified)

How checked: `grep -rniE "XTest|XWarpPointer|uinput|fake_input|virtual_pointer|virtual-pointer|RemoteDesktop|libei|xdo|wtype|ydotool|dotool|InputEmitter|fakeinput|XSendEvent|QTest::mouse"` over `src CMakeLists.txt cmake packaging integrations` returned only `cmake/Test*.cmake`, `cmake/TestSupport.cmake` (test targets linking `xcb-xtest`) and `cmake/Platform.cmake` (matched `xcb-xinput`/`xfixes`, not injection). `src/ui/Ui.{h,cpp}` matched only incidental substrings. Not vendored: no `wlr-virtual-pointer`, `fake-input`, `ei` XML in `src/platform/wayland/protocols` or `src/platform/kde/protocols`. `integrations/gnome/extension.js` has no `VirtualInputDevice`. Pointer *reading* exists: XFixes cursor image (`NativeRegionOverlay.cpp:222-226`), pointer grabs (`:233-234`), the Hyprland PressCatcher (a layer surface that receives presses, `src/platform/hyprland/PressCatcher.*`).
Dependencies already in the build: `xcb-xtest` is in the documented dev packages (`docs/release/build.md:11` `libxcb-xtest0-dev`) but linked only by tests: `cmake/TestsPlatform.cmake:28-29`, `TestsNativeSession.cmake:7-9,72`, `TestsRegionCapture.cmake:24`, `TestSupport.cmake:4-6`.

### 4.2 Lab and test tooling (reference implementations, not product code)

| Desktop / context | Mechanism | Where |
| --- | --- | --- |
| X11 in C++ tests | `xcb_test_fake_input` motion, button 1..n, keys | `tests/fixtures/X11DesktopFixture.h:14-17`, `tests/desktop/x11/test_native_region_overlay.cpp:42-46,238-240,303`, `tests/performance/bench_capture.cpp:110-126`, `tests/desktop/x11/test_x11.cpp:35,204`. Wheel = buttons 4/5 would use the same call; no wheel call exists |
| X11 lab shell | `xdotool` | `tools/lab/surface_driver/target.py:55,482`, `tools/lab/fluidity_run.py:29`, `docs/testing/surface-driver-prerequisites.md:15,20` |
| Physical desktops | kernel uinput through a forwarded QMP-compatible agent: keyboard + absolute pointer (EV_KEY/EV_ABS only, **no relative wheel**) | `tools/lab/host_input.py` (`validate()` accepts only key, btn, abs events; `ABS_MAX=32767`) |
| Physical desktops, wheel | RFB (VNC) pointer mask incl. `wheel-up=8`, `wheel-down=16` | `tools/lab/rfb.py:65-74`, `tools/lab/surface_driver/target.py:753-760` (`scroll_vnc`) |
| VMs | QMP `input-send-event` (abs + btn) | `tools/lab/lab.py:959-966`, `target.py:700-730` |
| wlroots (labwc, Magpie) | `zwlr_virtual_pointer_manager_v1` motion/button, stdlib Wayland client | `tools/lab/wayland_pointer.py` (opcodes: motion_absolute, button; no axis yet), driven from `tests/integration/test_budgie_labwc.cpp:287-308`; also covers Magpie headless (`docs/desktops/budgie.md:170`) |
| Multi-output lab | portal-VNC or uinput routes | `tools/lab/multi_output_native.py:62-77,220-223` |
| Portal consent witness | recognises ScreenCast/RemoteDesktop portal dialogs | `tools/lab/surface_driver/fixtures/consent.py:49,118` (`DIALOG_MEMBERS` includes `('RemoteDesktop','Start')`) |
| Desktop fixture app | synthetic window; **no scrollable content exists** (`grep -il scroll tests` hits only History/Settings tests) | `tests/fixtures/desktop_fixture.cpp` |

### 4.3 Per-desktop injection candidates (none verified on this repo's builders; all external knowledge **(unverified)** unless stated)

- X11: XTest `xcb_test_fake_input(MOTION_NOTIFY ...)` + buttons 4/5 (and 6/7 for horizontal). **Hazard (verified mechanism):** a hotkey like Ctrl+Shift+N leaves real modifiers down at start; a wheel event with Ctrl held zooms browsers. The resident sees raw key release (`X11Shortcuts.cpp:142`); the session must wait for all modifiers to be released or release them.
- Plasma: `org_kde_kwin_fake_input` (`axis` request) gated by `X-KDE-Wayland-Interfaces=org_kde_kwin_fake_input` in a desktop entry whose `Exec` is the connecting binary (same mechanism as `zkde_screencast_unstable_v1`, evidence `docs/history/flatpak.md:157-170`); or libei via the RemoteDesktop portal (consent dialog).
- GNOME: inside the extension via a Clutter virtual device, or Mutter `org.gnome.Mutter.RemoteDesktop` (`NotifyPointerAxis*`); not present in either place today.
- Budgie/Hyprland: `zwlr_virtual_pointer_v1` (`axis`, `axis_discrete`, `frame`). Proven for motion/button on headless labwc and Magpie by this repo's tests. Hyprland: protocol support and the `ecosystem:enforce_permissions` policy for a virtual pointer are unverified (`docs/desktops/hyprland.md` covers only `screencopy` permission rules).

---------------------------------------------------------------------------------------------------

## 5. Desktop adapter structure

### 5.1 Runtime choice (environment guards, then native verification)

- `src/platform/NativeSession.h`: `nativeX11SessionEnvironment` (`:14`), `cinnamonCoreSessionEnvironment` (`:22`), `gnomeCoreSessionEnvironment` (`:37`), `kdeCoreSessionEnvironment` (`:65`), `budgieCoreSessionEnvironment` (`:93`), `hyprlandCoreSessionEnvironment` (`:140`); each checks `XDG_SESSION_TYPE`, `WAYLAND_DISPLAY`/`DISPLAY`, `QT_QPA_PLATFORM` (first plugin must be `xcb`/`wayland`), and `XDG_CURRENT_DESKTOP` tokens (Budgie wins over GNOME; Hyprland also needs a live `HYPRLAND_INSTANCE_SIGNATURE` socket, `hyprlandSocketPath/hyprlandSocketAnswers`). The comment at `:12-13` says they are routing guards, not proof of a working display.
- `src/main.cpp:183-204` computes `coreResident/gnomeCoreResident/kdeCoreResident/budgieCoreResident/hyprlandCoreResident`; `:244-282` instantiates exactly one `std::unique_ptr<SourceAdapter>`: `X11CoreSourceAdapter` or `X11SourceAdapter` (X11), `GnomeAdapter`, `KdeSourceAdapter`, `BudgieSourceAdapter`, `HyprlandSourceAdapter`, else `DataControlSourceAdapter` (Wayland, clipboard only, `:279-280`) else `UnavailableSource` (`:282`, `OperationService.cpp:90`). Compile-time switches `PUTGD_NATIVE_X11/GNOME/KDE/BUDGIE/HYPRLAND`.
- Each adapter also wires `bindSource` (shortcut binding) and `operations.recording().setShell/setWindows` (`src/main.cpp:303-316`).

### 5.2 Interfaces an adapter implements

- `SourceAdapter` (`src/core/SourceAdapter.h`): `clipboardRevision`, `capabilities()`, `prepareAcquisition(action[,limits,terminal,released])`, `acquire`, `cancelAcquisition`, `copy`, `desktopSetup/recheckDesktopSetup`, `setUiProcess`, `invalidateCopyEligibility`; protected `captureAppearance_`, `captureOutcome_`, `regionScreenshotFirst_`.
- `RecordingShell` (`src/app/RecordingBackend.h:55-72`): `selectsRegions`, `regionError`, `selectRegion`, `cancelSelection`, `showFrame`, `hideFrame`. Implemented by `GnomeAdapter` only.
- `RecordingWindows` (`src/core/RecordingWindows.h`): `listWindows`. KDE, GNOME, Budgie, Hyprland.
- `ShortcutBackend` (`src/platform/wayland/ShortcutBackend.h`): `name/available/bind/status/setPaused/clear`, signals `changed/activated`. Implementations: `LabwcBridgeBackend`, `PortalGlobalShortcuts`, `HyprlandShortcuts`. X11 (`X11Shortcuts`) and KDE (`KdeShortcuts`) are standalone classes.
- Per-adapter helper classes: `X11Capture`, `X11NativeSnapshot`, `CaptureProcessController`, `KWinCapture`, `KWinWindows`, `WaylandRegionProcess`, `ImageCopyCapture`, `WaylandOutputs`, `DataControlClipboard`.

### 5.3 "Unavailable on this desktop"

- Capabilities JSON: `OperationService::capabilities()` (`OperationService.cpp:1118-1130`) = `{source: adapter.capabilities(), providers, editor{available, admissionPixels, ...}, recording: recording_->capabilities()}`. Per adapter: `{"adapter":"hyprland-wayland", "capture":{"region":{available,error?}, "window":..., "desktop":...}, "clipboard":..., "shortcuts":{available,bindings,...}}` (e.g. `X11CoreSourceAdapter.cpp:19-22`, `HyprlandSourceAdapter.cpp:169`, `BudgieSourceAdapter.cpp:53`, `GnomeAdapter.cpp:182-188` adds `helper{available,uuid,protocol,extensionVersion,packagedExtensionVersion,outdated,setup}`).
- UI reads them: `unavailableSource` in `src/ui/MainWindow.cpp:111-120` (checks `capabilities.source.capture.<kind>.available`, otherwise falls back to `source.<kind>`; only kinds `region|window|desktop`, `edit` maps to region) and sets the button badge/tooltip (`:180-186`); Settings "Desktop support details" shows the same.
- Failure codes are free string literals in `Error{code,message,details}` (`src/core/Error.h`), no central enum. Examples: `region_unavailable` (layer shell missing, `BudgieSourceAdapter.cpp:112`), `window_unavailable` (no toplevel capture source), `source_unsupported` (`UnavailableSource`, `KdeSourceAdapter capture()`), `helper_outdated`/`helper_incompatible` (GNOME, `GnomeAdapter.cpp:126,148,271,288,298`), `capture_permission` (KWin `NoAuthorized`, Hyprland transparent frame), `shortcut_unavailable/shortcut_conflict`, `recording_unavailable` with `details.reason` (`wlr_capture_unavailable`, `live_source_missing`, `portal_unavailable`...). The user-facing table: `docs/user/errors.md:7-34`.
- Recording shows the pattern for a feature that needs a helper: `RecordingBackend::capabilities()` -> `{available, reason?, targets, formats, ...}` and `UnavailableRecordingBackend` (`RecordingBackend.h:75-88`).

### 5.4 Files a new per-desktop capability (e.g. `ScrollInjector`) would parallel

- Interface in `src/core/` (like `SourceAdapter.h`, `RecordingWindows.h`): required by the layer rules (Q16.1).
- Implementations next to the adapter: `src/platform/x11/`, `src/platform/kde/`, `src/platform/gnome/` (+ extension), `src/platform/wayland/` (shared wlroots), constructed/owned by the adapter class (e.g. `KdeSourceAdapter` owns `KWinCapture capture_` and `KWinWindows windows_`), and attached in `src/main.cpp` next to `operations.recording().setWindows(...)` (`:303-316`).
- Capability reporting key in `capabilities()` of each adapter, a UI badge hook in `MainWindow.cpp:111`, docs table row in each `docs/desktops/*.md`.

---------------------------------------------------------------------------------------------------

## 6. Agent control surface (trace of recording start/stop through every layer)

### 6.1 Layers for `recording.start` / `recording.stop`

1. **Client**: `putgd-cli recording.start '{"id":"..."}'` (generic forwarder, `src/cli/main.cpp:26-55`; deadline from `LocalServer::replyDeadlineMs` shared via `app/` include, tolerated in `check_layers.py:56-59`).
2. **Transport/validation**: `src/app/LocalServer.cpp:168-171`: `QStringList{"recording.start","recording.pause","recording.resume","recording.stop","recording.cancel","recording.inspect","recording.raise"}` require exactly `{id}` (`fields(p,{"id"})`), then `operations_.recordingCommand(method.mid(10),p,reply)`. Reply deadlines `:63-72` (`recording.stop` and `action.invoke` = `helperStopMs+15000`; list at `:67`).
3. **Facade**: `OperationService::recordingCommand` (`OperationService.cpp:524-529`) -> `recording_->command(command,params,reply)`.
4. **Service**: `RecordingService::command` (`src/app/RecordingService.cpp:333`), `prepareSession` (`:354`), `commandSession` (`:527`), `handleEvent` (`:247`), `invoke` (tray/shortcut, `:166`). Owns the state machine, durable operation (`acceptRecording`, `OperationService.cpp:507`), exclusion with the editor, staging under `<data>/recording/<id>/`.
5. **Backend seam**: `src/app/RecordingBackend.h` (`prepare/control/preview/exportClip/setEdit/discard`), production `RecordingHelperBackend` (`src/app/RecordingHelperBackend.cpp:121-311`) spawning `putgd-record` over UiControl pipes (bootstrap -> ready; `command{requestId,command,params}` -> `commandResult`; `event{progress|stopped|failed}`; deadlines `helperStartupMs=10000, helperCommandMs=15000, helperStopMs=30000, helperPrepareMs/ExportMs=600000`, `RecordingBackend.h:11-13`). Detailed: `docs/design/recording/process-boundary.md`.
6. **Helper**: `src/record/main.cpp`, `RecordSession.cpp`, `RecordingPipeline.cpp`.
7. **MCP**: `tools/mcp/share_mcp/server.py`: `control_recording` (`:392-396`) -> `adapter.call('recording.' + command, {'id': id})`; sibling tools `:355-500`; arg checkers `safe_recording_target` (`:79`), `RECORDING_FORMATS` (`:57`); server instruction text `:188-200`; `perform_action` action allow-list `:229` (`{'region','window','desktop','clipboard','edit','record'}`).
8. **Config schema** for the action: `schemas/config.schema.json` `actions.record` (`:344-410`), `required` list of actions at `:18-26`.

### 6.2 Every file to touch for a new session method / command / tool

Code
- `src/app/LocalServer.cpp` (validation block + `replyDeadlineMs` if it waits on a helper).
- `src/app/OperationService.{h,cpp}` (facade method; `capabilities()` key) and a new service class (`src/app/ScrollCaptureService.*` by analogy to `RecordingService.*`).
- `tools/mcp/share_mcp/server.py` (tool, argument checker, instruction text, `perform_action` allow-list if the action is invocable).
- `src/ui/ViewState.cpp:32,60,101` (the UI view-state validator lists action keys `region,window,desktop,clipboard,edit,record` and preference scalars; unknown keys are rejected, so a new action/preference needs adding there).
- `src/core/Settings.{h,cpp}` if the action/preferences are persisted (Q7).

Parity tests that fail if a surface is forgotten
- `tests/integration/test_mcp.py:206-232` `test_official_sdk_discovery_and_cli_parity`: hard-coded `expected` tool-name set must equal the discovered tools; every tool schema must have `additionalProperties:false`; per-tool forwarding asserted at `:418-421` (`('control_recording', {...}, 'recording.start', ...)`).
- `tests/integration/test_recording_service.cpp:456` (malformed-request table), `:493-529,649-650` (stop deadlines, `replyDeadlineMs` must exceed helper deadlines) as the template for a service test; `tests/integration/test_cli.cpp` (CLI waits for slow stop).
- `tests/integration/test_config_schema.py` (schema vs defaults), `tests/unit/test_settings.cpp:439` (`invocableActionNames().last()=="record"`), `tests/integration/test_recording_service.cpp:543` (iterates `actionNames()` and skips `record`).

Docs (separate docs-only PR per `AGENTS.md`; `tools/ci/check_docs.py` enforces links/anchors and that each doc is linked from its folder README)
- `docs/automation/cli.md`, `docs/automation/mcp.md` (tool table `:46-149`), `docs/automation/agents.md` (source map `:11-50`), `docs/design/<feature>.md` (new, linked from `docs/design/README.md`).
- `docs/design/recording/agent-control-and-tests.md` is the model for a tool-to-method table.

Contracts CI: `tools/ci/contracts.py` has only suite groups (`release`, `proton`, `lab`); no automatic method/tool parity check exists beyond `test_mcp.py`. The "MCP integration suite" is run separately (`docs/automation/mcp.md:149+`).

### 6.3 Editor as the second model
`editor.inspect|apply|preview|saveCopy|fileDialog|submit|cancel|raise` all share one validator (`LocalServer.cpp:149-155`) and `OperationService::editorCommand` (`:530-542`); `editor.view` has its own field whitelist (`:157-165`). `drive_editor`, `edit_image`, `open_editor` in `server.py`.

---------------------------------------------------------------------------------------------------

## 7. Triggers and settings

### 7.1 Global shortcut registration per desktop

| Desktop | Mechanism | Files |
| --- | --- | --- |
| Cinnamon/X11 and X11 fallback | root `xcb_grab_key_checked` for each binding (`X11Shortcuts.cpp:97`) plus XInput2 raw key events (selected on root for `RAW_KEY_PRESS/RELEASE`, `:22-27`) so shortcuts work while a menu holds the keyboard (#341); `X11RawKeyMatcher.h` | `src/platform/x11/X11Shortcuts.{h,cpp}`; signals `pressed/activated/escapePressed/bindingsChanged/connectionLost` |
| GNOME | extension `Bind` (JSON of bindings), Shell key bindings, signal `Action(action,ticket)`; the **extension holds a fixed list** `const SOURCES=['region','window','desktop','clipboard']; const ACTIONS=[...SOURCES,'edit','record']` (`integrations/gnome/extension.js:27-28`, loop `:1617`). A new action requires an extension change and bump | `GnomeAdapter.cpp:163-172,339-357` (iterates `Settings::invocableActionNames()`) |
| Plasma | KGlobalAccel v2 over D-Bus: `doRegister`, `setShortcutKeys`, component `globalShortcutPressed` (`src/platform/kde/KdeShortcuts.cpp:114,134-137,150-151`) | `KdeShortcuts.*`, `KdeShortcutNormalization.*` |
| Budgie 10.10 (labwc) | `LabwcBridgeBackend`: relocatable gsettings custom keybindings `customputgd<action>` -> `rc.xml` `<keybind bridge=...>`, command `dbus-send ... org.putgd.App.Budgie.Trigger string:<action>` (resident owns `org.putgd.App.Budgie`); else `PortalGlobalShortcuts`; else unavailable | `src/platform/budgie/BudgieShortcuts.*`, `LabwcBridgeBackend.*`, `src/platform/wayland/PortalGlobalShortcuts.cpp:18` (description table includes record/edit) |
| Hyprland | `hyprland-global-shortcuts-v1` `putgd:<action>` + Lua `hl.bind(..., hl.dsp.global("putgd:<action>"))` via IPC `eval`; conflicts refused; re-applied after `configreloaded` | `src/platform/hyprland/HyprlandShortcuts.*`, `HyprlandIpc.*` |
| Shortcut recorder in Settings | `src/ui/ShortcutEditor.cpp:75-82,200` (labels per action), `ShortcutKeyboard.*`, `setShortcutRecordingHandler` in `src/main.cpp:~400-424` |

Defaults: `Ctrl+Shift+1/2/3` for region/window/desktop; clipboard, edit, record empty (`src/core/Settings.cpp:94-108`).

### 7.2 Tray menu
Resident-side: `src/ui/TrayController.cpp` builds both the native SNI/dbusmenu tray and the `QSystemTrayIcon` fallback: `:195-208` handlers, `:223-228` labels, `:410` glyph map, `:431,444` shortcut labels in the menu. Native table `src/ui/NativeTray.cpp:108-123` (IDs are stable 1-based table positions; **append only**, retired slots keep their id) and `childrenOf` ordering from `Settings::presentationOrder()` (`:129`).

### 7.3 Settings UI and `config.json`
- Settings window: `src/ui/SettingsWindow.cpp`. Capture page: `regionSelection_` combo `:991`, "Screen recording" section `:993-994` (`recordingFrameRate_`), help text map `:736-737`, save mapping `:1376-1382` ("An untouched config keeps no X; it reads as default"), shortcut rows `:965,1014,1273,1358,1800` iterate `presentationOrder()`; Advanced limits `:1038-1039` (`imagePixels`, `imageBytes`, `pendingImageBytes`).
- Main window action band `src/ui/MainWindow.cpp:137-186,245-251`; help/explanations `:157`.
- Core settings: `src/core/Settings.{h,cpp}`: `recordingFrameRate` `Settings.h:74`, validation `Settings.cpp:312-315`, optional-key allow-list `:265`, parse `:390-391`, `normalized()` `:63-90` (adds missing `edit`/`record` actions to old documents), `defaults()` `:93-120`.
- Schema: `schemas/config.schema.json` (`preferences` `:876+`, `actions` `:18+`, `regionSelectionMode` `:901`, `recordingFrameRate` `:909`, limits `:554+`); example `config/development.example.json`; docs `docs/design/configuration.md:105-160`.

### 7.4 File list for a new action "Scrolling capture" with shortcut + a few settings

New action `scroll` (name is a suggestion), patterned on `edit` (route-able) with `record` as the special-session precedent:
`src/core/Settings.cpp/.h` (`actionNames` or a separate name like `recordingActionName`, `presentationOrder`, `defaults`, `normalized`, validation, preferences `scrollCapture*`), `schemas/config.schema.json` (actions + preferences), `config/development.example.json`, `src/app/LocalServer.cpp` (`action.invoke` accepts it via `Settings::actionNames()`; add session methods), `src/app/OperationService.cpp` (special-case like `:270` or as a source), `src/ui/{MainWindow,TrayController,NativeTray,ShortcutEditor,SettingsWindow,ViewState,HistoryModel,IconArt}.cpp` (labels, glyph, tray entry, help text, `friendlyAction` `HistoryModel.cpp:67`, action-phase text `:117`), `src/core/UploadNaming.cpp:101-104` (template choice by action), `src/app/DiagnosticsBundle.cpp:212` (per-action loop), `src/platform/wayland/PortalGlobalShortcuts.cpp:18`, `integrations/gnome/extension.js:27-28` (+ version bump), `tools/mcp/share_mcp/server.py:229`, `tests/unit/test_settings.cpp`, `tests/gui/test_settings_capture.cpp`, `tests/gui/SettingsGuiFixture.h:84`, `tests/fixtures/U2Fixtures.h:69`, `tests/integration/test_config_schema.py`, `tests/gui/ui_catalog.cpp`, `docs/design/visual-language.md:150-160` (action ID table).

---------------------------------------------------------------------------------------------------

## 8. Large images and memory

### 8.1 Image worker (`putgd-ui --image-job`), `docs/design/image-worker.md`
- Tasks: `discover | decode | preview` only (`:11`, `src/ui/ImageJob.cpp`, parent `src/core/ImageJob.{h,cpp}`). `QT_QPA_PLATFORM=offscreen` always. Private `/tmp/pgi-XXXXXX` 0700 dir; input 0400 regular file, output 0600; SHA-256 checked before and after; UiControl framing with role `image-job`; eight-key bootstrap (role, nonce, generation, build, task, input, output, limits{imagePixels,imageBytes,outputBytes}); `checkpoint` then `checkpointAccepted` then exit 0; parent deadline <=10 s; stderr cap 1 MiB; preview output capped at 256 px/axis. **No encode or stitch task.** Qt's allocation policy is unchanged (`image-worker.md`, "Qt's existing image allocation policy is retained").
- Editor worker `putgd-ui --edit-image`: `docs/design/image-editor.md:190-217`; memory table `:345-358`: R = w*h*4, helper holds one base raster, export peak base R + crop render <=R + encoder buffers; target <=3R + 96 MiB; startup 20 s, finalize 120 s, editing unbounded.

### 8.2 Where large work must run (40 MiB idle target)
`docs/design/memory-strategy.md:1-40`: idle target 40 MiB RSS for the resident and surviving helpers; the resident keeps event loop, shortcuts, clipboard, operations; image editing, decode/preview, graphical capture, region surfaces, recording are in temporary helpers (table `:27-38`). Resident allocator policy (glibc): `M_MMAP_THRESHOLD=128 KiB`, `M_ARENA_MAX=1` (`src/core/AllocatorPolicy.h`); after work drains `malloc_trim(0)` after two quiet seconds, then 30 s later clean library pages released (`src/core/ImagePages.cpp`; `docs/design/architecture.md:236-255`). A 183 MiB QImage in the resident is a transient peak, not an idle cost, because it is mmap-backed and freed on release, but every existing flow that holds one there decodes helper output (`CaptureProcessController::decode`, `KdeSourceAdapter::compose`, ...).

### 8.3 Limits found (grep `setAllocationLimit|allocationLimit|32767|16384|65535|INT_MAX|imagePixels|maxEdge`)

| Limit | Value | Where | Effect for 1600 x 30000 (48 MP, 192,000,000 B = 183 MiB RGBA) |
| --- | --- | --- | --- |
| `limits.imagePixels` | 100,000,000 default, <=1e9 | `Settings.h:38`, `Settings.cpp:243`, checks `ClipboardPayload.cpp:15`, `ArtifactStore.cpp:223`, `capture/main.cpp:165,198`, every adapter | passes |
| `limits.imageBytes` | 512 MiB default | `Settings.h:39` | passes (192 MB) |
| `limits.pendingImageBytes` | **64 MiB default** | `Settings.h:36`, `OperationService.cpp:434-441` | **fails `image_memory_limit`** for `kind=="image"` payloads unless raised; a `kind=="png"` (or file) payload is not charged |
| `limits.maxFileBytes` / batch / pending artifacts | `auto` | `Settings.h:33-35` | PNG size only |
| `EditorJob::admissionPixels` | **24,000,000** | `src/core/EditorJob.h:49`, `:99`, helper side `EditorJob.cpp:198`, `ImageEditor.cpp:279`; capabilities expose it `OperationService.cpp:1123` | **edit refused** (`edit_input_too_large`, `EditorJob.cpp:57`). Max at 1600 wide = 15,000 px tall |
| `runFile` input | `min(maxFileBytes,256 MiB)` | `OperationService.cpp:469` | n/a |
| Qt `QImageReader` default allocation limit | 256 MB in Qt 6 **(unverified in repo)**; helper sets explicit limits: `reader.setAllocationLimit(pixels*4/MiB+2)` (`ImageEditor.cpp:281`); the capture decoder allocates the `QImage` itself to avoid the guard (`CaptureProcessController.cpp:~235`); tests set `QT_IMAGEIO_MAXALLOC=1` (`cmake/TestsPlatform.cmake:34`) | thumbnail path `ArtifactStore.cpp:94-98` uses `setScaledSize`; whether Qt's PNG handler decodes the whole raster first is unverified; width 1600 keeps it under 256 MB up to ~41,900 px tall |
| X11 selector geometry | coordinates within +-32768, size <=32768 | `NativeRegionOverlay.cpp:67`; `X11Capture.cpp:65` (frame extents >32767 rejected) | selection only, not output |
| ext-image-copy session buffer | clamps to 16384 per axis | `ImageCopySource.cpp:159` (recording) | output sizes only |
| Cinnamon PNG decode | `raw+raw/1000+h+65536` bound | `CinnamonRegionCapture.cpp:143-144` | per-frame |
| capture helper PNG budget | same formula via `BoundedFile` | `capture/main.cpp:167-168` | applies if a scroll helper reuses it |
| History preview | 256x256 keep ratio | `ArtifactStore.cpp:99` | a 14 x 256 px thumbnail |
| Clipboard result | encoded PNG bytes kept by the native adapter until release | `docs/design/memory-strategy.md:62-66` | tens of MB for a tall PNG |
| `ResourceLimits` frame budgets in compose | `min(imagePixels, imageBytes/4)` | `X11SourceAdapter.cpp:182-183`, `KdeSourceAdapter.cpp:220`, `GnomeProtocol.cpp:65` | the compose step is per capture, not per scroll |

### 8.4 How PNGs are written
- Always Qt: `QImage::save(&file/buffer,"PNG")` in `capture/main.cpp:168`, `ArtifactStore.cpp:224` (resident, whole image into a `QByteArray` first), `OperationService.cpp:1111`; `QImageWriter(&dev,"png")` with `setQuality(80)` (zlib fast level) for editor staging `EditorJob.cpp:105`; plain `QImageWriter` for editor output `EditDocument.cpp:223`, `ImageEditor.cpp:207`, `ui/ImageJob.cpp:125`. No `setCompression`, no libpng link (`cmake` has no PNG dependency). On Qt 6.4.2 and 6.8.2 the writer loads every installed image plugin (`image-worker.md`, "Resident PNG readers"; a libpng encoder was built and rejected, evidence record 2026-10-17).
- `inspectSanitizedPng` (`src/core/SanitizedPng.h`) accepts only IHDR, PLTE, tRNS, gAMA, cHRM, sRGB, pHYs, IDAT, IEND; it is the editor-export check, not a capture check.

### 8.5 What would break with 1600 x 30000
1. "Capture region & edit" with the scroll image: refused at 24 MP (needs cap <=15,000 px at that width, or raising `admissionPixels` plus re-measuring the editor's 3R budget = 550 MiB for 183 MiB R).
2. Plain path as `QImage` payload: `image_memory_limit` at the 64 MiB default (`OperationService.cpp:434-441`); also `ArtifactStore::commit` re-encodes the whole PNG into a QByteArray in the resident (`ArtifactStore.cpp:224`), so resident peak ~ 183 MiB raster + PNG bytes. Prefer delivering finalized PNG bytes/file (kind `png`/file) from the helper.
3. Resident decode of a helper PNG (the X11 pattern) would allocate 183 MiB in the resident.
4. Local-only clipboard copy of the image: bytes retained by the adapter.
5. Tall-image previews/History gallery: 256 px thumbnail is tiny but generated; History list view is fine.
6. Cap enforcement: a height cap belongs in the helper (stop at `min(imagePixels/width, editor cap if edit)`).

---------------------------------------------------------------------------------------------------

## 9. GNOME Shell extension

- Sources: `integrations/gnome/extension.js` (1642 lines) and `integrations/gnome/metadata.json`. Declares `"shell-version": ["50"]`, `"uuid":"putgd@put.gd"`, **`"version": 19`**.
- D-Bus: object `/org/gnome/Shell/Extensions/Putgd`, interface `org.putgd.Gnome50`, exported on Shell's own session-bus connection (`extension.js:17-18,29-50`). Client name `org.putgd.App.Gnome50` (the resident owns it; the extension accepts calls only from its current unique owner).
  Methods (`:30-46`): `Hello`, `SetUiProcess(u)`, `InvalidateCopy`, `Revision`, `Prepare(ss)`, `Preview(ss)`, `Acquire(ss)`, `Read(s,t,u)`, `Release(s)`, `BeginCopy`, `WriteCopy`, `CommitCopy`, `Bind(s)`, `SelectArea(s)`, `ShowRecordingFrame(s)`, `HideRecordingFrame`, `RecordingWindows`. Signals (`:47-49`): `Action(s,s)`, `ClipboardChanged(t)`, `CapabilitiesChanged`.
  `Hello` returns (`:956-959`): `{version:1, shellMajor, extensionVersion: this.metadata.version, clipboardRevision, uiProcessVersion:1, recordingVersion:2, previewVersion:1}`.
  Implementations follow the naming `<Method>Async([args], invocation)` using `this._run(invocation, ...)` (e.g. `HelloAsync :953`, `SelectAreaAsync :1419`, `ShowRecordingFrameAsync :1550`, `HideRecordingFrameAsync :1590`). Static lists: `SOURCES/ACTIONS :27-28`.
- Resident side: `src/platform/gnome/GnomeProtocol.{h,cpp}` (`protocolVersion=1`, `chunkBytes=65536`, `extensionVersion=PUTGD_GNOME_EXTENSION_VERSION` baked in at configure time from `metadata.json`: `cmake/Platform.cmake:29-33`; reconfigure dependency on the file), `GnomeAdapter.cpp` (discovery, `Hello` validation `:126`, `outdated()` `:268` = loaded `extensionVersion` < packaged), `GnomeExtensionSetup.*` (per-user install, `gsettings enabled-extensions`, states in `docs/user/errors.md:36-56`).
- Detecting an old or unloaded extension: `Hello` fails or the bus owner is absent -> `helper_incompatible`/`helperUnavailable` and a 3 s doubling retry to 15 min (`GnomeAdapter.h:43-46`, `docs/desktops/gnome.md` "Bridge contract"); older loaded extension -> `outdated()` -> `helper_outdated` for region and recording features that need new protocol, while window/desktop screenshots keep working (`GnomeAdapter.cpp:196,266-298`); capability flags per feature are in `Hello` (`recordingVersion`, `previewVersion`, `uiProcessVersion`); `capabilities().source.helper{outdated,extensionVersion,packagedExtensionVersion,setup}`.
- To add a method (checklist from the repo's own rule "Bump `metadata.json`'s `version` whenever the extension's D-Bus interface changes", `docs/desktops/gnome.md`):
  1. XML `<method>` in `extension.js:29-50`; `<Name>Async` handler; add a feature version to `HelloAsync` (e.g. `scrollVersion:1`) rather than relying only on `extensionVersion`.
  2. `integrations/gnome/metadata.json` `version` 19 -> 20 (compiled into the resident, `cmake/Platform.cmake:30-32`).
  3. Resident: `GnomeAdapter` method + gate on `helper_["<feature>Version"]` and `outdated()` with a `helper_outdated`/`helper_incompatible` message; `GnomeProtocol` validation of returned JSON; capabilities field.
  4. Tests: `tests/desktop/test_gnome_ownership.mjs` (gjs `-m`, ctest `gnome_ui_ownership_contract`, `cmake/TestsGnome.cmake:36`), `test_gnome_region.mjs` (`:34`), `tests/integration/test_gnome_bridge.cpp` (adapter transport on a private bus; `QT_QPA_PLATFORM=wayland dbus-run-session -- build/dev/test_gnome_bridge --adapter-transport`).
  5. Packaging picks files up by path: `packaging/linux/CMakeLists.txt:20` installs `integrations/gnome/${gnome_asset}`; source archive prefix `tools/releases/source_archive.py:26`; release bundle `tools/releases/release_bundle.py:158-159`; AppImage carries the matching extension and installs it per user with a `.putgd-managed` hash marker (`docs/desktops/gnome.md` "Setup").
  6. Docs: `docs/desktops/gnome.md` (bridge contract paragraph and version history such as "Extension v18", "Recording protocol 2 (extension version 19)"), `docs/user/errors.md` only if a new state.
- User impact: every extension change requires a **log out and back in**; the old code stays loaded until then and the resident reports `login_required`/`helper_outdated`.
- The extension currently has **no pointer or key injection**, no region-only capture method, and its bar-moving rule matches only the recording bar title and parentage (`extension.js:1550+`).

---------------------------------------------------------------------------------------------------

## 10. KDE specifics

- Two different desktop-entry keys are in use:
  - `X-KDE-DBUS-Restricted-Interfaces=org.kde.KWin.ScreenShot2` in `packaging/linux/app.desktop.in:10` (`Exec=@CMAKE_INSTALL_FULL_BINDIR@/putgd`), matched against the **resident executable** by `installedEntryMatches()` (`src/platform/kde/KWinCapture.cpp:20-41`: scans `applications/putgd.desktop` plus `putgd-appimage-*.desktop` in every XDG data dir, parses `Exec` and `X-KDE-DBUS-Restricted-Interfaces`, compares canonical path to `QCoreApplication::applicationFilePath()`).
  - `X-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1` in `packaging/linux/record.desktop.in:11` (`Exec=.../putgd-record`, `NoDisplay=true`, `StartupWMClass=putgd-record`). Installed list: those two entries only; no other restricted interface is requested anywhere (grep over repo for both keys found only these, the AppRun, tests and docs).
- AppImage: `packaging/appimage/AppRun:190-210` on Plasma writes two private, temporary entries per mount: `putgd-appimage-XXXXXXXX.desktop` (`Exec` = mounted `putgd`, ScreenShot2 key, `X-PutGD-AppImage-Owner`) and `putgd-record-appimage-XXXXXXXX.desktop` (mounted `putgd-record`, `X-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1`), refreshes sycoca with `kbuildsycoca6` (`host_cache`, refuses without it), and removes them on exit. Tests: `tests/unit/test_portable_appimage.py:83,101`, `tools/lab/surface_driver/appimage.py:83-93`, `tests/integration/test_kde_ownership.cpp:227`.
- Consequence for input injection: `org_kde_kwin_fake_input` would need `X-KDE-Wayland-Interfaces=org_kde_kwin_fake_input` on the entry of whichever binary binds it: add it to `app.desktop.in` and AppRun's resident entry if the resident binds it, or a new `*.desktop.in` + AppRun entry for a new helper (as for `putgd-record`), plus the package install lists and test assertions above. KWin must be restarted/sycoca refreshed; put.gd tells users to restart the resident after installing an entry (`docs/desktops/kde.md:58-61`). Do not set `KWIN_SCREENSHOT_NO_PERMISSION_CHECKS` (`docs/desktops/kde.md:60`).
- KWin scripts **are** used, for window lists only: `src/platform/kde/KWinWindows.{h,cpp}`: writes a one-shot script file under `$XDG_RUNTIME_DIR/putgd`, `org.kde.kwin.Scripting.loadScript` (`:99`), `run` (`:105`), `unloadScript` (`:35,130`); script calls `workspace.windowList()` (`:44`) and calls back the resident's unique bus name; only calls from the owner of `org.kde.KWin` are believed. Needs no desktop-entry permission (`docs/desktops/kde.md:45-55`). KWin scripts cannot inject input as far as this repo shows.
- Region selector on KDE needs LayerShellQt (Qt >=6.5): `cmake/Platform.cmake:132-146`; the Qt 6.4 compat build reports `region_unavailable`.

---------------------------------------------------------------------------------------------------

## 11. wlroots specifics

- `ImageCopyCapture` uses **its own** `wl_display` connection, not Qt's: `wl_display_connect(nullptr)` at `src/platform/wayland/ImageCopyCapture.cpp:77`, registry listener `:126-148` binds globals by interface name, event pump through `QSocketNotifier`s on `wl_display_get_fd` (`:80-81`). Same pattern in `WaylandOutputs`, `DataControlClipboard`, `PressCatcher`, `ImageCopySource`, `KdeScreencast` ("an independent Wayland connection", `KdeScreencast.h`). This keeps the resident `QCoreApplication` (no Qt Wayland platform).
- Protocol XML to code (exact pattern), `cmake/Platform.cmake`:
  - `find_program(PUTGD_WAYLAND_SCANNER wayland-scanner REQUIRED)` (`:40`), `protocol_dir = ${CMAKE_CURRENT_BINARY_DIR}/wayland-protocols` (`:42`).
  - Vendored XML in `src/platform/wayland/protocols/` (current: ext-data-control-v1, ext-foreign-toplevel-list-v1, ext-image-capture-source-v1, ext-image-copy-capture-v1, hyprland-global-shortcuts-v1, hyprland-toplevel-mapping-v1, wlr-data-control-unstable-v1, wlr-foreign-toplevel-management-unstable-v1, wlr-layer-shell-unstable-v1; KDE's in `src/platform/kde/protocols/zkde-screencast-unstable-v1.xml`). System XML via `PUTGD_WAYLAND_PROTOCOLS_DIR` for xdg-output and xdg-shell (`:57-67,123-126`).
  - For each protocol two custom commands: `wayland-scanner client-header X.xml X-client-protocol.h` and `wayland-scanner private-code X.xml X-protocol.c` (`:71-80` loop over `ext-image-copy-capture-v1 ext-image-capture-source-v1 ext-foreign-toplevel-list-v1 wlr-foreign-toplevel-management-unstable-v1`; `:111-121` loop for the Hyprland set), appended to `putgd_capture_protocol_sources` / `putgd_hyprland_protocol_sources`, listed as sources of the library (`putgd_wayland` `:86-93`, `putgd_hyprland` `:127-129`), with `target_include_directories(... "${protocol_dir}")` (`:94,99,130`).
  - **To add `wlr-virtual-pointer-unstable-v1`**: put the XML (BSD/MIT notice) in `src/platform/wayland/protocols/`, add its name to the `foreach` at `:71`, include `<wlr-virtual-pointer-unstable-v1-client-protocol.h>` from a new class in `src/platform/wayland/`. `putgd-record` also receives `${putgd_capture_protocol_sources}` (`cmake/Recording.cmake:14`). Install the XML as a notice: add a `putgd_install_snapshot(...)` line in `packaging/linux/CMakeLists.txt:104-123` (every vendored protocol has one), and update `THIRD_PARTY_NOTICES.md`.
  - The virtual-pointer manager needs a `wl_seat` bound too (see how `tools/lab/wayland_pointer.py:25-40` binds `wl_seat` v1 and the manager v1).
- Hyprland adapter uses IPC (`src/platform/hyprland/HyprlandIpc.{h,cpp}`, sockets `$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket.sock` and `.socket2.sock`) for: `j/activewindow`, `j/clients`, `j/binds`, `binds`, `eval <lua>` and `reload`, plus the `configreloaded>>` event; never `hyprctl` (so an AppImage's `LD_LIBRARY_PATH` never reaches a child). Replies capped at 8 MiB, 3 s deadline with connect retries (`HyprlandIpc.h`). Comment mentions `dispatch` replies as "ok" too (`:44`), but no `dispatch` is issued by the product today.
- What the adapter guarantees forbid (`docs/desktops/hyprland.md`, Protocols and Shortcuts): no `wlr-screencopy`, `hyprland-toplevel-export`, `grim`, `slurp`, Screenshot portal, GlobalShortcuts portal or ScreenCast portal; no `hyprctl`; capture only through ext-image-copy-capture; put.gd never writes `hyprland.lua`/`bindings.lua`/any file, never calls a bind handle's `:remove()` (crashed 0.56.2); `reload` only for a shared-key conflict (it drops other programs' runtime binds); own windows refused by PID and app ID; legacy `hyprland.conf` parser: shortcuts unavailable; no fallback to region selection for window capture. `ecosystem:enforce_permissions` is handled for screencopy only (transparent-frame detection, `capture_permission`). A virtual pointer is not mentioned either way; its permission behaviour is unverified.
- Budgie: no screencopy fallback (`docs/desktops/budgie.md` Protocols table); window capture needs `ext-foreign-toplevel-image-capture-source-manager-v1` (labwc 0.20+); labwc 0.9 on Fedora 44 / Ubuntu 26.04 lacks it. Bare labwc is not routed (`labwc:wlroots` keeps the unavailable source).

---------------------------------------------------------------------------------------------------

## 12. Build and packaging

Linked today (`cmake/Platform.cmake`, `cmake/Recording.cmake`, `cmake/Executables.cmake`):
- xcb: `xcb xcb-randr xcb-keysyms xcb-xfixes xcb-render` (`Platform.cmake:4`), `xcb-xinput` (XInput2 raw keys, `:6`), `xcb-damage` (`:9`, X11CompositorSettle), plus `libxcursor`; **no xtest, no Xtst, no libei, no libpng, no libpipewire in product targets** (xtest only in test targets: `TestsPlatform.cmake:28`, `TestsNativeSession.cmake:7`, `TestsRegionCapture.cmake:24`, `TestSupport.cmake:4`).
- wayland-client + xkbcommon (`:34-35`), LayerShellQt (Qt >=6.5, `:132-146`, compile definition `PUTGD_HAVE_LAYER_SHELL`), Qt DBus, Threads.
- Recording helper only: GStreamer >=1.24 (base/video/app), FFmpeg libs (`Recording.cmake:5-9`); PipeWire reached through GStreamer's `pipewiresrc`, never linked.
- Executables: `putgd`, `putgd-cli`, `putgd-region` (layer-shell, `Executables.cmake:60-66`), `putgd-clipboard-keeper`, `putgd-capture` (`:80-82`), `putgd-ui`, `putgd-record` (`Recording.cmake:9-39`), workers.

Dependencies per package:
- DEB: `CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON` (auto from linked sonames) + fixed `CPACK_DEBIAN_PACKAGE_DEPENDS` (`packaging/linux/CMakeLists.txt:252-257`; recording adds GStreamer packages `:308-309`).
- RPM: `CPACK_RPM_PACKAGE_REQUIRES` (`:271`, GStreamer `:314`), RPM autoreq for sonames.
- Arch: `packaging/arch/PKGBUILD:9-21` and `packaging/aur/PKGBUILD.in:10-17` (`depends`, `optdepends`, `makedepends`).
- AppImage: bundled runtime layout and pins `packaging/appimage/{components,media,runtime-source,tools.lock}.json`, `AppRun`; the 224 MB sources cache key is busted by editing those JSON files.
- Build-time dev packages: `docs/release/build.md:6-17` (already lists `libxcb-xtest0-dev`, `libxcb-shape0-dev`, `libwayland-dev`, `wayland-protocols`), CI installers `tools/ci/install-packages.sh`, `tools/releases/install-native-deps.sh:11-27`, `tools/verify_dependencies.py`, `cmake/dependency-lock.json`.
- Adding a runtime dependency touches: the `pkg_check_modules` line, the package metadata for DEB/RPM/Arch(+AUR), `docs/release/build.md`, CI/native install scripts, AppImage components if it must be bundled, `THIRD_PARTY_NOTICES.md`/SBOM (`packaging/sbom`), and `tools/ci/check_layers.py` if a new `src/` module appears. Libraries that dlopen at runtime (like `QLibrary("Xcursor")` in `src/capture/main.cpp:76-81`) are a precedent for optional libs.
- AGENTS.md: Qt dynamic from distro, Qt >=6.4.2 API floor, no substitute toolchains, C++20.

---------------------------------------------------------------------------------------------------

## 13. Tests and acceptance

### 13.1 Existing test kinds for capture and recording
- Unit: `tests/unit/test_region_selection.cpp` (`region_selection_contract`), `test_geometry.cpp`, `test_wayland_region_control.cpp`, `test_native_session.cpp` (routing rows), `test_recording_model.cpp`, `test_bar_placement.cpp`, `test_portal_streams.cpp`, `test_wayland_acquisition.cpp`, `test_hyprland.cpp`, `test_settings.cpp`, `test_operations.cpp`, `test_payload.cpp`.
- Offscreen / widget: `tests/gui/test_wayland_region_overlay.cpp`, `test_settings_capture.cpp`, `test_tray.cpp`, review-window suites; UI catalog `tests/gui/ui_catalog.cpp` (every window/overlay state, no pixel gate; new states must be deterministic, `docs/design/ui-catalog.md:61-67`).
- Integration with fake peers: `tests/integration/test_capture_process.cpp` (the helper protocol, with `QT_IMAGEIO_MAXALLOC=1` and Xvfb: `cmake/TestsPlatform.cmake:34`; **closest to copy for a scroll helper protocol**), `test_capture_control.cpp`, `test_recording_service.cpp` (**closest for a service + LocalServer + fake backend**: `tests/fixtures/FakeRecordingBackend.h`), `test_recording_helper.cpp` (supervisor against `tests/fixtures/record_helper_fixture.cpp`), `test_recording_pipeline.cpp`, `test_gnome_bridge.cpp`, `test_kde_ownership.cpp`, `test_kwin_transfer.cpp`, `test_kwin_windows.cpp`, `test_image_job.cpp`, `test_editor_job.cpp`, `test_cli.cpp`, `test_mcp.py`.
- Nested/headless compositors and Xvfb: `tests/integration/test_budgie_labwc.cpp` + `tests/fixtures/labwc_fixture.cpp` (headless labwc, `WLR_BACKENDS=headless WLR_RENDERER=pixman`, a known-colour client, drag via `tools/lab/wayland_pointer.py`; skips when labwc is missing; `docs/desktops/budgie.md` "Tests"); X11 tests under Xvfb with XTest: `tests/desktop/x11/test_x11.cpp`, `test_native_region_overlay.cpp`, `test_capture_preparation.cpp` (`cmake/TestsRegionCapture.cmake:23-36`); gjs contracts for the extension (`cmake/TestsGnome.cmake`). Hyprland cannot run headless in CI; routing/bind logic is tested against a fake IPC (`tests/fixtures/hyprland/`).
- Lab acceptance drivers: `tools/lab/surface_driver/` (recipes under `recipes/`, fixtures, `ownership.json`), surface map `tools/lab/surface_map/model.json` (has `bar.record` etc. with `source: src/record/Overlays.cpp`), `tools/lab/record_run.py` (moving pattern + motion score for recordings), `tools/lab/fluidity_run.py`, `tools/lab/multi_output*.py`, `tools/lab/nightly_desktops.py`, per-desktop scenario YAML `tests/desktop/{common,cinnamon,gnome,kde,budgie}.yaml` (the nightly check is a five-row, 60-cell table, `docs/testing/acceptance-matrix.md`).
- **No scrollable test content, no scroll/stitch tests exist** (checked: `grep -il stitch|scroll tests tools`).

### 13.2 What `docs/testing/` requires of a new interactive feature
- `docs/testing/README.md:5-12`: current-version evidence per declared desktop on the exact build; offscreen tests prove widget/core only; never substitute VM or XWayland for physical gates; synthetic payloads only.
- `docs/testing/acceptance-matrix.md`: add rows (recording rows are the model: `## Screen recording rows` `:164-190`; also "Native package full-acceptance profile" A-K `:507-571` and the Hyprland VM row `:122`); placement physical vs VM `:661`; ordering/evidence `:683`.
- `docs/testing/verification.md` (observed acceptance and blocked gates), `docs/testing/testing.md` (suite descriptions), evidence goes to put.gd-evidence via `tools/maintenance/evidence.py` (never add under `docs/evidence`; `AGENTS.md` last paragraph).
- Keep bar: `docs/testing/removed-tests.md:1-12`: only tests "whose failure would otherwise be silent and costly: data loss, credential exposure, uploads to the wrong place, irreversible release publication, **input to a live desktop**, destroyed golden images or false acceptance evidence". Input injection into a live desktop is explicitly in the keep list. Removals must be logged there.
- Nightly desktop controller admits cells per exact build; memory gate per row (`docs/design/memory-strategy.md:80-95`).
- Project practice: recording tests must verify real motion in the exported result; analogous requirement for scroll tests is a deterministic tall synthetic page whose stitched output can be compared exactly (no seam, no duplicated or missing rows).

---------------------------------------------------------------------------------------------------

## 14. Docs a new capture feature must update (and failure-code conventions)

Per `AGENTS.md`, `docs/`, `README.md`, `AGENTS.md`, `CLAUDE.md` edits go in a **separate docs-only PR** (CI runs `contracts` only); `docs/release/build.md` and `docs/user/proton-drive.md` are package inputs and select every job anyway.

| Doc | Section to add/change |
| --- | --- |
| `docs/design/overview.md` | executables table (`:25-37`), "Capture and upload pipeline" (`:46-70`), desktop adapters table (`:76-90`), agent interfaces (`:150-160`) |
| `docs/design/architecture.md` | "Process boundaries" table (`:19-30`) and helper paragraphs (`:48-80`); acquisition rules |
| `docs/design/memory-strategy.md` | temporary helper table (`:27-38`), "Bound live data" |
| `docs/design/<new>.md` (e.g. `scroll-capture.md`) + link from `docs/design/README.md` (check_docs rule 2) | contract, privacy, per-desktop injection and frame sources, limits |
| `docs/design/image-editor.md` | the 24 MP admission line `:180-181` if the cap changes; sources table `:176-181` |
| `docs/design/image-worker.md` | if a `stitch` task is added to the worker (task list, bootstrap keys, limits) |
| `docs/design/configuration.md` | settings table `:105-160` (new `actions.<name>`, preferences/limits) |
| `docs/design/visual-language.md` | "Words and actions" table `:150-160`, overlay/control rules |
| `docs/design/appearance.md` | "Recording overlays" `:92-107` (selection ring/dimming are fixed, not themed) |
| `docs/design/ui-catalog.md` | only if a catalog state is added |
| `docs/design/recording.md` and `recording/*.md` | only to cross-link (shared overlay/bar placement, `BarPlacement.cpp`) |
| `docs/desktops/{cinnamon,gnome,kde,budgie,hyprland}.md` | per-desktop frame source, injection mechanism, desktop-entry/protocol requirements, unavailable reasons; GNOME "Bridge contract" and extension version note; KDE desktop-entry paragraph; Hyprland protocols + guarantees; Budgie Protocols table |
| `docs/automation/cli.md`, `mcp.md`, `agents.md` | new method/tool rows; source-and-verification map `agents.md:11-50` |
| `docs/user/user-guide.md` | new section next to "Edit before uploading"/"Record the screen" (`:38-60`) |
| `docs/user/errors.md` | new codes (`:7-34`) and GNOME setup states if any |
| `docs/user/troubleshooting.md` | selector/injection problems (modifier keys, focus, smooth scrolling, browsers) |
| `docs/testing/acceptance-matrix.md`, `testing.md`, `verification.md`, `removed-tests.md` | new rows, suites, evidence, kept tests |
| `docs/release/build.md` | any new dev package; `docs/release/ci.md` only if CI jobs change |
| `docs/README.md` and each folder README | `check_docs.py` requires every doc to be linked from its folder README |
| `CHANGELOG.md`, `README.md` | product feature list (README is a living doc) |
| `docs/readme/` artwork (`sources.md`) | only if README screenshots change |

Failure codes: snake_case string literals in `Error{code,message,details}`; no central registry. Naming patterns seen: `<thing>_unavailable` (`region_unavailable`, `window_unavailable`, `capture_unavailable`, `recording_unavailable`, `shortcut_unavailable`), `<thing>_active` for exclusion (`editor_active`, `recording_active`, `busy_selecting`), `<thing>_incompatible/_outdated` for helpers, `input_excessive`, `image_memory_limit`, `capture_permission`, `capture_geometry`, `display_changed`, `capture_timeout`, `recording_helper_*`. Helpers add `details.stage` and `details.check` (never pixels or paths), `details.reason` for `*_unavailable` (`docs/design/recording/wayland.md` "recording_unavailable"). Documented in `docs/user/errors.md`. Also `Log.cpp:75` redaction list and `DiagnosticsBundle.cpp:212,220` known-code regex (a new action/code should be added to diagnostics classification).

---------------------------------------------------------------------------------------------------

## 15. Other constraints

- Scope: Linux only (DEB, RPM, pacman, AppImage); Flatpak and Windows out of scope; **do not add OCR features**; Qt >=6.4.2 floor; Qt dynamically linked (`AGENTS.md`).
- Explicit-action rule: "finalized files enter the shared pipeline only through the explicit Upload action" applies to recordings (`AGENTS.md`, `docs/design/recording.md:44-56`). Still-image captures go straight down the configured route (local save/upload/copy link, `action.invoke`). Project practice is not to add consent dialogs, "uploading" notices or undo buttons to explicit upload actions (no-upload-consent rule), and that put.gd always auto-copies upload links, so a scroll capture on a physical desktop writes the clipboard unless the route is local-only.
- Privacy: captured pixels never enter logs, diagnostics, journal or history rows (`Error` details are geometry/check names only: `src/capture/main.cpp:130-133`, `CinnamonRegionCapture.cpp:43-47`; "No source pixels enter diagnostics" `docs/desktops/kde.md:128`; logs redact payload keys `Log.cpp:75`). Helper staging lives in 0700 private directories (`/tmp/putgd-capture-XXXXXX`, `<data>/editing/pge-XXXXXX`, `/tmp/pgi-XXXXXX`) with 0600/0400 files, identity-checked and hash-verified; abandoned staging is discarded at start (`RecordingService::discardStaging`). Intermediate scroll frames must follow that discipline and must not persist beyond the session; they are not artifacts.
- Own windows are excluded from capture on every desktop (window-capture rules by PID/app ID); the ring/bar must not become capturable content nor trigger the "own window" refusals for other features.
- Live region overlay: selection is live by default; `screenshot_first` is an opt-in setting that applies to region screenshots only; recording selection is always live (`SourceAdapter.h:21-23`, schema `:901-907`). The selector must not appear in the saved image (outline-free pixel acceptance on every desktop, `docs/desktops/kde.md:21-23`).
- UI style: new windows reuse `putgd::Ui` (`src/ui/Ui.h`), `Theme` tokens, IBM Plex fonts, `IconArt` glyphs (`src/ui/IconArt.cpp:118-165`, names `region, window, desktop, clipboard, edit, record, record-dot, stop ...`); add a glyph there for the new action; every window/overlay state renders in `putgd-ui-catalog` (`tests/gui/ui_catalog.cpp`; `docs/design/ui-catalog.md`); helper windows take the resident's `appearance {scheme}` frames (`docs/design/appearance.md:92-107`); sizes shown as KB/MB with 1024 math; sentence case, ellipsis only when another choice is needed (`visual-language.md:148+`).
- Agent parity rule (`AGENTS.md`): "every interactive capability stays controllable through session methods, `putgd-cli` and the MCP helper". Interactive features must be driveable end to end including selection (`recording.select` completes a selector, `recording.cancel` closes it) and stop.
- Process boundary rules: resident stays `QCoreApplication` on Cinnamon/GNOME/KDE/Budgie/Hyprland and keeps heavy work in helpers; helpers verify build manifest, nonce, generation, bounds and normal exit; the resident never decodes unvalidated bytes; `OperationService` owns acceptance/journal; selection can precede the two journal saves but pixels cannot (`architecture.md:79-95`). Frozen target/layout: any layout change invalidates acquisition (`display_changed`). Interactive ownership by operation id (`selectingId_`). One interactive acquisition at a time (`busy_selecting`); recording and editor are mutually exclusive.
- Socket path limit: 107 bytes for isolated lab launches (`AGENTS.md`); no desktop work without `tools/lab/desktop_lock.py acquire` on physical builders (lab rules); heavy builds/tests stay off the workstation.
- Memory budget: 40 MiB idle RSS across resident plus surviving helpers (`memory-strategy.md:1-6`), enforced per desktop row in the nightly check.
- Shortcuts: global key binding conflicts are reported, never overwritten (`gnome.md`, `hyprland.md`, `budgie.md`).
- Overlay guarantees: ring/strips never overlap recorded pixels; selector surfaces withdrawn and destroyed before pixel read (`X11SourceAdapter.cpp:129-131` waits for `QObject::destroyed`; KDE waits for a Wayland display sync, `docs/desktops/kde.md:21-23`).

---------------------------------------------------------------------------------------------------

## 16. Recommended integration shape

### 16.1 Constraints that decide the shape

1. **Layering** (`tools/ci/check_layers.py:30-55`): `app` may include only `client, core, ipc, secrets`; `platform/<x>` only `core` (+`platform`, +`platform/wayland` for kde/budgie/hyprland, `ipc` for wayland/x11); helpers `capture`: `core, ipc, platform/x11, ui`; `record`: `core, ipc, platform, platform/wayland, platform/x11, ui`. So the shared interface must live in `src/core/` (as `SourceAdapter.h` and `RecordingWindows.h` do), a new `src/scroll/` module needs its own `ALLOWED` row, and the only tolerated backward edge to imitate is `GnomeAdapter.h -> app` (avoid).
2. **Privilege lives in the resident** on KDE (ScreenShot2 entry matches the resident exe), GNOME (bridge name pinned to the resident), and the wlroots/Hyprland adapters (resident holds the capture connection, IPC and shortcut state). X11 pixels need a Qt xcb process (`putgd-capture` on Cinnamon Core) or raw xcb in the resident.
3. **Memory**: tall rasters (up to 183 MiB at 1600 x 30000) must never sit in the resident or go through `kind=="image"` payloads (64 MiB queue limit) and "edit" caps at 24 MP.
4. **Cursor**: still-image sources already exclude it; streams embed it.
5. **No existing code** for injection, stitching, or scroll fixtures.

### 16.2 Proposal

**Who owns the scroll session: the resident**, as a new service parallel to `RecordingService`, because it needs durable intent in the operation journal, exclusion with the editor/recording/other selections, session methods for CLI/MCP, tray/shortcut toggle, and desktop adapters that only the resident can reach. Heavy raster work goes to a **transient helper**.

- `ScrollCaptureService` (`src/app/ScrollCaptureService.{h,cpp}`): states `preparing -> ready -> scrolling -> finishing -> done|cancelled|failed`; accepts via a new `OperationService::acceptScroll(Operation&)` (clone of `acceptRecording`, `OperationService.cpp:507`) with an action name `scroll`; stops on user Stop (bar, shortcut toggle, `scroll.stop`), height cap, no-movement, Esc/timeout, display change; on completion hands finalized PNG into `OperationService` as `ClipboardPayload{kind="png"}` (today's finalized-bytes path, `ArtifactStore.cpp:225`, which bypasses the `pendingImageBytes` charge) or, better for memory, a new payload kind that streams a validated private file (small change next to `kind=="files"`, `ArtifactStore.cpp:214-220`). For the editor variant reuse `editor.open` with `source:"scroll"` and respect `EditorJob::admissionPixels` (either cap the stitch at 24 MP when routed to edit or raise and re-measure that constant).
- Scroll helper `putgd-scroll` (`src/scroll/main.cpp`) is the GUI + stitcher: a QApplication transient helper spoken to with the same UiControl framing, bootstrap/ready/command/event envelope and deadlines as `putgd-record` (copy `RecordingHelperBackend` shape: `src/app/ScrollHelperBackend.{h,cpp}`) or `putgd-capture`. It owns: selection overlay (reuse `LayerShellRegionOverlay` on KDE/Budgie/Hyprland, `NativeRegionOverlay` on X11 as `putgd-capture` does, the extension's `SelectArea` on GNOME via the resident like `RecordingShell::selectRegion`), the ring (`BoundsOverlay`), a small stop bar, incremental stitching into a file-backed raster, PNG encoding with the `BoundedFile` budget from `src/capture/main.cpp:42-53,162-170`, and a descriptor `{bytes, sha256, width, height}` back to the resident. It must not link GStreamer/FFmpeg: that keeps it independent of the optional `PUTGD_RECORDING` build. This requires extracting `BoundsOverlay`, `BarPlacement` and the layer-shell `toLayer` helper out of `src/record/Overlays.cpp` into a shared module (suggested `src/ui/` or `src/platform/`), because `record` and a new `scroll` module are both leaf helpers that may not include each other.
- Who grabs frames and injects input: a per-desktop **driver** in `core/ScrollDriver.h`, implemented inside each existing adapter (resident), with the helper receiving each grabbed frame over a private fd/spool file and sending back control events. Step-wise loop (scroll N notches, wait for repaint settle, grab one still, compare overlap, append) fits every still source and keeps the cursor out of frames. One frame at a time in the resident (a region-sized `QImage`, a few MB), written straight to the helper.
  - X11/Cinnamon: driver in the resident using raw xcb: add `xcb-xtest` to `PUTGD_XCB` pkg-config list (`cmake/Platform.cmake:4`) and `x11/X11ScrollDriver`; grabs through `X11CompositorSettle` + `xcb_get_image` or Cinnamon `ScreenshotArea` with the region rect; first wait for all modifier keys released (raw key events, `X11Shortcuts.cpp:142`) and restore the pointer afterwards.
  - KDE: `KdeScrollDriver` using `KWinCapture` (add an area request or crop `CaptureScreen`) plus `org_kde_kwin_fake_input` on a new native connection; add `X-KDE-Wayland-Interfaces=org_kde_kwin_fake_input` to `packaging/linux/app.desktop.in` and AppRun's temporary resident entry (`packaging/appimage/AppRun:196-200`), and extend `tests/unit/test_portable_appimage.py`, `tools/lab/surface_driver/appimage.py`.
  - GNOME: extension v20 adds `ScrollBy(x,y,dx,dy,steps)` (Clutter virtual pointer) and `CaptureArea(x,y,w,h)` (`Shell.Screenshot.screenshot_area`, cursor excluded, returned through the existing `Read` chunking), advertised as `scrollVersion` in `Hello` (`extension.js:956-959`), `metadata.json` version 20, `GnomeAdapter` gating with `helper_outdated`. A streamed alternative is `MutterScreenCast.RecordArea` with cursor-mode 0 inside a helper.
  - Budgie 10.10 / Hyprland: new `platform/wayland/VirtualPointer.{h,cpp}` on its own `wl_display` (pattern `ImageCopyCapture.cpp:77`), protocol XML `src/platform/wayland/protocols/wlr-virtual-pointer-unstable-v1.xml` added to the `foreach` at `cmake/Platform.cmake:71`; frames from `ImageCopyCapture::captureOutput` already in these adapters; Hyprland doc guarantee table gets a row and an acceptance run to see whether a virtual pointer is permitted under `enforce_permissions` (unverified).
  - Capability reporting: each adapter's `capabilities()` gains `scroll{available,error?,injector,frameSource}`; `MainWindow::unavailableSource` and Settings diagnostics extend naturally; failure codes `scroll_unavailable` (details.reason: `injection_unavailable`, `helper_outdated`, `permission`...), `scroll_active`, `scroll_stalled`, `scroll_cap_reached`, `scroll_aborted`.
- Alternative considered: hosting the scroll mode inside `putgd-record` (it already has selection on every desktop, overlays, bar placement, KDE/Mutter/ImageCopy/X11 acquisition and the whole helper protocol). It would avoid the extraction, but ties the feature to the optional GStreamer/FFmpeg build and the recording session's clip/pause/export model, and would stream with the cursor embedded until five constants are changed and each hidden-cursor mode is accepted. Treat this as the fallback if the extraction is rejected.
- Stitching: not present anywhere. Needs a deterministic vertical-overlap matcher (row hash plus a cross-correlation fallback), fixed header/footer (sticky) region detection, end-of-content detection by identical frames, and a hard cap; unit-testable with synthetic tall images without a desktop.

### 16.3 New files (suggested paths, matching conventions)

Core / app
- `src/core/ScrollDriver.h` (interface: `probe()`, `begin(rect)`, `scrollBy(steps)`, `grab(rect, Reply)`, `end()`, `capabilities()`) and `src/core/ScrollModel.{h,cpp}` (session states, params parsing like `RecordingModel.*`).
- `src/app/ScrollCaptureService.{h,cpp}`, `src/app/ScrollBackend.h` (seam analogous to `RecordingBackend.h`), `src/app/ScrollHelperBackend.{h,cpp}`.
- Edits: `src/app/OperationService.{h,cpp}`, `src/app/LocalServer.cpp`, `src/main.cpp` (attach driver per adapter like `:303-316`), `src/core/Settings.*`.

Helper (new module, add to `tools/ci/check_layers.py ALLOWED`, `cmake/Executables.cmake`, `packaging` install lists, `docs/design/overview.md` table)
- `src/scroll/main.cpp`, `src/scroll/ScrollSession.{h,cpp}`, `src/scroll/Stitcher.{h,cpp}` (pure, testable), `src/scroll/ScrollBar.{h,cpp}`; shared extraction (e.g. `src/ui/BoundsOverlay.{h,cpp}`, `src/ui/BarPlacement.{h,cpp}`).

Platform
- `src/platform/x11/X11ScrollDriver.{h,cpp}`; `src/platform/kde/KdeScrollDriver.{h,cpp}` + `src/platform/kde/protocols/kwin-fake-input.xml` (note: it must be vendored and added to `Platform.cmake`'s KDE section); `src/platform/wayland/VirtualPointer.{h,cpp}` + `src/platform/wayland/protocols/wlr-virtual-pointer-unstable-v1.xml`; GNOME: `integrations/gnome/extension.js` + `metadata.json` v20 and `src/platform/gnome/GnomeAdapter.cpp` methods; `packaging/linux/scroll.desktop.in` only if a helper (not the resident) binds KDE fake_input.

Tools / tests
- `tests/unit/test_scroll_stitcher.cpp`, `tests/unit/test_scroll_model.cpp`, `tests/integration/test_scroll_service.cpp` (copy `test_recording_service.cpp` with a `FakeScrollBackend`), `tests/integration/test_scroll_helper.cpp` (+ `tests/fixtures/scroll_helper_fixture.cpp`, copy of `record_helper_fixture`), `tests/fixtures/scroll_page_fixture.cpp` (a Qt window with deterministic tall content, ruler rows, sticky header), X11 injection test beside `tests/desktop/x11/test_x11.cpp`, wlroots test beside `tests/integration/test_budgie_labwc.cpp` (extend `tools/lab/wayland_pointer.py` with an `axis` command), gjs test in `tests/desktop/test_gnome_ownership.mjs`, `tools/lab/host_input.py`/`rfb.py` already cover wheel for VNC; a lab recipe `tools/lab/surface_driver/recipes/scroll.py`; scenario YAML rows in `tests/desktop/*.yaml`.
- MCP: tools such as `prepare_scroll_capture`, `control_scroll_capture` (start/stop/cancel), `get_scroll_capture`, `select_scroll_region` in `tools/mcp/share_mcp/server.py`, and the expected-tool set in `tests/integration/test_mcp.py:206-232`.

Docs (separate PR)
- `docs/design/scroll-capture.md` plus the updates listed in Q14.

### 16.4 Open risks to resolve before coding

1. Hotkey modifiers still held at the first wheel event (Ctrl = zoom).
2. Smooth-scrolling apps: step size vs pixels moved is not 1:1; the stitcher must measure the actual shift, not trust the step.
3. Pointer must sit over the content while injecting, and the user's real pointer position must be restored; any human input during the session must abort it.
4. Overlay surfaces and the stop bar must not intercept the wheel nor be in frames; the full-monitor "handle" fallback of the recording bar is unusable here.
5. Wayland has no passive Esc; Stop must be the bar, the shortcut toggle or the CLI/MCP.
6. GNOME needs a re-login after the extension update; the feature must degrade to `helper_outdated` rather than failing silently.
7. Editor cap (24 MP) versus 1600 x 30000.
8. Hyprland's permission behaviour for a virtual pointer, KWin fake_input availability on each Plasma version, and Muffin's root-read staleness are unmeasured here.
