# Settings save queue (#1704, #1701)

Pictures for the Settings save queue: a conflict now offers Retry saving, which applies the
window's queued edits to the configuration file as it is now.

## Build

- Code: put.gd-desktop `fix/settings-save-queue-1704` at `3e01e00eb` (on nightly `48153b828`).
- Dev build (`cmake --preset dev`) synced without `.git`, so the footer reads `0.0.0-dev.unknown`.

## Pictures (m74, Linux Mint 22.3 Cinnamon X11, Qt 6.4)

A private resident on the real display. The destination, bucket names and file are synthetic.

1. `02-conflict-retry-annotated.png`: Region holds a value that can't be saved
   (`Western North America (WNAM)`), so it stays unsent. The bucket is then renamed in the
   configuration file from outside (putgd-cli `settings.save`). The window reports the
   conflict and now shows **Retry saving** beside the banner, which says what each choice does.
2. `03-after-retry-annotated.png`: after Retry saving, the form shows the bucket changed
   elsewhere, the Region is still as typed with its message under the field and in the
   footer, and the file keeps its saved Region (`us-east-2`).
