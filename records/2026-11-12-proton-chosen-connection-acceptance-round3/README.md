# Proton chosen-connection desktop acceptance round 3 (#1414)

All 64/64 PR-build item share attempts ended `shared`. No black or single-colour image among 24 PNGs. **Not clean acceptance:** Kubuntu back-to-back sampled two helpers, failing the expected one-helper gate. Debian, Mint and Fedora sampled one. The unchanged harness reports Kubuntu 15/15 because its verdict does not enforce helperProcessCount == 1.

Requested head `8596919291d0fb903bf8d1cf8f1fd4859f68d10e`, CI [43164839474](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43164839474). Published nightly control `26.1111.4633-nightly`. Packages extracted, never compiled. No product edits, merge, close or approval.

| Host | PR build | Original passes | Helpers left | Shared / attempts |
| --- | --- | --- | --- | --- |
| d69 | 26.1112.4656-dev+g1be97a258351 | 15/15 | [] | 18/18 |
| k72 | 26.1112.4656-dev+g1be97a258351 | 15/15 | [] | 18/18 |
| m74 | 26.1112.4656-dev+g1be97a258351 | 15/15 | [] | 18/18 |
| f44 | 26.1112.4656-dev+g1be97a258351 | 9/15 | [] | 10/10 |

Seconds: **2026-11-10 baseline / round 1 / round 2 / round 3**. Delayed captures exclude countdown; back-to-back totals share one invocation origin. † Debian round 2 8 MiB is an app-log interval, not a CLI total.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| file-64k | 5.39 / 3.74 / 3.9 / 3.87 | 5.56 / 4.01 / 6.22 / 5.67 | 5.3 / 5.95 / 6.66 / 3.89 | 4.97 / 4.92 / 4.83 / 4.88 |
| file-1m | 6.59 / 10.09 / 5.53 / 6.35 | 7.84 / 5.27 / 5.87 / 10.1 | 11.74 / 5.4 / 5.46 / 5.51 | 13.9 / 5.5 / 6.06 / 5.51 |
| file-8m | 9.26 / 13.0 / 8.152† / 8.7 | 7.95 / 15.95 / 8.88 / 8.19 | 10.7 / 14.57 / 8.53 / 10.52 | 8.42 / 12.03 / 8.37 / 9.9 |
| batch-3 | 12.45 / 7.99 / 8.1 / 8.67 | 16.89 / 8.25 / 7.7 / 7.88 | 11.29 / 8.02 / 8.07 / 8.66 | 10.33 / 8.41 / 8.27 / 8.97 |
| text-small | 4.03 / 2.83 / 2.71 / 3.36 | 3.78 / 2.84 / 3.06 / 3.02 | 5.67 / 3.06 / 3.06 / 3.09 | 4.63 / 3.18 / 3.16 / 3.07 |
| back-to-back | 5.9, 11.41 / 5.19, 8.25 / 4.96, 6.97 / 5.39, 7.59 | 9.02, 12.7 / 4.77, 7.99 / 5.28, 7.28 / 8.64, 8.66 | 5.52, 9.16 / 7.64, 7.66 / 5.38, 7.79 / 4.63, 6.63 | 8.82, 12.21 / 4.91, 8.96 / 8.28, 10.49 / 5.35, 7.71 |
| desktop-now | 7.22 / 3.59 / 4.44 / 5.16 | 6.76 / 4.42 / 4.49 / 4.47 | 8.88 / 4.5 / 4.71 / 4.55 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3 | 4.91 / 3.76 / 3.95 / 4.26 | 4.5 / 3.77 / 3.69 / 5.29 | 5.27 / 4.25 / 4.89 / 4.8 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| desktop-delay3-again | 7.27 / 3.76 / 3.92 / 4.06 | 6.08 / 5.6 / 5.21 / 3.72 | 8.27 / 4.33 / 4.91 / 4.72 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| monitor-delay3 | 6.59 / 3.62 / 3.96 / 4.2 | 4.69 / 3.72 / 5.43 / 3.69 | 7.79 / 4.51 / 4.98 / 4.51 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| cancel-countdown | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 | cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.01 / cancelled; helper gone 0.02 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| after-cancel | 3.95 / 3.01 / 3.1 / 3.28 | 3.81 / 3.18 / 3.26 / 3.8 | 5.06 / 3.1 / 3.31 / 3.35 | 3.68 / 3.27 / 3.82 / 3.5 |
| history-picture | 5.69 / 4.46 / 4.51 / 4.44 | 8.78 / 4.48 / 4.39 / 5.34 | 5.79 / 4.94 / 5.3 / 4.46 | gnome_extension_missing / gnome_extension_missing / gnome_extension_missing / gnome_extension_missing |
| link-answers | HTTP 200 / HTTP 200 / not run / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 | HTTP 200 / HTTP 200 / HTTP 200 / HTTP 200 |
| revoke-all | 15 revoked; 2.54–4.85/link / 15 revoked; 2.21–2.86/link / 15 revoked; 2.20–2.79/link / 15 revoked; 2.29–3.04/link | 15 revoked; 2.49–4.82/link / 15 revoked; 2.26–2.92/link / 15 revoked; 2.27–2.63/link / 15 revoked; 2.23–3.60/link | 15 revoked; 2.67–4.33/link / 15 revoked; 2.24–2.46/link / 15 revoked; 2.24–2.46/link / 15 revoked; 2.26–2.70/link | 10 revoked; 2.50–3.82/link / 10 revoked; 2.34–2.93/link / 10 revoked; 2.36–3.04/link / 10 revoked; 2.39–2.61/link |

