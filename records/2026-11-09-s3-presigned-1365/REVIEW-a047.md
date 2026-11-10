# Review correction and nightly merge at a047dde62

Final code head: `a047dde62ba943cb15b38d7206d8df5f167249ce`; code PR #1366, companion docs PR #1367. This extends the accepted d089 evidence below; it does not replace its unchanged storage, browser or five-desktop results.

The final head is a merge commit with parents 96dc08715 and cdac6e4b3. Nightly editor changes merged without conflicts; the review fixes themselves are byte-identical to 96dc. The docs PR still merges cleanly and needs no merge commit.

## Changes and regression proof

History copy captures the item ID and saved keychain mode before dispatch. Inspector, row action and row menu share the helper. Its reply discards another selection's result and never reads currentDetail_. Only the explicit unlock click dispatches history.unlockLinkCredentials; its remembered item ID must still match the selected item. A delayed same-item detail does not hide the offered action, and compact row failures open the details pane.

The S3 presigned example uses the endpoint host, ignores a stored custom link domain, displays ?X-Amz-Signature=… and is visible under validity instead of the hidden Link domain row. Public mode preserves its domain and ACL preference. The single extra review round also found mode changes saving incomplete dependent settings: validity and the B2 domain leaf now save together with the mode while preserving unrelated queued edits. The worker's existing omission of public ACLs in presigned mode is unchanged.

History public records always contain linkRefreshable, false without expiry; the identity-change test asserts the exact link_changed code.

On Debian builder d69, new tests against the accepted d089 UI reproduced five History failures (row/menu unlock missing, stale button/row/menu replies exposed unlock for another selection) and the wrong S3 example host. Corrected History GUI, Settings GUI and History unit suites passed. The extra-round regression reproduced three failures against 71cd (legacy validity/public-read combinations and blocked connection-test admission). The corrected full Settings suite passed in 53.97s, both local S3 presigned/no-public-ACL oracle cases passed, and the form test passed at 150%. CI's wait lint initially rejected two test-only settle/assert waits; the required steady helpers corrected them. All attempts remain privately archived on d69; `data/review-96dc-regression-proof.json` retains outcomes and log checksums.

## CI at the merged head

Required [CI 42739011540](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42739011540) and [full package CI 42739024320](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/42739024320) passed at a047dde62. The first two required attempts hit a 20-minute dependency-download timeout before tests. Failed jobs were retried without changing source; attempt 3 passed. The full workflow passed all 144 Ubuntu 24 tests, Ubuntu 26, sanitizers, native/AppImage/source/SBOM and vulnerability audits. Safe summaries and retry log checksums are in `data/review-a047-*.json`. The Ubuntu 24 DEB is version `26.1110.4430-dev+ga047dde62ba9`, SHA-256 `8035e4c7682dd994124b88ee548d6fa60acfc84feaadb4715fd38c16647a8e60`.

## Focused native acceptance

Passed on physical **k72, Kubuntu 26.04, Plasma 6.6.6 / Wayland, Qt 6.10.2**, using the Ubuntu 26.04 DEB extracted under a private root. The coordinator redirected this run from queued Cinnamon to free Plasma. Session `509`, shell PID `3440893`, boot `a4df139d-cadf-4e3e-845a-151648c295c3`; the session was visibly unlocked before use and stayed on its existing wall tile.

Package version `26.1110.4430-dev+ga047dde62ba9`, head `a047dde62ba943cb15b38d7206d8df5f167249ce`, SHA-256 `ddb956b907710cd8d05971e47422df28ec1813136f9b308ea4759f0196602527`. All five inspected product programs reported this head. The earlier Ubuntu 24 package download on m74 was an unused preflight, with no GUI run.

An existing-style public destination had `aclMode: public-read`, `publicUrlBase: https://cdn.example.invalid` and no stored validity. Real combo changes selected presigned, saved the default seven days and preserved the ACL preference, then returned to public and restored the CDN example; switching back to presigned displayed the S3 endpoint and signature marker. The same settings were checked at 150%.

For both AWS S3 and B2, a resident restart disabled startup credential loading. Inspector-button copy, the selected row's native accessible **Copy link** action, and pointer selection of **Copy link** in that row's real context menu all offered the correct bound unlock action. Cached-only credential hints stayed unavailable and links stayed expired through all six checks. Only clicking **Unlock saved credentials**, followed by a separate copy, loaded the reference and renewed the link. Each fresh GET returned 200 and native `wl-paste` equalled the copied link. The script-only short S3/B2 links were actually refused with 403/401.

