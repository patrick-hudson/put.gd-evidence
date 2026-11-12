# k72 Proton revoke reliability for PR #1414

The failure reproduced on both builds: PR 2/93 first-attempt revocations failed; nightly 1/93 failed. This run does not establish a failure unique to the PR. All failures ended `unknown` with `authentication_required`.

| Pass | Build | Shared of 31 | Revoked first time of 31 | Failures: index / UTC start / error |
| --- | --- | --- | --- | --- |
| 1 | PR | 31/31 | 30/31 | 11 / 2026-11-12T07:51:24.370Z / authentication_required |
| 2 | nightly | 31/31 | 31/31 | None |
| 3 | PR | 31/31 | 31/31 | None |
| 4 | nightly | 31/31 | 30/31 | 30 / 2026-11-12T08:04:17.986Z / authentication_required |
| 5 | PR | 31/31 | 30/31 | 3 / 2026-11-12T08:06:41.267Z / authentication_required |
| 6 | nightly | 31/31 | 31/31 | None |

Totals: PR shared 93/93, revoked first time 91/93, failures 2/93. Nightly shared 93/93, revoked first time 92/93, failures 1/93.

Tested only k72, six alternating app runs, one private profile per pass, 31 sequential 64 KiB synthetic file uploads per run to k72's configured isolated Proton lab folder. Uploads used the round-4 harness file-upload path. Revocations used its history.list order and linkAvailable filter, history.revokeLink per item, and unchanged share.inspect polling condition/interval/budget. Instrumentation adds UTC milliseconds, durations, identities and sanitized request/results. Index is revocation order, not upload order. No within-pass retry. Scripts as run are included; proton_accept.py is unchanged from round 4. Command: `cd ~/work/kr61 && python3 -u run.py`, orchestrated from `/tmp/kr61/drive.py`.

PR is the reused round-4 ubuntu26.04 DEB from CI run 43170857019, SHA-256 verified against round 4 at evidence commit a39b6a0f. Requested head 0a6014c8c42c1929d148cb6d13826d0a15c1509f; packaged merge fe1e300569344866158e968f4f9bd513457ca2a5, version 26.1112.4657-dev+gfe1e30056934. Control is latest published nightly at selection, v26.1111.4633-nightly, git commit 4f80bcfffc047087d69a5e469a08d9f6397249f3, ubuntu26.04 DEB; SHA-256 matched GitHub's asset digest. Both packages were freshly extracted with dpkg-deb -x; nothing compiled, installed or changed in product source. Package hashes and provenance are included.

Each failed link was inspected once after the sequence: all three inspections returned shared. Each single cleanup retry returned revoked before the next pass. Exact inspection/retry times and results are in per-pass results.json. Every link ended revoked (186/186). All six runs report no putgd processes left; 21 seconds of no putgd process separated passes, with another process check before each start. Socket preflight resolved /run/user/1000/putgd/session.sock to 33 UTF-8 bytes. Both locks were checked before app start and heartbeated every minute; verified-clean release receipts are included. No screenshots or other cases ran.

Odd observations: none of the three revocation failures produced a corresponding app-log error line. failure-context.txt contains the nearest app log lines bracketing each failed request; there are no log entries in between. Each pass logged the same startup warning: host portal could not register app ID putgd-ui (app info not found). There were no other warning/error lines in the six app logs. The error's suggestion to reconnect was not followed: the subsequent read-only inspection and explicit retry succeeded in the same app run, without sign-in, sign-out or session copying.

App logs are p1/app.jsonl through p6/app.jsonl; resident.log is captured stdout/stderr (empty). No share links, tokens, keyring contents or payloads are published. Source test files remain private on k72; no existing user objects were changed. No merge, close or approval performed.
