# Script check timing rows (#1981, PR #1986)

One JSON line per helper job, from `time.py` in the kit described in the PR: each image was read by its own `redact_fuzz_driver` process with the script check off (`detect: false`) and then on, so `driverPeakRssKiB` is that job's helper peak. The named images (latin, latin4k, ru, zh, ru4k, zh4k) ran five times per mode; the 176 `latin176` captures (#1428's ordinary captures) once per mode.

- `final/`: CI run 45320004396, PR head `4aad3e35c75890fda8ed5caa125b9e7f8fd34f25`, merge `a372952fe573dea61d29843875d0ff28d34d0c07` (tree `ec5e4ac249afd3524d8f61403ee52fa43e94f123`). aurora-amd: the AppImage, all 412 jobs. m74, f44, k72 and d69: the native packages, the named images only (60 jobs each).
- `earlier/`: CI run 45310837809, PR head `78d7987e2`, merge `9b8f9cc663fd100ca2da32aff9fb3c69dd585ad2` (tree `6528e671506c0cf8b22c1cf7ac8b92f9083271b8`), native packages, all 412 jobs. On that build a memory gate could skip the rest-of-page reread on large Chinese pages, so its non-Latin "on" times are low; its Latin rows (nothing triggered) are what the docs' Latin ratios for the native hosts come from.

The changes after `4aad3e35c` touch only which confident lines the rest-of-page pass replaces and which first words Quick redact keeps; their effect is in the PR's final sweep and fuzz.
