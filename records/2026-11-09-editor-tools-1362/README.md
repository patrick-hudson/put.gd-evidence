# Editor tools (#1362): step numbers, pen, ellipse, line, pixelate, Copy image

Build under test: `feat/editor-tools-2` at **5cf0067fc**, a dev build from that tree on k72 (the
builder's copy is a local git repository, so the binaries report `26.1109.1-dev+gbe7f3d27cd06.dirty`).
"Before" is nightly **32a9a763e** (CI run 42706400392, `putgd-26.1109.4404-dev+g32a9a763e350-x86_64.AppImage`).

Desktop: k72, Kubuntu 26.04, physical Plasma Wayland session (desktop lock `claude-1362-editor`),
frames from the wall VNC tile, cropped to the put.gd window (and to LibreOffice for the paste).
The resident ran with private XDG config/data/state/cache roots and uploaded to a loopback S3
fixture (`tools/lab/surface_driver/fixtures/s3_server.py`) with a synthetic, session-only key.
The source image is a synthetic page (`source1362.py` style: fake console, fake token).

Input was real: `tools/lab/host_input.py` (uinput) clicked the steps, drew the pen stroke, Shift-dragged
the line, pressed N/P/L/B, Ctrl+Shift+C in the editor and Ctrl+V in LibreOffice Draw. Redaction,
blur, pixelate and ellipse came from `editor.apply`. Overlays were drawn with put.gd's own editor
through `putgd-cli` (`editor.open` / `editor.apply` / `editor.saveCopy`).

| File | Shows |
| --- | --- |
| before.png / after.png | Toolbar on nightly vs this build at the same 1344×900 window; new tools and Copy image boxed |
| marks.png | Every new mark on one image, and the Blur tool in its Pixelate style with the shared warning |
| steps-next.png | Steps 1, 2, 3 by click, step 10 after setting the number, Next number now 11 |
| copied.png | "Image copied" on the button right after a real Ctrl+Shift+C |
| pasted.png | The copied image pasted with Ctrl+V into LibreOffice Draw |
| uploaded.png | The object uploaded by that edit, fetched back from the destination; same sha256 as the paste (54850c05…) |
| min100.png / min150.png | The window at its minimum width at 100% (603 px) and at QT_SCALE_FACTOR=1.5 (905 px): history and zoom wrap |
| scale150.png | 150% at the default size: all tools and both privacy labels on one row |
| driver-checks.png, driver-log.json | `tools/lab/editor_tools_check.py` on the same session: 26 checks, clipboard bytes = `editor.copy` reply = Save a copy |
