# Proton chosen-connection desktop acceptance round 4 (#1414)

All 36/36 pairs used one helper. All 119/119 upload items ended shared. No capture was black. **Not clean acceptance:** Kubuntu revoke-all failed for two items; separate cleanup later revoked both.

Tested PR head `0a6014c8c42c1929d148cb6d13826d0a15c1509f` using [successful CI run 43170857019](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43170857019) packages. Build merge commit `fe1e300569344866158e968f4f9bd513457ca2a5`, tree `742b4c8b92cbcaf16808cc6b0eda9affe4190c71`; merge second parent is the exact requested head (merge-provenance.json). Extracted packages; no compilation or product edits. No merge, close or approval.

| Host | Build | Original cases passed | Extra pairs passed (including one-helper gate) | Shared / attempts | Helpers left |
| --- | --- | --- | --- | --- | --- |
| d69 | 26.1112.4657-dev+gfe1e30056934 | 15/15 | 8/8 | 31/31 | [] |
| k72 | 26.1112.4657-dev+gfe1e30056934 | 14/15 | 8/8 | 31/31 | [] |
| m74 | 26.1112.4657-dev+gfe1e30056934 | 15/15 | 8/8 | 31/31 | [] |
| f44 | 26.1112.4657-dev+gfe1e30056934 | 9/15 | 8/8 | 26/26 | [] |

Seconds: round 1 / round 2 / round 3 / round 4. Each is a single network observation. Delayed captures exclude countdown; paired CLI timings follow first operation then second, so use app-log completion times below for finish order. Debian round 2 8 MiB (†) is an app-log interval.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| file-64k | 3.74 / 3.9 / 3.87 / 3.66 | 4.01 / 6.22 / 5.67 / 4.59 | 5.95 / 6.66 / 3.89 / 7.75 | 4.92 / 4.83 / 4.88 / 4.29 |
| file-1m | 10.09 / 5.53 / 6.35 / 5.32 | 5.27 / 5.87 / 10.1 / 5.35 | 5.4 / 5.46 / 5.51 / 5.35 | 5.5 / 6.06 / 5.51 / 5.9 |
| file-8m | 13.0 / 8.152† / 8.7 / 8.62 | 15.95 / 8.88 / 8.19 / 8.13 | 14.57 / 8.53 / 10.52 / 15.88 | 12.03 / 8.37 / 9.9 / 8.71 |
| batch-3 | 7.99 / 8.1 / 8.67 / 8.35 | 8.25 / 7.7 / 7.88 / 10.34 | 8.02 / 8.07 / 8.66 / 8.32 | 8.41 / 8.27 / 8.97 / 8.68 * |
| text-small | 2.83 / 2.71 / 3.36 / 3.15 | 2.84 / 3.06 / 3.02 / 2.84 | 3.06 / 3.06 / 3.09 / 3.01 | 3.18 / 3.16 / 3.07 / 3.17 * |
| back-to-back | 5.19, 8.25 / 4.96, 6.97 / 5.39, 7.59 / 4.66, 6.72 | 4.77, 7.99 / 5.28, 7.28 / 8.64, 8.66 / 4.73, 6.76 | 7.64, 7.66 / 5.38, 7.79 / 4.63, 6.63 / 4.69, 6.62 | 4.91, 8.96 / 8.28, 10.49 / 5.35, 7.71 / 5.02, 7.15 |
| desktop-now | 3.59 / 4.44 / 5.16 / 4.49 | 4.42 / 4.49 / 4.47 / 5.08 | 4.5 / 4.71 / 4.55 / 4.55 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3 | 3.76 / 3.95 / 4.26 / 3.69 | 3.77 / 3.69 / 5.29 / 4.56 | 4.25 / 4.89 / 4.8 / 4.76 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3-again | 3.76 / 3.92 / 4.06 / 3.66 | 5.6 / 5.21 / 3.72 / 3.72 | 4.33 / 4.91 / 4.72 / 4.39 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| monitor-delay3 | 3.62 / 3.96 / 4.2 / 3.81 | 3.72 / 5.43 / 3.69 / 3.84 | 4.51 / 4.98 / 4.51 / 4.34 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| cancel-countdown | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.02 / cancelled; helper gone 0.01 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| after-cancel | 3.01 / 3.1 / 3.28 / 3.18 | 3.18 / 3.26 / 3.8 / 3.25 | 3.1 / 3.31 / 3.35 / 3.14 | 3.27 / 3.82 / 3.5 / 3.29 * |
| history-picture | 4.46 / 4.51 / 4.44 / 4.54 | 4.48 / 4.39 / 5.34 / 4.83 | 4.94 / 5.3 / 4.46 / 4.48 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| link-answers | HTTP 200 / not run / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 |
| revoke-all | 15 revoked; 2.21–2.86/link / 15 revoked; 2.20–2.79/link / 15 revoked; 2.29–3.04/link / 31 revoked; 2.21–2.84/link | 15 revoked; 2.26–2.92/link / 15 revoked; 2.27–2.63/link / 15 revoked; 2.23–3.60/link / 29 revoked; 2.22–3.69/link | 15 revoked; 2.24–2.46/link / 15 revoked; 2.24–2.46/link / 15 revoked; 2.26–2.70/link / 31 revoked; 2.24–4.24/link | 10 revoked; 2.34–2.93/link / 10 revoked; 2.36–3.04/link / 10 revoked; 2.39–2.61/link / 26 revoked; 2.36–3.75/link |

