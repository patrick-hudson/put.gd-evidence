# Aurora Fedora 45, Plasma 6.8.2 Wayland

The physical Aurora desktop ran the unmodified AppImage from CI run 45310837809. The OCR helper reported merge commit `9b8f9cc663fd100ca2da32aff9fb3c69dd585ad2` and tree `6528e671506c0cf8b22c1cf7ac8b92f9083271b8`. The AppImage verified OSD and all nine script-language files in its bundled tessdata.

| Region and preference | Operation | Recorded result | Desktop result |
| --- | --- | --- | --- |
| Sina headline column, Automatic | `ac0f5091-6fbb-48a4-8362-2ecd563ef831` | `{"script":"Han","language":"chi_sim","outcome":"kept"}`; languages `eng`, `chi_sim` | Notified “Copied 290 characters”. The text pasted into KWrite was readable Chinese with some OCR errors. |
| RIA article body, Automatic | `43a51de0-ae4c-414c-a0fd-73413f5cc339` | `{"script":"Cyrillic","language":"rus","outcome":"kept"}`; languages `eng`, `rus` | Notified “Copied 447 characters”. The text pasted into KWrite was readable Russian. |
| Same RIA region, English | `32bb27b6-b5a7-4034-8bef-199c458ce0c1` | Detection field absent. Language `eng`. | The capture completed and copied text. The preference was restored to Automatic afterwards. |

The production CLI invoked Copy text, changed the isolated profile's language for the English control and annotated the images through put.gd's editor. The real region selector, clipboard paste and Plasma notifications were observed on the physical desktop.
