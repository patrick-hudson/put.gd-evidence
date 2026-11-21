# Copy text emoji desktop acceptance, round 2

The coordinating thread approved CI merge commit `d38651d2af809325f75ea6fe36558b39f0037741` (tree `3d6c99784c6931dfddd0c0233b4f00a7d9e69dcf`) as the target for PR #1751 head `648946bf3f6de8df5ccd4ba1d7a238db75c6d495`. The only 15 differing paths are desktop and lab documentation, desktop tests and lab tools from newer nightly. The packaged product files are identical to the head. [CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44843335878) · [Tree comparison](head-vs-ci.txt)

The physical desktop checks use the Ctrl+Shift+9 hotkey, real selector drag, an independent native clipboard reader and desktop notifications. The measured putgd-ocr helpers were observed through the kernel process connector and VmHWM is reported in KiB.

“Words intact” checks the expected words in sequence. Recognized junk is visible in the literal clipboard lines and exact text files. “Hello glue” checks literal Hello👋. Only the uncoloured Twemoji coffee is exempted when the browser draws Twemoji. The four line 6 glyphs are tracked separately. On Aurora, both Firefox zooms require white background pixels before the hotkey runs.

## Test packages

| Host | OS and session | Firefox and emoji artwork | Running identity | Package / SHA-256 |
|---|---|---|---|---|
| f44 | Fedora Linux 44 (Workstation Edition) · GNOME Shell 50.6 · wayland | Mozilla Firefox 158.0.1 · Noto Color Emoji | 26.1121.5949-dev+gd38651d2af80 | `putgd-26.1121.5949~dev+gd38651d2af80-1.fc44.x86_64.rpm` / `ea89e9b54c65b7ed30460aa2f2b6138a2529928314273aea8b7c8a549b28e6d7` |
| k72 | Ubuntu 26.04.1 LTS · QThreadStorage: entry 1 destroyed before end of thread 0x624f7aeb5dc0
QThreadStorage: entry 0 destroyed before end of thread 0x624f7aeb5dc0
kwin 6.6.6 · wayland | Mozilla Firefox 159.0.1 · Noto Color Emoji | 26.1121.5949-dev+gd38651d2af80 | `putgd_26.1121.5949~dev+gd38651d2af80_amd64.deb` / `458fe482a881ae58244a80707666ca5bb7b96ceb7980c67551f348848156a9a5` |
| m74 | Linux Mint 22.3 · Cinnamon 6.6.9 · x11 | Mozilla Firefox 158.0 · Noto Color Emoji | 26.1121.5949-dev+gd38651d2af80 | `putgd_26.1121.5949~dev+gd38651d2af80_amd64.deb` / `3dc7226e63f3702f7b075b1691106d9d8e6086c914b5f6060d83d20d99a7b870` |
| d69 | Debian GNU/Linux 13 (trixie) · QThreadStorage: Thread 0x5594257a94c0 exited after QThreadStorage 8 destroyed
QThreadStorage: Thread 0x5594257a94c0 exited after QThreadStorage 1 destroyed
QThreadStorage: Thread 0x5594257a94c0 exited after QThreadStorage 0 destroyed
kwin 6.3.6 · wayland | Mozilla Firefox 153.5.0esr · Noto Color Emoji | 26.1121.5949-dev+gd38651d2af80 | `putgd_26.1121.5949~dev+gd38651d2af80_amd64.deb` / `75356014d664fcf63115a441839e316d3a8eed59f49cc2c76ddfaf2402b3b475` |
| aurora-amd | Aurora (Version: testing-45.20261101.2) · kwin 6.8.2 · wayland | Mozilla Firefox 160.0.1 · Noto Color Emoji (Flatpak runtime) | 26.1121.5949-dev+gd38651d2af80 | `putgd-26.1121.5949-dev+gd38651d2af80-x86_64.AppImage` / `3efa92ff582ca0c59f8537341af8e4ed17eab3126f618d289f2043cadc779fe2` |