All nine pairs per host. Times are UTC from app logs, listed in invocation order; first=512 KiB for pairs 1–5 and 64 KiB for pairs 6–9. Pair 1 is the original case. Completion means `Operation finished`, not the later CLI observation. Helpers are distinct PID/kernel-startTicks sampled every 10 ms through helper exit, not an exec audit.

| Host/pair | KiB order | Accepted 1 / 2 UTC | Completed 1 / 2 UTC | Finished first | Helpers |
| --- | --- | --- | --- | --- | --- |
| d69/1 | 512 / 64 | 07:11:45.503 / 07:11:45.569 | 07:11:50.088 / 07:11:52.124 | 1 | 1 |
| d69/2 | 512 / 64 | 07:12:30.044 / 07:12:30.092 | 07:12:34.657 / 07:12:36.576 | 1 | 1 |
| d69/3 | 512 / 64 | 07:12:36.695 / 07:12:36.777 | 07:12:41.505 / 07:12:43.475 | 1 | 1 |
| d69/4 | 512 / 64 | 07:12:43.593 / 07:12:43.673 | 07:12:48.172 / 07:12:50.110 | 1 | 1 |
| d69/5 | 512 / 64 | 07:12:50.209 / 07:12:50.296 | 07:12:54.888 / 07:12:56.730 | 1 | 1 |
| d69/6 | 64 / 512 | 07:12:56.851 / 07:12:56.912 | 07:12:59.978 / 07:13:03.519 | 1 | 1 |
| d69/7 | 64 / 512 | 07:13:03.612 / 07:13:03.700 | 07:13:06.708 / 07:13:10.157 | 1 | 1 |
| d69/8 | 64 / 512 | 07:13:10.301 / 07:13:10.382 | 07:13:13.397 / 07:13:16.883 | 1 | 1 |
| d69/9 | 64 / 512 | 07:13:16.977 / 07:13:17.082 | 07:13:20.100 / 07:13:26.522 | 1 | 1 |
| k72/1 | 512 / 64 | 07:05:19.813 / 07:05:19.897 | 07:05:24.502 / 07:05:26.517 | 1 | 1 |
| k72/2 | 512 / 64 | 07:06:06.319 / 07:06:06.392 | 07:06:11.018 / 07:06:12.990 | 1 | 1 |
| k72/3 | 512 / 64 | 07:06:13.109 / 07:06:13.167 | 07:06:17.719 / 07:06:19.616 | 1 | 1 |
| k72/4 | 512 / 64 | 07:06:19.742 / 07:06:19.779 | 07:06:24.669 / 07:06:26.617 | 1 | 1 |
| k72/5 | 512 / 64 | 07:06:26.689 / 07:06:26.759 | 07:06:31.633 / 07:06:34.219 | 1 | 1 |
| k72/6 | 64 / 512 | 07:06:34.484 / 07:06:34.537 | 07:06:37.632 / 07:06:41.145 | 1 | 1 |
| k72/7 | 64 / 512 | 07:06:41.234 / 07:06:41.344 | 07:06:44.613 / 07:06:48.085 | 1 | 1 |
| k72/8 | 64 / 512 | 07:06:48.178 / 07:06:48.280 | 07:06:51.319 / 07:06:54.833 | 1 | 1 |
| k72/9 | 64 / 512 | 07:06:54.946 / 07:06:55.036 | 07:06:58.174 / 07:07:01.888 | 1 | 1 |
| m74/1 | 512 / 64 | 07:27:09.887 / 07:27:09.916 | 07:27:14.533 / 07:27:16.450 | 1 | 1 |
| m74/2 | 512 / 64 | 07:27:56.829 / 07:27:56.857 | 07:28:03.943 / 07:28:00.420 | 2 | 1 |
| m74/3 | 512 / 64 | 07:28:04.034 / 07:28:04.067 | 07:28:08.831 / 07:28:10.772 | 1 | 1 |
| m74/4 | 512 / 64 | 07:28:10.833 / 07:28:10.865 | 07:28:15.530 / 07:28:17.534 | 1 | 1 |
| m74/5 | 512 / 64 | 07:28:17.624 / 07:28:17.654 | 07:28:22.344 / 07:28:24.300 | 1 | 1 |
| m74/6 | 64 / 512 | 07:28:24.371 / 07:28:24.461 | 07:28:28.160 / 07:28:31.624 | 1 | 1 |
| m74/7 | 64 / 512 | 07:28:31.726 / 07:28:31.752 | 07:28:38.272 / 07:28:36.305 | 2 | 1 |
| m74/8 | 64 / 512 | 07:28:38.399 / 07:28:38.427 | 07:28:41.427 / 07:28:45.034 | 1 | 1 |
| m74/9 | 64 / 512 | 07:28:45.129 / 07:28:45.210 | 07:28:48.192 / 07:28:51.647 | 1 | 1 |
| f44/1 | 512 / 64 | 07:15:43.621 / 07:15:43.676 | 07:15:48.571 / 07:15:50.747 | 1 | 1 |
| f44/2 | 512 / 64 | 07:16:05.267 / 07:16:05.312 | 07:16:10.191 / 07:16:12.694 | 1 | 1 |
| f44/3 | 512 / 64 | 07:16:12.770 / 07:16:12.821 | 07:16:20.178 / 07:16:16.346 | 2 | 1 |
| f44/4 | 512 / 64 | 07:16:20.352 / 07:16:20.472 | 07:16:25.441 / 07:16:27.645 | 1 | 1 |
| f44/5 | 512 / 64 | 07:16:27.721 / 07:16:27.764 | 07:16:32.785 / 07:16:34.967 | 1 | 1 |
| f44/6 | 64 / 512 | 07:16:35.013 / 07:16:35.078 | 07:16:39.052 / 07:16:42.859 | 1 | 1 |
| f44/7 | 64 / 512 | 07:16:42.914 / 07:16:42.964 | 07:16:46.363 / 07:16:50.070 | 1 | 1 |
| f44/8 | 64 / 512 | 07:16:50.198 / 07:16:50.241 | 07:16:53.587 / 07:16:57.274 | 1 | 1 |
| f44/9 | 64 / 512 | 07:16:57.407 / 07:16:57.454 | 07:17:04.683 / 07:17:02.464 | 2 | 1 |

