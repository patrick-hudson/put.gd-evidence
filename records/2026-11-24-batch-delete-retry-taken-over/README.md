# Retrying an old batch deletion leaves a file a newer deletion took over (#1773)

Acceptance for put.gd-desktop #1773 on d69 (Debian 13, Plasma Wayland, physical desktop, under its desktop lock),
2026-11-24. Build: a dev build of nightly `b0e0287bd` with the fix (branch `fix/batch-delete-retry-1773`,
commit `f5d33efe5`; the build tree shows `26.1123.1-dev+gb0e0287bd1a0.dirty`). Private resident with its own
XDG folders; destination: the Backblaze B2 test bucket `testphputgd`, prefix `acceptance/b1773-d69/`, restricted
test key held for this session only (scan after cleanup: 16 files, 0 matches).

Steps and observed results:

1. Two synthetic PNGs, `b1773-first.png` and `b1773-second.png`, uploaded to B2 for real.
2. With the resident stopped, the old batch deletion's stopped state was written into the History database the
   way `HistoryStore` writes it: both files `failed` with `destination_removed`, nothing sent (`progress` has no
   `phase`). There is no practical way to make a real batch stop for one file before any request on demand;
   everything after this step is real.
3. `b1773-first.png` deleted on its own through `delete.prepare` / `delete.confirm`: B2 removed it; its History
   entry names the newer deletion (`4aecae7f…`), `removed`.
4. History (frame `history-before-retry.png`): `b1773-second` shows Deletion failed with **Retry deletion**;
   `b1773-first` shows Deleted from destination.
5. **Retry deletion** clicked with a real pointer through the wall VNC. The old batch finished `completed`:
   `b1773-second` `removed` on B2, `b1773-first` `taken_over` with `takenOverBy` the newer deletion and no request
   sent. `b1773-first`'s History entry still names the newer deletion. B2 lists neither file afterwards.
6. History said: "Deleted “b1773-second.png” from #1773 B2 d69 · testphputgd." and "“b1773-first.png” is handled by
   a newer deletion of it; its entry in History shows that one." (`history-after-retry.png`, annotated in
   `history-retry-taken-over-annotated.png` with put.gd's editor).

Before the fix the old batch's retry rewrote `b1773-first`'s History state with its own deletion ID and outcome;
the regression test `StorageContract::retriedBatchLeavesAFileANewerDeletionTookOver` fails on nightly `b0e0287bd`
for that reason (d69: `deleteOperationId` was `old-batch`, expected `newer`).
