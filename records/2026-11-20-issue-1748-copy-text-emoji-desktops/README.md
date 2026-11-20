# Desktop acceptance for Copy text emoji in PR #1751

The physical desktop campaign tested the packages from CI run 44831121751. The packaged build reports commit `224387ee1a1a3aba9d812ae595dda95f44310e20` and tree `b30c4489bcd77165cfa0358e5d501f233896a6b2`. That tree is byte-identical to PR head `fb6155b4b2c1a79a8530bf65c1a415be6c804fdb`. The candidate version is `26.1120.5923-dev+g224387ee1a1a`. The published `v26.1120.5875-nightly` at `779e2517303d8fcb08aca99840589e728d9b98ff` supplied the plain-text control. No binaries were compiled for this campaign. [CI run](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/44831121751)

Every valid case was run with the native desktop session, `Ctrl+Shift+9` and an actual drag in the Copy text region selector. Selected rectangles are in each receipt. Clipboard bytes were read independently with `wl-paste -n` or `xclip`. The notification was captured from the desktop notification bus. The selected Firefox 100% OCR helper per host was observed with the #1428 process-connector watcher and reports kernel `VmHWM` in KiB.

Firefox coffee is the documented colour-core exception and appears in the per-line results outside the emoji totals. The totals cover 12 expected Firefox emoji and 13 expected native editor emoji. The four excluded glyphs on line 6 are checked separately. “Words intact” means the target words remain in order, with additional OCR junk recorded in each line and in the exact clipboard files. “Glue” checks the literal sequence `Hello👋`.

## Test packages

| Host | OS and desktop | Firefox | CI artifact | SHA-256 |
|---|---|---|---|---|
| f44 | Fedora Linux 44 (Workstation Edition) · GNOME Shell 50.6 · wayland | Mozilla Firefox 158.0.1 | `release-native-fedora44` · `putgd-26.1120.5923~dev+g224387ee1a1a-1.fc44.x86_64.rpm` | `26955d358f02abecf1991d9813b73c0a32b89a216e15b37d9ec7b9e08668bfce` |
| k72 | Ubuntu 26.04.1 LTS · kwin 6.6.6 · wayland | Mozilla Firefox 159.0.1 | `release-native-ubuntu26.04` · `putgd_26.1120.5923~dev+g224387ee1a1a_amd64.deb` | `1ec093036819bcac6cd296c863e2319eb8e249eaaa86403e39a10a32c45484e7` |
| m74 | Linux Mint 22.3 · Cinnamon 6.6.9 · x11 | Mozilla Firefox 158.0 | `release-native-ubuntu24.04` · `putgd_26.1120.5923~dev+g224387ee1a1a_amd64.deb` | `205eca1e5b0b34def74151fff7e993a2173b65e61325f1e4491bc2fc94d551f7` |
| d69 | Debian GNU/Linux 13 (trixie) · kwin 6.3.6 · wayland | Mozilla Firefox 153.5.0esr | `release-native-debian13` · `putgd_26.1120.5923~dev+g224387ee1a1a_amd64.deb` | `4ff93cb09308b18c6319f99f82eb9281654caaca8ac214d4f6b013aeaf8c4b6f` |
| aurora-amd | Aurora (Version: testing-45.20261101.2) · kwin 6.8.2 · wayland | Mozilla Firefox 160.0.1 | `release-appimage` · `putgd-26.1120.5923-dev+g224387ee1a1a-x86_64.AppImage` | `ef83f78197b82a12eb42b2498e30c6ff92b89e8fd81a745545561842abe51bcc` |

The Fedora session was restarted once under its lease to load the packaged GNOME extension. The lab tools came from origin/nightly at `6900ba90d7bdd873134253d3cc313dab38b95412`. The two figures combine verified desktop crops from the same Copy text actions. The rectangles around the laughing faces were added with put.gd’s editor on m74.

Debian’s KWrite displayed missing or monochrome glyphs for the emoji fixture. The installed GNOME Text Editor rendered the color emoji in the same Plasma Wayland session and supplied the reported native emoji and plain-text cells. An early GTK selection included adjacent app chrome, so the scored GTK selection was repeated inside the verified client rectangle. The KWrite diagnostic and control are retained under the Debian host directory.

## Results