| Host | Back-to-back helpers | PID/startTicks |
| --- | --- | --- |
| d69 | 1 | [{'pid': 3945071, 'startTicks': '225102505'}] |
| k72 | 2 | [{'pid': 3323360, 'startTicks': '114553567'}, {'pid': 3323491, 'startTicks': '114553937'}] |
| m74 | 1 | [{'pid': 512201, 'startTicks': '186252502'}] |
| f44 | 1 | [{'pid': 3925097, 'startTicks': '91604855'}] |

Helpers sampled every 10 ms as distinct PID/startTicks pairs, unchanged from round 2; this is not an exec audit.

| Host | Screenshot 1 stage / total | Screenshot 2 stage / total | Screenshot 3 stage / total |
| --- | --- | --- | --- |
| d69 | 2.03 / 4.56 (completed) | 4.34 / 7.14 (completed) | 2.13 / 4.98 (completed) |
| k72 | 1.89 / 4.26 (completed) | 1.88 / 4.81 (completed) | 1.93 / 4.44 (completed) |
| m74 | 2.09 / 4.56 (completed) | 2.43 / 4.94 (completed) | 2.31 / 4.75 (completed) |
| f44 | unobserved / not testable (gnome_extension_missing) | unobserved / not testable (gnome_extension_missing) | unobserved / not testable (gnome_extension_missing) |

Order-balanced large-file control: one network sample per build/case. Upload stage = first observed sharing minus first observed uploading. Total = invocation to terminal observation. These numbers support no conclusion about sustained speed.

| Host | First build | Case | PR stage / total | Nightly stage / total |
| --- | --- | --- | --- | --- |
| d69 | nightly | file-1m | 2.85 / 6.35 (completed) | 4.21 / 10.15 (completed) |
| d69 | nightly | file-8m | 5.37 / 8.7 (completed) | 13.11 / 17.36 (completed) |
| k72 | PR | file-1m | 7.49 / 10.1 (completed) | 2.84 / 6.3 (completed) |
| k72 | PR | file-8m | 4.43 / 8.19 (completed) | 5.32 / 9.56 (completed) |
| m74 | nightly | file-1m | 2.72 / 5.51 (completed) | 3.51 / 11.15 (completed) |
| m74 | nightly | file-8m | 7.53 / 10.52 (completed) | 13.39 / 17.66 (completed) |
| f44 | PR | file-1m | 2.84 / 5.51 (completed) | 7.65 / 11.81 (completed) |
| f44 | PR | file-8m | 6.73 / 9.9 (completed) | 5.46 / 9.7 (completed) |