| Host | PNGs checked | Black | Single colour | Revocations | No available links in initial history read |
| --- | --- | --- | --- | --- | --- |
| d69 | 5 | 0 | 0 | 31 revoked | True |
| k72 | 5 | 0 | 0 | 29 revoked | True |
| m74 | 5 | 0 | 0 | 31 revoked | True |
| f44 | 0 | 0 | 0 | 26 revoked | True |

Failures and oddities (no retries):

- k72: revoke-all: 29 revoked, None, 71.27 s.
- f44: desktop-now: failed, gnome_extension_missing, 0.21 s.
- f44: desktop-delay3: failed, gnome_extension_missing, 0.12 s.
- f44: desktop-delay3-again: failed, gnome_extension_missing, 0.11 s.
- f44: monitor-delay3: failed, gnome_extension_missing, 0.18 s.
- f44: cancel-countdown: failed, gnome_extension_missing, 0.16 s.
- f44: history-picture: failed, gnome_extension_missing, 0.1 s.

Fedora’s six screenshot cases are not testable (`gnome_extension_missing`), expected; no workaround. All warning/error log lines follow in warnings.md. Full sanitized app events are in each host’s events.jsonl, and every paired operation log line in pairs.json. No link outcome is relabelled by an inspection. Any nonshared outcome has a read-only history.inspectLink diagnostic in nonshared-inspections.jsonl.

