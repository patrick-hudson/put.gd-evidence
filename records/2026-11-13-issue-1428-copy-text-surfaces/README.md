# Issue 1428: Copy text in the command band, the tray and Settings

Pictures for put.gd-desktop pull request "Copy text on every desktop" (issue #1428, item 4b). They show the new **Copy text** control on three surfaces.

- **Source:** put.gd-desktop branch `feat/text-desktops` at commit `84c6f4f66` (tree identical to the build that was rendered).
- **How:** `putgd-ui-catalog` through `tools/ci/check_catalog_render.py`, offscreen, on k72 (Kubuntu 26.04, Qt 6.10.2), dark and light, and once at 150 % text (`--text-scale 1.5`). The catalog uses synthetic data and a fixed text recognition report (English and German installed), so nothing here is real user content.
- **Checks on the same dark render:** `tools/lab/surface_map/surface_map.py check` passed (240 captures with controls) and `tools.lab.surface_driver.gate check-catalog` passed with the secret-control pin unchanged (33 states).
- **Annotation:** the red boxes and labels were drawn with put.gd's own editor, headless (`editor.open`, `editor.apply`, `editor.saveCopy`).

| Picture | What it shows |
| --- | --- |
| `band-full-dark.png`, `band-full-light.png` | The command band at 1440 px: "Copy text" after Capture scrolling region, before Upload clipboard |
| `band-minimum-dark.png` | The window's minimum width, 1060 px: the narrow label "Text" |
| `band-minimum-large-text-dark.png` | 150 % text at 1060 px: icon only, with Monitor, Record, Scroll and Clipboard; the band still fits |
| `band-full-large-text-dark.png` | 150 % text at 1440 px, not annotated |
| `tray-menu-dark.png` | The tray menu: "Copy text from region" after Capture scrolling region |
| `settings-text-recognition-dark.png`, `settings-text-recognition-light.png` | Settings → Capture → Text recognition |

These are renders of the interface, not desktop acceptance: no compositor, hotkey or clipboard was involved.
