# Real-desktop checklist: tray menu and action bar (PR #1532, head f63d24dbc)

Each row is the designed behaviour. A row passes when the desktop does what it
says, with no lab overrides.

## Tray: every row on GNOME, KDE Plasma, Cinnamon, Budgie and Hyprland/Omarchy

| # | Designed behaviour |
|---|---|
| T1 | Idle menu, in order: Capture region, Repeat last region, Capture window, Capture monitor, Capture desktop, Capture scrolling region ─ Capture region & edit, Edit image ▸, Record screen ─ Copy text from region, Upload clipboard ─ Capture delay: none ▸, Capture output: … ▸ ─ Open put.gd, Settings ─ Quit put.gd. There is no History, Destinations or About put.gd row, and nothing shows above Capture region. |
| T2 | Edit image ▸ shows Edit clipboard image and Edit an image file…; each opens the editor or the file chooser. |
| T3 | Capture delay ▸ shows None / 3 / 5 / 10 seconds with exactly one radio mark. Choosing 5 relabels the row "Capture delay: 5 seconds" and adds a disabled "Hotkeys capture at once" row. With "Also delay captures started by a hotkey" on, that row disappears. |
| T4 | Capture output ▸ shows disabled rows (All actions or Default, then the timing row, then exceptions), a separator, then Change output…, which opens Settings → Capture. |
| T5 | Bound hotkeys show beside their rows; unbound rows show none. |
| T6 | During an upload, a disabled "Uploading N files…" row and Cancel upload appear at the top, with one separator under them. With several uploads it reads "Cancel all uploads…". |
| T7 | After a failure, "Failed uploads (n)" (or another attention label) appears at the top; opening it clears the badge. |
| T8 | During a recording, a disabled phase row (for example "Recording paused") and Show recording appear at the top. Show recording raises the bar or review window. Record screen keeps its label and also only raises it, never starting a second recording or stopping this one. |
| T9 | Recording, upload, failure and an update all at once: the block's rows stack in order above a single separator, and "Update available: <version>" appears after Settings. |
| T10 | A long destination name (rename a destination to about 50 characters): the Capture output row and its detail rows show in full or are cut off cleanly, and the menu stays usable. |
| T11 | Change a setting in the window (delay, an output, a hotkey) without opening the tray menu, then open it once: it already shows the new values. Pay most attention on Cinnamon, which never signals AboutToShow. |
| T12 | Left-click on the tray icon: record per host whether it opens the window on History (put.gd sends that on Activate) or opens the menu. This row records a fact; it has no pass or fail. |
| T13 | Open put.gd opens the main window on History. Every capture row starts its action (one real capture per row is enough; Repeat last region after a region capture). |

## Window and status band: on each desktop

| # | Designed behaviour |
|---|---|
| W1 | A fresh profile opens at 1,440 × 880 with all nine buttons in one row, the divider before Capture region & edit, and Copy text plus Upload clipboard at the far right. Record what happens on a screen narrower than 1,440 px if one is available. |
| W2 | Narrower than about 1,413 px, the second group moves to a second row with the same labels, Copy text and Upload clipboard still at the right. The window can't be made narrower than 1,060 px. |
| W3 | Enlarged desktop text: the bar wraps in the same order and no label shortens or becomes icon-only. |
| W4 | Capture region's ▾ and a right-click on it both open a menu with Repeat last region. Capture region & edit's ▾ and a right-click both open Edit clipboard image and Edit an image file…. A right-click on any other button opens nothing. Only one menu opens per click. |
| W5 | Tab to Capture region, then Alt+Down (also F4, the Menu key, Shift+F10) opens its menu with the first row highlighted; Enter chooses it and Esc closes it. Same on Capture region & edit. Focus is visible throughout. |
| W6 | Dropping a PNG or JPEG on Capture region & edit opens the editor. Its ▾ still works when region capture is reported unavailable. |
| W7 | The status band shows "Capture delay: none ▾" on History, Destinations and every Settings tab, including Capture, where the output summary hides. Choosing 5 seconds highlights the control and updates the tray. The control never gets cut off: in a narrow window, "Settings save automatically" disappears first, then the output summary shortens. |
| W8 | With a delay set, the tooltips of Capture region, Window, Monitor, Desktop, Capture region & edit and Copy text end with "Waits 5 seconds first"; Scrolling region, Record screen and Upload clipboard don't. A click on a delayed button waits; the same action's hotkey captures at once unless the hotkey-delay option is on. |
| W9 | During a recording, Record screen keeps its label, and its tooltip and screen-reader description include the phase. |
| W10 | The ☰ menu reads How capture actions work, Check for updates, About put.gd, Quit put.gd. Settings → Hotkeys lists ten rows with a gap at each group boundary. |