The unchanged proton_accept.py SHA-256 is 945751b11a52f31004021b8754f4906910c3e85ffab02066532ed4193135d810. Round 3 adapters are retained unchanged. round4.py disables the nightly-control hook, selects the original 15 cases explicitly (skipping sequential screenshots), and runs eight more original back-to-back cases before final revoke-all. Only synthetic payload generation sizes are swapped for pairs 6–9. Every pair waits for both completions and helper exit. All pairs share one resident start and a fresh resident log per host.

Capture PNGs remain private on builders; only pixel statistics exported. Read-only display probes are retained; no logout, unlock, power/display change, keyring extraction or unrelated scratch changes. Socket preflight is in run.log. Both leases were acquired with checked success, heartbeated every minute, and released verified-clean after cleanup. All work is before the nightly window.

Not covered: the intentionally omitted three sequential screenshots and nightly large-file control; memory gates, Aurora, pointer-based region/window selection, expired-token injection or sustained speed. No acceptance case rerun. Kubuntu required separately recorded targeted cleanup for two test links; the original revoke-all result remains failed. Evidence source is /tmp/p4a on the workstation and ~/work/p4a on each builder. Earlier rounds remain untouched.

Kubuntu revoke-all failed and remains failed: `29 revoked`, failures `['unknown', 'unknown']`. The original final history read had zero available links, which did **not** prove revocation: unknown clears local link availability. A separate diagnostic start found 29 `revoked`, two `unknown`. One read-only inspection per uncertain item then found both still `shared`. One targeted cleanup action per exact test item returned `revoked`; these cleanup actions do not turn the original acceptance gate into a pass. Every run-created link now has a confirmed revoke result in the durable sharing journal: d69 31, k72 31, m74 31, f44 26 (119 total). Kubuntu's two original unknown records remain in sharing-journal.json.

Kubuntu durable failure records (the app emitted no corresponding revoke failure log line):

```jsonl
{"id": "09b30d5b-fad4-472e-aeb0-fd22a40eabe3", "historyId": "bcca53d9-4c03-4487-b636-cb2a324eaa9f", "action": "revoke", "state": "completed", "status": "unknown", "error": {"code": "authentication_required", "details": {}, "message": "The Proton session is unavailable. Reconnect this account before explicitly inspecting or retrying the saved operation."}, "progress": {"schemaVersion": 1}}
{"id": "378e6e34-2e69-4867-85bd-2e36f2a02e59", "historyId": "512a728d-ae34-46f3-a757-1fb6c341246d", "action": "revoke", "state": "completed", "status": "unknown", "error": {"code": "authentication_required", "details": {}, "message": "The Proton session is unavailable. Reconnect this account before explicitly inspecting or retrying the saved operation."}, "progress": {"schemaVersion": 1}}
```

Mint pairs 2 and 7 and Fedora pairs 3 and 9 finished the second-invoked operation first while still using one helper each. Pair operation IDs are matched using the harness result history IDs, preserving invocation order even when log events arrive out of order.

Read-only reconciliation and separate cleanup are in k72/diag2/inspections.json and k72/diag3/inspections.json. Each diagnostic launch used a fresh log under a new directory, checked both locks, stopped its resident and helper, and released verified-clean; no sign-in, sign-out or session copy occurred. These were diagnostic/cleanup launches after the single acceptance run, not repeat acceptance cases.

The initial acquire attempts on d69, m74 and f44 were refused while `scroll-fix7-1398` held their desktop leases; no app started on those attempts. Their logs are preserved as lock-refused.log. The corrected driver allows an existing *empty* output directory left by a refused acquire, but refuses to rerun any host with run.log. The old driver is drive4-initial.py. Coordination occurred with the scrolling screenshot campaign; no lease was broken or foreign process stopped.

Fedora failed screenshot operations, straight from the app log:

