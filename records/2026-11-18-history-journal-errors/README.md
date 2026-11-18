# History when the journal cannot be read or written (#1576, #1579)

Pictures and fault-shim results for put.gd-desktop PRs #1577 (startup journal recovery) and the #1579 fix
(an operation's final result that the journal refused). Host: d69 (Debian 13, Qt 6.8.2), ASan builds,
private `dbus-run-session`, offscreen QPA. No real cloud accounts: the opaque test provider, the loopback
custom-uploader fixture and the offline S3 oracle from the fault harness (#1585).

## Pictures

- `1577-history-journal-error-annotated.png`: History while startup recovery fails (`history.sqlite` cannot
  be opened). Built from `fix/journal-recovery-retry` at 218e28cd4 (later commits on the branch change tests
  only). Before this change the footer said "Waiting for the resident journal to initialize." forever.
- `1579-history-unsaved-result-annotated.png`: an upload that finished while the journal refused writes.
  History shows the real outcome ("Uploaded") marked "Not saved in History yet; put.gd keeps trying".
  Built from `fix/history-terminal-write-retry` at 44bade37.

## Fault shim: a read error partway through startup recovery (#1577, S3)

A journal of 200 operations (132 pages) where only the last one, `op-199`, is still running. The resident
starts under `faultshim.c` with `rule read history.sqlite 1.0 EIO skip=K count=1`: one read of the
operations scan fails, then the disk works again.

| Build | K = 20, 40, 60, 80, 100 |
| --- | --- |
| old recovery (ac3a49cce) | resident ready, `op-199` stays `running` for good |
| fixed (#1577 head) | `op-199` recovered as `interrupted` (the failed recovery is retried) |

With every read failing from K on (`rule read,open history.sqlite 1.0 EIO skip=K`), K = 20 to 110 leaves the
fixed resident not ready during the fault, and after the fault is lifted it is ready with `op-199` interrupted.

## Fault shim: the #1579 repro

Custom uploader fixture, a 6 MiB `upload.files`, then `rule write,truncate,fallocate,fsync history.sqlite 1.0 EIO`
after 0.4 s (and after 0.1 s), lifted when the operation has ended, then 60 s.

| Fault after | During the fault (`operation.recent`) | After the lift |
| --- | --- | --- |
| 0.4 s, before | `running/uploading` | row `uploading` forever, server holds the file |
| 0.4 s, fixed | `completed`, item `uploaded`, `resultUnsaved: history_io`, `unsavedResults` 1 | row `uploaded`, operation `completed`, server holds the file |
| 0.1 s, before | `acquiring/preparing`, no History row | unchanged |
| 0.1 s, fixed | `failed` with `history_io`, `resultUnsaved` | operation `failed` (`history_io`, Retry offered), nothing on the server |
