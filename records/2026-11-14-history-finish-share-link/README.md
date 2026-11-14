# History Finish share link: m74 desktop acceptance, PR #1512

Acceptance is blocked by a detail-pane wording defect and the specified CI run's failed required summary. No product code was changed by this test worker.

## Build and host

- Linux Mint 22.3 (Zena), physical Cinnamon 6.6.9 on X11, display :0, distro Qt 6.4.2 (`6.4.2+dfsg-21.1build5`). Light theme, 1100×700 History window. Native desktop remained visible on the display wall.
- Package: `26.1114.4981~dev+g19cf0d74a6c4`, Ubuntu 24.04 DEB from artifact `release-native-ubuntu24.04` of [CI run 43568252357](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/43568252357).
- Tested commit: `19cf0d74a6c424b9357aa3cfc96d8e5478b5766e`; tested tree: `884fcb0cc4dd30b19ad14b0330ea2dcef5524230`. Both were read from the test worktree's HEAD before CI completed. Installed `putgd-cli diagnostics` reports exactly this commit/tree and a clean build; see [identity](identity.json).
- The worktree advanced during the wait to `cba0ea68150cfd5893db3413fe7efc302f3e9d44` (tree `a165979bebda53501a9acbf052932a2ff7784c87`). That commit changes only the legacy migration test expectation. This record does not claim that newer exact tree was tested.
- CI was watched in the foreground to completion with `gh run watch 43568252357 -R patrick-hudson/put.gd-desktop --interval 60`. All package jobs passed. Linux 24.04, Linux 26.04 and sanitizer jobs failed `HistoryTest::populatedLegacyMigrationPreservesReceipts`; the old expected JSON lacks `linkFinishable:false`. Required `CI` failed; `packages / collect` was skipped.

## Method and observed results

An installed private resident used `/tmp/l1512` with separate config/data/state/cache/runtime directories and the m74 lab Proton keychain reference. Resolved socket preflight: session socket 37 UTF-8 bytes, session bus 18, X11 socket 17; all below 107. Every CLI request used `--socket` and `--params-stdin`. Synthetic PNGs were 63,293 bytes (about 62 KiB). Uploads stayed within the isolated lab folder. No account session or token was exported; no user object or bucket policy was changed.

Each unknown state came from stopping the exact resident PID, adding a `running` create journal row using the item's receipt, and restarting. Recovery returned `shareStatus=unknown`, `shareIntent=create`, `linkFinishable=true`. It did not replay sharing automatically. Row 1 used an actual xdotool pointer click on its row button. Annotations were saved by put.gd's own editor (`editor.open`, `editor.apply`, `editor.saveCopy`, `editor.cancel`).

| Brief row | Result | Observed values |
| --- | --- | --- |
| 1. Link not made → one click | **FAIL (wording); functional PASS** | Row says Share link not finished; finishableIds includes the item. Finish share link and Inspect link are offered; Create share link is hidden. Click completes shared, link present, clipboard exactly matches, one item and one upload attempt total. Logs show inspect/private then create/shared. Row becomes Shared link. Firefox (the default browser) loads the uploaded PNG. **Before clicking, the detail pane omits Share link not finished and shows only No local copy is available…** |
| 2. Existing link | PASS | ui.history finishShareLink returns shared with the exact original URL. One upload attempt total. Original upload logs create/shared; recovery retry logs inspect/shared only, with no second create. |
| 3. Agent path | PASS | operation.retry scope sharing resolves unknown to shared, a link is present, one item and one upload attempt total, inspection then create. Bogus scope returns invalid_request. |
| 4. Refusal | PASS | A real upload to a syntactically valid nonexistent lab folder ends partial with one failed item (operation_failed). Sharing retry returns retry_would_upload; operation.inspect is unchanged afterward, zero Upload attempt events and zero sharing calls. The row offers Retry upload and finishableIds is empty. |
| 5. File changed | NOT RUN | Inspected tools/proton runtime/protocol for a revision-upload action; the helper exposes upload/stat/reconcile/share but no revision replacement action. No external file revision was made. Product testing stopped when the pane defect was identified during evidence inspection. The fixture contract named in the brief is not live desktop evidence. |
| 6. Running wording | PASS | Captured Creating share link… in the active row and progress heading. See running-00.png. |

Numeric receipts: [row 1](row1-outcome.json), [row 2](row2-outcome.json), [row 3](row3-outcome.json), [refusal](row4b-retry.json), [refusal UI](row4b-ui.json), [structured log summary](log-summary.json). Log order in the summary groups files rather than sorting time; timestamps identify original upload versus retry.

## Defect for implementation owner

When the upload has no retained local copy, the unknown/create item's inspector loses its sharing outcome. Reproduction: private upload; recovered running create journal; select the item with the inspector open. Expected: Share link not finished remains in the pane alongside the local-copy hint. Observed: only No local copy is available. You may still be able to download the uploaded image from its destination. The row and Finish button are correct.

The [before pane screenshot](annotated/before.png) proves the missing pane line while the row displays it. Code inspection points at `src/ui/HistoryWindow.cpp:152`: `missingLocalCopyHint` compares `remoteStateText(data)` against `remoteStateText({shareStatus})`; the latter omits shareIntent, so unknown/create produces different phrases and the outcome prefix is dropped. This is a diagnosis from source inspection, not a fix. No further product testing was performed after recognizing this defect.

## Pictures

- [Before, pane](annotated/before.png)
- [Before, row button](annotated/before-row.png)
- [After, pane](annotated/after-pane.png)
- [After, row](annotated/after-row.png)
- [Running wording](running-00.png)
- [Default Firefox loaded image](browser.png)
- [Refused operation's Retry upload](refusal-corrected.png)

## Attempts, retention and cleanup

Harness corrections were retained: initial item-ID lookup used the wrong operation field; initial selection needed ui.show/history; the native window title is put.gd rather than History. The first unreadable-file attempt was correctly refused as files_rejected before creating an operation. Two invalid profile shapes were rejected before the final syntactically valid nonexistent folder produced the failed upload. The initial refusal screenshot used stale geometry; refusal-corrected.png uses the actual app window. An export attempt could not read the intentionally unreadable synthetic file; permissions were restored before the successful export. These are harness/setup attempts, not additional product defects.

Private attempts and raw structured logs were exported with matching SHA-256 `109d71ace3c584d02cc409f19f96efa92cb22b80a08ee0c42a94d5620cea277b` on m74 and the workstation. The private archive excludes config/data/cache/runtime and full diagnostics. It remains outside release source and this record.

After export, the exact resident PID was terminated; its UI/helpers exited. Only putgd was removed with apt (no autoremove or upgrade). dpkg reports deinstall ok config-files; no putgd or putgd-ui processes remain. All test config/data/state/cache/runtime files were unlinked individually, then their empty directories removed (27 files). Both leases released with --verified-clean: desktop at 2026-11-14T07:14:40Z, Proton at 07:14:43Z. Cleanup preserved shared SSH PIDs 313646 and 313651. Host receipts are under ~/putgd-lab/locks/history/2026-11-14T07-14-40Z-release.json and 2026-11-14T07-14-43Z-proton-release.json. No lent Proton copy or VM was created. The three small successful synthetic uploads remain in the lab account by design.