```jsonl
{"category": "putgd.operation", "fields": {"action": "desktop", "byteCount": 0, "durationMs": 65, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "68fa2885-4031-443f-9ded-c0a36669b3eb", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:50.899Z", "v": 1}
{"category": "putgd.operation", "fields": {"action": "desktop", "byteCount": 0, "durationMs": 57, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "d9c06991-d6be-4ed2-b759-6044466269e7", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:52.006Z", "v": 1}
{"category": "putgd.operation", "fields": {"action": "desktop", "byteCount": 0, "durationMs": 49, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "dd1318b5-949a-4c6c-a37c-4aacacc1de26", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:53.191Z", "v": 1}
{"category": "putgd.operation", "fields": {"action": "monitor", "byteCount": 0, "durationMs": 107, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "8bdf31ef-8929-4240-81fe-88be32db38e4", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:54.446Z", "v": 1}
{"category": "putgd.operation", "fields": {"action": "desktop", "byteCount": 0, "durationMs": 69, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "6e825b29-0f81-408c-b01e-5ba83dd3a956", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:55.581Z", "v": 1}
{"category": "putgd.operation", "fields": {"action": "desktop", "byteCount": 0, "durationMs": 55, "error": {"code": "gnome_extension_missing", "details": {"shellVersion": "50.6"}, "message": "put.gd's GNOME extension is not installed. Reinstall the put.gd package."}, "itemId": null, "items": 0, "provider": "proton-drive", "state": "failed", "uploadStatus": {}}, "level": "warning", "message": "Operation finished", "operationId": "233c7cfc-1ab5-49b3-a0b7-4bbaaa907ef5", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:03.670Z", "v": 1}
```

* Fedora logged `clipboard_unavailable` on all 24 completed upload operations. The CLI terminal snapshots carried that error for 11 operations; the full app log contains 24 clipboard failure events. These are different observation points. Asterisks in the time table mark only the CLI snapshots with that error. Every uploaded item still ended shared. The unchanged harness pass criterion checks upload/share completion, not clipboard ownership. All 24 warning lines are retained below and in warnings.md.

```jsonl
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "7caad894-6b3d-4710-bb7d-28a618e4052a", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:17.066Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "1472e256-9134-41ed-b15f-53acc8dc8377", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:22.956Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "41175a49-85a7-421c-95d1-e3e13786b994", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:31.698Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 3}, "level": "warning", "message": "Automatic copy finished", "operationId": "c23f0a8f-ff4b-4c17-b73d-dfa1eaf14b3e", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:40.368Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "6ce38a7f-e684-43ce-973c-e8e5805ea1e1", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:43.541Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "b674219b-19e2-4dd4-b979-bc6ea99acc01", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:48.571Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "74df9ea0-a2d8-4971-bb21-50a323b84c7f", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:15:50.747Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "95319ae7-9220-4741-bd2d-39539a7a353a", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:00.534Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "082e6a98-767c-4fec-bec5-d4567cf6189b", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:10.197Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "75b46753-18c3-4431-ae45-c13be97c096c", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:12.694Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "56f90541-8a93-469c-9f4e-d121d4516fac", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:16.360Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "578c21cb-3340-4a24-8af1-3b1a33e6de42", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:20.185Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "ed56d4f0-b770-494d-abf2-b2e519ca0680", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:25.441Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "76f7382d-4e0d-4f01-8bb5-e0823b856eff", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:27.656Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "33bb8405-97da-4a1f-b1b8-0d33b8c709b9", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:32.785Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "d6ede1b1-e1f0-4ae3-a8f5-6b68025c442e", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:34.967Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "8b3ffc20-21be-49d3-85b2-48c2c7aa70aa", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:39.060Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "fefea162-f77e-47a0-a41c-6968cd4513ad", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:42.870Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "e50a62e6-8313-4040-99e2-2922350c77c5", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:46.363Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "4c3b4f8d-4ebf-45f1-ab33-c7cc19161fe2", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:50.072Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "a98eb696-7116-407d-957c-b9bcf41fc90a", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:53.601Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "82c14116-97a0-4d00-b4f3-ba043abfbbf1", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:16:57.275Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "a440fb1c-344c-4c2e-b0c9-eafe872fa82d", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:17:02.483Z", "v": 1}
{"category": "putgd.clipboard", "fields": {"action": "files", "automatic": true, "behavior": "each_link", "cancelled": false, "copyStatus": "failed", "error": {"code": "clipboard_unavailable", "details": {}, "message": "GNOME helper cannot own CLIPBOARD"}, "itemId": null, "links": 1}, "level": "warning", "message": "Automatic copy finished", "operationId": "3edcb806-0290-4db2-8766-69ba1d7db43b", "pid": 3935739, "process": "putgd", "time": "2026-11-12T07:17:04.690Z", "v": 1}
```

Kubuntu’s runtime binary matched round 3 byte for byte: SHA-256 `42e1decb6d718e2640f0a419b3d135a3755f65a27e66682126ed16a2f6581065`.

Publication correction: the first evidence commit described 11 clipboard errors from terminal CLI snapshots. Full-log counting showed 24 distinct completed operations with a clipboard warning. This README was amended to state both counts; all original result JSON and app logs are unchanged.
