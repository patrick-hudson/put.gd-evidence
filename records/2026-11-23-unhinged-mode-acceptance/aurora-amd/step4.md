# Aurora Copy text follow-up

PR #1948, issue #1937. Tested candidate `26.1123.6699-dev+ga773c51e5947` from [CI run 45111701983](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45111701983), head `a773c51e5947993b9b47c435528ab331a8229570` and tree `941d212d6aba88311cd269955e631ccf7e09bb0a`. The Aurora Fedora 45 physical desktop ran Plasma/KWin 6.8.2 on Wayland with 12 logical CPUs (Ryzen 5 PRO 8500GE). The coordinator waived d69 and k72 step 4. Their functional results remain in the [initial record](../README.md).

The native region check observed a peak of nine helper threads with the switch on, versus eight off. The full 3840 × 2160 file peaked at ten on versus six off. Both inputs exceeded eight process threads with the switch on and fell short of the original 12-thread target. The 10 ms repeat saw the same peaks. The on/off clipboard hashes matched within each input. Published nightly has no enabled-mode equivalent for the thread threshold.

| Desktop | Identity | Default off | Click saves on/off | Peak threads on / CPUs | Keys lost / worst gap on | OCR time off / on | Copied text identical | Quick redact | Cleanup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aurora-amd · Plasma Wayland | ✓ | ✓ | ✓ | 9 / 12 | 0 / 69.88 ms | 0.903 / 0.899 s | ✓ | ✓ | ✓ |

The row uses the native region run at 200 ms. Settings and Quick redact are from the original candidate acceptance run.

## Measurements

| Input and sampling interval | Switch | Peak Threads | OCR job time | Truncated | Keys lost | Worst input gap | Receipts within sampled helper lifetime | Clipboard SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Native region, 200 ms](region-ocr-on.json) | On | 9 | 0.899 s | false | 0 | 69.88 ms | 11 / 40 | `f82c5e124eda56b8c1f05f00e1e60f0fc90b54621db980a04bd403083c590291` |
| [Native region, 200 ms](region-ocr-off.json) | Off | 8 | 0.903 s | false | 0 | 64.10 ms | 11 / 40 | `f82c5e124eda56b8c1f05f00e1e60f0fc90b54621db980a04bd403083c590291` |
| [Full 4K file, 200 ms](ocr-on.json) | On | 10 | 1.183 s | false | 0 | 50.42 ms | 20 / 40 | `abbeb1067d623e000452aa0675a33d1fdd3cbe28963c9fae6c317a233d3276b3` |
| [Full 4K file, 200 ms](ocr-off.json) | Off | 6 | 1.544 s | false | 0 | 50.60 ms | 28 / 40 | `abbeb1067d623e000452aa0675a33d1fdd3cbe28963c9fae6c317a233d3276b3` |
| [Native region, 10 ms](10ms/ocr-on.json) | On | 9 | 0.849 s | false | 0 | 64.55 ms | 15 / 40 | `f82c5e124eda56b8c1f05f00e1e60f0fc90b54621db980a04bd403083c590291` |
| [Native region, 10 ms](10ms/ocr-off.json) | Off | 8 | 0.890 s | false | 0 | 83.74 ms | 16 / 40 | `f82c5e124eda56b8c1f05f00e1e60f0fc90b54621db980a04bd403083c590291` |
| [Full 4K file, 10 ms](10ms/ocr-file-on.json) | On | 10 | 1.208 s | false | 0 | 51.50 ms | 24 / 40 | `abbeb1067d623e000452aa0675a33d1fdd3cbe28963c9fae6c317a233d3276b3` |
| [Full 4K file, 10 ms](10ms/ocr-file-off.json) | Off | 6 | 1.557 s | false | 0 | 50.86 ms | 31 / 40 | `abbeb1067d623e000452aa0675a33d1fdd3cbe28963c9fae6c317a233d3276b3` |

## Method

- The AppImage SHA-256 was `733059e6502adb1dcfca00c6d7f2a46439fa01e725b58697f3502795754d8421`. Each private resident used a 44-byte session socket, and the mounted package's `putgd-cli diagnostics --params-stdin` returned the expected tree before recognition.
- The synthetic `term4k-tokens.png` fixture SHA-256 was `c08f07314f71879ecb8040cade60081fe0cd4da1207df339d35801c75aa02c59`. The driver verified the fixture on Aurora's native 1920 × 1080 output and selected the same region with real uinput. The supplemental file run passed the original 3840 × 2160 file to the same `text.recognize` method. Both methods requested an actual clipboard copy and hashed the exact copied bytes.
- The driver read `Threads` from the helper's `/proc/<pid>/status`. That is a process thread count, which can include threads beyond Tesseract workers. The 10 ms repeat sampled the resident's own OCR child without walking the full process table. Job time is the resident's `timings.totalMs`.
- Each 40-key burst began while the OCR helper was active. The observed jobs were shorter than the roughly two-second burst, so some keys arrived after OCR finished. The receipt counts and raw monotonic timestamps record that overlap. Worst gap includes the initial send-to-receipt gap.
- Two setup attempts stopped before capture because the visual check could not confirm the fixture. Launching the resident first, then raising and clicking the verified fullscreen test window corrected the setup. The failed attempts and cleanup receipts are retained alongside the data.
- All measured pairs ran under both owned leases. The driver quit the exact resident, removed the KWin entries it mirrored and the private run directories, and released both leases. See the [native region cleanup](region-step4-cleanup.txt), [4K file cleanup](step4-cleanup.txt) and [10 ms repeat cleanup](10ms/step4-cleanup.txt).