| Host | PNGs | Black | Single-colour | PR revoked | Nightly revoked |
| --- | --- | --- | --- | --- | --- |
| d69 | 8 | 0 | 0 | 15 revoked, 3 revoked | 2 revoked |
| k72 | 8 | 0 | 0 | 15 revoked, 3 revoked | 2 revoked |
| m74 | 8 | 0 | 0 | 15 revoked, 3 revoked | 2 revoked |
| f44 | 0 | 0 | 0 | 10 revoked | 2 revoked |

Failures and oddities:

- f44 PR: desktop-now: failed, error `gnome_extension_missing`, 0.2 s; items `[]`.
- f44 PR: desktop-delay3: failed, error `gnome_extension_missing`, 0.11 s; items `[]`.
- f44 PR: desktop-delay3-again: failed, error `gnome_extension_missing`, 0.13 s; items `[]`.
- f44 PR: monitor-delay3: failed, error `gnome_extension_missing`, 0.12 s; items `[]`.
- f44 PR: cancel-countdown: failed, error `gnome_extension_missing`, 0.12 s; items `[]`.
- f44 PR: history-picture: failed, error `gnome_extension_missing`, 0.09 s; items `[]`.

Every operation log event is retained in each build’s events.jsonl, with addresses and secret-bearing fields omitted. Non-shared outcomes, if any, have one immediate read-only history.inspectLink and share.inspect completion in nonshared-inspections.jsonl. An inspection does not relabel the original outcome.

Method: proton_accept.py is byte-identical to round 2 (SHA-256 945751b11a52f31004021b8754f4906910c3e85ffab02066532ed4193135d810). round3.py is the additive round-2 adapter adjusted for balanced ordering, a fresh log on every start, no black-capture retry, and immediate non-shared inspections. drive3.py uses new /tmp/p3a and ~/work/p3a paths. On PR-first hosts the resident is stopped after file-8m, nightly runs and revokes its links, then PR resumes with a new resident log. On nightly-first hosts the nightly process finishes before PR starts. No failed product case is retried. Read-only display probes precede the first capture and are inside that first case’s reported timer. Pixel analysis follows terminal timing.

Capture PNGs remain private on their builders; byte sizes, dimensions and RGB extrema are exported. No desktop logout, unlock, power change or GNOME extension workaround. The display wall remains enabled. No memory gate, region/window pointer selection, Aurora, package install audit, or transport/expired-token injection is covered. No statistical speed claim. Protected inputs, keyrings and earlier scratch were not read or modified.


CI packages identify merge commit `1be97a25835175db460ec8cccc27756ca8e3db2c`, tree `cce1e5c83de497f454570be3ae340aba41a25669`; its second parent is the exact requested PR head (merge-provenance.json). All four residents reported `26.1112.4656-dev+g1be97a258351`. Control release published 2026-11-11 10:45 UTC; its downloaded files matched the release API SHA-256 digests. CI artifact hashes are in package-sha256.txt.

No non-shared item occurred, so no history.inspectLink failure diagnostic was needed. Original and added PR revocations totalled 64, controls revoked 8; each profile's final history.list had zero available links. No helper remained on either build. Helpers are sampled, not audited; Kubuntu's two identities were PID 3323360/startTicks 114553567 and PID 3323491/startTicks 114553937. k72-b2b-events.jsonl holds every app event for the two operations. The log has `06:27:01.660 Operation accepted` and `06:27:01.691 Operation accepted`, then `06:27:05.306 Sharing finished status=shared` and `06:27:10.187 Sharing finished status=shared`. Both finished completed; the first-invoked operation finished last. No app log line explains the two Proton helper lifetimes, and their cause is not established. No retry.