| Host | Surface | Emoji right / wrong / missed | Words intact | Hello glue | Plain exact | Notification | Helper peak / exit |
|---|---|---|---|---|---|---|---|
| f44 | Firefox 100% | 9/1/2 | yes | yes | — | Copied 183 characters | 75,288 KiB / 0 |
| f44 | Firefox 150% | 8/0/4 | yes | yes | — | Copied 182 characters | — |
| f44 | Native editor (GNOME Text Editor) | 11/0/2 | yes | yes | — | Copied 188 characters | — |
| f44 | Plain text | — | yes | — | yes | Copied 185 characters | — |
| k72 | Firefox 100% | 10/0/2 | no | yes | — | Copied 182 characters | 76,528 KiB / 0 |
| k72 | Firefox 150% | 9/0/3 | yes | yes | — | Copied 184 characters | — |
| k72 | Native editor (KWrite) | 8/0/5 | no | no | — | Copied 190 characters | — |
| k72 | Plain text | — | yes | — | no | Copied 186 characters | — |
| m74 | Firefox 100% | 10/0/2 | no | yes | — | Copied 182 characters | 75,988 KiB / 0 |
| m74 | Firefox 150% | 9/0/3 | yes | yes | — | Copied 187 characters | — |
| m74 | Native editor (xed) | 11/0/2 | no | yes | — | Copied 184 characters | — |
| m74 | Plain text | — | yes | — | no | Copied 186 characters | — |
| d69 | Firefox 100% | 10/0/2 | no | yes | — | Copied 179 characters | 75,464 KiB / 0 |
| d69 | Firefox 150% | 9/0/3 | yes | yes | — | Copied 187 characters | — |
| d69 | Native editor (GNOME Text Editor) | 10/0/3 | yes | yes | — | Copied 191 characters | — |
| d69 | Plain text | — | yes | — | no | Copied 186 characters | — |
| aurora-amd | Firefox 100% | 0/0/12 | no | no | — | Copied 167 characters | 60,076 KiB / 0 |
| aurora-amd | Firefox 150% | 0/0/12 | no | no | — | Copied 174 characters | — |
| aurora-amd | Native editor (KWrite) | 10/0/3 | yes | yes | — | Copied 190 characters | — |
| aurora-amd | Plain text | — | no | — | no | Copied 186 characters | — |

## Reproduction

Open the supplied emoji HTML in the recorded Firefox version. At the specified zoom, trigger Copy text from region and drag the receipt coordinates from upper left to lower right. Read the clipboard after the Copy text notification. To reproduce the native cases, open the supplied text fixture in the recorded editor at its default font size and select the receipt coordinates.

The Fedora Firefox 100% line 5 changes the England flag to Guernsey. On Aurora, both Firefox zooms omit every tested emoji. The screenshot shows a dimmed fixture, and clicking the focused test page raised a sampled background pixel to RGB (97, 97, 97) at both zooms. Both clipboard results were identical across the focus retry.

## Evidence images

- [Fedora GNOME Firefox selection and pasted result](f44-firefox-150-annotated.png)
- [Kubuntu Plasma Firefox selection and pasted result](k72-firefox-150-annotated.png)

## Exact observations

### f44 · Firefox 100%

