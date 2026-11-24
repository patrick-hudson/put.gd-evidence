# Linux Mint 22.3, Cinnamon 6.6.9 X11

The physical Mint desktop ran the Ubuntu 24.04 DEB from CI run 45310837809. The installed OCR helper reported the CI merge commit and tree recorded in the root README. Apt installed nine recommended script-language packages and the existing OSD package was present.

| Region and preference | Operation | Recorded result | Desktop result |
| --- | --- | --- | --- |
| Sina headline column, Automatic | `e9ae5743-e105-4249-9d95-9089d1597504` | `{"script":"Han","language":"chi_sim","outcome":"kept"}`. Languages `eng`, `chi_sim`. | Readable Chinese pasted into Xed. A D-Bus call from the resident to Cinnamon's notification service reported “Copied 287 characters”. |
| RIA article body, Automatic | `99a90766-e358-49b6-a2ea-05712dfc591c` | `{"script":"Cyrillic","language":"rus","outcome":"kept"}`. Languages `eng`, `rus`. | Readable Russian pasted into Xed. A D-Bus call from the resident to Cinnamon's notification service reported “Copied 447 characters”. |
| Same RIA region, English | `3b336267-25bc-4706-a55e-f5e9ac58bb84` | Detection field absent. Language `eng`. | The capture completed and copied text. The preference was restored to Automatic. |

The physical region selector and clipboard paste were observed on Cinnamon. The CLI invoked Copy text, changed the isolated profile's language for the English control and annotated the images through put.gd's editor.
