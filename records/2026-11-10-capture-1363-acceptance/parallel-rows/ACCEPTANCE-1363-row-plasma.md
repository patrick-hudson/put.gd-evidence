# Plasma Wayland acceptance — PASS

Fresh guest **ap6** on **k72 / 192.168.68.72**, KVM; run965434e2-8722-48e4-8a4c-359b74ed16e4. Kubuntu26.04.1, native Plasma/KWin6.6.6 Wayland (seat0 session1, active), two real outputs1280×800+0+0 and1024×768+1280+0. Run2026-11-10 approximately06:49–07:00UTC. Did not use ak4 or the physical desktop.

Really installed CI42763770262 Ubuntu26.04 DEB: `putgd_26.1110.4498~dev+g0cf6a17ae4f2_amd64.deb`; SHA256`c5b7adc4951930e994eee2c29b9ff9b7ade767d4295c9adbb32790c8eb41ecbd`. PR head`13570fca94df85b799755494d4914fb7009f7e4d`, CI merge`0cf6a17ae4f2fbac36fbaa2e4d64a4e6ceb704bf`, matching source tree`1e2d35a411dc2f281b3c3414c87503a62476eba8`, build4498. Running `/usr/bin/putgd`; actual mapped QtCore **6.10.2**, distro dynamic library `/usr/lib/x86_64-linux-gnu/libQt6Core.so.6.10.2`. No compile on any machine.

| Item | Result | Observed |
| --- | --- | --- |
| a | PASS | Supplied checks.py all15 checks, zero failures: head0/head1 monitor sizes, whole desk, repeat/refusals/layout restoration, visible and omitted countdown, delayed region, both cancel paths, lock refusal and recovery. |
| b | PASS | Settings rows bind Ctrl+Alt+M and Ctrl+Alt+R through KGlobalAccel, both actual bindings reported bound. Real M with pointer on head1 saved1024×768. Real R before a region displayed “There is no region to repeat yet. Capture a region first.” Real shortcut region300×200 then R returned identical pixels (mean difference0.0). |
| c | PASS | Added Capture monitor local-output exception in Settings. With default set to an unavailable synthetic upload route, real M saved locally with empty profile and local_only status. Restored default afterward. |
| d | PASS | Selected3 seconds through window monitor button context submenu; tray reports3 seconds. Tray desktop and window monitor both displayed countdown. Saved capture pill area matches clean screen exactly (difference0.0). Clicked a tray countdown to cancel; archive file list identical before/after, no new file. |
| e | PASS | GUI delay still3 seconds, real Ctrl+Shift+1 region capture stayed immediate; new result present0.812 seconds after release. |

Evidence: https://github.com/patrick-hudson/put.gd-evidence/tree/3e66a18d6da6e1fc2e80c51423b0b87d874ce47a/records/2026-11-10-plasma-1363-ap6

Annotated using installed put.gd's own editor through session methods:

- **Bound Shortcuts:** Repeat last region Ctrl+Alt+R and Capture monitor Ctrl+Alt+M, both boxed. https://raw.githubusercontent.com/patrick-hudson/put.gd-evidence/3e66a18d6da6e1fc2e80c51423b0b87d874ce47a/records/2026-11-10-plasma-1363-ap6/plasma-bound-shortcuts.png
- **Tray delay:** tray menu set to3 seconds beside the countdown it started; box and arrow mark the changed surfaces. https://raw.githubusercontent.com/patrick-hudson/put.gd-evidence/3e66a18d6da6e1fc2e80c51423b0b87d874ce47a/records/2026-11-10-plasma-1363-ap6/plasma-tray-countdown.png

No product failure or fix. Preserved harness corrections: early install before SSH readiness, exact-PID duplicate launcher cancellation before VM boot, corrected shifted shortcut-row click, and early window screenshots before countdown mapping. Final witnesses supersede those attempts without deleting them.

Cleanup completed07:00:18UTC: resident quit, guest stopped, guarded overlay cleanup completed; tunnel `putgd-vm-1363-ap6.service` inactive; both group1363-ap6 wall entries removed. Final sweep shows ownedProcessesRemaining=[], qemuPidAbsent=true, overlayAbsent=true. Owned /tmp/ap6 scratch files exported then deleted by exact name. Golden and host-side run/evidence records preserved. No branch, PR, ACCEPTANCE-1363.md or earlier STATUS lines edited.
