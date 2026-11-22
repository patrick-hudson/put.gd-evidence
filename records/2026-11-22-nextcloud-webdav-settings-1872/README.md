# Nextcloud and WebDAV destination forms in Settings (#1872)

Offscreen renders (QT_QPA_PLATFORM=offscreen, dark scheme) from `putgd-ui-catalog`, made by
`tools/ci/check_catalog_render.py` on m74 (Linux Mint 22.3) from put.gd-desktop
`feat/nextcloud-webdav-destinations` at 886af0592 (PR #1879). The forms were filled through
`ui.davDestination`, the same driver agents use.

- `settings-nextcloud-dark.png`: a new Nextcloud destination. A pasted Files link
  (`https://cloud.example.com/index.php/apps/files/?dir=/`) was reduced to the server's base
  address. It shows the account row (Signed out, Sign in…, Use an app password instead) and the
  folder card.
- `settings-nextcloud-app-password-dark.png`: Use an app password instead, opened. It shows the
  Login name and App password fields under Credentials.
- `settings-webdav-dark.png`: a WebDAV destination with a folder address typed without a
  scheme (`https://` was added) and a public link address, with User and Password under
  Credentials.

These are offscreen widget renders, not desktop acceptance evidence.
