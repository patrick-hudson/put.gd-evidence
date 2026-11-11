# Proton uploads on four desktops after the helper speed-up (#1400)

Desktop acceptance of put.gd-desktop #1400 ("upload with a share link in about 2 seconds instead of 16"),
run on 2026-11-10 (local) / 2026-11-11 (UTC) on four physical lab desktops against the live Proton test
account. One script ran the same 15 cases on each desktop and timed every upload.

## Result

| Host | Desktop | Package | Passed |
| --- | --- | --- | --- |
| d69 | Debian 13, KDE Plasma on Wayland | debian13 .deb | 15 of 15 |
| k72 | Kubuntu 26.04, KDE Plasma on Wayland | ubuntu26.04 .deb | 15 of 15 |
| m74 | Linux Mint 22.3, Cinnamon on X11 | AppImage | 15 of 15 |
| f44 | Fedora 44, GNOME 50 on Wayland | AppImage | 9 of 15 |

Every Proton case that could run passed on all four desktops. The six cases that did not pass on f44 are
its screenshot cases: GNOME refused each capture in about 0.1 s with `gnome_extension_missing`, because an
unpacked AppImage has no put.gd GNOME Shell extension. No capture reached the upload stage there, so GNOME
screenshot-to-Proton is not covered by this record.

No Proton helper process was left running after any case on any desktop, no `proton_*` error or
`proton_account_busy` appears in any log, and every lock was released.

## Time for each upload

Seconds from invoking the action until the share link was ready, unless the cell says otherwise.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| `file-64k` | 5.39 s | 5.56 s | 5.3 s | 4.97 s |
| `text-small` | 4.03 s | 3.78 s | 5.67 s | 4.63 s |
| `after-cancel` | 3.95 s | 3.81 s | 5.06 s | 3.68 s |
| `file-1m` | 6.59 s | 7.84 s | 11.74 s | 13.9 s |
| `file-8m` | 9.26 s | 7.95 s | 10.7 s | 8.42 s |
| `batch-3` | 12.45 s | 16.89 s | 11.29 s | 10.33 s |
| `back-to-back` | 5.9 s, 11.41 s | 9.02 s, 12.7 s | 5.52 s, 9.16 s | 8.82 s, 12.21 s |
| `desktop-now` | 7.22 s | 6.76 s | 8.88 s | not testable (`gnome_extension_missing`) |
| `desktop-delay3` | 4.91 s after capture | 4.5 s after capture | 5.27 s after capture | not testable (`gnome_extension_missing`) |
| `desktop-delay3-again` | 7.27 s after capture | 6.08 s after capture | 8.27 s after capture | not testable (`gnome_extension_missing`) |
| `monitor-delay3` | 6.59 s after capture | 4.69 s after capture | 7.79 s after capture | not testable (`gnome_extension_missing`) |
| `cancel-countdown` | cancelled; helper gone in 0.01 s | cancelled; helper gone in 0.01 s | cancelled; helper gone in 0.01 s | not testable (`gnome_extension_missing`) |
| `history-picture` | 5.69 s | 8.78 s | 5.79 s | not testable (`gnome_extension_missing`) |
| `link-answers` | HTTP 200 | HTTP 200 | HTTP 200 | HTTP 200 |
| `revoke-all` | 15 links, 2.54–4.85 s each | 15 links, 2.49–4.82 s each | 15 links, 2.67–4.33 s each | 10 links, 2.5–3.82 s each |

- `file-64k` is the first upload after the app starts: it includes the one-time hash of the helper binary.
- The file cases have no lead time, so the helper starts cold when the upload is invoked.
- The delayed captures show the wait after the picture was taken. On each desktop the helper was seen
  starting during the countdown, 0.04–0.11 s after the action was invoked.
- A full-desktop PNG was 230–540 KB here, over the 128 KiB single-request limit, so its upload stage
  (five sequential SDK requests plus the transfer) took 2.4–4 s and is most of the wait after capture.
- `cancel-countdown` cancels a capture during its 5 s countdown; the helper started for it ended by itself.
- `revoke-all` revokes every link the run made, one helper per link.

## What was tested

- Build: `26.1110.4619-dev+g96bc599dfb83`, the CI packages of pull request #1400's final head (run 42923021470). Their
  source is identical to the merged nightly head `81b136264` outside `docs/`.
- The app ran on each builder's live desktop session with a private profile folder, under that builder's
  desktop lock and Proton lock, uploading synthetic files and its own screenshots to the builder's
  isolated lab folder. On Plasma the script wrote a temporary desktop entry so KWin allowed screenshots,
  and removed it afterwards.
- `proton_accept.py` is the test; `run_accept.sh` is the wrapper that takes the locks, runs it and
  releases them. Each host folder holds `results.json` (per-case states and phase times), `summary.txt`
  and, where a capture worked, `history.png`: the app's own screenshot of its History window listing the
  run's uploads as "Shared link".
- No share link is recorded anywhere in this record.

## Not covered

- Screenshot uploads on GNOME (see above), and Aurora.
- Region and window selection with a real pointer drag; the countdown stood in for the selection time.
- Memory and resource measurements, and the installed-package audits of release gate P6 (#1399).

## Notes

- The m74 picture shows a "Local save failed" desktop notification. It is not from this run: the run's
  app logged the 13 notifications it showed, all "Upload complete", its database holds no failed local
  save, and all 15 local copies exist. Which process raised it was not established.
- f44 logged `clipboard_unavailable` for link auto-copy eight times, another effect of the missing GNOME
  setup. Uploads and links were unaffected.
