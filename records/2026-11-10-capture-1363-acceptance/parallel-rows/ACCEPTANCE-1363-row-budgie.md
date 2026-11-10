# Budgie acceptance row — PR #1368

Result: **PASS a–e**; f is the requested observation. Tested 2026-11-10 06:50–06:55 UTC.

Fresh guest **ab9**, host **d69 / 192.168.68.69**, Fedora45 Budgie **10.10.3-3.fc45**, **labwc0.20.2-2.fc45**, native Wayland. Two connected heads: Virtual-1 **1280×800 at1024,0**, Virtual-2 **1024×768 at0,0**. Run ID `6113db71-532a-417e-a71a-d71b66527514`; exact QEMU PID1853957, KVM acceleration. Both heads stayed visible on the wall at6090/6091 during testing. No physical-desktop session was used; the owner's d69 demos and the unrelated bc8 guest were untouched.

Package: CI run **42763770262**, `release-appimage`, `putgd-26.1110.4498-dev+g0cf6a17ae4f2-x86_64.AppImage`, build **4498**. SHA256 `f9239c5b1e75a4559eccfe3cea0a331b211b133cdc7cd6d83524c93e0d2007ee` matches the workstation's downloaded artifact. PR head `13570fca94df85b799755494d4914fb7009f7e4d`; running PR merge commit `0cf6a17ae4f2fbac36fbaa2e4d64a4e6ceb704bf`, tree `1e2d35a411dc2f281b3c3414c87503a62476eba8`, identical to the head. Actual loaded **Qt6.12.0**, verified by mapped AppImage QtCore path and its `qVersion` symbol. No builder compilation.

| Item | Result | Observed behavior |
| --- | --- | --- |
| a | **PASS,15/15** | Full checks.py sequence: both monitor sizes;2304×800 desktop; empty repeat refusal;300×200 region and exact repeat; moved-layout refusal/restoration; visible countdown absent from saved pixels; delayed region; click/API cancellation; locked-countdown refusal; capture after unlock. |
| b | **PASS** | GUI-bound Repeat `Ctrl+Alt+R` and Monitor `Ctrl+Alt+M`; both report **bound**, backend `labwc-bridge`, effective keys confirmed in capabilities. Real repeat key before a region returned `repeat_unavailable` and “There is no region to repeat yet. Capture a region first.” Real monitor key captured the pointer's1024×768 head. After a real shortcut region, real Repeat returned identical300×200 pixels. |
| c | **PASS** | Added Capture monitor exception in Settings: local only. With a different, synthetic unavailable upload default, Monitor still completed locally with empty destination profileId. Settings/default restored afterward; no upload or user-object changes. |
| d | **PASS** | Selected3seconds in window-button menu; window Desktop capture and tray Monitor capture both showed countdowns. Pixel comparisons: saved vs clean0.0 and saved vs countdown58.95, for each. A further3second tray countdown was clicked to cancel: `cancelled=true`, error `cancelled`, `items=[]`, no file produced. |
| e | **PASS** | With GUI delay3 selected, plain `Ctrl+Shift+1` showed the live selector immediately, saved300×200 region1.26seconds after release, and showed no countdown. Repeat via real key returned identical pixels. |
| f | **OBSERVATION** | With gtklock visibly up, immediate CLI Desktop capture **completed with a picture of the lock screen** on both heads, not a refusal. Locked witness, returned capture, operation and unlocked witness retained. No fix attempted. |

No product failure. Preserved harness attempts and corrected commands in `harness-attempts.log`: first install ran before launch readiness; removing the no-output banner shifted the shortcut rows and one initial binding hit Window instead of Repeat. Saved the wrong-row screenshot, corrected coordinates, then reran binding and real-key proofs successfully. The original driver is unchanged.

Evidence: https://github.com/patrick-hudson/put.gd-evidence/tree/d3858eceaa0d163522ce5859ee80d0f79605403f/records/2026-11-10-1363-budgie-ab9

Pictures drawn with put.gd's production editor session methods, cropped to its own surfaces, exact4498 build:

- **Budgie/labwc native shortcut bridge:** Repeat last region and Capture monitor bound, both rows boxed. https://raw.githubusercontent.com/patrick-hudson/put.gd-evidence/d3858eceaa0d163522ce5859ee80d0f79605403f/records/2026-11-10-1363-budgie-ab9/budgie-bound-shortcuts.png
- **Budgie tray-started delayed capture:** visible3second countdown, click-to-cancel surface boxed. https://raw.githubusercontent.com/patrick-hudson/put.gd-evidence/d3858eceaa0d163522ce5859ee80d0f79605403f/records/2026-11-10-1363-budgie-ab9/budgie-tray-countdown.png

Cleanup: stopped ab9 via lab.py reset; verified PID1853957 and launch PID1853670 absent. Stopped `putgd-vm-1363-ab9.service`, removed only its two wall entries. Exported and SHA256-verified84 evidence files before guarded cleanup; dry-run then cleanup completed and removed only ab9's `disk.qcow2`. Receipt `overlay-cleanup.json` published. Deleted exact owned `/tmp/ab9-*` helper files by name; retained host evidence, run identities and immutable golden. No test process of this row remains on d69. No PR, source branch, ACCEPTANCE-1363.md or earlier STATUS.md line edited.
