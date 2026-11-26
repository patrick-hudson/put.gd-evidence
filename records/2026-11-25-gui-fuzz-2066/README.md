# Issue 2066 published-nightly GUI fuzz campaign

This private record contains the reviewed evidence for the 2026-11-25/26 on-screen GUI-fuzz campaign against `v26.1125.7045-nightly`. The campaign used fresh disposable guests made from the lab goldens and displayed every active guest on Patrick's wall.

The selected record keeps aggregate summaries, package/golden identities, replay archives for desktop-session failures, complete saved desktop-process backtraces, targeted-control results, triage decisions, and guarded overlay-retirement receipts. The much larger ring buffers and all per-seed archives remain in the private local campaign archive.

Completed results:

- Aurora KDE Plasma: 34 sessions, 15,655 walk/control-seconds (4.35 hours), 10,658 actions, and no confirmed put.gd defect. Eight random-walk plasmashell SIGSEGVs all match the known `QtWaylandClient::QWaylandXdgSurface::applyConfigure` output/scale-churn trap. Fresh controls with no app, the idle resident, selectors open, and History plus Edit image surfaces open each produced zero shell crashes.
- Kubuntu 26.04 KDE Plasma: 30 seeds, 10,549 walk-seconds, 8,876 actions, no confirmed put.gd defect. The KWin fence loaded. Three plasmashell SIGSEGVs all match the same known trap.
- Fedora 44 GNOME: six sessions, 4,045 walk/control-seconds (1.12 hours), 1,525 actions, and no confirmed put.gd defect. Two random-walk gnome-shell crashes occurred; the retired crash guests lacked full coredump backtraces and the audit records that limitation. Fresh no-app, idle-resident, and selector-open controls produced zero shell crashes in every phase.
- Mint Cinnamon: 30 sessions, 8,991 walk-seconds (2.50 hours), 7,490 actions, and no confirmed put.gd defect. One Cinnamon SIGSEGV and two Nemo desktop crashes are retained as desktop-process run-summary events, not put.gd issues.

No memory corruption or other security-relevant put.gd finding has been confirmed.
