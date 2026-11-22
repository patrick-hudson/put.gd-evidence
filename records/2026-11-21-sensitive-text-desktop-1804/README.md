# Sensitive text check desktop acceptance for PR 1806

The desktop campaign used CI packages and a loopback HTTP receiver serving synthetic PNGs.
Each resident ran with private configuration and data directories on the real compositor.
The build tree came from the running resident's diagnostics. Screenshots came from the
active desktop displays. The comparison used the same fixture, rectangle, and receiver for
each set of five timed region captures, with one warm-up per set. Times ran from completing
the selection to the first polling response with an uploaded link. Monitor timings ran from
invoking capture through the same link observation.

## Initial candidate

The initial candidate was `56fd9638742bbbf31d498b666b6e2cb017da1a83`, tree
`d560dae80b9ee1acf4551f3b2f33d0a5a188c8a9`, from CI run 44962909895.

- Mint Cinnamon X11, 1920 × 1080. The default-off card capture uploaded the original in
  0.324 s without entering a sensitive-text phase. The five clean default-off region samples
  had a 0.363 s median at 676 × 138. The full monitor default-off capture took 0.594 s.
  The real Settings toggle saved card, key, and list, but the Look for area drew only the
  Card numbers label and clipped the other checkbox controls. Toggling off and on reproduced
  the defect at the default window size. Both frames and an annotated crop are recorded.
- Kubuntu Plasma Wayland, 1920 × 1080. The default-off card capture uploaded the original
  in 0.197 s. Clean region medians at 676 × 138 were 0.188 s off and 0.530 s on, adding
  0.342 s. A 1920 × 1080 monitor capture took 0.333 s off and 0.752 s on, adding 0.419 s.
  The hotkey opened a frameless gold-edge prompt with the default action focused. Pressing
  Return opened the editor with one suggested card redaction at `[102, 64, 489, 40]`.
  The receiver's PNG was opaque black throughout that rectangle with identical pixels
  outside it compared with the default-off object. The undecided prompt went behind the
  fixture after clicking it at `(1640, 440)`. The before and after frames show reproduction
  operation `0f091184-0b82-43a7-81a1-4b056482f128`, which remained in
  `sensitive_text_found` with one card finding. The subsequent CLI Cancel was cleanup
  and left one saved local-only item.
- Fedora GNOME Wayland also ran the initial timing fixture. Its old-build operation
  records are included for traceability. The requested full GNOME row follows the final
  candidate because the window activation behavior changed.

The intended stacking behavior was updated after the initial test. The remaining gate is
that the prompt appears raised and focused and can be brought back by the tray icon or
the notification's Show action after another window covers it.

## Candidate 74327614e

Run 44965483052 passed for `74327614eb995653fa215d4dda2f8b1431b0cfe0`, tree
`97823471989f3636ae93867f42f7ccb6161f3f72`. Its packages report
`26.1122.6198-dev+g74327614eb99`.

### Fedora GNOME Wayland

All seven Look for labels were visible and unclipped. The option saved enabled with
Card numbers, Keys and tokens, and My redaction list. A first fixture rectangle
clipped the bottom of the synthetic glyphs. The receiver's retained PNG identified
the problem. The rerun used a larger region for both timing sets and the functional
checks, with the exact candidate running in both attempts.

The clean region at 676 × 178 took 0.188 s off and 0.420 s on at the median, adding
0.232 s. The 1920 × 1080 monitor capture took 0.291 s off and 0.749 s on, adding
0.458 s. The default-off card capture had no sensitive-text phase.

The card prompt was frameless and drew a gold edge. Return went directly to the
editor with one suggested Redact mark selected as the tool. The receiver's stored
PNG was opaque black throughout the suggested rectangle and matched the original
outside it. Upload anyway matched the default-off capture pixel for pixel.
Escape saved one local-only History item with Keep a local copy enabled. Clicking
Cancel with the option disabled produced no object or History item. The AWS example
key produced one key finding and Escape cancelled it.

Clicking the fixture covered the panel. GNOME had no put.gd tray icon, so a click on
the notification's Show action brought the panel back and the same operation uploaded
after Upload anyway. The notification center retained an older notice from a resolved
prompt until it was dismissed. Those notices and the candidate package were removed
after the run.

In report mode, a card capture waited with no prompt or new notification. The agent
decision to upload settled it. A second report-mode capture cancelled without a
decision 300.482 s after the selection, with zero new receiver objects and no History
item. Diagnostics answered with zero active operations immediately afterwards.

### Mint Cinnamon X11

