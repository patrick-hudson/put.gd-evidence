# Encrypted links says it needs one passed Test upload and link (#2118)

Live acceptance for put.gd-desktop PR #2125 (issue #2118). Both runs were on the builder's real desktop under `desktop_lock.py run`, shown on the display wall, and used a Cloudflare R2 bucket with public https r2.dev links.

- **Pre-existing destination.** The nightly 26.1124.6905 AppImage, from before the encrypted-page check existed (#2097), set up "R2 set up before" with keychain credentials and passed Test upload and link. This branch's build then started on the same configuration.
- **Fresh destination.** "R2 fresh", added by this build, with session credentials.

Hosts and builds:

- **KDE:** aurora-amd, Aurora Fedora 45 Plasma Wayland, 2026-11-28 03:15Z. Dev build of branch head 622195b18 (reads 0.0.0-dev.unknown; built from a git archive).
- **GNOME:** f44, Fedora 44 GNOME Wayland with the AppIndicator tray host active, 2026-11-28 02:53Z. Dev build of 1c4a85646. Its card and tray code are the same as 622195b18; the later commits change only answers and session rules.

Steps, the same on both desktops (see `kde-report.jsonl` and `gnome-report.jsonl`):

1. The fresh destination's card is opened through `ui.encryptedLinks show` on a fresh UI start. It is scrolled into view and says "Needs one passed Test upload and link first. The test checks that this destination opens encrypted pages in a browser over https." It shows its own **Test upload and link**. `mode on` is refused with the same words.
2. `putgd-cli upload --encrypt` to it is refused before sending with `encrypt_check_required` and the destination-named message (`cli-upload-encrypt.txt`).
3. The pre-existing destination's card says "Needs one more Test upload and link. Uploads work here, but the test hasn't checked that encrypted pages open in a browser over https."
4. In the editor, **Encrypt** routed to the pre-existing destination doesn't turn on. It shows the reason in the editor's message line.
5. The card's Test passes in about 3 s, and **On** is offered in place. On is saved, then the pre-existing destination's Test passes too.
6. The fresh destination's bucket prefix changes: "Needs Test upload and link again. The destination changed after its last encrypted-page check. Encrypted uploads here fail until it passes."
7. Tray **Capture region (encrypted)**, clicked through the app's own dbusmenu, starts no capture. It opens that card with Test focused. One real Space over the wall VNC starts the test, it passes, and On is available again.
8. Cleanup: both R2 test prefixes are empty, the keychain entry is cleared, the profiles are removed and the lock is released.

The pictures are cropped to the Encrypted links card, so the credentials card is left out, and annotated with put.gd's own editor (headless resident, the same build).