Selection `[18, 20, 487, 292]`. Operation `bec1edab-1edd-4637-ad3d-272cde51c01a`. Exact clipboard bytes in [firefox-100.txt](f44/firefox-pictures/firefox-100.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂so much 👍🏽`.
4. 🚀 missed, 🔥 right. Words intact yes. Clipboard line `Ship it before Friday 🔥`.
5. 👋 right, 🇬🇧 right, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 wrong → 🇬🇬, 💯 missed. Words intact yes. Clipboard line `Hello👋 from 🇬🇧 and 🇬🇬 with 2`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

The desktop showed “Copied 183 characters”. The literal sequence `Hello👋` was retained.

### f44 · Firefox 150%

Selection `[31, 34, 725, 437]`. Operation `5d393e67-ea29-4713-95b3-b09750e42f27`. Exact clipboard bytes in [firefox-150.txt](f44/firefox-pictures/firefox-150.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this😂😂 so much 👍🏽`.
4. 🚀 missed, 🔥 right. Words intact yes. Clipboard line `Ship it before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello👋 from and with 2`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ {J and colourless`.

The desktop showed “Copied 182 characters”. The literal sequence `Hello👋` was retained.

### f44 · Native editor (GNOME Text Editor)

Selection `[2, 86, 528, 231]`. Operation `575c8a57-078f-42df-8476-8820b6324727`. Exact clipboard bytes in [native.txt](f44/relogin/native.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 missed, 🔥 right. Words intact yes. Clipboard line `Ship it before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 right, 💯 right. Words intact yes. Clipboard line `Hello👋 from and 🏴󠁧󠁢󠁥󠁮󠁧󠁿 with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ §J and colourless **`.

The desktop showed “Copied 188 characters”. The literal sequence `Hello👋` was retained.

### f44 · Plain text

Selection `[2, 86, 891, 187]`. The result matched the input file byte for byte. Exact clipboard bytes in [plain.txt](f44/relogin/plain.txt).

### k72 · Firefox 100%

Selection `[18, 21, 487, 298]`. Operation `97f46da6-4ce9-4d22-93c7-5b23de3a1587`. Exact clipboard bytes in [firefox-100.txt](k72/candidate/firefox-100.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 right. Words intact yes. Clipboard line `Hello👋 from and with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ (J and colourless`.

The desktop showed “Copied 182 characters”. The literal sequence `Hello👋` was retained.

### k72 · Firefox 150%

Selection `[31, 35, 724, 443]`. Operation `e96f092b-91c4-4b28-b746-c6c695504108`. Exact clipboard bytes in [firefox-150.txt](k72/candidate/firefox-150.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello👋 from and with`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [ij and colourless`.

The desktop showed “Copied 184 characters”. The literal sequence `Hello👋` was retained.

### k72 · Native editor (KWrite)

Selection `[30, 97, 495, 211]`. Operation `3ff33ecf-fe7f-470c-91a1-4cb6eaa4d80e`. Exact clipboard bytes in [native.txt](k72/candidate/native.txt).

1. 🎉 right. Words intact no. Clipboard line `fbreat job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 missed, 😂 missed, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this @@& so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello®👋 from and + with @`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless ++`.

The desktop showed “Copied 190 characters”. The literal sequence `Hello👋` was absent.

### k72 · Plain text

Selection `[30, 97, 462, 179]`. The exact-region nightly comparison yielded same bytes · same region. Exact clipboard bytes in [plain.txt](k72/candidate/plain.txt).

Baseline clipboard [plain.txt](k72/baseline/plain.txt).

### m74 · Firefox 100%

Selection `[18, 21, 487, 298]`. Operation `e46e4fad-3474-4fda-a50a-828f548ff27f`. Exact clipboard bytes in [firefox-100.txt](m74/candidate/firefox-100.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 right. Words intact yes. Clipboard line `Hello👋 from and with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ (J and colourless`.

The desktop showed “Copied 182 characters”. The literal sequence `Hello👋` was retained.

### m74 · Firefox 150%

Selection `[31, 35, 724, 443]`. Operation `dc6685d6-0b35-44fb-9013-af3c7935ae33`. Exact clipboard bytes in [firefox-150.txt](m74/candidate/firefox-150.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello👋 from 2% and with`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [fj and colourless`.

The desktop showed “Copied 187 characters”. The literal sequence `Hello👋` was retained.

### m74 · Native editor (xed)

Selection `[0, 130, 457, 250]`. Operation `af877214-aff0-4efd-952e-2557338a49e0`. Exact clipboard bytes in [native.txt](m74/candidate/native.txt).

1. 🎉 right. Words intact no. Clipboard line `reat job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 right. Words intact yes. Clipboard line `Hello👋 from and with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless ++`.

The desktop showed “Copied 184 characters”. The literal sequence `Hello👋` was retained.

### m74 · Plain text

Selection `[0, 130, 428, 216]`. The exact-region nightly comparison yielded same bytes · same region. Exact clipboard bytes in [plain.txt](m74/candidate/plain.txt).

Baseline clipboard [plain.txt](m74/baseline-exact-retry/plain.txt).

### d69 · Firefox 100%

Selection `[18, 21, 487, 298]`. Operation `c16faaeb-b801-4e7e-9507-09355fa77a05`. Exact clipboard bytes in [firefox-100.txt](d69/gtk/firefox-100.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact no. Clipboard line `I ❤️ this 😂😂 much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 right. Words intact yes. Clipboard line `Hello👋 from and with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

The desktop showed “Copied 179 characters”. The literal sequence `Hello👋` was retained.

### d69 · Firefox 150%

Selection `[31, 35, 724, 443]`. Operation `e4bc7982-22e0-42dd-8534-5899522d061c`. Exact clipboard bytes in [firefox-150.txt](d69/candidate/firefox-150.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee =`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello👋 from 2 and with`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ [ijJ and colourless`.

The desktop showed “Copied 187 characters”. The literal sequence `Hello👋` was retained.

### d69 · Native editor (GNOME Text Editor)

Selection `[613, 311, 1139, 451]`. Operation `ef9f8d3a-cf57-4892-b801-baeb304ec6e8`. Exact clipboard bytes in [native.txt](d69/gtk-cropped/native.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 right, 🔥 right. Words intact yes. Clipboard line `Ship it 🚀 before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello👋 from and with @`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ §J and colourless ** *|`.

The desktop showed “Copied 191 characters”. The literal sequence `Hello👋` was retained.

### d69 · Plain text

Selection `[2, 53, 486, 148]`. The exact-region nightly comparison yielded same bytes · same region. Exact clipboard bytes in [plain.txt](d69/gtk-cropped/plain.txt).

Baseline clipboard [plain.txt](d69/baseline-gtk/plain.txt).

### aurora-amd · Firefox 100%

Selection `[19, 22, 533, 277]`. Operation `6e5dbd35-2f11-4038-912c-b48979058660`. Exact clipboard bytes in [firefox-100.txt](aurora-amd/firefox-focus/firefox-100.txt).

1. 🎉 missed. Words intact yes. Clipboard line `Great job on the release thanks!`.
2. 👋 missed, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow and bring coffee`.
3. ❤️ missed, 😂 missed, 😂 missed, 👍🏽 missed. Words intact no. Clipboard line `|W this so much`.
4. 🚀 missed, 🔥 missed. Words intact yes. Clipboard line `Ship it # before Friday`.
5. 👋 missed, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello®) from and with`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

The desktop showed “Copied 167 characters”. The literal sequence `Hello👋` was absent.

### aurora-amd · Firefox 150%

Selection `[31, 26, 792, 411]`. Operation `c92f2e4a-b451-4797-8e18-e478048d1067`. Exact clipboard bytes in [firefox-150.txt](aurora-amd/firefox-focus/firefox-150.txt).

1. 🎉 missed. Words intact yes. Clipboard line `Great job on the release & thanks!`.
2. 👋 missed, ☕ missed (Twemoji exception). Words intact yes. Clipboard line `See you tomorrow and bring coffee =`.
3. ❤️ missed, 😂 missed, 😂 missed, 👍🏽 missed. Words intact no. Clipboard line `this SS so much`.
4. 🚀 missed, 🔥 missed. Words intact yes. Clipboard line `Ship it # before Friday ia`.
5. 👋 missed, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 missed. Words intact yes. Clipboard line `Hello®) from and with`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ and colourless`.

The desktop showed “Copied 174 characters”. The literal sequence `Hello👋` was absent.

### aurora-amd · Native editor (KWrite)

Selection `[32, 99, 511, 223]`. Operation `8dee175a-595e-4e69-aacd-10a6e0ca79fb`. Exact clipboard bytes in [native.txt](aurora-amd/candidate/native.txt).

1. 🎉 right. Words intact yes. Clipboard line `Great job on the release 🎉 thanks!`.
2. 👋 right, ☕ right. Words intact yes. Clipboard line `See you tomorrow 👋 and bring coffee ☕`.
3. ❤️ right, 😂 right, 😂 right, 👍🏽 right. Words intact yes. Clipboard line `I ❤️ this 😂😂 so much 👍🏽`.
4. 🚀 missed, 🔥 right. Words intact yes. Clipboard line `Ship it # before Friday 🔥`.
5. 👋 right, 🇬🇧 missed, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 missed, 💯 right. Words intact yes. Clipboard line `Hello👋 from 3% and with 💯`.
6. 🔴 absent (expected), 1️⃣ absent (expected), 👀 absent (expected), 💀 absent (expected). Words intact yes. Clipboard line `Plain shapes stay out @ MM and colourless @`.

The desktop showed “Copied 190 characters”. The literal sequence `Hello👋` was retained.

### aurora-amd · Plain text

Selection `[32, 99, 463, 187]`. The exact-region nightly comparison yielded same bytes · same region. Exact clipboard bytes in [plain.txt](aurora-amd/candidate/plain.txt).

Baseline clipboard [plain.txt](aurora-amd/baseline/plain.txt).

