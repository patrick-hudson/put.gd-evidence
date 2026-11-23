# Unhinged mode desktop acceptance

PR #1948, issue #1937. Tested 2026-11-23 UTC on the five physical Tier 1 desktops.

- Candidate version `26.1123.6699-dev+ga773c51e5947`
- Candidate head `a773c51e5947993b9b47c435528ab331a8229570`
- Candidate tree `941d212d6aba88311cd269955e631ccf7e09bb0a`
- [CI run 45111701983](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45111701983)
- AppImage SHA-256 `733059e6502adb1dcfca00c6d7f2a46439fa01e725b58697f3502795754d8421`
- Ubuntu 24.04 DEB SHA-256 `3219f508cc445a9e721fc05d8b8465d6797cac9fd4ed01ec56000777591df42a`

## Results

| Desktop | Build identity | Default off | Click saves on and off | Peak helper threads on / nproc | Input lost / worst gap on | OCR time off / on | Copied text identical | Quick redact on | Cleanup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f44 · Fedora 44 GNOME Wayland | Pass | Pass | Pass | 4 / 4 | 0 / 63.78 ms | 2.477 / 2.599 s | Pass | Pass · 105 suggestions | Pass |
| d69 · Debian 13 Plasma Wayland | Pass | Pass | Pass | Deferred / 4 | Deferred | Deferred | Deferred | Pass · 105 suggestions | Pass |
| k72 · Kubuntu 26.04.1 Plasma Wayland | Pass | Pass | Pass | Deferred / 4 | Deferred | Deferred | Deferred | Pass · 100 suggestions | Pass |
| m74 · Mint 22.3 Cinnamon X11 | Pass · AppImage and DEB | Pass | Pass | 4 / 4 | 0 / 114.59 ms | 3.753 / 4.190 s | Pass | Pass · 106 suggestions | Pass |
| aurora-amd · Aurora Fedora 45 Plasma Wayland | Pass | Pass | Pass | Deferred / 12 | Deferred | Deferred | Deferred | Pass · 128 suggestions | Pass |

At 05:01 UTC the quiet leases for d69, k72 and aurora-amd were still held for #1939, #1942 and #1941 respectively. Each received the Settings and a single functional editor check. The OCR timing, responsiveness and output-parity checks on those three desktops remain pending. The reported checks exposed no candidate defect requiring a nightly comparison. Mint's package was restored to published nightly `26.1122.6439-nightly` after the test.

## Method

Installed desktops were GNOME and Mutter 50.6 on f44, Plasma and KWin 6.3.6 on d69, 6.6.6 on k72, 6.8.2 on aurora-amd, and Cinnamon 6.6.9 with Muffin 6.6.3 on m74.

- Ran the AppImage directly under Cinnamon X11 and native GNOME or Plasma Wayland in a private resident session. `putgd-cli diagnostics --params-stdin` reported the exact build tree on every desktop. The session socket paths were 44 UTF-8 bytes. The per-host identity files include CPU model, CPU count, OS and session type.
- Opened Settings → Advanced through the resident. A fresh `settings.get` omitted `preferences.unhingedMode`. Real pointer clicks went through xdotool on Cinnamon and the lab's uinput agent on Wayland. The on click saved `true` in the accepted configuration and on disk. A real off click saved `false` or removed the key. The A and B images are cropped to the Advanced pane and annotated with ImageMagick.
- Used the synthetic `term4k-tokens.png` corpus, SHA-256 `c08f07314f71879ecb8040cade60081fe0cd4da1207df339d35801c75aa02c59`, fit to a 1920 × 1080 native desktop test window. The driver verified the visible synthetic frame before invoking `text.recognize` with `{"source":"region","copy":true}` and performing the recorded drag. Mint used the CI Ubuntu 24.04 DEB for this check. Its helper linked both Tesseract and `libgomp`. Both completed OCR pairs had `truncated=false`, and the exact clipboard bytes matched the result hash within each pair.
- Sampled the resident's OCR helper's `/proc/<pid>/status` at 200 ms intervals. Typed 40 synthetic lowercase letters and digits at 20 keys/s into a second GTK test window. The raw sample and key-receipt files use each host's monotonic clock. Each of the 40 keys arrived during the sampled helper lifetime on both runs on both measured desktops. Worst gap includes first key send to first receipt. Job time is the resident's `timings.totalMs`. Each host's on and off helper maxima were four threads.
- Opened the full 3840 × 2160 corpus via `editor.open`. With the preference on, `editor.inspect` confirmed the editor opened, and `editor.apply` with `{"op":"redactText","categories":["email","key"]}` returned created shapes. `editor.cancel` closed the editor without an upload.
- Initial harness retries addressed native Qt linkage for the mounted AppImage CLI, Aurora's canonical home path for KWin entry staging, GNOME's overview covering the fullscreen fixture, and an xdotool movement wait when the pointer was already at its target. These were corrected before the reported measurements. Product code and desktop packages were unchanged except for the requested candidate DEB swap and nightly restoration on Mint.
- Released owned desktop locks and quiet leases after cleanup. The release checks briefly showed the candidate's shutdown-only file-manager helper on some hosts. That process exited and each final cleanup check passed.

## Settings screenshots

| Desktop | Default off | On |
| --- | --- | --- |
| f44 | [A](f44/annotated-A.png) | [B](f44/annotated-B.png) |
| d69 | [A](d69/annotated-A.png) | [B](d69/annotated-B.png) |
| k72 | [A](k72/annotated-A.png) | [B](k72/annotated-B.png) |
| m74 | [A](m74/annotated-A.png) | [B](m74/annotated-B.png) |
| aurora-amd | [A](aurora-amd/annotated-A.png) | [B](aurora-amd/annotated-B.png) |