AWS operation `77427e49-9d98-4525-9a6d-cae419316754`, History `72920922-dbc3-4176-846c-88f36ebbf8bd`; B2 operation `d0ac11ef-901d-46ae-aa24-bb325ff5b239`, History `8e0928df-d9d0-42ed-b0eb-2fe973e7b41a`. These two objects were reused across driver resumes; no extra uploads were made.

Four retakes from this exact package, all annotated with put.gd's production MCP editor and cropped to its own surface:

| Picture | What is called out |
| --- | --- |
| [100% form](pictures/review-a047-s3-form-100.png) | Endpoint-host example and signature marker, with a CDN domain configured |
| [150% form](pictures/review-a047-s3-form-150.png) | Same example, mode, seven-day validity and domain/temporary-credential notes |
| [S3 row unlock](pictures/review-a047-s3-row-unlock.png) | Explicit unlock after the selected S3 row action |
| [B2 row unlock](pictures/review-a047-b2-row-unlock.png) | Explicit unlock after the selected B2 row action |

The retakes show **Plasma**, replacing the earlier Cinnamon views. Every other after picture retains the accepted d089 identity, and before pictures retain round-start nightly. No working bearer URL is shown in full.

The coordinator explicitly limited this correction to one desktop: the presigned form and saved-credential copy through the button, row action and row menu, followed by explicit unlock and copy. No full five-desktop, live Test connection, R2, browser or memory campaign is repeated. Four pictures are retaken: form 100%/150% with a domain configured, and S3/B2 explicit unlock reached through the row action. Other pictures retain their accepted d089 identities. `data/review-96dc-unchanged-storage.json` records the seven lane correction paths before the nightly merge. `data/review-a047-scope.json` proves the backend paths remain byte-identical to accepted d089 and those correction paths remain unchanged by the merge.

## Review handling

The initial three inline threads received explanatory replies and were resolved. Both nitpicks were fixed. The docstring-coverage note received one line explaining it is not a repository rule. The requested single extra round was audited about seven minutes after the prior push, and its outside-diff mode-saving finding was fixed at 96dc. CodeRabbit's subsequent review of 96dc completed at 01:33:34 UTC with no new inline thread. Its merge-head review completed at 02:04:45 UTC, selecting the two merged MCP files; it repeated only the nonbinding docstring note and raised no actionable finding. Zero threads remain open. No review was requested, no PR watch was registered, and neither pull request was merged.

The merged tree was built on d69, then passed eight affected suites (History GUI, Settings destinations, History unit, local IPC, editor unit, editor job, edit operations, editor window), plus all seven MCP integration tests using the production CLI. Safe results/log checksums are in data/review-a047-merge-tests.json. No documentation merge was needed: #1367 remained mergeable against the new nightly.

## Driver preparation and cleanup

Driver preparation needed the distro AT-SPI probe packages, explicit KWin placement, the RFB Enter key name, the custom label's accessible name, and native handling of painted row actions and unexported menu items. Pointer clicks wait for stable geometry after preview reflow; offscreen inspector controls are revealed by scrolling. Qt's 150% accessibility coordinates are logical while KWin reports physical coordinates, so the final 150% frame was positioned and checked visibly, then annotated through the same MCP editor. Failed preparation views/logs are retained privately and checksummed in `data/review-a047-acceptance-proof.json`; none required a product change. Five preflight references were removed before the two-object acceptance run.

Both objects were guarded-deleted and their refreshed URLs confirmed 404. Both run references were removed, and only the known test bearer clipboard was cleared. The two newly installed probe packages (`python3-pyatspi`, `libatk-adaptor`) were purged without autoremove; no system put.gd package was installed or changed. Owned app/helper processes stopped, and the original idle Plasma desktop was saved visibly. The lease was released with its cleanup check at **03:12:32 UTC**.

Private source, packages, drivers and failed attempts are archived on k72 at `~/work/putgd-archives/2026-11-09-1365/review-a047`. Eight private temporary roots were archived with all 95 regular-file checksums verified; archive SHA-256 `f06b1342e9474b2bf81554456b7684cd69df05bc793e5a11f98721d9ec2d03ae`. The restore index is `data/review-a047-archive.json`. d69's merged source/tests remain under its existing `scratch` archive; m74's unused preparation is archived as `review-pending`. No VM, tunnel, golden or workstation build/test/encoding was used.