## Results

| Desktop | Surface | Emoji right / wrong / missed | Words intact | Hello glue | Plain exact / nightly | Notification | Helper peak / exit |
|---|---|---|---|---|---|---|---|
| f44 | Firefox 100% | 13/0/0 | yes | yes | — | Copied 185 characters | 77,592 KiB / 0 |
| f44 | Firefox 150% | 13/0/0 | yes | yes | — | Copied 188 characters | — |
| f44 | Native editor (GNOME Text Editor) | 12/0/1 | yes | yes | — | Copied 190 characters | — |
| f44 | Plain text (GNOME Text Editor) | — | yes | — | yes / — | Copied 185 characters | — |
| k72 | Firefox 100% | 13/0/0 | no | yes | — | Copied 186 characters | 78,360 KiB / 0 |
| k72 | Firefox 150% | 12/0/1 | yes | yes | — | Copied 190 characters | — |
| k72 | Native editor (KWrite) | 12/0/1 | yes | no | — | Copied 187 characters | — |
| k72 | Plain text (KWrite) | — | yes | — | no / same | Copied 186 characters | — |
| m74 | Firefox 100% | 13/0/0 | no | yes | — | Copied 186 characters | 76,096 KiB / 0 |
| m74 | Firefox 150% | 12/0/1 | yes | yes | — | Copied 190 characters | — |
| m74 | Native editor (xed) | 12/0/1 | yes | yes | — | Copied 190 characters | — |
| m74 | Plain text (xed) | — | yes | — | no / same | Copied 186 characters | — |
| d69 | Firefox 100% | 13/0/0 | no | yes | — | Copied 183 characters | 75,616 KiB / 0 |
| d69 | Firefox 150% | 12/0/1 | yes | yes | — | Copied 191 characters | — |
| d69 | Native editor (GNOME Text Editor) | 12/0/1 | yes | yes | — | Copied 193 characters | — |
| d69 | Plain text (GNOME Text Editor) | — | yes | — | no / same | Copied 186 characters | — |
| aurora-amd | Firefox 100% | 12/0/1 | no | yes | — | Copied 185 characters | 59,976 KiB / 0 |
| aurora-amd | Firefox 150% | 12/0/1 | no | yes | — | Copied 187 characters | — |
| aurora-amd | Native editor (KWrite) | 12/0/1 | yes | yes | — | Copied 192 characters | — |
| aurora-amd | Plain text (KWrite) | — | no | — | no / same | Copied 186 characters | — |

## Comparison with round 1