The final candidate displayed all seven labels and the expected three defaults.
The five clean region captures at 676 × 138 had medians of 0.377 s off and 0.760 s
on, adding 0.383 s. A 1920 × 1080 monitor capture took 0.567 s off and 1.064 s on,
adding 0.497 s. The default-off hotkey card capture uploaded with no check phase.

The frameless prompt opened with the default action focused. Return opened the
editor with a suggested card mark. Its received PNG was black throughout the mark's
489 × 40 rectangle and otherwise unchanged. Clicking the fixture covered the next
card prompt, and clicking the put.gd tray icon brought it back. Upload anyway
matched the default-off card PNG pixel for pixel. Escape saved a local-only History
item when configured to keep one. Clicking Cancel with local copies disabled
produced zero uploads and zero History items. The AWS sample key prompted, and
Escape cancelled it. An agent waited without a panel, accepted a Cancel decision,
and a separate unattended operation cancelled 300.563 s after selection. Diagnostics
responded with zero active operations.

The file selection `a.png`, `b.png`, and `c.png` produced the expected File 2 of 3
prompt for `b.png` and File 3 of 3 prompt for `c.png`, each offering only Upload
anyway and Cancel. Choosing Upload anyway for `b.png` and Cancel for `c.png` left
the receiver unchanged. The selections were handled in the same operation, with
prompt counters 1 and 2.

### Kubuntu Plasma Wayland

The default-off and clean timed captures and pixel-verified Redact upload from the
initial candidate remain applicable. The final candidate passed the seven-label
Settings check, and the tray icon brought the covered card prompt back. Its
Upload anyway PNG matched the original capture byte for byte. The final prompt
opened focused, and Escape saved one local-only item with Keep a local copy on.
Clicking Cancel with local copies disabled produced no upload or History item.
The sample key prompted and Escape cancelled it.

The native agent decision path waited without a visible panel and accepted
Cancel. A second report-mode operation cancelled after 300.359 s from selection,
with zero receiver objects and no History item. Diagnostics answered immediately
afterwards. A foreground window initially prevented the driver from seeing its
fixture on startup. The retry kept the synthetic-pixel check for every capture
and allowed opening Settings before the fixture took the foreground.

### Omarchy Hyprland Wayland

The AppImage resident reported the final tree and the native Hyprland adapter.
This overlay ran at 1280 × 800 and stayed visible on the display wall. The first
overlay used the generic Debian host bootstrap identity. Its SSH authentication
failed, and the documented Omarchy identity authenticated on the same endpoint.
The first overlay was retired with its failure record and a second overlay booted
with the corrected command.

The fixture originally gave the resident its own runtime directory. That hid
Hyprland's native IPC endpoints and resulted in the clipboard-only adapter.
The rerun used the guest's actual runtime directory and kept its configuration,
data, state and cache private. The validated compositor socket paths were 94 and
95 bytes. The put.gd session socket was 33 bytes. The lease heartbeat was
recorded at about 11 minutes, before the lease's stale threshold.

All seven Look for labels fit, and the expected three defaults remained selected.
The clean region medians at 676 × 178 were 0.497 s off and 0.788 s on, adding
0.291 s. The 1280 × 800 monitor capture took 0.405 s off and 0.717 s on, adding
0.312 s. The default-off card capture uploaded without checking.

The prompt floated without a desktop title bar and was initially focused.
Return opened the editor with the suggested card mark. The receiver PNG differed
from the default-off image only in the opaque black 489 × 40 rectangle. Upload
anyway preserved the card and the original pixels apart from an I-beam cursor
difference in the far corner across the two independent captures. Escape with
local retention produced one local-only History item. Clicking Cancel with
retention disabled produced zero uploads and no History item. The sample key
prompted and cancelled with Escape.

The tiled fixture took focus and left the floating prompt visible. Toggling that
same fixture to a floating window covered the prompt. Hovering the tray revealed
put.gd's icon, and a click on it brought the prompt back. Agent mode paused for
a decision without a visible panel and accepted a Cancel decision.

The unattended agent operation cancelled 300.689 s after selection, with no
receiver object or History item. Diagnostics answered with zero active operations.
Both Omarchy overlay retirement receipts are included.

### Fedora Budgie labwc Wayland on 74327614e

The active guest ran the exact AppImage at 1280 × 800. The option was off by
default, all seven Settings labels fit, and Card numbers, Keys and tokens,
and My redaction list were selected after enabling it. At 676 × 178 the clean
region medians were 0.395 s off and 0.615 s on, adding 0.220 s. The full monitor
capture took 0.409 s off and 0.780 s on, adding 0.371 s. The card prompt opened
raised and focused. Return opened the editor with a suggested mark, and only
its 489 × 40 rectangle changed to opaque black in the receiver's PNG.

