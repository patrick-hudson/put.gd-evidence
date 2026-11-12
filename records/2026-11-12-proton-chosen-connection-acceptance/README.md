# Proton chosen-connection desktop acceptance (#1414)

**The expected helper handover did not happen: back-to-back counted two helper processes on every host, rather than one.** Upload/share behavior passed wherever captures were available, but d69’s first screenshot was entirely black and fails visual acceptance. No helper was left running. The six GNOME capture failures match the baseline. Timings were mixed: every 8 MiB upload was slower than baseline; screenshots were faster.

Tested head `65c9292f6544952e7fe4e1d53bd2bbbd5774b866`, branch `perf/proton-link-faster`, using CI run [43150631416](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43150631416). The packages identify GitHub PR merge commit `73458e4cbeea4194267ec7d4eb71d25ab6e3e364`, whose second parent is the requested head, build `26.1112.4652-dev+g73458e4cbeea`. CI concluded success. No builder compilation. Exact build identities are in each results.json.

An earlier attempt on dcfa09b3b stopped on a CI lint failure; no desktop tests ran in that attempt.

| Host | Desktop / package | Original cases passed | Helpers left |
| --- | --- | --- | --- |
| d69 | plasmashell / wayland / .deb | 15/15 | [] |
| k72 | plasmashell / wayland / .deb | 15/15 | [] |
| m74 | cinnamon / x11 / AppImage | 15/15 | [] |
| f44 | gnome-shell / wayland / AppImage | 9/15 | [] |

## Baseline beside new times

Seconds, baseline → current. Back-to-back times share one invocation origin. Delayed captures subtract the countdown, as in the baseline. Revocations list their count and range per link.

| Case | d69 | k72 | m74 | f44 |
| --- | --- | --- | --- | --- |
| `file-64k` | 5.39 → 3.74 | 5.56 → 4.01 | 5.3 → 5.95 | 4.97 → 4.92 |
| `file-1m` | 6.59 → 10.09 | 7.84 → 5.27 | 11.74 → 5.4 | 13.9 → 5.5 |
| `file-8m` | 9.26 → 13.0 | 7.95 → 15.95 | 10.7 → 14.57 | 8.42 → 12.03 |
| `batch-3` | 12.45 → 7.99 | 16.89 → 8.25 | 11.29 → 8.02 | 10.33 → 8.41 |
| `text-small` | 4.03 → 2.83 | 3.78 → 2.84 | 5.67 → 3.06 | 4.63 → 3.18 |
| `back-to-back` | 5.9, 11.41 → 5.19, 8.25 | 9.02, 12.7 → 4.77, 7.99 | 5.52, 9.16 → 7.64, 7.66 | 8.82, 12.21 → 4.91, 8.96 |
| `desktop-now` | 7.22 → 3.59 | 6.76 → 4.42 | 8.88 → 4.5 | gnome_extension_missing → gnome_extension_missing |
| `desktop-delay3` | 4.91 → 3.76 | 4.5 → 3.77 | 5.27 → 4.25 | gnome_extension_missing → gnome_extension_missing |
| `desktop-delay3-again` | 7.27 → 3.76 | 6.08 → 5.6 | 8.27 → 4.33 | gnome_extension_missing → gnome_extension_missing |
| `monitor-delay3` | 6.59 → 3.62 | 4.69 → 3.72 | 7.79 → 4.51 | gnome_extension_missing → gnome_extension_missing |
| `cancel-countdown` | cancelled; helper gone 0.01 → cancelled; helper gone 0.01 | cancelled; helper gone 0.01 → cancelled; helper gone 0.01 | cancelled; helper gone 0.01 → cancelled; helper gone 0.01 | gnome_extension_missing → gnome_extension_missing |
| `after-cancel` | 3.95 → 3.01 | 3.81 → 3.18 | 5.06 → 3.1 | 3.68 → 3.27 |
| `history-picture` | 5.69 → 4.46 | 8.78 → 4.48 | 5.79 → 4.94 | gnome_extension_missing → gnome_extension_missing |
| `link-answers` | HTTP 200 → HTTP 200 | HTTP 200 → HTTP 200 | HTTP 200 → HTTP 200 | HTTP 200 → HTTP 200 |
| `revoke-all` | 15 revoked; 2.54–4.85 each → 15 revoked; 2.21–2.86 each | 15 revoked; 2.49–4.82 each → 15 revoked; 2.26–2.92 each | 15 revoked; 2.67–4.33 each → 15 revoked; 2.24–2.46 each | 10 revoked; 2.5–3.82 each → 10 revoked; 2.34–2.93 each |

## Added measurements

Helper count samples the user’s `/proc` entries every 10 ms over back-to-back through helper exit, counting distinct (PID, kernel start-time) pairs with comm beginning `putgd-proton-ru`. This is a sampled process inventory, not an exec audit.

