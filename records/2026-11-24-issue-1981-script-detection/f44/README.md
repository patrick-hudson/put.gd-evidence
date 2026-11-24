# Fedora 44, GNOME Shell 50.6 Wayland

The physical Fedora desktop ran the Fedora 44 RPM from CI run 45310837809. The installed OCR helper reported the CI merge commit and tree recorded in the root README. DNF installed OSD and nine recommended script-language packages.

| Region and preference | Operation | Recorded result | Desktop result |
| --- | --- | --- | --- |
| Sina headline column, Automatic | `f7500eae-7b35-489b-bafd-37e40633ef9e` | `{"script":"Han","language":"chi_sim","outcome":"kept"}`. Languages `eng`, `chi_sim`. | GNOME showed “Copied 273 characters”. Readable Chinese pasted into GNOME Text Editor. |
| RIA article body, Automatic | `3a94a5b0-d984-44b2-9aad-0de78130ec06` | `{"script":"Cyrillic","language":"rus","outcome":"kept"}`. Languages `eng`, `rus`. | GNOME showed “Copied 447 characters”. Readable Russian pasted into GNOME Text Editor. |
| Same RIA region, English | `69024cee-2fef-482a-9540-5c301a766355` | Detection field absent. Language `eng`. | The capture completed and copied text. The preference was restored to Automatic. |

The physical region selector, clipboard paste and GNOME notifications were observed on Wayland. The CLI invoked Copy text, changed the isolated profile's language for the English control and annotated the images through put.gd's editor.