The initial local driver attempt stopped with `FileExistsError: /tmp/p3a/m74` before taking any lease or starting an app: the round-2 evidence extraction had made that path. The failed command was `python3 /tmp/p3a/drive3.py m74 > /tmp/p3a/m74-driver.log 2>&1`. Corrected command: `python3 /tmp/p3a/drive3.py m74 > /tmp/p3a/m74-driver-corrected.log 2>&1`, with new output under `/tmp/p3a/new/m74`. Both logs are retained. No product case was retried. Raw text/profile-state evidence remains private under /tmp/p3a/new; captures remain on builders under ~/work/p3a. The supplied round-2 shell orchestrator was not run because its fixed paths address earlier scratch; the corrected Python driver was reused with fresh paths. Scripts as run and the adaptation script are included.

Both locks were checked after every acquire and heartbeated once per minute. Each acquire was for 45 minutes. No lease was broken. Verified-clean desktop releases: Mint 06:25:23Z, Kubuntu 06:28:51Z, Fedora 06:31:20Z, Debian 06:34:57Z, all before 12:15Z. Their driver logs retain host-side receipt paths and the no-new-items cleanup results. Debian's baseline item and shared SSH processes were preserved. The prior holder released Debian naturally; no coordination message, logout, unlock or display change was needed.

Timing interpretation: back-to-back follows the first operation to completion before observing the second. If the second finishes first (as on Kubuntu), its reported time is the later CLI observation, not its actual completion latency. Upload-stage measurements are polling observations, not internal transfer-only timers. PR first controls interrupt the resident sequence; nightly first controls use separate private profiles. These are single samples on a varying network; no comparison establishes sustained performance.

Read-only pre-capture display observations:

- d69: VTNr=0, Type=tty, Active=yes, State=active, LockedHint=no; VTNr=1, Type=wayland, Active=yes, State=active, LockedHint=no; /sys/class/drm/card0-DP-1/dpms=Off; /sys/class/drm/card0-DP-2/dpms=Off; /sys/class/drm/card0-DP-3/dpms=Off; /sys/class/drm/card0-HDMI-A-1/dpms=On; /sys/class/drm/card0-HDMI-A-2/dpms=Off; /sys/class/drm/card0-HDMI-A-3/dpms=Off.

- k72: VTNr=0, Type=tty, Active=yes, State=active, LockedHint=no; VTNr=3, Type=wayland, Active=yes, State=active, LockedHint=no; /sys/class/drm/card1-DP-1/dpms=Off; /sys/class/drm/card1-DP-2/dpms=Off; /sys/class/drm/card1-DP-3/dpms=Off; /sys/class/drm/card1-HDMI-A-1/dpms=On; /sys/class/drm/card1-HDMI-A-2/dpms=Off; /sys/class/drm/card1-HDMI-A-3/dpms=Off.

- m74: VTNr=0, Type=tty, Active=yes, State=active, LockedHint=no; VTNr=7, Type=x11, Active=yes, State=active, LockedHint=no; /sys/class/drm/card1-DP-1/dpms=Off; /sys/class/drm/card1-DP-2/dpms=Off; /sys/class/drm/card1-DP-3/dpms=Off; /sys/class/drm/card1-HDMI-A-1/dpms=On; /sys/class/drm/card1-HDMI-A-2/dpms=Off; /sys/class/drm/card1-HDMI-A-3/dpms=Off.

- f44: VTNr=0, Type=tty, Active=yes, State=active, LockedHint=no; VTNr=2, Type=wayland, Active=yes, State=active, LockedHint=no; /sys/class/drm/card0-DP-1/dpms=Off; /sys/class/drm/card0-DP-2/dpms=Off; /sys/class/drm/card0-DP-3/dpms=Off; /sys/class/drm/card0-HDMI-A-1/dpms=On; /sys/class/drm/card0-HDMI-A-2/dpms=Off; /sys/class/drm/card0-HDMI-A-3/dpms=Off.

All warning/error lines, including Fedora clipboard and capture errors, portal registration, tray, Fontconfig, GStreamer, Wayland text-input and Mint nightly NoReply warnings, are retained in [warnings.md](warnings.md). They were not suppressed or used to trigger retries.