The tray reactivation check failed twice. For each attempt, capture the test
card using Ctrl+Shift+F9, wait for the prompt, click the maximized synthetic
fixture at `(1120, 345)`, then click the visible put.gd tray icon at
`(1110, 781)`. The prompt stays covered. The reproduction operation
`10390735-f3b8-431d-9192-c09306ac84ee` stayed in `sensitive_text_found` with
one complete card finding and no uploaded items. The header-only D-Bus trace
recorded the tray host sending `org.kde.StatusNotifierItem.Activate` and did not
show a `ProvideXdgActivationToken` call. Both waiting operations were cancelled
through the CLI for cleanup. The remaining cells were deferred until the fix.
The guest was retired with the exported evidence and failure manifest.

## Candidate 764f60936

CI run 44971254571 passed at `764f60936d2feaedf9ff04fae6c2eb1d67c69d2b`.
The AppImage reported tree `e1b732e3f7fe3daff40616a702384a8a11024f07`
in both guest residents. This candidate changes the prompt raise path on
Wayland. The earlier passed cells still apply.

### Fedora Budgie labwc Wayland retest

The 1280 × 800 guest passed launch preflight and ran a fresh AppImage extraction.
The default-off capture uploaded the test card without a check phase.
All seven Look for kinds were readable, with Card numbers, Keys and tokens,
and My redaction list selected after enabling the option in Settings.
The clean 676 × 178 region medians were 0.376 s off and 0.630 s on, adding
0.254 s. Full-screen capture took 0.356 s off and 0.686 s on, adding 0.330 s.

The frameless gold-edge card panel opened raised and focused. Pressing Return
opened the editor at the suggested 489 × 40 mark. The receiver's PNG differs
from the original only inside that fully black rectangle. After another
window covered the next panel, a click at the tray icon center `(1107, 782)`
restored that same prompt. The header-only trace recorded Activate and no
ProvideXdgActivationToken. The first pointer attempt recorded no Activate
and left the prompt covered. Upload anyway returned a byte-identical PNG
to the default-off card capture. Escape with Keep a local copy enabled saved
one local-only History item without uploading. Clicking Cancel after disabling
it produced zero uploads and zero History items. The AWS example key produced
one key finding, and Escape dismissed it with no object or History item.

The CLI card capture reached `sensitive_text_found` without opening a panel
and accepted a Cancel decision. The guest evidence includes the covered and
restored frames, header-only traces, receiver PNGs, and operation records.
The unattended operation `ad85c0d0-674a-4004-ac00-5311b7cc819e` cancelled
300.391 s after selection. The receiver and History both stayed unchanged,
and diagnostics responded with zero active operations. The default-off card
upload, `c5f64e6c-56ae-4d82-8a5b-3dfa36730bb7`, produced a link in 0.446 s.

### Omarchy Hyprland Wayland tray recovery retest

The 1280 × 800 guest passed launch preflight and ran the same AppImage.
The hotkey opened operation `908f5df6-7a3e-41b6-9633-df556e22c045` raised
and focused. Clicking the tiled fixture took focus. Toggling it to floating
with Super+T covered the panel. One click on put.gd's expanded tray icon at
`(1124, 12)` restored the same pending operation, and Escape cancelled it
with one local-only History item and no uploads. The tray trace shows
Activate without ProvideXdgActivationToken. The other Hyprland cells use
the full run on `74327614e`.

## Mint Settings draft retest on 1eafcaf18

CI run 44973033446 passed at `1eafcaf18fd7a0bfd48309e7d949c81bd9f3ea72`.
The installed Ubuntu 24.04 DEB reported the exact tree
`c0098c5317bfa210788daa44b1ab7c250e247a2a` on m74 Cinnamon X11.

In the real Settings window, the check started off. Enabling it selected
Card numbers, Keys and tokens, and My redaction list. Clicking Email addresses
added that fourth selection. Closing through the window's X produced a normal
UI helper exit and a retained 11,869-byte checkpoint. The relaunched UI helper
reopened the same Capture section. The toggle and all four selected kinds were
still set and all seven labels were visible. The resident's structured logs
and output had zero matches for `ui_state_invalid` or other UI state errors.

Clicking the dashboard's Capture region button closed the dashboard with a
normal helper exit and captured a clean 676 × 178 rectangle. Operation
`1c4d1c83-aacb-4e34-9967-782952ea58e7` checked the image, uploaded the PNG
without a prompt, and produced the receiver link in 0.720 s. The default
benchmark timings above use their original paired samples. This capture
confirms the fixed dashboard path.

The root Settings picture is the reopened frame from this DEB, cropped and
annotated with its own put.gd editor. The root prompt picture comes from the
GNOME session on `74327614e` and was annotated in that build's editor.
