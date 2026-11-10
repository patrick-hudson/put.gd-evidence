# Custom HTTP uploader with ShareX .sxcu import (#1361): pictures and checks at the PR head

Implementer's own run for put.gd-desktop PR #1371 (issue #1361). The five-desktop acceptance
is a separate record made from the PR's CI packages.

## Build and host

- Source: `feat/custom-http-uploader` at `8f69043ee` (PR #1371 head when taken).
- Build: a dev build of that tree on **m74** (Linux Mint 22.3, Cinnamon, X11, Qt 6.4.2). The
  build tree has no git metadata, so the window's version reads `0.0.0-dev.unknown`.
- Receivers: Zipline 4.8.3, Chibisafe 6.7.0 and XBackBone 3.8.2 in rootless Podman pods on
  aurora-amd, lab network only, each with the `.sxcu` file it generated itself
  (`tools/lab/http_receivers/` in the PR). Synthetic uploads only.

## Results

`results.json` has the numbers. In short:

- `http_uploader_rules`: 158 passed, 0 failed. `http_uploader_integration` (production provider
  and worker against the scripted loopback receiver): 41 passed, 0 failed.
- The three real receivers through a headless private resident (`check_uploads.py
  --allow-insecure-http`): Test connection, upload and link fetch pass for all three. XBackBone's
  upload is deleted through its deletion URL and the link then answers 404. Zipline and Chibisafe
  return no deletion URL, and deletion is refused with that reason. No token of the three files is
  in any configuration, data or state file or in a diagnostics package made with names included.
  Without the flag every import is refused with `http_insecure_url`.
- On the m74 desktop, with a private resident on the real display: the Settings form, the import,
  storing the token, Test connection, an upload, the real Firefox (throwaway profile) loading the
  uploaded link, the prepared deletion and the deletion, an upload with no deletion URL, and a
  lost reply followed by an explicit Retry that leaves two copies on the scripted receiver.

## Pictures

`pictures/` holds the annotated set; `raw/` the same captures untouched. The marks (boxes, arrows
and labels) were drawn with put.gd's own image editor through `putgd-cli` (`editor.open`,
`editor.apply`, `editor.saveCopy`) in a headless resident of the same build:
`tools/annotate1361.py` with `tools/annotations.json`.

| Picture | Shows |
| --- | --- |
| `01-add-destination-menu.png` | Add destination with the new type, Custom uploader (HTTP) |
| `02-new-custom-uploader.png` | The new form as Add destination leaves it |
| `03-import-dialog.png` | The import dialog: choose a file or paste its text |
| `04-imported-plain-http-refused.png` | XBackBone's own file imported; its plain-HTTP address refused until allowed |
| `04b-imported-plain-http-allowed.png` | Allow plain HTTP ticked: the destination saves |
| `05-imported-fields-masked.png` | The imported token: masked, marked Secret, not saved yet |
| `06-stored-masked.png` | After Store: the field shows only that a value is stored |
| `07-test-connection-result.png` | Test connection: upload, link fetch and deletion passed |
| `08-history-uploaded.png` | A History item uploaded to the real XBackBone receiver |
| `09-browser-shows-upload.png` | The real Firefox loading that link |
| `10-prepared-deletion.png` | The prepared deletion with its target |
| `11-history-deleted.png` | The item after deletion |
| `12-retry-may-duplicate.png` | A lost reply: outcome unknown, and the duplicate-on-retry notice |
| `13-after-retry.png` | After Retry upload: uploaded, the notice gone, two copies on the receiver |
| `14-no-deletion-url.png` | An upload to Zipline: no Delete button, and the reason |
| `15-test-suites.png` | Terminal panel with the parser, scripted-receiver and real-receiver results |

`catalog-150/` has two renders of the same form from `putgd-ui-catalog` of the same build at
150% text scale (synthetic catalog data).

## How it was taken

- `tools/desktop1361.py`: starts a private resident (own XDG folders, session credentials) on the
  X11 display, drives it through `putgd-cli`, makes two real pointer clicks with `xdotool` (the
  Allow plain HTTP box and Delete from destination), captures put.gd's window with ImageMagick,
  and opens the link in Firefox with a throwaway profile through a temporary handler;
  `~/.config/mimeapps.list` is restored byte for byte. Run under the m74 desktop lock.
- `tools/headless-check.sh`: the real-receiver check against a headless resident.
- The token rows are shown masked and were never revealed; no picture or file here holds a token.