| Host | Back-to-back helper count | Sequential screenshots (upload stage, total seconds) |
| --- | --- | --- |
| d69 | 2 | 1: (2.1, 4.43); 2: (1.93, 4.21); 3: (1.87, 4.37) |
| k72 | 2 | 1: (1.97, 4.28); 2: (1.95, 4.41); 3: (2.02, 4.73) |
| m74 | 2 | 1: (2.08, 4.58); 2: (2.1, 4.51); 3: (2.1, 4.65) |
| f44 | 2 | Not attempted; GNOME capture unavailable |

Upload-stage times are first observed `sharing` minus first observed `uploading`, sampled by the production CLI; total is invocation to terminal state. The three captures ran sequentially in the same resident after the original 15 cases. Storage-host choices were not captured, so these times cannot establish whether hints hit or missed.

## Failures, oddities and coverage

- f44: `desktop-now` state `failed`, error `gnome_extension_missing`, 0.13 s.
- f44: `desktop-delay3` state `failed`, error `gnome_extension_missing`, 0.16 s.
- f44: `desktop-delay3-again` state `failed`, error `gnome_extension_missing`, 0.14 s.
- f44: `monitor-delay3` state `failed`, error `gnome_extension_missing`, 0.12 s.
- f44: `cancel-countdown` state `failed`, error `gnome_extension_missing`, 0.21 s.
- f44: `history-picture` state `failed`, error `gnome_extension_missing`, 0.14 s.

All attempts are retained; no failed case was retried. `revoke-all` covers original links; `revoke-additions` covers the three extra captures where available. Per-host results retain operation IDs, phase observations, helper cleanup times and revocation results. Share addresses, tokens, keyring contents and payloads are excluded.

Scripts retain the original 15 case bodies, with fresh scratch paths, heartbeats, socket preflight, a back-to-back process observer and three sequential captures plus revocation. The `.original` files are unchanged baseline scripts. Private raw logs and screenshots remain under `/tmp/p1414-final/accept-results/` and each host’s `~/work/pf65/r65`.

Not covered: Aurora; GNOME screenshot uploads when the extension is missing; real region/window pointer selection; memory/resource release gates, installed-package audits, expired-token startup and transport fallback fault injection. This is one timing round with network/service variance.

## Cleanup, warnings and limits

All hosts ended with `helpersLeft: []`; every case that started a helper recorded its disappearance. Original revocation counts were 15/15/15/10 on d69/k72/m74/f44; each capture-capable host revoked all three additional links. All eight locks were released after verified-clean checks. `run.log` holds the actual commands’ output and releases; final lock status files confirm release. Socket preflight measured 33 UTF-8 bytes on all four hosts.

`warning-and-handover-excerpts.txt` and per-host `events.jsonl` retain sanitized operation and warning lines. k72, m74 and f44 logged portal app-ID registration warnings; d69 logged no warnings or errors. m74 and f44 logged GStreamer external plugin loader warnings (recording was not tested). m74 logged two Qt GNOME-theme D-Bus NoReply warnings; these may have affected elapsed time, but their cause was not established. f44 additionally logged tray ServiceUnknown, three Wayland text-input warnings and eight `clipboard_unavailable` automatic-copy outcomes; uploads and shares still completed. No warning was suppressed or retried. The two-helper observations are additional acceptance failures even though the original harness marks back-to-back passed based on successful uploads and cleanup.

No task-family cancelled-attempt scratch or held lock was found. d69 initially had another family’s stale `scroll-fix7-1398` desktop lock; its owner released it at 04:07 UTC after coordination, before our acquire. We broke no locks and stopped no other family’s process. Their shared build/test work continued and can affect timing. Environment snapshots include uptime/load at 04:12 UTC (during d69, after the other runs); start-of-run load was not recorded. Existing d69 `~/work/pf2` was untouched. No desktop logout, compositor changes, extension workaround or wall redirection occurred.

`history.png` on d69, k72 and m74 was visually inspected: the real app’s History window lists the synthetic uploads and captures as Shared link and displays the tested build. f44 has no screenshot evidence because capture was unavailable. Older `ci-status.json` and `ci-failure.log` preserve only the stopped dcfa09b3b attempt; `ci-final-status.json` describes this successful exact-head CI run.

Observed process pairs (PID/startTicks):

- d69: 3882718/224258475, 3882893/224258983.
- k72: 3296407/113687762, 3296595/113688234.
- m74: 495425/185428694, 495566/185429001.
- f44: 3904306/90760381, 3904493/90760872.

## Black capture found in visual inspection

d69 `desktop-now` uploaded and shared an entirely black 1920×1080 PNG; the harness marked it passed because it checks upload/share states, not pixels. This is a visual acceptance failure. `black-desktop-now.png` preserves it; `capture-pixel-check.json` records RGB extrema (0,0) for all three channels. The original `results.json` has not been relabeled. The 3.59 s total must not be treated as a like-for-like screenshot speed improvement: this PNG was only 8,151 bytes, versus 359,853 bytes in the baseline. Later d69 PNGs and all k72/m74 PNGs were nonblack. The cause was not established, and no retry was run.