Round-one exact clipboard bytes are scored with the same coffee convention wherever the font matches. [Round-one record](https://github.com/patrick-hudson/put.gd-evidence/blob/b9088e7f3d0c847d615fd37b0be22da67a6474a5/records/2026-11-20-issue-1748-copy-text-emoji-desktops/README.md)

- f44 Firefox 100% moved from 9/1/3 to 13/0/0.
- f44 Firefox 150% moved from 8/0/5 to 13/0/0.
- f44 Native editor (GNOME Text Editor) moved from 11/0/2 to 12/0/1.
- f44 Plain text (GNOME Text Editor) yielded the same clipboard bytes compared with round 1.
- k72 Firefox 100% moved from 10/0/3 to 13/0/0.
- k72 Firefox 150% moved from 9/0/4 to 12/0/1.
- k72 Native editor (KWrite) moved from 8/0/5 to 12/0/1.
- k72 Plain text (KWrite) yielded the same clipboard bytes compared with round 1.
- m74 Firefox 100% moved from 10/0/3 to 13/0/0.
- m74 Firefox 150% moved from 9/0/4 to 12/0/1.
- m74 Native editor (xed) moved from 11/0/2 to 12/0/1.
- m74 Plain text (xed) yielded the same clipboard bytes compared with round 1.
- d69 Firefox 100% moved from 10/0/3 to 13/0/0.
- d69 Firefox 150% moved from 9/0/4 to 12/0/1.
- d69 Native editor (GNOME Text Editor) moved from 10/0/3 to 12/0/1.
- d69 Plain text (GNOME Text Editor) yielded the same clipboard bytes compared with round 1.
- aurora-amd Firefox 100% scored 12/0/1 on a white page. The dimmed round-one frame had no valid emoji score.
- aurora-amd Firefox 150% scored 12/0/1 on a white page. The dimmed round-one frame had no valid emoji score.
- aurora-amd Native editor (KWrite) moved from 10/0/3 to 12/0/1.
- aurora-amd Plain text (KWrite) yielded the same clipboard bytes compared with round 1.

## Reproduction

Open the included fixture in the named application and use the documented zoom or default native font size. Trigger Copy text from region and drag the recorded rectangle. Read the clipboard and notification after the action completes. The selected source crops accompany each operation receipt.

## Test setup and evidence

All applicable package jobs passed. The release-collection job was skipped by its release-tag condition. No package was compiled on a builder. The lab tools came from origin/nightly at 994c04218c16ca0fbce77e02a3ae8759ead3eba9.

The figures pair the visible Firefox 150% selector with the actual clipboard pasted into the desktop editor. The source and paste are individually cropped from live frames. The green rectangles were added with put.gd's editor on Cinnamon. [Fedora figure](m74/candidate/f44-annotated.png) · [Kubuntu figure](m74/candidate/k72-annotated.png)

The control package was the published v26.1120.5875-nightly, commit 779e2517303d8fcb08aca99840589e728d9b98ff. Candidate and control each used a private resident and the exact same desktop rectangle. Where a source-frame hash differs, the changed pixels are confined to a few pixels at the lower-right edge. [Pixel comparison](plain-control-pixel-differences.json)

The desktop notification character totals match the number of grapheme clusters in each recorded clipboard value, including clusters with a skin tone or flag sequence.

Debian's KWrite still displayed empty boxes and monochrome glyphs. GNOME Text Editor supplied the scored native emoji and plain-text cases in the same Plasma Wayland session. The first editor geometry probe timed out during the headless measurements. Its receipt was kept and the native case was retried with extra time for the editor window to appear. The headless runs were left alone and the startup load was recorded. [KWrite preview](d69/candidate/kwrite-preview.png) · [Debian load](d69/load-before.txt)

Aurora ran Mozilla Firefox 160.0.1 from Flathub, deployment 3ab15a895b6a9935e2cc33dd2771c600422ed3cfa153bcadf8c60dff5b8f41fc. The fresh profile disabled startup prompts. All four background pixels were RGB (255, 255, 255) before each capture. Its fixture used the Flatpak runtime's Noto Color Emoji bitmap face. The browser additionally listed Twemoji Mozilla, and its web content process loaded the Noto bitmap character map. Aurora's first plain-text selection included KWrite's line-number gutter. The scored retry uses the round-one rectangle. [Aurora receipt](aurora-amd/candidate/receipt.json) · [Firefox font log](aurora-amd/candidate/firefox-font.log)

## Outstanding OCR differences

- Firefox at 100% drops “so” on Kubuntu, Mint and Debian. Aurora drops the initial “I” on line 3 at both zooms. Fedora keeps the words and occasionally removes the space beside the contiguous laughing faces.
- Noto coffee is missed on line 2 at Firefox 150% on Kubuntu, Mint and Debian, and at both zooms on Aurora. Fedora recognizes it at both zooms.
- Each native editor misses the UK flag on line 5. The flag in Aurora's KWrite is the documented small COLRv1 flag case. The England flag is copied. Kubuntu KWrite inserts an OCR artifact between “Hello” and the wave. All four excluded line 6 glyphs remain absent as emoji in the scored runs.
- Reproduce each difference with the fixture, zoom, application and rectangle in the exact observation and receipt below.

## Exact observations

### f44 · Firefox 100%

Selection `[18, 20, 487, 292]`, operation `2db4597d-a8ec-4a1e-8c2f-d0821b59987b`. [Clipboard bytes](f44/candidate/firefox-100.txt) · [Selected pixels](f44/candidate/firefox-100-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

Notification “Copied 185 characters”. Literal Hello👋 retained **yes**.

### f44 · Firefox 150%

Selection `[31, 34, 725, 437]`, operation `2f00119f-c321-4471-9c1a-fbf47fe5076d`. [Clipboard bytes](f44/candidate/firefox-150.txt) · [Selected pixels](f44/candidate/firefox-150-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ {J and colourless`.

Notification “Copied 188 characters”. Literal Hello👋 retained **yes**.

### f44 · Native editor (GNOME Text Editor)

Selection `[3, 126, 500, 271]`, operation `05cdca8d-4310-4519-85b0-8588b290426c`. [Clipboard bytes](f44/candidate/native.txt) · [Selected pixels](f44/candidate/native-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ §J and colourless **`.

Notification “Copied 190 characters”. Literal Hello👋 retained **yes**.

### f44 · Plain text (GNOME Text Editor)

Selection `[2, 126, 477, 227]`, operation `94c0eba0-1d45-488d-99a1-3a19cc5b665c`. [Clipboard bytes](f44/candidate/plain.txt) · [Selected pixels](f44/candidate/plain-region.png)

### k72 · Firefox 100%

Selection `[18, 21, 487, 298]`, operation `9d608cac-09b0-459e-8dba-264c03e07c69`. [Clipboard bytes](k72/candidate/firefox-100.txt) · [Selected pixels](k72/candidate/firefox-100-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ (J and colourless`.

Notification “Copied 186 characters”. Literal Hello👋 retained **yes**.

### k72 · Firefox 150%

Selection `[31, 35, 724, 443]`, operation `132b6248-b0ed-42f0-97df-2c1798e9dfcd`. [Clipboard bytes](k72/candidate/firefox-150.txt) · [Selected pixels](k72/candidate/firefox-150-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [ij and colourless`.

Notification “Copied 190 characters”. Literal Hello👋 retained **yes**.

### k72 · Native editor (KWrite)

Selection `[30, 97, 474, 211]`, operation `2388c071-3c1f-4cbe-8d35-490a132f199c`. [Clipboard bytes](k72/candidate/native.txt) · [Selected pixels](k72/candidate/native-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello®👋 from and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `plain shapes stay out @ J and colourless`.

Notification “Copied 187 characters”. Literal Hello👋 retained **no**.

### k72 · Plain text (KWrite)

Selection `[30, 97, 455, 179]`, operation `b49cf194-94dc-4055-a93f-c37c06526c49`. [Clipboard bytes](k72/candidate/plain.txt) · [Selected pixels](k72/candidate/plain-region.png)

Nightly clipboard bytes match **True**, coordinates match **True**, and pixel hashes match **False**. [Nightly clipboard](k72/baseline/plain.txt)

### m74 · Firefox 100%

Selection `[18, 21, 487, 298]`, operation `d6cc569d-7763-4fc5-9722-3784046f9165`. [Clipboard bytes](m74/candidate/firefox-100.txt) · [Selected pixels](m74/candidate/firefox-100-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ (J and colourless`.

Notification “Copied 186 characters”. Literal Hello👋 retained **yes**.

### m74 · Firefox 150%

Selection `[31, 35, 724, 443]`, operation `262d1076-be73-4213-91b1-7dc9b3f73a55`. [Clipboard bytes](m74/candidate/firefox-150.txt) · [Selected pixels](m74/candidate/firefox-150-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [fj and colourless`.

Notification “Copied 190 characters”. Literal Hello👋 retained **yes**.

### m74 · Native editor (xed)

Selection `[0, 130, 457, 250]`, operation `3502d843-39c8-4587-b0a1-073cf9878c40`. [Clipboard bytes](m74/candidate/native.txt) · [Selected pixels](m74/candidate/native-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ (J and colourless ++`.

Notification “Copied 190 characters”. Literal Hello👋 retained **yes**.

### m74 · Plain text (xed)

Selection `[0, 130, 428, 216]`, operation `12314bca-9ed7-4812-bc5e-0cb53f00c0d1`. [Clipboard bytes](m74/candidate/plain.txt) · [Selected pixels](m74/candidate/plain-region.png)

Nightly clipboard bytes match **True**, coordinates match **True**, and pixel hashes match **False**. [Nightly clipboard](m74/baseline/plain.txt)

### d69 · Firefox 100%

Selection `[18, 21, 506, 298]`, operation `8fe093e1-2072-4926-8dd7-7960bd9dac79`. [Clipboard bytes](d69/candidate/firefox-100.txt) · [Selected pixels](d69/candidate/firefox-100-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

Notification “Copied 183 characters”. Literal Hello👋 retained **yes**.

### d69 · Firefox 150%

Selection `[31, 35, 724, 443]`, operation `34f9cc45-be6e-41db-841f-86cc84ac4bd7`. [Clipboard bytes](d69/candidate/firefox-150.txt) · [Selected pixels](d69/candidate/firefox-150-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [ijJ and colourless`.

Notification “Copied 191 characters”. Literal Hello👋 retained **yes**.

### d69 · Native editor (GNOME Text Editor)

Selection `[3, 53, 534, 193]`, operation `ecf16319-406a-4bab-9e89-4f4000c83c38`. [Clipboard bytes](d69/native-clean/native.txt) · [Selected pixels](d69/native-clean/native-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ §J and colourless ** *|`.

Notification “Copied 193 characters”. Literal Hello👋 retained **yes**.

### d69 · Plain text (GNOME Text Editor)

Selection `[2, 93, 486, 188]`, operation `cd56c9a7-452b-422b-bf9a-07e837e08ad4`. [Clipboard bytes](d69/plain-only/plain.txt) · [Selected pixels](d69/plain-only/plain-region.png)

Nightly clipboard bytes match **True**, coordinates match **True**, and pixel hashes match **False**. [Nightly clipboard](d69/baseline/plain.txt)

### aurora-amd · Firefox 100%

Selection `[19, 18, 516, 274]`, operation `43f4fe70-4e5c-457b-9050-19ec43fce35d`. [Clipboard bytes](aurora-amd/candidate/firefox-100.txt) · [Selected pixels](aurora-amd/candidate/firefox-100-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ §J and colourless`.

Notification “Copied 185 characters”. Literal Hello👋 retained **yes**.

### aurora-amd · Firefox 150%

Selection `[31, 30, 768, 408]`, operation `44d6f4cb-eef1-4544-be9f-85d13c67b2aa`. [Clipboard bytes](aurora-amd/candidate/firefox-150.txt) · [Selected pixels](aurora-amd/candidate/firefox-150-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [J and colourless`.

Notification “Copied 187 characters”. Literal Hello👋 retained **yes**.

### aurora-amd · Native editor (KWrite)

Selection `[32, 99, 511, 220]`, operation `cb7fdbfd-ac63-4b4b-8176-76d59245ee50`. [Clipboard bytes](aurora-amd/candidate/native.txt) · [Selected pixels](aurora-amd/candidate/native-region.png)

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from 3% and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ MM and colourless @`.

Notification “Copied 192 characters”. Literal Hello👋 retained **yes**.

### aurora-amd · Plain text (KWrite)

Selection `[32, 99, 463, 187]`, operation `8dc6865f-d6c8-40f9-9c26-36b36df9c003`. [Clipboard bytes](aurora-amd/plain-only/plain.txt) · [Selected pixels](aurora-amd/plain-only/plain-region.png)

Nightly clipboard bytes match **True**, coordinates match **True**, and pixel hashes match **False**. [Nightly clipboard](aurora-amd/baseline/plain.txt)

